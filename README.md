# Hệ thống Gợi ý Món ăn Thông minh

Đây là ứng dụng gợi ý món ăn được xây dựng bằng Streamlit và các kỹ thuật học máy hiện đại. Hệ thống kết hợp nhiều phương pháp gợi ý khác nhau để đưa ra những đề xuất món ăn phù hợp với sở thích của người dùng. Dữ liệu được lưu trữ trong MySQL database giúp việc quản lý thông tin hiệu quả và bền vững.

## Tính năng
   
- **Gợi ý món ăn cá nhân hóa** sử dụng 3 phương pháp:
  - Content-Based (dựa trên nội dung)
  - Collaborative Filtering (dựa trên cộng đồng)
  - Hybrid (kết hợp)
- **Phân tích dữ liệu** với biểu đồ trực quan:
  - Phân phối đánh giá
  - Ẩm thực phổ biến
  - Hương vị phổ biến
  - Giá trung bình theo ẩm thực
- **Thông tin khách hàng** với lịch sử đánh giá
- **Khám phá món ăn mới** theo nhiều cách thức khác nhau
- **Lưu trữ dữ liệu** trong MySQL database

## Yêu cầu hệ thống

- Python 3.7+
- MySQL Server 5.7+ (cổng 3307)
- Streamlit
- Pandas, NumPy, Scikit-learn
- Plotly
- mysql-connector-python

## Cài đặt

1. Clone repository này về máy của bạn:
   ```
   git clone <repository-url>
   cd food-recommendation-system
   ```

2. Cài đặt các thư viện cần thiết:
   ```
   pip install -r requirements.txt
   ```

3. Cấu hình MySQL:
   - Đảm bảo MySQL Server đang chạy trên cổng 3307
   - Cập nhật thông tin kết nối trong file `db_utils.py` nếu cần thiết:
     ```python
     host="localhost"
     port=3307
     user="root"
     password=""
     database="food_recommendation"
     ```

4. Khởi tạo database và dữ liệu mẫu:
   ```
   python init_database.py
   python import_sample_data.py
   ```

5. Chạy ứng dụng:
   ```
   streamlit run app.py
   ```

## Cấu trúc Database

Hệ thống sử dụng MySQL database với 3 bảng chính:

1. **foods** - Lưu thông tin về món ăn:
   - food_id (PK): Mã món ăn
   - name: Tên món ăn
   - category: Loại món ăn
   - cuisine: Loại ẩm thực
   - price: Giá tiền
   - ingredients: Nguyên liệu
   - flavors: Hương vị
   - features: Đặc điểm món ăn (để phục vụ gợi ý dựa trên nội dung)

2. **customers** - Lưu thông tin về khách hàng:
   - customer_id (PK): Mã khách hàng
   - name: Tên khách hàng
   - age: Tuổi
   - gender: Giới tính
   - price_sensitivity: Độ nhạy cảm về giá (0.1-1.0)

3. **ratings** - Lưu thông tin đánh giá:
   - id (PK): Mã đánh giá
   - customer_id (FK): Mã khách hàng
   - food_id (FK): Mã món ăn
   - rating: Điểm đánh giá (1-5)
   - timestamp: Thời gian đánh giá

## Cách sử dụng

1. **Chọn khách hàng** từ danh sách ở sidebar để xem gợi ý và đánh giá dành cho họ
2. **Chọn chức năng** từ menu:
   - **Gợi ý món ăn**: Xem các món ăn được gợi ý theo nhiều phương pháp
   - **Tìm kiếm món ăn**: Tìm món ăn theo bộ lọc và từ khóa
   - **Đánh giá món ăn**: Đánh giá món ăn mới hoặc xem lịch sử đánh giá
   - **Phân tích dữ liệu**: Xem các biểu đồ và thống kê về dữ liệu

## Các phương pháp gợi ý

1. **Dựa trên nội dung (Content-Based)**:
   - Sử dụng TF-IDF để phân tích đặc điểm món ăn
   - Tính toán độ tương tự cosine giữa các món ăn

2. **Dựa trên cộng đồng (Collaborative Filtering)**:
   - Sử dụng SVD (Singular Value Decomposition) để dự đoán đánh giá
   - Gợi ý món ăn dựa trên sở thích của người dùng tương tự

3. **Kết hợp (Hybrid)**:
   - Kết hợp kết quả từ cả hai phương pháp trên
   - Có thể tùy chỉnh theo món ăn yêu thích và đặc điểm mong muốn

## Thông tin kỹ thuật

- Kết nối database được quản lý thông qua `db_utils.py`
- Session state trong Streamlit được sử dụng để lưu trữ kết nối database và các mô hình gợi ý
- Visualizations sử dụng thư viện Plotly để tạo biểu đồ tương tác

## Tùy chỉnh

Bạn có thể tùy chỉnh cấu hình kết nối MySQL trong file `db_utils.py`:
