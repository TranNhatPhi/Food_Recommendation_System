import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from collections import Counter

def plot_rating_distribution(ratings_df):
    """Tạo biểu đồ phân phối đánh giá"""
    rating_counts = ratings_df['rating'].value_counts().sort_index()
    
    fig = px.bar(
        x=rating_counts.index,
        y=rating_counts.values,
        labels={'x': 'Điểm đánh giá', 'y': 'Số lượng'},
        title='Phân phối điểm đánh giá',
        color=rating_counts.values,
        color_continuous_scale=px.colors.sequential.Reds
    )
    
    fig.update_layout(
        xaxis=dict(tickmode='linear', tick0=1, dtick=1),
        coloraxis_showscale=False
    )
    
    return fig

def plot_popular_cuisines(foods_df, ratings_df):
    """Tạo biểu đồ ẩm thực phổ biến dựa trên số lượng đánh giá"""
    # Kết hợp foods và ratings
    merged_df = pd.merge(ratings_df, foods_df[['food_id', 'cuisine']], on='food_id')
    
    # Đếm số đánh giá theo cuisine
    cuisine_counts = merged_df['cuisine'].value_counts().reset_index()
    cuisine_counts.columns = ['cuisine', 'count']
    
    # Lấy top 10 cuisine
    top_cuisines = cuisine_counts.head(10)
    
    fig = px.bar(
        top_cuisines,
        x='cuisine',
        y='count',
        color='count',
        labels={'cuisine': 'Ẩm thực', 'count': 'Số lượng đánh giá'},
        title='Top 10 ẩm thực phổ biến nhất',
        color_continuous_scale=px.colors.sequential.Reds
    )
    
    fig.update_layout(coloraxis_showscale=False)
    
    return fig

def plot_popular_flavors(foods_df):
    """Tạo biểu đồ hương vị phổ biến"""
    # Tách các hương vị và đếm tần suất
    all_flavors = []
    for flavors in foods_df['flavors']:
        all_flavors.extend([f.strip() for f in flavors.split(',')])
    
    flavor_counter = Counter(all_flavors)
    top_flavors = pd.DataFrame(flavor_counter.most_common(10), columns=['flavor', 'count'])
    
    fig = px.bar(
        top_flavors,
        x='flavor',
        y='count',
        color='count',
        labels={'flavor': 'Hương vị', 'count': 'Số lượng món ăn'},
        title='Top 10 hương vị phổ biến nhất',
        color_continuous_scale=px.colors.sequential.Reds
    )
    
    fig.update_layout(coloraxis_showscale=False)
    
    return fig

def plot_avg_price_by_cuisine(foods_df):
    """Tạo biểu đồ giá trung bình theo ẩm thực"""
    avg_price = foods_df.groupby('cuisine')['price'].mean().reset_index()
    avg_price = avg_price.sort_values('price', ascending=False)
    
    # Lấy top 15 ẩm thực có giá trung bình cao nhất
    top_cuisines = avg_price.head(15)
    
    fig = px.bar(
        top_cuisines,
        x='cuisine',
        y='price',
        color='price',
        labels={'cuisine': 'Ẩm thực', 'price': 'Giá trung bình (đồng)'},
        title='Giá trung bình theo ẩm thực',
        color_continuous_scale=px.colors.sequential.Reds
    )
    
    fig.update_layout(
        coloraxis_showscale=False,
        yaxis=dict(tickformat=',')
    )
    
    return fig

def plot_rating_trends(ratings_df):
    """Tạo biểu đồ xu hướng đánh giá theo thời gian"""
    # Chuyển đổi timestamp thành datetime nếu cần
    if not pd.api.types.is_datetime64_any_dtype(ratings_df['timestamp']):
        ratings_df['timestamp'] = pd.to_datetime(ratings_df['timestamp'])
    
    # Nhóm theo tháng và tính trung bình
    ratings_df['month'] = ratings_df['timestamp'].dt.to_period('M')
    monthly_avg = ratings_df.groupby('month')['rating'].mean().reset_index()
    monthly_avg['month'] = monthly_avg['month'].dt.to_timestamp()
    
    fig = px.line(
        monthly_avg,
        x='month',
        y='rating',
        labels={'month': 'Tháng', 'rating': 'Điểm đánh giá trung bình'},
        title='Xu hướng đánh giá theo thời gian',
        markers=True
    )
    
    fig.update_layout(
        xaxis=dict(tickformat='%m/%Y'),
        yaxis=dict(range=[0, 5])
    )
    
    return fig

def plot_category_distribution(foods_df):
    """Tạo biểu đồ phân phối loại món ăn"""
    category_counts = foods_df['category'].value_counts()
    
    fig = px.pie(
        values=category_counts.values,
        names=category_counts.index,
        title='Phân phối loại món ăn',
        color_discrete_sequence=px.colors.sequential.Reds_r
    )
    
    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(uniformtext_minsize=12, uniformtext_mode='hide')
    
    return fig

def plot_price_distribution(foods_df):
    """Tạo biểu đồ phân phối giá"""
    fig = px.histogram(
        foods_df,
        x='price',
        nbins=20,
        labels={'price': 'Giá (đồng)', 'count': 'Số lượng món ăn'},
        title='Phân phối giá món ăn',
        color_discrete_sequence=['#ff4b4b']
    )
    
    fig.update_layout(
        xaxis=dict(tickformat=','),
        bargap=0.1
    )
    
    return fig
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from collections import Counter

def plot_rating_distribution(ratings_df):
    """Tạo biểu đồ phân phối đánh giá"""
    rating_counts = ratings_df['rating'].value_counts().sort_index()
    
    fig = px.bar(
        x=rating_counts.index,
        y=rating_counts.values,
        labels={'x': 'Điểm đánh giá', 'y': 'Số lượng'},
        title='Phân phối điểm đánh giá',
        color=rating_counts.values,
        color_continuous_scale=px.colors.sequential.Reds
    )
    
    fig.update_layout(
        xaxis=dict(tickmode='linear', tick0=1, dtick=1),
        coloraxis_showscale=False
    )
    
    return fig

def plot_popular_cuisines(foods_df, ratings_df):
    """Tạo biểu đồ ẩm thực phổ biến dựa trên số lượng đánh giá"""
    # Kết hợp foods và ratings
    merged_df = pd.merge(ratings_df, foods_df[['food_id', 'cuisine']], on='food_id')
    
    # Đếm số đánh giá theo cuisine
    cuisine_counts = merged_df['cuisine'].value_counts().reset_index()
    cuisine_counts.columns = ['cuisine', 'count']
    
    # Lấy top 10 cuisine
    top_cuisines = cuisine_counts.head(10)
    
    fig = px.bar(
        top_cuisines,
        x='cuisine',
        y='count',
        color='count',
        labels={'cuisine': 'Ẩm thực', 'count': 'Số lượng đánh giá'},
        title='Top 10 ẩm thực phổ biến nhất',
        color_continuous_scale=px.colors.sequential.Reds
    )
    
    fig.update_layout(coloraxis_showscale=False)
    
    return fig

def plot_popular_flavors(foods_df):
    """Tạo biểu đồ hương vị phổ biến"""
    # Tách các hương vị và đếm tần suất
    all_flavors = []
    for flavors in foods_df['flavors']:
        all_flavors.extend([f.strip() for f in flavors.split(',')])
    
    flavor_counter = Counter(all_flavors)
    top_flavors = pd.DataFrame(flavor_counter.most_common(10), columns=['flavor', 'count'])
    
    fig = px.bar(
        top_flavors,
        x='flavor',
        y='count',
        color='count',
        labels={'flavor': 'Hương vị', 'count': 'Số lượng món ăn'},
        title='Top 10 hương vị phổ biến nhất',
        color_continuous_scale=px.colors.sequential.Reds
    )
    
    fig.update_layout(coloraxis_showscale=False)
    
    return fig

def plot_avg_price_by_cuisine(foods_df):
    """Tạo biểu đồ giá trung bình theo ẩm thực"""
    avg_price = foods_df.groupby('cuisine')['price'].mean().reset_index()
    avg_price = avg_price.sort_values('price', ascending=False)
    
    # Lấy top 15 ẩm thực có giá trung bình cao nhất
    top_cuisines = avg_price.head(15)
    
    fig = px.bar(
        top_cuisines,
        x='cuisine',
        y='price',
        color='price',
        labels={'cuisine': 'Ẩm thực', 'price': 'Giá trung bình (đồng)'},
        title='Giá trung bình theo ẩm thực',
        color_continuous_scale=px.colors.sequential.Reds
    )
    
    fig.update_layout(
        coloraxis_showscale=False,
        yaxis=dict(tickformat=',')
    )
    
    return fig

def plot_rating_trends(ratings_df):
    """Tạo biểu đồ xu hướng đánh giá theo thời gian"""
    # Chuyển đổi timestamp thành datetime nếu cần
    if not pd.api.types.is_datetime64_any_dtype(ratings_df['timestamp']):
        ratings_df['timestamp'] = pd.to_datetime(ratings_df['timestamp'])
    
    # Nhóm theo tháng và tính trung bình
    ratings_df['month'] = ratings_df['timestamp'].dt.to_period('M')
    monthly_avg = ratings_df.groupby('month')['rating'].mean().reset_index()
    monthly_avg['month'] = monthly_avg['month'].dt.to_timestamp()
    
    fig = px.line(
        monthly_avg,
        x='month',
        y='rating',
        labels={'month': 'Tháng', 'rating': 'Điểm đánh giá trung bình'},
        title='Xu hướng đánh giá theo thời gian',
        markers=True
    )
    
    fig.update_layout(
        xaxis=dict(tickformat='%m/%Y'),
        yaxis=dict(range=[0, 5])
    )
    
    return fig

def plot_category_distribution(foods_df):
    """Tạo biểu đồ phân phối loại món ăn"""
    category_counts = foods_df['category'].value_counts()
    
    fig = px.pie(
        values=category_counts.values,
        names=category_counts.index,
        title='Phân phối loại món ăn',
        color_discrete_sequence=px.colors.sequential.Reds_r
    )
    
    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(uniformtext_minsize=12, uniformtext_mode='hide')
    
    return fig

def plot_price_distribution(foods_df):
    """Tạo biểu đồ phân phối giá"""
    fig = px.histogram(
        foods_df,
        x='price',
        nbins=20,
        labels={'price': 'Giá (đồng)', 'count': 'Số lượng món ăn'},
        title='Phân phối giá món ăn',
        color_discrete_sequence=['#ff4b4b']
    )
    
    fig.update_layout(
        xaxis=dict(tickformat=','),
        bargap=0.1
    )
    
    return fig

def plot_customer_ratings_radar(customer_id, ratings_df, foods_df):
    """Tạo biểu đồ radar cho sở thích của khách hàng theo loại ẩm thực"""
    # Lấy đánh giá của khách hàng
    customer_ratings = ratings_df[ratings_df['customer_id'] == customer_id]
    
    if customer_ratings.empty:
        return None
    
    # Kết hợp với thông tin món ăn
    customer_data = pd.merge(customer_ratings, foods_df[['food_id', 'cuisine']], on='food_id')
    
    # Tính điểm trung bình theo loại ẩm thực
    cuisine_avg = customer_data.groupby('cuisine')['rating'].mean().reset_index()
    
    # Lấy top ẩm thực có nhiều đánh giá nhất
    cuisine_counts = customer_data['cuisine'].value_counts().reset_index()
    cuisine_counts.columns = ['cuisine', 'count']
    top_cuisines = cuisine_counts.head(8)['cuisine'].tolist()
    
    # Lọc dữ liệu
    radar_data = cuisine_avg[cuisine_avg['cuisine'].isin(top_cuisines)]
    
    # Tạo biểu đồ radar
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=radar_data['rating'],
        theta=radar_data['cuisine'],
        fill='toself',
        name='Điểm đánh giá',
        line=dict(color='#ff4b4b')
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 5]
            )
        ),
        title='Sở thích của khách hàng theo loại ẩm thực'
    )
    
    return fig

