# story/urls.py

from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    # URL gốc của app 'story' (thường là trang chủ)
    path("", views.home, name="home"),
    # Trang chi tiết truyện
    path('doc/<slug:story_slug>/', views.story_detail, name='story_detail'),
    path("categories/<slug:category_slug>/", views.category_detail, name="category_detail"),
    # trang chi tiết chương truyện
    path('doc/<slug:story_slug>/<chapter_number>/', views.chapter_detail, name='chapter_detail'),
 # Nếu bạn vẫn muốn hàm banner riêng
   # view banner
    path("banner-data/", views.home_banner, name="banner_data"),
    # view list stories
    path("stories/", views.story_list, name="stories"),  # <--- Dùng tên 'stories',
    path(
        "categories/", views.category_list, name="categories"
    ),  # <--- Dùng tên 'categories',
    path("register/", views.register_view, name="register"),
    path("login/", views.login_view, name="login"),
    # 1. Gửi email reset
    path(
        "password_reset/",
        auth_views.PasswordResetView.as_view(
            template_name="story/account/password_reset_form.html"
        ),
        name="password_reset",
    ),
    # 2. Xác nhận đã gửi email thành công
    path(
        "password_reset/done/",
        auth_views.PasswordResetDoneView.as_view(
            template_name="story/account/password_reset_done.html"
        ),
        name="password_reset_done",
    ),
    # 3. Đặt lại mật khẩu (từ link email)
    path(
        "reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="story/account/password_reset_confirm.html"
        ),
        name="password_reset_confirm",
    ),
    # 4. Xác nhận đặt lại mật khẩu thành công
    path(
        "reset/done/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="story/account/password_reset_complete.html"
        ),
        name="password_reset_complete",
    ),
    path("search_results/", views.search_results, name="search_results"),
    path("accounts/profile/", views.profile_view, name="profile"),
    path("accounts/profile/edit/", views.profile_edit_view, name="profile_edit"),
    path("logout/", views.custom_logout_view, name="logout"),
    path('favorite/<int:story_id>/', views.toggle_favorite, name='toggle_favorite'),
]
