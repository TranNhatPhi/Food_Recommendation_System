import pandas as pd
import plotly.express as px
import random

def format_price(price):
    """Format giá tiền sang định dạng VND"""
    return f"{price:,.0f} VND"


def generate_food_card(food, score_type=None, score=None):
    """Tạo card hiển thị một món ăn"""
    html = f"""
    <div class="food-card">
        <div class="food-name">{food['name']}</div>
        <div class="food-category">{food['category']} | {food['cuisine']}</div>
        <div>Hương vị: <span class="highlight">{food['flavors']}</span></div>
        <div>Nguyên liệu: {food['ingredients']}</div>
        <div class="food-price">{format_price(food['price'])}</div>
    """

    if score_type and score:
        if score_type == "similarity":
            html += f'<div class="rating">Độ tương tự: {score:.2f}</div>'
        elif score_type == "predicted":
            html += f'<div class="rating">Dự đoán: {score:.2f}/5 ⭐</div>'
        elif score_type == "hybrid":
            html += f'<div class="rating">Điểm gợi ý: {score:.2f}/5 ⭐</div>'
        elif score_type == "user":
            html += f'<div class="rating">Đánh giá: {score}/5 ⭐</div>'

    html += "</div>"
    return html


def get_popular_foods(ratings_df, foods_df, top_n=10):
    """Lấy các món phổ biến nhất dựa trên số lượng đánh giá và điểm trung bình"""
    # Tính số lượng đánh giá và điểm trung bình cho mỗi món
    food_stats = ratings_df.groupby('food_id').agg(
        count=('rating', 'count'),
        avg_rating=('rating', 'mean')
    ).reset_index()

    # Món ăn phải có ít nhất 5 đánh giá
    popular_foods = food_stats[food_stats['count'] >= 5].sort_values('avg_rating', ascending=False).head(top_n)

    # Merge với thông tin chi tiết
    result = pd.merge(popular_foods, foods_df, on='food_id', how='left')
    return result


def get_customer_history(customer_id, ratings_df, foods_df):
    """Lấy lịch sử đánh giá của khách hàng"""
    if customer_id not in ratings_df['customer_id'].values:
        return pd.DataFrame()

    history = ratings_df[ratings_df['customer_id'] == customer_id]
    result = pd.merge(history, foods_df[['food_id', 'name', 'category', 'cuisine', 'price', 'flavors', 'ingredients']],
                      on='food_id', how='left')
    return result.sort_values('rating', ascending=False)


def get_cuisine_popularity(ratings_df, foods_df):
    """Phân tích mức độ phổ biến của các loại ẩm thực"""
    cuisine_ratings = pd.merge(ratings_df, foods_df[['food_id', 'cuisine']], on='food_id')
    cuisine_avg = cuisine_ratings.groupby('cuisine').agg(
        avg_rating=('rating', 'mean'),
        count=('rating', 'count')
    ).reset_index()

    # Lọc các loại có ít nhất 10 đánh giá
    cuisine_avg = cuisine_avg[cuisine_avg['count'] >= 10].sort_values('avg_rating', ascending=False)
    return cuisine_avg


def get_flavor_popularity(ratings_df, foods_df):
    """Phân tích mức độ phổ biến của các hương vị"""
    # Tách cột flavors thành các hương vị riêng lẻ
    all_flavors = []

    for _, row in ratings_df.iterrows():
        food_id = row['food_id']
        rating = row['rating']

        # Lấy hương vị của món ăn
        food_row = foods_df[foods_df['food_id'] == food_id]
        if not food_row.empty:
            flavors_str = food_row['flavors'].values[0]
            flavors = [f.strip() for f in flavors_str.split(',')]

            for flavor in flavors:
                all_flavors.append({
                    'flavor': flavor,
                    'rating': rating
                })

    flavor_df = pd.DataFrame(all_flavors)

    # Tính điểm trung bình và số lượng đánh giá cho mỗi hương vị
    flavor_stats = flavor_df.groupby('flavor').agg(
        avg_rating=('rating', 'mean'),
        count=('rating', 'count')
    ).reset_index()

    # Lọc các hương vị có ít nhất 20 đánh giá
    flavor_stats = flavor_stats[flavor_stats['count'] >= 20].sort_values('avg_rating', ascending=False)

    return flavor_stats


def plot_ratings_distribution(ratings_df):
    """Tạo biểu đồ phân phối điểm đánh giá"""
    fig = px.histogram(
        ratings_df,
        x='rating',
        nbins=9,
        title='Phân phối điểm đánh giá',
        labels={'rating': 'Điểm đánh giá', 'count': 'Số lượng'},
        color_discrete_sequence=['#FF7043']
    )

    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(tickvals=[1, 1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5]),
        yaxis=dict(gridcolor='rgba(200,200,200,0.2)'),
        bargap=0.1
    )

    return fig


def plot_cuisine_popularity(cuisine_data):
    """Tạo biểu đồ đánh giá theo loại ẩm thực"""
    fig = px.bar(
        cuisine_data,
        x='cuisine',
        y='avg_rating',
        color='avg_rating',
        title='Điểm đánh giá trung bình theo loại ẩm thực',
        labels={'cuisine': 'Ẩm thực', 'avg_rating': 'Điểm trung bình'},
        color_continuous_scale=px.colors.sequential.Oranges
    )

    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(title_font=dict(size=14)),
        yaxis=dict(title_font=dict(size=14), gridcolor='rgba(200,200,200,0.2)'),
    )

    return fig
