from db_utils import create_connection, execute_query
import os
from dotenv import load_dotenv

load_dotenv()
host = os.getenv("DB_HOST")
port = os.getenv("DB_PORT")
user = os.getenv("DB_USER")
password = os.getenv("DB_PASSWORD")
database = os.getenv("DB_NAME")
port = int(port)
def create_database():
    """Tạo database nếu chưa tồn tại"""
    try:
        # Kết nối tới MySQL server mà không chọn database
        conn = create_connection(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database
        )
        
        if conn:
            cursor = conn.cursor()
            # Tạo database nếu chưa tồn tại
            cursor.execute("CREATE DATABASE IF NOT EXISTS food_recommendation")
            cursor.close()
            conn.close()
            print("Database đã được tạo hoặc đã tồn tại")
            return True
    except Exception as e:
        print(f"Lỗi khi tạo database: {e}")
        return False

def initialize_tables():
    """Khởi tạo các bảng cần thiết trong database"""
    conn = create_connection(
        host=host,
        port=port,
        user=user,
        password=password,
        database=database
    )
    
    if not conn:
        return False
    
    # Tạo bảng foods
    create_foods_table = """
    CREATE TABLE IF NOT EXISTS foods (
        food_id VARCHAR(50) PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        category VARCHAR(100),
        cuisine VARCHAR(100),
        price DECIMAL(10, 2),
        ingredients TEXT,
        flavors TEXT,
        features TEXT
    );
    """
    
    # Tạo bảng customers
    create_customers_table = """
    CREATE TABLE IF NOT EXISTS customers (
        customer_id VARCHAR(50) PRIMARY KEY,
        name VARCHAR(255),
        age INT,
        gender VARCHAR(20),
        price_sensitivity DECIMAL(3, 2)
    );
    """
    
    # Tạo bảng ratings
    create_ratings_table = """
    CREATE TABLE IF NOT EXISTS ratings (
        id INT AUTO_INCREMENT PRIMARY KEY,
        customer_id VARCHAR(50),
        food_id VARCHAR(50),
        rating INT NOT NULL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
        FOREIGN KEY (food_id) REFERENCES foods(food_id)
    );
    """
    
    # Thực thi các câu lệnh tạo bảng
    tables_created = True
    tables_created = tables_created and execute_query(conn, create_foods_table)
    tables_created = tables_created and execute_query(conn, create_customers_table)
    tables_created = tables_created and execute_query(conn, create_ratings_table)
    
    # Đóng kết nối
    conn.close()
    
    if tables_created:
        print("Các bảng đã được khởi tạo thành công")
    else:
        print("Có lỗi khi khởi tạo các bảng")
    
    return tables_created

if __name__ == "__main__":
    # Chạy script để khởi tạo database và các bảng
    if create_database():
        initialize_tables()
