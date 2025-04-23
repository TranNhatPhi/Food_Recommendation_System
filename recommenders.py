import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
from surprise import Dataset, Reader, SVD, KNNBasic

class ContentBasedRecommender:
    def __init__(self):
        self.tfidf = None
        self.cosine_sim = None
        self.foods = None
        self.indices = None

    def fit(self, foods_df):
        self.foods = foods_df
        # Tạo ma trận TF-IDF từ đặc điểm món ăn
        self.tfidf = TfidfVectorizer(stop_words='english')
        tfidf_matrix = self.tfidf.fit_transform(foods_df['features'])

        # Tính độ tương tự cosine
        self.cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)

        # Tạo mapping từ food_id sang vị trí trong ma trận
        self.indices = pd.Series(foods_df.index, index=foods_df['food_id']).drop_duplicates()

    def recommend(self, food_id, top_n=10):
        if food_id not in self.indices:
            return pd.DataFrame()

        idx = self.indices[food_id]
        sim_scores = list(enumerate(self.cosine_sim[idx]))
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
        sim_scores = sim_scores[1:top_n + 1]  # bỏ chính nó, lấy top_n
        food_indices = [i[0] for i in sim_scores]

        result = self.foods.iloc[food_indices].copy()
        # Thêm điểm tương tự vào kết quả
        result['similarity_score'] = [i[1] for i in sim_scores]
        return result

    def get_similar_by_features(self, features, top_n=10):
        # Chuyển đổi đặc điểm thành vector TF-IDF
        features_vec = self.tfidf.transform([features])

        # Tính độ tương tự với tất cả món ăn
        sim_scores = cosine_similarity(features_vec, self.tfidf.transform(self.foods['features']))
        sim_scores = sim_scores.flatten()

        # Tạo DataFrame với điểm tương tự
        result_df = self.foods.copy()
        result_df['similarity_score'] = sim_scores

        # Sắp xếp và trả về top_n
        return result_df.sort_values('similarity_score', ascending=False).head(top_n)


class CollaborativeRecommender:
    def __init__(self, algorithm='svd'):
        self.algorithm = algorithm
        self.model = None
        self.foods = None
        self.ratings = None
        self.reader = Reader(rating_scale=(1, 5))

    def fit(self, ratings_df, foods_df):
        self.ratings = ratings_df
        self.foods = foods_df

        # Chuyển ratings thành dạng surprise có thể sử dụng
        data = Dataset.load_from_df(ratings_df[['customer_id', 'food_id', 'rating']], self.reader)
        trainset = data.build_full_trainset()

        # Chọn và huấn luyện mô hình
        if self.algorithm == 'svd':
            self.model = SVD()
        elif self.algorithm == 'knn':
            self.model = KNNBasic()
        else:
            self.model = SVD()  # default

        self.model.fit(trainset)

    def recommend_for_customer(self, customer_id, top_n=10):
        if customer_id not in self.ratings['customer_id'].unique():
            return pd.DataFrame()

        # Lấy danh sách món ăn mà khách hàng chưa đánh giá
        rated_foods = self.ratings[self.ratings['customer_id'] == customer_id]['food_id'].unique()
        foods_to_predict = [food_id for food_id in self.foods['food_id'] if food_id not in rated_foods]

        # Dự đoán điểm cho các món chưa đánh giá
        predictions = []

        for food_id in foods_to_predict:
            predicted_rating = self.model.predict(customer_id, food_id).est
            predictions.append((food_id, predicted_rating))

        # Sắp xếp theo điểm dự đoán
        predictions.sort(key=lambda x: x[1], reverse=True)
        top_pred = predictions[:top_n]

        # Lấy thông tin chi tiết về món ăn
        recommended_food_ids = [p[0] for p in top_pred]
        result = self.foods[self.foods['food_id'].isin(recommended_food_ids)].copy()

        # Thêm điểm dự đoán vào kết quả
        rating_dict = {p[0]: p[1] for p in top_pred}
        result['predicted_rating'] = result['food_id'].map(rating_dict)

        return result.sort_values('predicted_rating', ascending=False)


