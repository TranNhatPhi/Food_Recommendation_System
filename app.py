import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import random
import plotly.express as px
import plotly.graph_objects as go
from PIL import Image
import time
import base64
from io import BytesIO

# Import modules
from data_generator import create_food_items, create_customers, create_ratings
from recommenders import ContentBasedRecommender, CollaborativeRecommender, HybridRecommender
from utils import (format_price, generate_food_card, get_popular_foods, get_customer_history,
                   get_cuisine_popularity, get_flavor_popularity, plot_ratings_distribution,
                   plot_cuisine_popularity)
from ui import load_css, setup_page_config, create_sidebar, create_header, create_footer, show_about_tab

# Đặt seed cho kết quả nhất quán
np.random.seed(42)
random.seed(42)


def show_recommendation_tab(sidebar_options, foods_df, ratings_df, content_rec, collab_rec, hybrid_rec):
    """Display content for the Recommendation tab"""
    if sidebar_options["recommend_button"]:
        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
        st.markdown(
            f'<h2 class="sub-header">Món ăn được gợi ý cho khách hàng #{sidebar_options["selected_customer"]}</h2>',
            unsafe_allow_html=True)

        with st.spinner("Đang tạo gợi ý món ăn cho bạn..."):
            # Lấy gợi ý dựa trên phương pháp được chọn
            if sidebar_options["rec_type"] == "Content-Based (Dựa trên nội dung)":
                # Lấy món ăn khách hàng đã đánh giá cao nhất
                user_ratings = ratings_df[ratings_df['customer_id'] == sidebar_options["selected_customer"]]
                if len(user_ratings) > 0:
                    top_rated = user_ratings.sort_values('rating', ascending=False).head(1)
                    top_food_id = top_rated['food_id'].values[0]
                    recommendations = content_rec.recommend(top_food_id,
                                                            top_n=sidebar_options["num_recommendations"] * 3)
                else:
                    # Nếu khách hàng chưa có đánh giá nào
                    popular_foods = get_popular_foods(ratings_df, foods_df,
                                                      top_n=sidebar_options["num_recommendations"])
                    recommendations = popular_foods

            elif sidebar_options["rec_type"] == "Collaborative (Dựa trên cộng đồng)":
                if collab_rec is None:
                    # Nếu recommender chưa được khởi tạo
                    st.warning("Chưa khởi tạo collaborative recommender. Đang hiển thị món ăn phổ biến thay thế.")
                    recommendations = get_popular_foods(ratings_df, foods_df,
                                                        top_n=sidebar_options["num_recommendations"])
                else:
                    if collab_rec is None:
                        # Nếu recommender chưa được khởi tạo
                        st.warning("Chưa khởi tạo collaborative recommender. Đang hiển thị món ăn phổ biến thay thế.")
                        recommendations = get_popular_foods(ratings_df, foods_df,
                                                            top_n=sidebar_options["num_recommendations"])
                    else:
                        recommendations = collab_rec.recommend_for_customer(sidebar_options["selected_customer"],
                                                                            top_n=sidebar_options[
                                                                                      "num_recommendations"] * 3)
                        if recommendations.empty:
                            # Nếu không có đủ dữ liệu
                            popular_foods = get_popular_foods(ratings_df, foods_df,
                                                              top_n=sidebar_options["num_recommendations"])
                            recommendations = popular_foods

            else:  # Hybrid
                # Lấy món ăn khách hàng đã đánh giá cao nhất
                user_ratings = ratings_df[ratings_df['customer_id'] == sidebar_options["selected_customer"]]
                if hybrid_rec is None:
                    # Nếu recommender chưa được khởi tạo
                    st.warning("Chưa khởi tạo hybrid recommender. Đang hiển thị món ăn phổ biến thay thế.")
                    recommendations = get_popular_foods(ratings_df, foods_df,
                                                        top_n=sidebar_options["num_recommendations"])
                else:
                    # Sử dụng món ăn được đánh giá cao nhất (nếu có) như một gợi ý nội dung
                    food_id = None
                    if len(user_ratings) > 0:
                        top_rated = user_ratings.sort_values('rating', ascending=False).head(1)
                        food_id = top_rated['food_id'].values[0]

                    recommendations = hybrid_rec.recommend(
                        customer_id=sidebar_options["selected_customer"],
                        food_id=food_id,
                        top_n=sidebar_options["num_recommendations"] * 3
                    )

                    if recommendations.empty:
                        # Nếu không có đủ dữ liệu
                        popular_foods = get_popular_foods(ratings_df, foods_df,
                                                          top_n=sidebar_options["num_recommendations"])
                        recommendations = popular_foods

            # Áp dụng bộ lọc nếu có
            if sidebar_options["cuisine_filter"]:
                recommendations = recommendations[recommendations['cuisine'].isin(sidebar_options["cuisine_filter"])]

            if sidebar_options["price_range"]:
                recommendations = recommendations[(recommendations['price'] >= sidebar_options["price_range"][0]) &
                                                  (recommendations['price'] <= sidebar_options["price_range"][1])]

            if sidebar_options["flavors_filter"]:
                # Lọc món ăn có chứa ít nhất một trong các hương vị được chọn
                recommendations = recommendations[recommendations['flavors'].apply(
                    lambda x: any(flavor.strip() in sidebar_options["flavors_filter"] for flavor in x.split(',')))]

            # Hiển thị kết quả
            if recommendations.empty:
                st.warning("Không tìm thấy món ăn phù hợp với bộ lọc. Vui lòng thử lại với các điều kiện khác.")
            else:
                recommendations = recommendations.head(sidebar_options["num_recommendations"])

                # Hiển thị món ăn dưới dạng grid
                cols = st.columns(3)
                for i, (_, food) in enumerate(recommendations.iterrows()):
                    col_idx = i % 3

                    with cols[col_idx]:
                        if 'similarity_score' in food:
                            food_card = generate_food_card(food, "similarity", food['similarity_score'])
                        elif 'predicted_rating' in food:
                            food_card = generate_food_card(food, "predicted", food['predicted_rating'])
                        elif 'hybrid_score' in food:
                            food_card = generate_food_card(food, "hybrid", food['hybrid_score'])
                        else:
                            food_card = generate_food_card(food)

                        st.markdown(food_card, unsafe_allow_html=True)

    # Hiển thị món ăn phổ biến nếu không nhấn nút gợi ý
    else:
        st.markdown('<h2 class="sub-header">Món ăn phổ biến</h2>', unsafe_allow_html=True)
        popular = get_popular_foods(ratings_df, foods_df, top_n=9)

        cols = st.columns(3)
        for i, (_, food) in enumerate(popular.iterrows()):
            col_idx = i % 3
            with cols[col_idx]:
                food_card = generate_food_card(food, "user", food['avg_rating'])
                st.markdown(food_card, unsafe_allow_html=True)


