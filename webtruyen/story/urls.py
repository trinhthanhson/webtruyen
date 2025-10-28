# story/urls.py

from django.urls import path
from . import views

urlpatterns = [
    # URL gốc của app 'story' (thường là trang chủ)
    path('', views.story_list, name='home'), 
    
    # Trang chi tiết truyện
    path('truyen/<int:story_id>/', views.story_detail, name='story_detail'),
    
    # Trang đọc chương. Chấp nhận số chương có thể là Decimal (ví dụ: 1.5)
    # Vì chapter_number là Decimal, ta dùng float trong URL patterns
path('doc/<int:story_id>/<str:chapter_number>/', views.chapter_detail, name='chapter_detail'),
    # Nếu bạn vẫn muốn hàm banner riêng
    path('banner-data/', views.home_banner, name='banner_data'), 
]