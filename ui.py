import streamlit as st

def load_css():
    """Load custom CSS styling"""
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

def setup_page_config():
    """Configure the Streamlit page settings"""
    st.set_page_config(
        page_title="Hệ thống Gợi ý Món ăn",
        page_icon="🍽️",
        layout="wide",
        initial_sidebar_state="expanded"
    )

def create_sidebar(ratings_df, foods_df):
    """Create and configure the sidebar"""
    with st.sidebar:
        st.image(
            "https://img.freepik.com/free-vector/organic-flat-people-asking-questions-illustration_23-2148906283.jpg?w=900",
            use_container_width=True)

        st.markdown("### 🔍 Khám phá món ăn")

        # Chọn khách hàng
        customer_ids = sorted(list(ratings_df['customer_id'].unique()))
        selected_customer = st.selectbox("👤 Chọn Khách hàng ID:", customer_ids)

        # Chọn kiểu gợi ý
        rec_type = st.radio(
            "💭 Phương pháp gợi ý:",
            ["Hybrid (Kết hợp)", "Content-Based (Dựa trên nội dung)", "Collaborative (Dựa trên cộng đồng)"]
        )

        # Số lượng kết quả
        num_recommendations = st.slider("🔢 Số lượng gợi ý:", 1, 20, 5)

        # Nút gợi ý
        recommend_button = st.button("🔍 Xem gợi ý món ăn", type="primary")

        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

        # Bộ lọc
        st.markdown("### ⚙️ Bộ lọc nâng cao")
        cuisine_filter = st.multiselect(
            "🌏 Ẩm thực:",
            sorted(foods_df['cuisine'].unique())
        )

        price_range = st.slider(
            "💰 Khoảng giá (VND):",
            0, 300000, (0, 300000), step=10000
        )

        flavors_filter = st.multiselect(
            "🌶️ Hương vị:",
            sorted(set([flavor.strip() for flavors in foods_df['flavors'] for flavor in flavors.split(',')]))
        )
        
    return {
        "selected_customer": selected_customer,
        "rec_type": rec_type,
        "num_recommendations": num_recommendations,
        "recommend_button": recommend_button,
        "cuisine_filter": cuisine_filter,
        "price_range": price_range,
        "flavors_filter": flavors_filter
    }

def create_header():
    """Create the main application header"""
    st.markdown('<h1 class="main-header">🍽️ Hệ thống Gợi ý Món ăn Thông minh</h1>', unsafe_allow_html=True)

def create_footer():
    """Create the application footer"""
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    st.markdown('<div class="footer">', unsafe_allow_html=True)
    st.markdown("""
    © 2024 Hệ thống Gợi ý Món ăn | Được phát triển bằng Streamlit

    Dữ liệu được tạo tự động cho mục đích minh họa.
    """)
    st.markdown('</div>', unsafe_allow_html=True)

def show_about_tab():
    """Display content for the About tab"""
    st.markdown('<h2 class="sub-header">ℹ️ Giới thiệu hệ thống</h2>', unsafe_allow_html=True)

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("""
    ### 🍽️ Hệ thống Gợi ý Món ăn

    Ứng dụng này sử dụng các công nghệ trí tuệ nhân tạo tiên tiến để gợi ý món ăn phù hợp với sở thích của từng khách hàng. 
    Hệ thống kết hợp nhiều phương pháp gợi ý khác nhau để đưa ra những đề xuất chính xác nhất.

    #### 📌 Các phương pháp gợi ý:

    **1. Content-Based (Dựa trên nội dung):**
    - Phân tích đặc điểm của món ăn (ẩm thực, hương vị, nguyên liệu...)
    - Tìm món ăn tương tự với những món khách hàng đã thích trước đó
    - Sử dụng kỹ thuật TF-IDF và Cosine Similarity

    **2. Collaborative Filtering (Lọc cộng tác):**
    - Phân tích hành vi đánh giá của nhiều khách hàng
    - Tìm kiếm mẫu đánh giá tương tự giữa các khách hàng
    - Sử dụng giải thuật SVD (Singular Value Decomposition)

    **3. Hybrid (Kết hợp):**
    - Kết hợp cả hai phương pháp trên
    - Cân bằng giữa nội dung món ăn và xu hướng cộng đồng
    - Mang lại gợi ý đa dạng và phù hợp hơn

    #### 🎯 Hướng dẫn sử dụng:
    1. Chọn khách hàng ID trong menu bên trái
    2. Chọn phương pháp gợi ý phù hợp
    3. Điều chỉnh số lượng gợi ý và bộ lọc (nếu cần)
    4. Nhấn nút "Xem gợi ý món ăn" và khám phá!
    """)
    st.markdown('</div>', unsafe_allow_html=True)
