import pandas as pd
from db_utils import get_connection, get_dataframe_from_query

def load_foods_from_db():
    """Tải dữ liệu món ăn từ database"""
    conn = get_connection()
    if not conn:
        return pd.DataFrame()
    
    query = "SELECT * FROM foods"
    return get_dataframe_from_query(conn, query)

def load_customers_from_db():
    """Tải dữ liệu khách hàng từ database"""
    conn = get_connection()
    if not conn:
        return pd.DataFrame()
    
    query = "SELECT * FROM customers"
    return get_dataframe_from_query(conn, query)

def load_ratings_from_db():
    """Tải dữ liệu đánh giá từ database"""
    conn = get_connection()
    if not conn:
        return pd.DataFrame()
    
    query = """
    SELECT r.*, f.name as food_name, f.category, f.cuisine, f.price 
    FROM ratings r
    JOIN foods f ON r.food_id = f.food_id
    ORDER BY r.timestamp DESC
    """
    return get_dataframe_from_query(conn, query)

def get_customer_ratings(customer_id):
    """Lấy lịch sử đánh giá của một khách hàng"""
    conn = get_connection()
    if not conn:
        return pd.DataFrame()
    
    query = """
    SELECT r.*, f.name as food_name, f.category, f.cuisine, f.price 
    FROM ratings r
    JOIN foods f ON r.food_id = f.food_id
    WHERE r.customer_id = %s
    ORDER BY r.timestamp DESC
    """
    return get_dataframe_from_query(conn, query, params=(customer_id,))

def add_rating(customer_id, food_id, rating):
    """Thêm hoặc cập nhật đánh giá của khách hàng"""
    conn = get_connection()
    if not conn:
        return False
    
    # Kiểm tra xem đánh giá đã tồn tại chưa
    check_query = """
    SELECT id FROM ratings 
    WHERE customer_id = %s AND food_id = %s
    """
    cursor = conn.cursor()
    cursor.execute(check_query, (customer_id, food_id))
    result = cursor.fetchone()
    
    if result:
        # Cập nhật đánh giá hiện có
        update_query = """
        UPDATE ratings 
        SET rating = %s, timestamp = CURRENT_TIMESTAMP
        WHERE customer_id = %s AND food_id = %s
        """
        cursor.execute(update_query, (rating, customer_id, food_id))
    else:
        # Thêm đánh giá mới
        insert_query = """
        INSERT INTO ratings (customer_id, food_id, rating)
        VALUES (%s, %s, %s)
        """
        cursor.execute(insert_query, (customer_id, food_id, rating))
    
    conn.commit()
    cursor.close()
    return True

def get_food_details(food_id):
    """Lấy thông tin chi tiết của một món ăn"""
    conn = get_connection()
    if not conn:
        return None
    
    query = "SELECT * FROM foods WHERE food_id = %s"
    result = get_dataframe_from_query(conn, query, params=(food_id,))
    
    if result.empty:
        return None
    return result.iloc[0].to_dict()
