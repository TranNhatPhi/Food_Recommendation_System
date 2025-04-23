import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta
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
def import_sample_foods():
    """Tạo và import dữ liệu mẫu cho món ăn"""
    # Kết nối tới database
    conn = create_connection(
        host=host,
        port=port,
        user=user,
        password=password,
        database=database
    )
    
    if not conn:
        print("Không thể kết nối tới database")
        return False
    
    # Tạo danh sách mẫu
    categories = ["Món chính", "Món phụ", "Món tráng miệng", "Món ăn nhẹ", "Món nước", "Món nướng", "Món hấp", "Món chiên"]
    cuisines = ["Việt Nam", "Trung Hoa", "Nhật Bản", "Hàn Quốc", "Thái Lan", "Ý", "Pháp", "Mỹ", "Ấn Độ", "Mexico"]
    flavors_list = ["cay", "ngọt", "mặn", "chua", "đắng", "thơm", "béo", "bùi", "giòn", "mềm", "dai", "xốp", "đậm đà", "nhẹ nhàng"]
    
    # Tạo dictionary giá trị trung bình theo ẩm thực
    cuisine_price_range = {
        "Việt Nam": (30000, 150000),
        "Trung Hoa": (40000, 200000),
        "Nhật Bản": (50000, 250000),
        "Hàn Quốc": (45000, 220000),
        "Thái Lan": (35000, 180000),
        "Ý": (60000, 300000),
        "Pháp": (80000, 400000),
        "Mỹ": (50000, 250000),
        "Ấn Độ": (40000, 220000),
        "Mexico": (45000, 230000)
    }
    
    # Danh sách các món ăn mẫu
    food_names = [
        # Việt Nam
        ("F001", "Phở bò", "Món chính", "Việt Nam", "bò, bánh phở, hành, rau thơm", "mặn, thơm, nóng", "phở bò truyền thống nước dùng ngọt thanh đậm đà"),
        ("F002", "Bún chả", "Món chính", "Việt Nam", "thịt lợn, bún, rau sống, nước mắm", "mặn, ngọt, chua", "bún chả Hà Nội thơm ngon đặc trưng"),
        ("F003", "Bánh mì thịt", "Món ăn nhẹ", "Việt Nam", "bánh mì, thịt, rau, đồ chua", "mặn, chua, cay", "bánh mì giòn với nhân thịt và rau"),
        ("F004", "Cơm tấm", "Món chính", "Việt Nam", "sườn, cơm tấm, đồ chua, mỡ hành", "mặn, ngọt, béo", "cơm tấm sườn bì chả đậm đà hương vị"),
        ("F005", "Gỏi cuốn", "Món phụ", "Việt Nam", "tôm, thịt lợn, bún, rau sống", "mặn, tươi, nhẹ", "gỏi cuốn tươi mát kèm nước chấm"),
        
        # Trung Hoa
        ("F006", "Dimsum", "Món phụ", "Trung Hoa", "thịt, bột, nấm", "mặn, thơm, béo", "dimsum nhân thịt hấp nóng thơm ngon"),
        ("F007", "Vịt quay Bắc Kinh", "Món chính", "Trung Hoa", "vịt, hành, bánh, hoisin", "mặn, béo, giòn", "vịt quay giòn da thơm béo"),
        ("F008", "Hoành thánh", "Món phụ", "Trung Hoa", "thịt, bột, hành, nước dùng", "mặn, ngọt, thơm", "hoành thánh vỏ mỏng nhân thịt"),
        ("F009", "Mì xào hải sản", "Món chính", "Trung Hoa", "mì, tôm, mực, rau", "mặn, cay, thơm", "mì xào hải sản tươi ngon đậm đà"),
        ("F010", "Cơm chiên Dương Châu", "Món chính", "Trung Hoa", "cơm, thịt, trứng, rau", "mặn, thơm, béo", "cơm chiên với nhiều loại nhân"),
        
        # Nhật Bản
        ("F011", "Sushi", "Món chính", "Nhật Bản", "cơm, cá hồi, rong biển, wasabi", "tươi, mặn, cay", "sushi cá hồi tươi ngon"),
        ("F012", "Ramen", "Món chính", "Nhật Bản", "mì, thịt heo, trứng, rau", "mặn, đậm đà, thơm", "ramen nước dùng đậm đà với mì dai"),
        ("F013", "Tempura", "Món phụ", "Nhật Bản", "tôm, rau, bột chiên xù", "giòn, béo, nhẹ", "tempura giòn rụm hương vị hải sản"),
        ("F014", "Udon", "Món chính", "Nhật Bản", "mì udon, thịt, rau, nước dùng", "mặn, ngọt, thơm", "udon sợi to dai ngon với nước dùng"),
        ("F015", "Takoyaki", "Món ăn nhẹ", "Nhật Bản", "bạch tuộc, bột, hành, sốt", "mặn, cay, béo", "takoyaki nóng hổi với nhân bạch tuộc"),
        
        # Hàn Quốc
        ("F016", "Kimchi", "Món phụ", "Hàn Quốc", "bắp cải, ớt, tỏi, muối", "cay, chua, mặn", "kimchi cay nồng đặc trưng Hàn Quốc"),
        ("F017", "Bibimbap", "Món chính", "Hàn Quốc", "cơm, thịt bò, rau, trứng", "mặn, cay, thơm", "bibimbap đầy đủ dinh dưỡng nhiều màu sắc"),
        ("F018", "Bulgogi", "Món chính", "Hàn Quốc", "thịt bò, nấm, hành, gừng", "ngọt, mặn, thơm", "bulgogi thịt bò nướng thơm ngon"),
        ("F019", "Tteokbokki", "Món ăn nhẹ", "Hàn Quốc", "bánh gạo, sốt ớt, hành, trứng", "cay, ngọt, dai", "tteokbokki cay nồng với bánh gạo dai"),
        ("F020", "Kimbap", "Món ăn nhẹ", "Hàn Quốc", "cơm, rau, thịt, rong biển", "mặn, thơm, nhẹ", "kimbap nhiều nhân cuộn trong rong biển"),
        
        # Thái Lan
        ("F021", "Pad Thai", "Món chính", "Thái Lan", "phở khô, tôm, đậu phộng, trứng", "chua, cay, ngọt", "pad thai chua ngọt thơm ngon"),
        ("F022", "Tom Yum", "Món nước", "Thái Lan", "tôm, nấm, sả, chanh", "chua, cay, thơm", "tom yum chua cay nồng đặc trưng"),
        ("F023", "Som Tum", "Món phụ", "Thái Lan", "đu đủ xanh, tôm, ớt, đậu phộng", "chua, cay, mặn", "som tum gỏi đu đủ chua cay"),
        ("F024", "Massaman Curry", "Món chính", "Thái Lan", "thịt bò, khoai tây, đậu phộng, cà ri", "cay, béo, thơm", "massaman curry hương vị đậm đà béo ngậy"),
        ("F025", "Khao Pad", "Món chính", "Thái Lan", "cơm, thịt, trứng, rau", "mặn, thơm, cay", "khao pad cơm chiên thơm ngon kiểu Thái"),
        
        # Ý
        ("F026", "Pizza Margherita", "Món chính", "Ý", "bột mì, phô mai, cà chua, húng quế", "mặn, thơm, chua", "pizza truyền thống Ý với phô mai và húng quế"),
        ("F027", "Pasta Carbonara", "Món chính", "Ý", "mì, thịt xông khói, trứng, phô mai", "mặn, béo, thơm", "pasta béo ngậy với sốt trứng và thịt xông khói"),
        ("F028", "Risotto", "Món chính", "Ý", "gạo arborio, hành, rượu vang, phô mai", "béo, thơm, mặn", "risotto thơm ngon béo ngậy"),
        ("F029", "Lasagna", "Món chính", "Ý", "mì lá, thịt bò, phô mai, sốt cà chua", "mặn, béo, thơm", "lasagna nhiều lớp với nhân thịt và phô mai"),
        ("F030", "Tiramisu", "Món tráng miệng", "Ý", "bánh quy, cà phê, phô mai mascarpone, ca cao", "ngọt, đắng, mềm", "tiramisu mềm mịn hương vị cà phê"),
        
        # Pháp
        ("F031", "Croissant", "Món ăn nhẹ", "Pháp", "bột mì, bơ, men nở", "béo, ngọt, giòn", "croissant giòn xốp nhiều lớp"),
        ("F032", "Coq au Vin", "Món chính", "Pháp", "gà, rượu vang, nấm, thịt xông khói", "mặn, thơm, đậm đà", "coq au vin gà hầm rượu vang kiểu Pháp"),
        ("F033", "Ratatouille", "Món phụ", "Pháp", "cà tím, ớt chuông, zucchini, cà chua", "thơm, chua, ngọt", "ratatouille món rau củ hầm kiểu Pháp"),
        ("F034", "Boeuf Bourguignon", "Món chính", "Pháp", "thịt bò, rượu vang, hành, nấm", "mặn, đậm đà, thơm", "boeuf bourguignon thịt bò hầm mềm"),
        ("F035", "Crème Brûlée", "Món tráng miệng", "Pháp", "kem, trứng, đường, vani", "ngọt, béo, giòn", "crème brûlée mặt caramel giòn béo ngậy"),
        
        # Mỹ
        ("F036", "Hamburger", "Món ăn nhẹ", "Mỹ", "thịt bò, bánh mì, phô mai, rau", "mặn, béo, thơm", "hamburger thịt bò mọng nước"),
        ("F037", "BBQ Ribs", "Món chính", "Mỹ", "sườn heo, sốt BBQ, gia vị", "cay, ngọt, thơm", "sườn nướng BBQ thơm ngon đậm đà"),
        ("F038", "Mac and Cheese", "Món phụ", "Mỹ", "mì ống, phô mai, sữa, bơ", "béo, mặn, thơm", "mac and cheese béo ngậy đậm đà"),
        ("F039", "Fried Chicken", "Món chính", "Mỹ", "gà, bột, gia vị, dầu", "mặn, cay, giòn", "gà rán giòn rụm thơm ngon"),
        ("F040", "Apple Pie", "Món tráng miệng", "Mỹ", "táo, bột mì, đường, bơ", "ngọt, thơm, giòn", "bánh táo nướng truyền thống"),
        
        # Ấn Độ
        ("F041", "Butter Chicken", "Món chính", "Ấn Độ", "gà, bơ, kem, cà ri", "béo, cay, thơm", "butter chicken sốt cà ri béo ngậy"),
        ("F042", "Naan", "Món phụ", "Ấn Độ", "bột mì, men, sữa chua", "mềm, thơm, nhẹ", "bánh naan mềm thơm nướng trong lò tandoor"),
        ("F043", "Biryani", "Món chính", "Ấn Độ", "gạo basmati, thịt, gia vị, hành", "thơm, cay, đậm đà", "biryani cơm gia vị thơm nồng"),
        ("F044", "Samosa", "Món ăn nhẹ", "Ấn Độ", "bột mì, khoai tây, đậu, gia vị", "giòn, cay, thơm", "samosa nhân khoai tây giòn rụm"),
        ("F045", "Tandoori Chicken", "Món chính", "Ấn Độ", "gà, sữa chua, gia vị", "cay, thơm, mặn", "tandoori chicken gà nướng đỏ au thơm nồng"),
        
        # Mexico
        ("F046", "Tacos", "Món ăn nhẹ", "Mexico", "tortilla, thịt bò, salsa, rau", "cay, mặn, thơm", "tacos nhân thịt bò cay nồng"),
        ("F047", "Guacamole", "Món phụ", "Mexico", "bơ, hành, cà chua, chanh", "béo, chua, mặn", "guacamole sốt bơ tươi mát"),
        ("F048", "Enchiladas", "Món chính", "Mexico", "tortilla, thịt gà, phô mai, sốt", "cay, mặn, thơm", "enchiladas cuộn nhân thịt phủ sốt"),
        ("F049", "Chili Con Carne", "Món chính", "Mexico", "thịt bò, đậu, ớt, cà chua", "cay, thơm, đậm đà", "chili con carne đậm đà cay nồng"),
        ("F050", "Quesadilla", "Món ăn nhẹ", "Mexico", "tortilla, phô mai, thịt, ớt", "béo, mặn, cay", "quesadilla giòn với nhân phô mai tan chảy")
    ]
    
    # Tạo thêm 50 món ăn ngẫu nhiên
    for i in range(51, 101):
        food_id = f"F{i:03d}"
        category = random.choice(categories)
        cuisine = random.choice(cuisines)
        
        # Tạo tên món ăn
        prefix = random.choice(["Món", "Chè", "Bánh", "Cơm", "Súp", "Mì", "Salad", "Gỏi", "Khoai", "Đậu"])
        suffix = random.choice(["đặc biệt", "truyền thống", "cay", "ngọt", "hấp dẫn", "thơm ngon", "lạ miệng", "dân dã", "sang trọng", "đậm đà"])
        name = f"{prefix} {cuisine} {suffix}"
        
        # Tạo nguyên liệu
        num_ingredients = random.randint(3, 6)
        all_ingredients = ["thịt bò", "thịt gà", "thịt heo", "cá", "tôm", "mực", "cua", "bạch tuộc", 
                         "rau cải", "cà rốt", "bắp cải", "hành", "tỏi", "ớt", "nấm", "khoai tây", 
                         "gạo", "bún", "mì", "miến", "đậu", "đậu phụ", "đậu nành", "trứng", 
                         "sữa", "phô mai", "bơ", "dầu olive", "nước mắm", "nước tương", "sốt cà chua", "tương ớt"]
        ingredients = ", ".join(random.sample(all_ingredients, num_ingredients))
        
        # Tạo hương vị
        num_flavors = random.randint(2, 4)
        flavors = ", ".join(random.sample(flavors_list, num_flavors))
        
        # Tạo đặc điểm
        features = f"{name.lower()} {ingredients} {flavors} {cuisine.lower()} {category.lower()}"
        
        # Thêm vào danh sách
        food_names.append((food_id, name, category, cuisine, ingredients, flavors, features))
    
    # Tạo DataFrame
    foods_df = pd.DataFrame(food_names, columns=['food_id', 'name', 'category', 'cuisine', 'ingredients', 'flavors', 'features'])
    
    # Tạo giá ngẫu nhiên dựa trên ẩm thực
    foods_df['price'] = foods_df.apply(
        lambda row: random.randint(cuisine_price_range[row['cuisine']][0], cuisine_price_range[row['cuisine']][1]), 
        axis=1
    )
    
    # Import dữ liệu vào database
    cursor = conn.cursor()
    
    # Xóa dữ liệu cũ (nếu có)
    cursor.execute("DELETE FROM foods")
    conn.commit()
    
    # Thêm dữ liệu mới
    for _, row in foods_df.iterrows():
        insert_query = """
        INSERT INTO foods (food_id, name, category, cuisine, ingredients, flavors, features, price)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        cursor.execute(insert_query, (
            row['food_id'], row['name'], row['category'], row['cuisine'],
            row['ingredients'], row['flavors'], row['features'], float(row['price'])
        ))
    
    conn.commit()
    cursor.close()
    conn.close()
    
    print(f"Đã import {len(foods_df)} món ăn vào database")
    return True

def import_sample_customers():
    """Tạo và import dữ liệu mẫu cho khách hàng"""
    # Kết nối tới database
    conn = create_connection(
        host=host,
        port=port,
        user=user,
        password=password,
        database=database
    )
    
    if not conn:
        print("Không thể kết nối tới database")
        return False
    
    # Tạo danh sách họ và tên
    first_names = ["Nguyễn", "Trần", "Lê", "Phạm", "Hoàng", "Huỳnh", "Phan", "Vũ", "Võ", "Đặng", "Bùi", "Đỗ", "Hồ", "Ngô", "Dương"]
    middle_names = ["Văn", "Thị", "Hữu", "Đức", "Công", "Minh", "Quốc", "Thanh", "Quang", "Thành", "Thu", "Như", "Anh", "Tuấn", "Hương"]
    last_names = ["An", "Bình", "Cường", "Dũng", "Giang", "Hải", "Hùng", "Huyền", "Lâm", "Linh", "Mai", "Nam", "Phúc", "Quân", "Thắng",
                 "Thảo", "Trang", "Trung", "Tuyết", "Vinh", "Yến", "Đạt", "Hà", "Khánh", "Long", "Minh", "Nhung", "Phương", "Quyên", "Sơn"]
    
    # Tạo danh sách khách hàng
    customers = []
    
    for i in range(1, 51):
        customer_id = f"C{i:03d}"
        
        # Tạo tên
        first = random.choice(first_names)
        middle = random.choice(middle_names)
        last = random.choice(last_names)
        name = f"{first} {middle} {last}"
        
        # Tạo tuổi
        age = random.randint(18, 65)
        
        # Tạo giới tính
        gender = random.choice(["Nam", "Nữ"])
        
        # Tạo độ nhạy cảm về giá
        price_sensitivity = round(random.uniform(0.1, 1.0), 2)
        
        customers.append((customer_id, name, age, gender, price_sensitivity))
    
    # Tạo DataFrame
    customers_df = pd.DataFrame(customers, columns=['customer_id', 'name', 'age', 'gender', 'price_sensitivity'])
    
    # Import dữ liệu vào database
    cursor = conn.cursor()
    
    # Xóa dữ liệu cũ (nếu có)
    cursor.execute("DELETE FROM customers")
    conn.commit()
    
    # Thêm dữ liệu mới
    for _, row in customers_df.iterrows():
        insert_query = """
        INSERT INTO customers (customer_id, name, age, gender, price_sensitivity)
        VALUES (%s, %s, %s, %s, %s)
        """
        
        cursor.execute(insert_query, (
            row['customer_id'], row['name'], int(row['age']), row['gender'], float(row['price_sensitivity'])
        ))
    
    conn.commit()
    cursor.close()
    conn.close()
    
    print(f"Đã import {len(customers_df)} khách hàng vào database")
    return True

def import_sample_ratings():
    """Tạo và import dữ liệu mẫu cho đánh giá"""
    # Kết nối tới database
    conn = create_connection(
        host=host,
        port=port,
        user=user,
        password=password,
        database=database
    )
    
    if not conn:
        print("Không thể kết nối tới database")
        return False
    
    # Lấy danh sách food_id
    cursor = conn.cursor()
    cursor.execute("SELECT food_id FROM foods")
    food_ids = [row[0] for row in cursor.fetchall()]
    
    # Lấy danh sách customer_id
    cursor.execute("SELECT customer_id FROM customers")
    customer_ids = [row[0] for row in cursor.fetchall()]
    
    # Tạo danh sách đánh giá
    ratings = []
    
    # Mỗi khách hàng đánh giá khoảng 10-30 món ăn
    for customer_id in customer_ids:
        # Số lượng món ăn sẽ đánh giá
        num_ratings = random.randint(10, 30)
        
        # Chọn ngẫu nhiên các món ăn
        selected_foods = random.sample(food_ids, num_ratings)
        
        # Tạo các đánh giá
        for food_id in selected_foods:
            # Tạo điểm đánh giá (1-5)
            rating = random.choices([1, 2, 3, 4, 5], weights=[0.05, 0.1, 0.2, 0.35, 0.3])[0]
            
            # Tạo thời gian đánh giá (trong 3 tháng gần đây)
            days_ago = random.randint(0, 90)
            timestamp = datetime.now() - timedelta(days=days_ago)
            
            ratings.append((customer_id, food_id, rating, timestamp))
    
    # Tạo DataFrame
    ratings_df = pd.DataFrame(ratings, columns=['customer_id', 'food_id', 'rating', 'timestamp'])
    
    # Import dữ liệu vào database
    # Xóa dữ liệu cũ (nếu có)
    cursor.execute("DELETE FROM ratings")
    conn.commit()
    
    # Thêm dữ liệu mới
    for _, row in ratings_df.iterrows():
        insert_query = """
        INSERT INTO ratings (customer_id, food_id, rating, timestamp)
        VALUES (%s, %s, %s, %s)
        """
        
        cursor.execute(insert_query, (
            row['customer_id'], row['food_id'], int(row['rating']), row['timestamp']
        ))
    
    conn.commit()
    cursor.close()
    conn.close()
    
    print(f"Đã import {len(ratings_df)} đánh giá vào database")
    return True

def import_all_sample_data():
    """Import tất cả dữ liệu mẫu"""
    print("Bắt đầu import dữ liệu mẫu...")
    
    # Import dữ liệu món ăn
    if not import_sample_foods():
        print("Lỗi khi import dữ liệu món ăn")
        return False
    
    # Import dữ liệu khách hàng
    if not import_sample_customers():
        print("Lỗi khi import dữ liệu khách hàng")
        return False
    
    # Import dữ liệu đánh giá
    if not import_sample_ratings():
        print("Lỗi khi import dữ liệu đánh giá")
        return False
    
    print("Import dữ liệu mẫu thành công!")
    return True

if __name__ == "__main__":
    import_all_sample_data()
