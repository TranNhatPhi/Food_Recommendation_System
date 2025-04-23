import pandas as pd
import numpy as np
import random

# Đặt seed cho kết quả nhất quán
np.random.seed(42)
random.seed(42)

def create_food_items(num_items=100):
    categories = ['Món chính', 'Món khai vị', 'Món tráng miệng', 'Đồ uống', 'Món đặc biệt']
    cuisines = ['Việt Nam', 'Trung Hoa', 'Nhật Bản', 'Ý', 'Pháp', 'Ấn Độ', 'Thái Lan', 'Hàn Quốc']
    flavors = ['cay', 'ngọt', 'mặn', 'chua', 'đắng', 'béo', 'thơm']
    ingredients = ['thịt bò', 'thịt gà', 'thịt heo', 'hải sản', 'rau củ', 'gạo', 'mì', 'nấm', 'đậu', 'trứng']
    cooking_methods = ['nướng', 'xào', 'hấp', 'chiên', 'luộc', 'lẩu', 'nấu', 'ủ']

    foods = []

    for i in range(1, num_items + 1):
        item_category = random.choice(categories)
        item_cuisine = random.choice(cuisines)

        # Tạo tên món ăn
        prefix = random.choice(['', 'Món ', 'Đặc sản '])
        if item_category == 'Đồ uống':
            name_options = ['Nước', 'Sinh tố', 'Trà', 'Cà phê', 'Rượu', 'Cocktail']
            name_suffix = random.choice([' đặc biệt', ' truyền thống', ' fusion', ' nhà làm', ' premium'])
            name_base = random.choice(name_options)
            name = f"{name_base}{name_suffix} #{i}"
        else:
            name_suffix = random.choice(['', ' đặc biệt', ' truyền thống', ' fusion', ' nhà làm', ' premium'])
            if random.random() < 0.5:
                ingredient = random.choice(ingredients)
                method = random.choice(cooking_methods)
                name = f"{prefix}{ingredient} {method}{name_suffix} #{i}"
            else:
                name = f"{prefix}Món {item_cuisine}{name_suffix} #{i}"

        # Chọn ngẫu nhiên 1-3 hương vị
        num_flavors = random.randint(1, 3)
        item_flavors = ', '.join(random.sample(flavors, num_flavors))

        # Chọn ngẫu nhiên 1-4 nguyên liệu
        num_ingredients = random.randint(1, 4)
        item_ingredients = ', '.join(random.sample(ingredients, num_ingredients))

        # Tạo giá từ 20,000 đến 300,000 VND
        price = round(random.uniform(2, 30), 1) * 10000

        # Tạo đặc điểm món ăn
        features = f"{item_category} {item_cuisine} {item_flavors} {item_ingredients}"

        # Độ phổ biến (dùng để tạo rating sau này)
        popularity = random.uniform(2.5, 5.0)

        foods.append({
            'food_id': i,
            'name': name,
            'category': item_category,
            'cuisine': item_cuisine,
            'flavors': item_flavors,
            'ingredients': item_ingredients,
            'price': price,
            'features': features,
            'popularity': popularity
        })

    return pd.DataFrame(foods)

def create_customers(num_customers=500):
    customers = []

    for i in range(1, num_customers + 1):
        age = random.randint(18, 70)
        gender = random.choice(['Nam', 'Nữ', 'Khác'])
        preferred_flavors = random.sample(['cay', 'ngọt', 'mặn', 'chua', 'đắng', 'béo', 'thơm'], random.randint(1, 4))
        preferred_cuisines = random.sample(
            ['Việt Nam', 'Trung Hoa', 'Nhật Bản', 'Ý', 'Pháp', 'Ấn Độ', 'Thái Lan', 'Hàn Quốc'], random.randint(1, 3))
        price_sensitivity = random.uniform(0.2, 1.0)

        customers.append({
            'customer_id': i,
            'age': age,
            'gender': gender,
            'preferred_flavors': ', '.join(preferred_flavors),
            'preferred_cuisines': ', '.join(preferred_cuisines),
            'price_sensitivity': price_sensitivity
        })

    return pd.DataFrame(customers)

def create_ratings(customers_df, foods_df, sparsity=0.05):
    all_ratings = []

    for cust_id in customers_df['customer_id']:
        # Mỗi khách hàng chỉ đánh giá một số món (sparsity là mật độ đánh giá)
        num_ratings = int(len(foods_df) * sparsity * random.uniform(0.5, 1.5))

        # Lấy thông tin khách hàng để tính rating phù hợp
        customer = customers_df[customers_df['customer_id'] == cust_id].iloc[0]
        preferred_flavors = customer['preferred_flavors'].split(', ')
        preferred_cuisines = customer['preferred_cuisines'].split(', ')
        price_sensitivity = customer['price_sensitivity']

        # Chọn ngẫu nhiên các món để đánh giá
        foods_to_rate = foods_df.sample(min(num_ratings, len(foods_df)))

        for _, food in foods_to_rate.iterrows():
            base_rating = food['popularity'] * random.uniform(0.7, 1.3)

            # Điều chỉnh rating dựa trên sở thích
            flavor_match = any(flavor in food['flavors'] for flavor in preferred_flavors)
            cuisine_match = food['cuisine'] in preferred_cuisines

            adjustment = 0
            if flavor_match:
                adjustment += random.uniform(0.2, 0.8)
            if cuisine_match:
                adjustment += random.uniform(0.2, 0.8)

            # Điều chỉnh theo giá
            if food['price'] > 150000 and price_sensitivity < 0.5:
                adjustment -= random.uniform(0.2, 0.8)

            rating = min(5.0, max(1.0, base_rating + adjustment))

            # Thêm ngày đánh giá ngẫu nhiên trong vòng 6 tháng qua
            days_ago = random.randint(1, 180)

            all_ratings.append({
                'customer_id': cust_id,
                'food_id': food['food_id'],
                'rating': round(rating, 1),
                'days_ago': days_ago
            })

    return pd.DataFrame(all_ratings)