class HybridRecommender:
    def __init__(self, content_weight=0.4, collab_weight=0.6):
        self.content_weight = content_weight
        self.collab_weight = collab_weight
        self.content_recommender = ContentBasedRecommender()
        self.collab_recommender = CollaborativeRecommender()
        self.foods = None
        self.customers = None

    def fit(self, foods_df, ratings_df, customers_df=None):
        self.foods = foods_df
        self.customers = customers_df
        self.content_recommender.fit(foods_df)
        self.collab_recommender.fit(ratings_df, foods_df)

    def recommend(self, customer_id, food_id=None, features=None, top_n=10):
        # Lấy gợi ý từ collaborative filtering
        collab_recs = pd.DataFrame()
        if hasattr(self, 'collab_recommender') and self.collab_recommender is not None:
            try:
                collab_recs = self.collab_recommender.recommend_for_customer(customer_id, top_n=top_n * 2)
            except Exception as e:
                print(f"Lỗi khi lấy gợi ý từ collaborative filtering: {e}")
                collab_recs = pd.DataFrame()
    
        # Nếu có food_id hoặc features, lấy gợi ý từ content-based
        if food_id is not None:
            content_recs = self.content_recommender.recommend(food_id, top_n=top_n * 2)
            content_type = 'food'
        elif features is not None:
            content_recs = self.content_recommender.get_similar_by_features(features, top_n=top_n * 2)
            content_type = 'features'
        else:
            # Nếu không có thông tin và có collaborative filtering
            if not collab_recs.empty:
                return collab_recs.head(top_n)
            # Không có đủ dữ liệu, trả về DataFrame rỗng
            return pd.DataFrame()

        # Chuẩn bị kết quả cho content và collab
        content_result = pd.DataFrame()
        collab_result = pd.DataFrame()

        if not content_recs.empty:
            if content_type == 'food':
                content_result = content_recs[['food_id', 'similarity_score']].copy()
                # Chuẩn hóa điểm tương tự
                if not content_result.empty:
                    max_sim = content_result['similarity_score'].max()
                    if max_sim > 0:
                        content_result['normalized_score'] = content_result['similarity_score'] / max_sim * 5
                    else:
                        content_result['normalized_score'] = content_result['similarity_score']
            else:  # features
                content_result = content_recs[['food_id', 'similarity_score']].copy()
                # Chuẩn hóa điểm tương tự
                if not content_result.empty:
                    max_sim = content_result['similarity_score'].max()
                    if max_sim > 0:
                        content_result['normalized_score'] = content_result['similarity_score'] / max_sim * 5
                    else:
                        content_result['normalized_score'] = content_result['similarity_score']

        if not collab_recs.empty:
            collab_result = collab_recs[['food_id', 'predicted_rating']].copy()
            collab_result.rename(columns={'predicted_rating': 'normalized_score'}, inplace=True)

        # Kết hợp kết quả
        if not content_result.empty and not collab_result.empty:
            # Kết hợp với trọng số
            content_result['weighted_score'] = content_result['normalized_score'] * self.content_weight
            content_set = set(content_result['food_id'])

            collab_result['weighted_score'] = collab_result['normalized_score'] * self.collab_weight
            collab_set = set(collab_result['food_id'])

            # Món ăn xuất hiện ở cả hai
            common_items = content_set.intersection(collab_set)

            # Gộp điểm
            combined_scores = {}

            # Trường hợp món ăn xuất hiện ở cả hai hệ thống
            for food_id in common_items:
                content_score = content_result[content_result['food_id'] == food_id]['weighted_score'].values[0]
                collab_score = collab_result[collab_result['food_id'] == food_id]['weighted_score'].values[0]
                combined_scores[food_id] = content_score + collab_score

            # Trường hợp món ăn chỉ xuất hiện ở content-based
            for food_id in content_set - common_items:
                score = content_result[content_result['food_id'] == food_id]['weighted_score'].values[0]
                combined_scores[food_id] = score

            # Trường hợp món ăn chỉ xuất hiện ở collaborative filtering
            for food_id in collab_set - common_items:
                score = collab_result[collab_result['food_id'] == food_id]['weighted_score'].values[0]
                combined_scores[food_id] = score

            # Sắp xếp và lấy top_n
            sorted_items = sorted(combined_scores.items(), key=lambda x: x[1], reverse=True)[:top_n]
            recommended_food_ids = [item[0] for item in sorted_items]

            # Tạo DataFrame kết quả
            result = self.foods[self.foods['food_id'].isin(recommended_food_ids)].copy()
            score_dict = {item[0]: item[1] for item in sorted_items}
            result['hybrid_score'] = result['food_id'].map(score_dict)

            return result.sort_values('hybrid_score', ascending=False)
        elif not content_result.empty:
            top_items = content_result.sort_values('normalized_score', ascending=False).head(top_n)
            result = self.foods[self.foods['food_id'].isin(top_items['food_id'])].copy()
            score_dict = dict(zip(top_items['food_id'], top_items['normalized_score']))
            result['hybrid_score'] = result['food_id'].map(score_dict)
            return result.sort_values('hybrid_score', ascending=False)
        else:
            top_items = collab_result.sort_values('normalized_score', ascending=False).head(top_n)
            result = self.foods[self.foods['food_id'].isin(top_items['food_id'])].copy()
            score_dict = dict(zip(top_items['food_id'], top_items['normalized_score']))
            result['hybrid_score'] = result['food_id'].map(score_dict)
            return result.sort_values('hybrid_score', ascending=False)