def show_analysis_tab(ratings_df, foods_df):
    """Display content for the Analysis tab"""
    st.markdown('<h2 class="sub-header">📊 Phân tích dữ liệu</h2>', unsafe_allow_html=True)

    # Phân tích theo loại
    analysis_type = st.radio(
        "Chọn loại phân tích:",
        ["Phân phối đánh giá", "Ẩm thực phổ biến", "Hương vị phổ biến", "Giá trung bình theo ẩm thực"],
        horizontal=True
    )

    if analysis_type == "Phân phối đánh giá":
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.plotly_chart(
            plot_ratings_distribution(ratings_df),
            use_container_width=True
        )
        st.markdown('</div>', unsafe_allow_html=True)

    elif analysis_type == "Ẩm thực phổ biến":
        st.markdown('<div class="card">', unsafe_allow_html=True)
        cuisine_data = get_cuisine_popularity(ratings_df, foods_df)
        st.plotly_chart(
            plot_cuisine_popularity(cuisine_data),
            use_container_width=True
        )
        st.markdown('</div>', unsafe_allow_html=True)

    elif analysis_type == "Hương vị phổ biến":
        st.markdown('<div class="card">', unsafe_allow_html=True)
        flavor_data = get_flavor_popularity(ratings_df, foods_df)

        fig = px.bar(
            flavor_data,
            x='flavor',
            y='avg_rating',
            text=flavor_data['avg_rating'].round(2),
            title='Đánh giá trung bình theo hương vị',
            color='avg_rating',
            color_continuous_scale=px.colors.sequential.Purples,
            labels={'flavor': 'Hương vị', 'avg_rating': 'Điểm trung bình'}
        )

        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(title_font=dict(size=14)),
            yaxis=dict(title_font=dict(size=14), gridcolor='rgba(200,200,200,0.2)'),
        )

        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    else:  # Giá trung bình theo ẩm thực
        st.markdown('<div class="card">', unsafe_allow_html=True)
        cuisine_price = foods_df.groupby('cuisine')['price'].mean().reset_index()
        cuisine_price = cuisine_price.sort_values('price', ascending=False)

        fig = px.bar(
            cuisine_price,
            x='cuisine',
            y='price',
            text=cuisine_price['price'].apply(lambda x: f"{x / 1000:.1f}k"),
            title='Giá trung bình theo loại ẩm thực',
            color='price',
            color_continuous_scale=px.colors.sequential.Greens,
            labels={'cuisine': 'Ẩm thực', 'price': 'Giá trung bình (VND)'}
        )

        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(title_font=dict(size=14)),
            yaxis=dict(title_font=dict(size=14), gridcolor='rgba(200,200,200,0.2)'),
        )

        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # Số liệu tổng quan
    st.markdown('<h3 class="sub-header">Số liệu tổng quan</h3>', unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Tổng số món ăn", f"{len(foods_df):,}")
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Tổng số khách hàng", f"{len(set(ratings_df['customer_id'])):,}")
        st.markdown('</div>', unsafe_allow_html=True)

    with col3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Tổng số đánh giá", f"{len(ratings_df):,}")
        st.markdown('</div>', unsafe_allow_html=True)

    with col4:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        avg_rating = round(ratings_df['rating'].mean(), 2)
        st.metric("Điểm đánh giá trung bình", f"{avg_rating} ⭐")
        st.markdown('</div>', unsafe_allow_html=True)


def show_customer_tab(sidebar_options, customers_df, ratings_df, foods_df):
    """Display content for the Customer tab"""
    selected_customer = sidebar_options["selected_customer"]

    st.markdown('<h2 class="sub-header">👤 Thông tin khách hàng</h2>', unsafe_allow_html=True)

    # Thông tin cơ bản về khách hàng
    if selected_customer in customers_df['customer_id'].values:
        customer_info = customers_df[customers_df['customer_id'] == selected_customer].iloc[0]

        st.markdown('<div class="card">', unsafe_allow_html=True)
        col1, col2 = st.columns(2)

        with col1:
            st.markdown(f"**ID Khách hàng:** {customer_info['customer_id']}")
            st.markdown(f"**Tuổi:** {customer_info['age']}")
            st.markdown(f"**Giới tính:** {customer_info['gender']}")

        with col2:
            st.markdown(f"**Độ nhạy cảm về giá:** {customer_info['price_sensitivity']:.2f}/1.0")
            st.markdown(f"**Ẩm thực ưa thích:** {customer_info['preferred_cuisines']}")
            st.markdown(f"**Hương vị ưa thích:** {customer_info['preferred_flavors']}")
        st.markdown('</div>', unsafe_allow_html=True)

        # Lịch sử đánh giá của khách hàng
        st.markdown('<h3 class="sub-header">Lịch sử đánh giá</h3>', unsafe_allow_html=True)

        history = get_customer_history(selected_customer, ratings_df, foods_df)
        if not history.empty:
            # Tính toán một số thống kê
            avg_rating = history['rating'].mean()
            most_rated_cuisine = history.groupby('cuisine')['rating'].count().sort_values(ascending=False).index[0]
            highest_rated = history[history['rating'] == history['rating'].max()]

            col1, col2, col3 = st.columns(3)

            with col1:
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                st.metric("Số lượng đánh giá", f"{len(history)}")
                st.markdown('</div>', unsafe_allow_html=True)

            with col2:
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                st.metric("Điểm trung bình", f"{avg_rating:.2f} ⭐")
                st.markdown('</div>', unsafe_allow_html=True)

            with col3:
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                st.metric("Ẩm thực đánh giá nhiều nhất", most_rated_cuisine)
                st.markdown('</div>', unsafe_allow_html=True)

            # Hiển thị các món ăn được đánh giá cao nhất
            st.markdown('<h4 class="sub-header">Món ăn được đánh giá cao nhất</h4>', unsafe_allow_html=True)

            cols = st.columns(3)
            for i, (_, food) in enumerate(highest_rated.head(3).iterrows()):
                col_idx = i % 3
                with cols[col_idx]:
                    food_card = generate_food_card(food, "user", food['rating'])
                    st.markdown(food_card, unsafe_allow_html=True)

            # Biểu đồ phân phối đánh giá của khách hàng
            st.markdown('<div class="card">', unsafe_allow_html=True)
            fig = px.histogram(
                history,
                x='rating',
                nbins=9,
                title=f'Phân phối đánh giá của khách hàng #{selected_customer}',
                labels={'rating': 'Điểm đánh giá', 'count': 'Số lượng'},
                color_discrete_sequence=['#7E57C2']
            )

            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                xaxis=dict(tickvals=[1, 1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5]),
                yaxis=dict(gridcolor='rgba(200,200,200,0.2)'),
                bargap=0.1
            )

            st.plotly_chart(fig, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

            # Danh sách tất cả các đánh giá
            with st.expander("Xem tất cả đánh giá"):
                st.dataframe(
                    history[['name', 'category', 'cuisine', 'price', 'rating', 'days_ago']].sort_values('rating',
                                                                                                        ascending=False),
                    use_container_width=True,
                    column_config={
                        'name': 'Tên món ăn',
                        'category': 'Loại món',
                        'cuisine': 'Ẩm thực',
                        'price': st.column_config.NumberColumn('Giá', format="%d VND"),
                        'rating': st.column_config.NumberColumn('Đánh giá', format="%.1f ⭐"),
                        'days_ago': 'Ngày đánh giá (ngày trước)'
                    }
                )


def show_explore_section(foods_df):
    """Display the Explore New Foods section"""
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    st.markdown('<h2 class="sub-header">✨ Khám phá món ăn mới</h2>', unsafe_allow_html=True)

    explore_options = st.radio(
        "Chọn cách khám phá:",
        ["Ngẫu nhiên", "Theo giá", "Theo ẩm thực", "Theo hương vị"],
        horizontal=True
    )

    col1, col2 = st.columns([3, 1])
    with col2:
        explore_button = st.button("✨ Khám phá ngay", type="primary")

    if explore_button:
        with st.spinner("Đang tìm kiếm món ăn mới cho bạn..."):
            if explore_options == "Ngẫu nhiên":
                discoveries = foods_df.sample(6)
            elif explore_options == "Theo giá":
                price_min = st.session_state.get('price_min', 0)
                price_max = st.session_state.get('price_max', 300000)
                discoveries = foods_df[(foods_df['price'] >= price_min) & (foods_df['price'] <= price_max)].sample(
                    min(6, len(foods_df)))
            elif explore_options == "Theo ẩm thực":
                selected_cuisine = st.session_state.get('selected_cuisine', random.choice(foods_df['cuisine'].unique()))
                discoveries = foods_df[foods_df['cuisine'] == selected_cuisine].sample(
                    min(6, len(foods_df[foods_df['cuisine'] == selected_cuisine])))
            else:  # Theo hương vị
                # Tạo danh sách hương vị duy nhất
                all_flavors = list(set(
                    f.strip() for flavors in foods_df['flavors'] for f in flavors.split(',')
                ))

                # Chọn hương vị mặc định nếu chưa có trong session
                selected_flavor = st.session_state.get('selected_flavor', random.choice(all_flavors))
                discoveries = foods_df[foods_df['flavors'].str.contains(selected_flavor)].sample(
                    min(6, len(foods_df[foods_df['flavors'].str.contains(selected_flavor)])))

            st.markdown("<h3>Món ăn được khám phá:</h3>", unsafe_allow_html=True)

            # Hiển thị kết quả dưới dạng grid
            cols = st.columns(3)
            for i, (_, food) in enumerate(discoveries.iterrows()):
                col_idx = i % 3
                with cols[col_idx]:
                    food_card = generate_food_card(food)
                    st.markdown(food_card, unsafe_allow_html=True)

        # Thiết lập tùy chọn cho lần khám phá tiếp theo
        if explore_options == "Theo giá":
            col1, col2 = st.columns(2)
            with col1:
                st.session_state.price_min = st.slider("Giá tối thiểu:", 0, 300000, step=10000)
            with col2:
                st.session_state.price_max = st.slider("Giá tối đa:", 0, 300000, 300000, step=10000)
        elif explore_options == "Theo ẩm thực":
            st.session_state.selected_cuisine = st.selectbox(
                "Chọn ẩm thực:",
                sorted(foods_df['cuisine'].unique()),
                key=f"cuisine_selectbox_{explore_options}"
            )
        elif explore_options == "Theo hương vị":
            # Tạo danh sách hương vị duy nhất
            all_flavors = set()
            for flavors_str in foods_df['flavors']:
                for flavor in flavors_str.split(','):
                    all_flavors.add(flavor.strip())

            st.session_state.selected_flavor = st.selectbox(
                "Chọn hương vị:",
                sorted(list(all_flavors)),
                key=f"flavor_selectbox_{explore_options}"
            )


def main():
    """Main application function"""
    # Thiết lập giao diện
    setup_page_config()
    load_css()
    create_header()


import streamlit as st
import pandas as pd
from recommenders import ContentBasedRecommender, CollaborativeRecommender, HybridRecommender
from data_loader import load_foods_from_db, load_customers_from_db, load_ratings_from_db, get_customer_ratings, \
    add_rating, get_food_details
from db_utils import get_connection, close_connection
import visualizations as viz

# Thiết lập trang
st.set_page_config(
    page_title="Hệ thống Gợi ý Món ăn Thông minh",
    page_icon="🍲",
    layout="wide"
)

# CSS tùy chỉnh
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #FF5722;
        text-align: center;
        margin-bottom: 1rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    .sub-header {
        font-size: 1.8rem;
        font-weight: bold;
        color: #FF9800;
        margin-top: 1rem;
        margin-bottom: 1rem;
    }
    .card {
        border-radius: 10px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        background-color: #FFF8E1;
    }
    .metric-card {
        background-color: #E3F2FD;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        text-align: center;
    }
    .food-card {
        background-color: white;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
        transition: transform 0.3s;
    }
    .food-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
    .food-name {
        font-weight: bold;
        color: #E65100;
        font-size: 1.2rem;
    }
    .food-category {
        color: #7E57C2;
        font-size: 0.9rem;
    }
    .food-price {
        color: #00897B;
        font-weight: bold;
        font-size: 1.1rem;
    }
    .rating {
        color: #FFA000;
        font-weight: bold;
    }
    .highlight {
        background-color: #FFE0B2;
        padding: 0.2rem 0.5rem;
        border-radius: 4px;
        font-weight: bold;
    }
    .divider {
        height: 3px;
        background: linear-gradient(90deg, rgba(255,87,34,0.7) 0%, rgba(255,193,7,0.7) 100%);
        margin: 1rem 0;
        border-radius: 2px;
    }
    .footer {
        text-align: center;
        margin-top: 2rem;
        padding: 1rem;
        color: #78909C;
        font-size: 0.8rem;
    }
    .stButton>button {
        background-color: #FF5722;
        color: white;
        border: none;
        border-radius: 5px;
        padding: 0.5rem 1rem;
    }
    .stButton>button:hover {
        background-color: #E64A19;
    }
    .sidebar-content {
        padding: 1rem;
    }
    .tab-content {
        padding: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)


def format_price(price):
    """Định dạng giá tiền"""
    return f"{price:,.0f}đ"


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


def load_data():
    """Tải dữ liệu từ database"""
    with st.spinner('Đang tải dữ liệu...'):
        foods_df = load_foods_from_db()
        customers_df = load_customers_from_db()
        ratings_df = load_ratings_from_db()

        # Hiển thị thông báo nếu không thể tải dữ liệu
        if foods_df.empty or customers_df.empty or ratings_df.empty:
            st.error("Không thể kết nối tới database hoặc dữ liệu trống. Vui lòng kiểm tra kết nối.")
            st.stop()

        return foods_df, customers_df, ratings_df


def initialize_recommenders(foods_df, ratings_df, customers_df):
    """Khởi tạo các recommender"""
    if 'recommenders_initialized' not in st.session_state:
        with st.spinner('Đang huấn luyện mô hình gợi ý...'):
            # Khởi tạo recommenders
            content_recommender = ContentBasedRecommender()
            collab_recommender = CollaborativeRecommender()
            hybrid_recommender = HybridRecommender()

            # Huấn luyện các mô hình
            content_recommender.fit(foods_df)
            collab_recommender.fit(ratings_df, foods_df)
            hybrid_recommender.fit(foods_df, ratings_df, customers_df)

            # Lưu các recommender vào session_state
            st.session_state.content_recommender = content_recommender
            st.session_state.collab_recommender = collab_recommender
            st.session_state.hybrid_recommender = hybrid_recommender
            st.session_state.recommenders_initialized = True


def main():
    st.title("🍲 Hệ thống Gợi ý Món ăn Thông minh")

    # Khởi tạo recommenders trong session state nếu chưa có
    if "content_recommender" not in st.session_state:
        st.session_state.content_recommender = None
    if "collab_recommender" not in st.session_state:
        st.session_state.collab_recommender = None
    if "hybrid_recommender" not in st.session_state:
        st.session_state.hybrid_recommender = None

    # Tải dữ liệu
    foods_df, customers_df, ratings_df = load_data()

    # Khởi tạo các recommender
    initialize_recommenders(foods_df, ratings_df, customers_df)

    # Sidebar: Chọn khách hàng và chức năng
    st.sidebar.title("Tùy chọn")

    # Chọn khách hàng
    customer_id = st.sidebar.selectbox(
        "Chọn khách hàng:",
        options=customers_df['customer_id'].tolist(),
        format_func=lambda x: f"{x} - {customers_df[customers_df['customer_id'] == x]['name'].values[0]}"
    )

    # Hiển thị thông tin khách hàng
    customer_info = customers_df[customers_df['customer_id'] == customer_id].iloc[0]
    st.sidebar.write(f"**Tên:** {customer_info['name']}")
    st.sidebar.write(f"**Tuổi:** {customer_info['age']}")
    st.sidebar.write(f"**Giới tính:** {customer_info['gender']}")

    # Chọn chức năng
    menu = st.sidebar.radio(
        "Chọn chức năng:",
        options=["Gợi ý món ăn", "Tìm kiếm món ăn", "Đánh giá món ăn", "Phân tích dữ liệu"]
    )

    # Hiển thị chức năng tương ứng
    if menu == "Gợi ý món ăn":
        show_recommendations(customer_id, foods_df, ratings_df, customers_df)
    elif menu == "Tìm kiếm món ăn":
        search_foods(foods_df)
    elif menu == "Đánh giá món ăn":
        rate_foods(customer_id, foods_df, ratings_df)
    elif menu == "Phân tích dữ liệu":
        analyze_data(foods_df, ratings_df)

    # Đảm bảo đóng kết nối khi app kết thúc
    st.sidebar.markdown("---")
    if st.sidebar.button("Đóng kết nối Database"):
        close_connection()
        st.sidebar.success("Đã đóng kết nối Database")


def show_recommendations(customer_id, foods_df, ratings_df, customers_df):
    st.header("Gợi ý món ăn")

    # Chọn phương pháp gợi ý
    recommendation_type = st.radio(
        "Chọn phương pháp gợi ý:",
        options=["Dựa trên cộng đồng", "Dựa trên nội dung", "Kết hợp"]
    )

    # Hiển thị các tùy chọn dựa trên phương pháp được chọn
    if recommendation_type == "Dựa trên cộng đồng":
        st.subheader("Gợi ý dựa trên cộng đồng")
        st.write("Hệ thống sẽ gợi ý món ăn dựa trên đánh giá của những khách hàng có sở thích tương tự bạn.")

        # Trích xuất recommender từ session state
        collab_recommender = st.session_state.collab_recommender

        # Hiển thị số lượng gợi ý muốn nhận
        num_recommendations = st.slider(
            "Số lượng gợi ý:",
            min_value=5,
            max_value=20,
            value=10,
            step=5
        )

        # Thêm bộ lọc tùy chọn
        with st.expander("Bộ lọc tùy chọn"):
            # Lọc theo ẩm thực
            cuisine_options = sorted(foods_df['cuisine'].unique())
            cuisine_filter = st.multiselect(
                "Lọc theo ẩm thực:",
                options=cuisine_options,
                key="collab_cuisine_filter"
            )

            # Lọc theo khoảng giá
            min_price = int(foods_df['price'].min())
            max_price = int(foods_df['price'].max())
            price_range = st.slider(
                "Khoảng giá:",
                min_value=min_price,
                max_value=max_price,
                value=(min_price, max_price),
                step=10000,
                key="collab_price_range"
            )

        # Lấy gợi ý dựa trên collaborative filtering
        with st.spinner("Đang tạo gợi ý món ăn dựa trên cộng đồng..."):
            # Lấy nhiều gợi ý hơn để có thể áp dụng bộ lọc
            recommendations = collab_recommender.recommend_for_customer(customer_id, top_n=num_recommendations * 3)

            # Áp dụng bộ lọc nếu có
            if cuisine_filter:
                recommendations = recommendations[recommendations['cuisine'].isin(cuisine_filter)]

            if price_range != (min_price, max_price):
                recommendations = recommendations[(recommendations['price'] >= price_range[0]) &
                                                  (recommendations['price'] <= price_range[1])]

            # Cắt lại danh sách kết quả theo số lượng yêu cầu
            recommendations = recommendations.head(num_recommendations)

            # Hiển thị kết quả
            if not recommendations.empty:
                st.write(
                    f"### Top {len(recommendations)} món ăn được gợi ý cho {customers_df[customers_df['customer_id'] == customer_id]['name'].values[0]}")

                # Hiển thị kết quả dưới dạng grid
                cols = st.columns(3)
                for i, (idx, row) in enumerate(recommendations.iterrows()):
                    food = row.to_dict()
                    score = row['predicted_rating']
                    with cols[i % 3]:
                        st.markdown(generate_food_card(food, "predicted", score), unsafe_allow_html=True)
            else:
                st.info("Chưa có đủ dữ liệu để gợi ý món ăn. Vui lòng đánh giá thêm món ăn.")

                # Tính độ phổ biến dựa trên số lượt đánh giá
                popularity_df = ratings_df.groupby('food_id').size().reset_index(name='popularity')

                # Gộp vào bảng foods_df
                foods_df = foods_df.merge(popularity_df, on='food_id', how='left')
                foods_df['popularity'] = foods_df['popularity'].fillna(0).astype(int)

                # cols = st.columns(3)
                # for i, (idx, food) in enumerate(popularity_df.iterrows()):
                #     with cols[i % 3]:
                #         st.markdown(generate_food_card(food.to_dict()), unsafe_allow_html=True)

    elif recommendation_type == "Dựa trên nội dung":
        st.subheader("Gợi ý dựa trên nội dung")
        st.write("Chọn một món ăn yêu thích để tìm các món tương tự:")

        # Hiển thị số lượng gợi ý muốn nhận
        num_recommendations = st.slider(
            "Số lượng gợi ý:",
            min_value=5,
            max_value=20,
            value=10,
            step=5
        )

        # Trích xuất recommender từ session state
        content_recommender = st.session_state.content_recommender

        # Tạo danh sách món ăn đã đánh giá bởi khách hàng
        rated_foods = ratings_df[ratings_df['customer_id'] == customer_id]

        if not rated_foods.empty:
            # Lấy danh sách món ăn đã đánh giá cao
            highly_rated = rated_foods[rated_foods['rating'] >= 4]

            if not highly_rated.empty:
                selected_food = st.selectbox(
                    "Chọn món ăn yêu thích:",
                    options=highly_rated['food_id'].tolist(),
                    format_func=lambda
                        x: f"{foods_df[foods_df['food_id'] == x]['name'].values[0]} (Đánh giá: {rated_foods[rated_foods['food_id'] == x]['rating'].values[0]}/5)"
                )

                # Lấy gợi ý dựa trên nội dung
                recommendations = content_recommender.recommend(selected_food, top_n=10)

                # Hiển thị kết quả
                if not recommendations.empty:
                    st.write(
                        f"### Các món ăn tương tự với {foods_df[foods_df['food_id'] == selected_food]['name'].values[0]}")

                    for idx, row in recommendations.iterrows():
                        food = row.to_dict()
                        score = row['similarity_score']
                        st.markdown(generate_food_card(food, "similarity", score), unsafe_allow_html=True)
            else:
                st.info(
                    "Bạn chưa đánh giá cao món ăn nào. Hãy đánh giá các món ăn với 4 sao trở lên để nhận gợi ý tốt hơn.")
        else:
            st.info("Bạn chưa đánh giá món ăn nào. Hãy đánh giá một số món ăn để nhận gợi ý tốt hơn.")

        # Tùy chọn tìm kiếm dựa trên đặc điểm
        st.write("### Hoặc nhập đặc điểm món ăn bạn muốn")
        features = st.text_area("Nhập các đặc điểm (ví dụ: cay, ngọt, hải sản, Ý, nướng...):",
                                "cay ngọt hải sản",
                                key="main_features_text_area")

        if st.button("Tìm kiếm"):
            recommendations = content_recommender.get_similar_by_features(features, top_n=10)

            # Hiển thị kết quả
            if not recommendations.empty:
                st.write(f"### Các món ăn phù hợp với đặc điểm: '{features}'")

                for idx, row in recommendations.iterrows():
                    food = row.to_dict()
                    score = row['similarity_score']
                    st.markdown(generate_food_card(food, "similarity", score), unsafe_allow_html=True)

    elif recommendation_type == "Kết hợp":
        st.subheader("Gợi ý kết hợp")
        st.write("Hệ thống sẽ kết hợp nhiều phương pháp để đưa ra gợi ý tốt nhất.")

        # Trích xuất recommender từ session state
        hybrid_recommender = st.session_state.hybrid_recommender

        # Tùy chọn tùy chỉnh
        col1, col2 = st.columns(2)

        with col1:
            food_id = None
            # Tạo danh sách món ăn đã đánh giá bởi khách hàng
            rated_foods = ratings_df[ratings_df['customer_id'] == customer_id]

            if not rated_foods.empty:
                st.write("Chọn món ăn yêu thích (không bắt buộc):")
                include_favorite = st.checkbox("Bao gồm món ăn yêu thích")

                if include_favorite:
                    # Lấy danh sách món ăn đã đánh giá cao
                    highly_rated = rated_foods[rated_foods['rating'] >= 4]

                    if not highly_rated.empty:
                        food_id = st.selectbox(
                            "Chọn món ăn yêu thích:",
                            options=highly_rated['food_id'].tolist(),
                            format_func=lambda
                                x: f"{foods_df[foods_df['food_id'] == x]['name'].values[0]} (Đánh giá: {rated_foods[rated_foods['food_id'] == x]['rating'].values[0]}/5)"
                        )

        with col2:
            st.write("Tùy chọn đặc điểm (không bắt buộc):")
            include_features = st.checkbox("Bao gồm đặc điểm")

            features = None
            if include_features:
                features = st.text_area("Nhập các đặc điểm:", "cay ngọt hải sản")

        if st.button("Nhận gợi ý"):
            # Lấy gợi ý kết hợp
            recommendations = hybrid_recommender.recommend(
                customer_id=customer_id,
                food_id=food_id,
                features=features,
                top_n=10
            )

            # Hiển thị kết quả
            if not recommendations.empty:
                st.write(
                    f"### Top 10 món ăn được gợi ý cho {customers_df[customers_df['customer_id'] == customer_id]['name'].values[0]}")

                for idx, row in recommendations.iterrows():
                    food = row.to_dict()
                    score = row['hybrid_score']
                    st.markdown(generate_food_card(food, "hybrid", score), unsafe_allow_html=True)
            else:
                st.info("Chưa có đủ dữ liệu để gợi ý món ăn. Vui lòng đánh giá thêm món ăn.")


def search_foods(foods_df):
    st.header("Tìm kiếm món ăn")

    # Các bộ lọc
    col1, col2, col3 = st.columns(3)

    with col1:
        category_filter = st.multiselect(
            "Loại món:",
            options=sorted(foods_df['category'].unique()),
            key="category_filter_select"
        )

    with col2:
        cuisine_filter = st.multiselect(
            "Ẩm thực:",
            options=sorted(foods_df['cuisine'].unique()),
            key="cuisine_filter_select"
        )

    with col3:
        price_range = st.slider(
            "Khoảng giá:",
            min_value=float(foods_df['price'].min()),
            max_value=float(foods_df['price'].max()),
            value=(float(foods_df['price'].min()), float(foods_df['price'].max())),
            step=10000.0,
            key="price_range_slider"
        )

    # Tìm kiếm theo từ khóa
    search_term = st.text_input("Tìm kiếm:", "")

    # Lọc dữ liệu
    filtered_df = foods_df.copy()

    if category_filter:
        filtered_df = filtered_df[filtered_df['category'].isin(category_filter)]

    if cuisine_filter:
        filtered_df = filtered_df[filtered_df['cuisine'].isin(cuisine_filter)]

    filtered_df = filtered_df[(filtered_df['price'] >= price_range[0]) & (filtered_df['price'] <= price_range[1])]

    if search_term:
        # Tìm kiếm trong nhiều cột
        filtered_df = filtered_df[
            filtered_df['name'].str.contains(search_term, case=False) |
            filtered_df['ingredients'].str.contains(search_term, case=False) |
            filtered_df['flavors'].str.contains(search_term, case=False) |
            filtered_df['features'].str.contains(search_term, case=False)
            ]

    # Hiển thị kết quả
    st.write(f"Tìm thấy {len(filtered_df)} món ăn")

    # Sắp xếp
    sort_option = st.selectbox(
        "Sắp xếp theo:",
        options=["Tên (A-Z)", "Tên (Z-A)", "Giá (Thấp-Cao)", "Giá (Cao-Thấp)"]
    )

    if sort_option == "Tên (A-Z)":
        filtered_df = filtered_df.sort_values('name', ascending=True)
    elif sort_option == "Tên (Z-A)":
        filtered_df = filtered_df.sort_values('name', ascending=False)
    elif sort_option == "Giá (Thấp-Cao)":
        filtered_df = filtered_df.sort_values('price', ascending=True)
    elif sort_option == "Giá (Cao-Thấp)":
        filtered_df = filtered_df.sort_values('price', ascending=False)

    # Hiển thị kết quả dưới dạng card
    for idx, row in filtered_df.iterrows():
        food = row.to_dict()
        st.markdown(generate_food_card(food), unsafe_allow_html=True)


def rate_foods(customer_id, foods_df, ratings_df):
    st.header("Đánh giá món ăn")

    # Tab để chuyển đổi giữa 2 chế độ
    tab1, tab2 = st.tabs(["Đánh giá món ăn mới", "Lịch sử đánh giá"])

    with tab1:
        # Danh sách món ăn chưa đánh giá
        rated_foods = ratings_df[ratings_df['customer_id'] == customer_id]['food_id'].unique()
        unrated_foods = foods_df[~foods_df['food_id'].isin(rated_foods)]

        if not unrated_foods.empty:
            st.write(f"Còn {len(unrated_foods)} món ăn bạn chưa đánh giá")

            # Chọn món ăn để đánh giá
            selected_food = st.selectbox(
                "Chọn món ăn để đánh giá:",
                options=unrated_foods['food_id'].tolist(),
                format_func=lambda x: f"{foods_df[foods_df['food_id'] == x]['name'].values[0]}"
            )

            # Hiển thị thông tin món ăn
            food_info = foods_df[foods_df['food_id'] == selected_food].iloc[0].to_dict()
            st.markdown(generate_food_card(food_info), unsafe_allow_html=True)

            # Đánh giá
            rating = st.slider("Đánh giá của bạn:", 1, 5, 3)

            if st.button("Gửi đánh giá"):
                # Thêm đánh giá vào database
                success = add_rating(customer_id, selected_food, rating)

                if success:
                    st.success(f"Đã đánh giá món {food_info['name']} với {rating} sao!")
                    # Cập nhật lại ratings_df
                    # st.experimental_rerun()
                    st.rerun()
                else:
                    st.error("Không thể thêm đánh giá. Vui lòng thử lại sau.")
        else:
            st.info("Bạn đã đánh giá tất cả các món ăn. Thật tuyệt!")

    with tab2:
        # Lấy lịch sử đánh giá từ database
        user_ratings = get_customer_ratings(customer_id)

        if not user_ratings.empty:
            st.write(f"Bạn đã đánh giá {len(user_ratings)} món ăn")

            # Hiển thị lịch sử đánh giá
            for idx, row in user_ratings.iterrows():
                food = {
                    'name': row['food_name'],
                    'category': row['category'],
                    'cuisine': row['cuisine'],
                    'price': row['price'],
                    'ingredients': foods_df[foods_df['food_id'] == row['food_id']]['ingredients'].values[0],
                    'flavors': foods_df[foods_df['food_id'] == row['food_id']]['flavors'].values[0]
                }
                st.markdown(generate_food_card(food, "user", row['rating']), unsafe_allow_html=True)
        else:
            st.info("Bạn chưa đánh giá món ăn nào. Hãy đánh giá một số món ăn để nhận gợi ý tốt hơn.")


def analyze_data(foods_df, ratings_df):
    st.header("Phân tích dữ liệu")

    # Chọn loại phân tích
    analysis_type = st.selectbox(
        "Chọn loại phân tích:",
        options=["Phân phối đánh giá", "Ẩm thực phổ biến", "Hương vị phổ biến", "Giá trung bình theo ẩm thực"],
        key="analysis_type_select"
    )

    # Hiển thị phân tích tương ứng
    if analysis_type == "Phân phối đánh giá":
        st.subheader("Phân phối đánh giá")

        # Tạo biểu đồ phân phối đánh giá
        fig = viz.plot_rating_distribution(ratings_df)
        st.plotly_chart(fig, use_container_width=True)

    elif analysis_type == "Ẩm thực phổ biến":
        st.subheader("Ẩm thực phổ biến")

        # Tạo biểu đồ ẩm thực phổ biến
        fig = viz.plot_popular_cuisines(foods_df, ratings_df)
        st.plotly_chart(fig, use_container_width=True)

    elif analysis_type == "Hương vị phổ biến":
        st.subheader("Hương vị phổ biến")

        # Tạo biểu đồ hương vị phổ biến
        fig = viz.plot_popular_flavors(foods_df)
        st.plotly_chart(fig, use_container_width=True)

    elif analysis_type == "Giá trung bình theo ẩm thực":
        st.subheader("Giá trung bình theo ẩm thực")

        # Tạo biểu đồ giá trung bình theo ẩm thực
        fig = viz.plot_avg_price_by_cuisine(foods_df)
        st.plotly_chart(fig, use_container_width=True)


if __name__ == "__main__":
    main()
    # Tạo hoặc lấy dữ liệu từ session state
    if 'foods_df' not in st.session_state:
        with st.spinner("Đang tạo dữ liệu món ăn..."):
            foods_df = create_food_items(num_items=100)
            customers_df = create_customers(num_customers=500)
            ratings_df = create_ratings(customers_df, foods_df, sparsity=0.05)

            # Lưu vào session state
            st.session_state.foods_df = foods_df
            st.session_state.customers_df = customers_df
            st.session_state.ratings_df = ratings_df

            # Khởi tạo recommenders
            content_rec = ContentBasedRecommender()
            content_rec.fit(foods_df)

            collab_rec = CollaborativeRecommender()
            collab_rec.fit(ratings_df, foods_df)

            hybrid_rec = HybridRecommender()
            hybrid_rec.fit(foods_df, ratings_df, customers_df)

            st.session_state.content_rec = content_rec
            st.session_state.collab_rec = collab_rec
            st.session_state.hybrid_rec = hybrid_rec
    else:
        # Lấy từ session state
        foods_df = st.session_state.foods_df
        customers_df = st.session_state.customers_df
        ratings_df = st.session_state.ratings_df
        content_rec = st.session_state.content_rec
        collab_rec = st.session_state.collab_rec
        hybrid_rec = st.session_state.hybrid_rec

    # Tạo sidebar
    sidebar_options = create_sidebar(ratings_df, foods_df)

    # Tab chính của ứng dụng
    tabs = st.tabs(["🍽️ Gợi ý món ăn", "📊 Phân tích", "👤 Khách hàng", "ℹ️ Giới thiệu"])

    # Tab 1: Gợi ý món ăn
    with tabs[0]:
        show_recommendation_tab(sidebar_options, foods_df, ratings_df, content_rec, collab_rec, hybrid_rec)

        show_explore_section(foods_df)

    # Tab 2: Phân tích
    with tabs[1]:
        show_analysis_tab(ratings_df, foods_df)

    # Tab 3: Khách hàng
    with tabs[2]:
        show_customer_tab(sidebar_options, customers_df, ratings_df, foods_df)

    # Tab 4: Giới thiệu
    with tabs[3]:
        show_about_tab()

    # Footer
    create_footer()