def plot_rating_heatmap(ratings_df, foods_df):
    """Tạo biểu đồ heatmap cho đánh giá theo loại ẩm thực và loại món ăn"""
    # Kết hợp ratings và foods
    merged_df = pd.merge(ratings_df, foods_df[['food_id', 'cuisine', 'category']], on='food_id')
    
    # Tính điểm trung bình theo cuisine và category
    heatmap_data = merged_df.groupby(['cuisine', 'category'])['rating'].mean().reset_index()
    
    # Tạo pivot table
    pivot_data = heatmap_data.pivot(index='cuisine', columns='category', values='rating')
    
    # Lấy top N cuisine có nhiều đánh giá nhất
    top_cuisines = merged_df['cuisine'].value_counts().head(10).index.tolist()
    pivot_data = pivot_data.loc[pivot_data.index.isin(top_cuisines)]
    
    # Tạo biểu đồ heatmap
    fig = px.imshow(
        pivot_data,
        labels=dict(x='Loại món', y='Ẩm thực', color='Điểm đánh giá'),
        x=pivot_data.columns,
        y=pivot_data.index,
        color_continuous_scale='Reds',
        title='Điểm đánh giá trung bình theo loại ẩm thực và loại món ăn'
    )
    
    fig.update_layout(
        xaxis={'side': 'top'},
        coloraxis_colorbar=dict(
            title='Điểm đánh giá',
            titleside='right',
            ticks='outside',
            tickvals=[1, 2, 3, 4, 5],
            ticktext=['1', '2', '3', '4', '5'],
            len=0.6
        )
    )
    
    return fig
def plot_customer_ratings_radar(customer_id, ratings_df, foods_df):
    """Tạo biểu đồ radar cho sở thích của khách hàng theo loại ẩm thực"""
    # Lấy đánh giá của khách hàng
    customer_ratings = ratings_df[ratings_df['customer_id'] == customer_id]
    
    if customer_ratings.empty:
        return None
    
    # Kết hợp với thông tin món ăn
    customer_data = pd.merge(customer_ratings, foods_df[['food_id', 'cuisine']], on='food_id')
    
    # Tính điểm trung bình theo loại ẩm thực
    cuisine_avg = customer_data.groupby('cuisine')['rating'].mean().reset_index()
    
    # Lấy top ẩm thực có nhiều đánh giá nhất
    cuisine_counts = customer_data['cuisine'].value_counts().reset_index()
    cuisine_counts.columns = ['cuisine', 'count']
    top_cuisines = cuisine_counts.head(8)['cuisine'].tolist()
    
    # Lọc dữ liệu
    radar_data = cuisine_avg[cuisine_avg['cuisine'].isin(top_cuisines)]
    
    # Tạo biểu đồ radar
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=radar_data['rating'],
        theta=radar_data['cuisine'],
        fill='toself',
        name='Điểm đánh giá',
        line=dict(color='#ff4b4b')
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 5]
            )
        ),
        title='Sở thích của khách hàng theo loại ẩm thực'
    )
    
    return fig

def plot_rating_heatmap(ratings_df, foods_df):
    """Tạo biểu đồ heatmap cho đánh giá theo loại ẩm thực và loại món ăn"""
    # Kết hợp ratings và foods
    merged_df = pd.merge(ratings_df, foods_df[['food_id', 'cuisine', 'category']], on='food_id')
    print("🧪 Kiểm tra cột của foods_df:", foods_df.columns.tolist())
    assert 'cuisine' in foods_df.columns, "❌ Cột 'cuisine' KHÔNG TỒN TẠI trong foods_df!"

    # Tính điểm trung bình theo cuisine và category
    heatmap_data = merged_df.groupby(['cuisine', 'category'])['rating'].mean().reset_index()
    
    # Tạo pivot table
    pivot_data = heatmap_data.pivot(index='cuisine', columns='category', values='rating')
    
    # Lấy top N cuisine có nhiều đánh giá nhất
    top_cuisines = merged_df['cuisine'].value_counts().head(10).index.tolist()
    pivot_data = pivot_data.loc[pivot_data.index.isin(top_cuisines)]
    
    # Tạo biểu đồ heatmap
    fig = px.imshow(
        pivot_data,
        labels=dict(x='Loại món', y='Ẩm thực', color='Điểm đánh giá'),
        x=pivot_data.columns,
        y=pivot_data.index,
        color_continuous_scale='Reds',
        title='Điểm đánh giá trung bình theo loại ẩm thực và loại món ăn'
    )
    
    fig.update_layout(
        xaxis={'side': 'top'},
        coloraxis_colorbar=dict(
            title='Điểm đánh giá',
            titleside='right',
            ticks='outside',
            tickvals=[1, 2, 3, 4, 5],
            ticktext=['1', '2', '3', '4', '5'],
            len=0.6
        )
    )
    
    return fig
