import mysql.connector
from mysql.connector import Error
import pandas as pd
import streamlit as st
import os
from dotenv import load_dotenv
load_dotenv()
host1 = os.getenv("DB_HOST")
port1 = os.getenv("DB_PORT")
user1 = os.getenv("DB_USER")
password1 = os.getenv("DB_PASSWORD")
database1 = os.getenv("DB_NAME")
port1 = int(port1)
def create_connection(host=host1, port=port1, user=user1, password=password1, database=database1):
    """
    Tạo kết nối tới MySQL database
    
    Args:
        host (str): Địa chỉ máy chủ MySQL
        port (int): Cổng kết nối MySQL, mặc định là 3307
        user (str): Tên người dùng MySQL
        password (str): Mật khẩu MySQL
        database (str): Tên database
        
    Returns:
        connection: Đối tượng kết nối MySQL hoặc None nếu có lỗi
    """
    connection = None
    try:
        connection = mysql.connector.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database
        )
        print("Kết nối MySQL thành công")
    except Error as e:
        print(f"Lỗi kết nối MySQL: {e}")
    
    return connection

def execute_query(connection, query, params=None):
    """
    Thực thi câu truy vấn SQL
    
    Args:
        connection: Đối tượng kết nối MySQL
        query (str): Câu truy vấn SQL
        params (tuple, optional): Tham số cho câu truy vấn
        
    Returns:
        bool: True nếu thành công, False nếu thất bại
    """
    cursor = connection.cursor()
    try:
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        connection.commit()
        return True
    except Error as e:
        print(f"Lỗi thực thi truy vấn: {e}")
        return False
    finally:
        cursor.close()

def execute_read_query(connection, query, params=None):
    """
    Thực thi câu truy vấn SQL và trả về kết quả
    
    Args:
        connection: Đối tượng kết nối MySQL
        query (str): Câu truy vấn SQL
        params (tuple, optional): Tham số cho câu truy vấn
        
    Returns:
        list: Danh sách kết quả hoặc None nếu có lỗi
    """
    cursor = connection.cursor(dictionary=True)
    result = None
    try:
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        result = cursor.fetchall()
        return result
    except Error as e:
        print(f"Lỗi thực thi truy vấn đọc: {e}")
        return None
    finally:
        cursor.close()

def get_dataframe_from_query(connection, query, params=None):
    """
    Thực thi câu truy vấn SQL và trả về kết quả dưới dạng DataFrame
    
    Args:
        connection: Đối tượng kết nối MySQL
        query (str): Câu truy vấn SQL
        params (tuple, optional): Tham số cho câu truy vấn
        
    Returns:
        DataFrame: DataFrame pandas hoặc DataFrame rỗng nếu có lỗi
    """
    try:
        if params:
            return pd.read_sql_query(query, connection, params=params)
        else:
            return pd.read_sql_query(query, connection)
    except Error as e:
        print(f"Lỗi đọc DataFrame: {e}")
        return pd.DataFrame()

# Hàm tiện ích sử dụng với Streamlit để lưu kết nối trong session state
def get_connection():
    """
    Lấy hoặc tạo kết nối MySQL từ session state của Streamlit
    
    Returns:
        connection: Đối tượng kết nối MySQL
    """
    if 'db_connection' not in st.session_state:
        # Thay đổi thông tin kết nối phù hợp với cấu hình của bạn

        st.session_state.db_connection = create_connection(
            host=host1,
            port=port1,
            user=user1,
            password=password1,
            database=database1
        )
    
    return st.session_state.db_connection

def close_connection():
    """Đóng kết nối database nếu tồn tại trong session state"""
    if 'db_connection' in st.session_state and st.session_state.db_connection:
        st.session_state.db_connection.close()
        del st.session_state.db_connection
        print("Đã đóng kết nối MySQL")
