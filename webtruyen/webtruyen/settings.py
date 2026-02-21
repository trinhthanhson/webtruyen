
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-15&9bm1ik@+8py!xjzxn&6k3_td#8mi79wq-#m4df%bz(0$3r7'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'cloudinary', 
    'story',
]

JAZZMIN_SETTINGS = {
    "site_title": "Nguyệt Mộng Thư Admin",
    "site_header": "Nguyệt Mộng Thư",
    "site_brand": "Quản trị Nguyệt Mộng",
    "welcome_sign": "Chào mừng bạn đến với hệ thống quản trị truyện",
    "copyright": "Nguyệt Mộng Thư Ltd",
    "search_model": ["story.Story"],
    "topmenu_links": [
        {"name": "Trang chủ web", "url": "/", "new_window": True},
    ],
    "show_sidebar": True,
    "navigation_expanded": True,
    "icons": {
        "auth": "fas fa-users-cog",
        "auth.user": "fas fa-user",
        "story.Story": "fas fa-book",
        "story.Category": "fas fa-list",
        "story.Chapter": "fas fa-file-alt",
        "story.Comment": "fas fa-comments",
    },
    "order_with_respect_to": ["story", "story.Story", "story.Chapter", "story.Category"],
}

JAZZMIN_UI_TWEAKS = {
    "theme": "flatly",  # Có thể chọn: pulse, flatly, darkly, slate
    "navbar_variant": "navbar-dark",
    "accent": "accent-primary",
}
# 1. Cấu hình thông tin Cloudinary (Lấy từ Dashboard của Cloudinary)
CLOUDINARY_CLOUD_NAME = 'dqb9trxs4'  # Ví dụ: 'webtruyen-project'
CLOUDINARY_API_KEY = '526277124128331'
CLOUDINARY_API_SECRET = 'lBNZfs38GP1iGvMKXCRzjDzZcss'

import cloudinary

try:
    cloudinary.config(cloud_name = CLOUDINARY_CLOUD_NAME,api_key = CLOUDINARY_API_KEY,api_secret = CLOUDINARY_API_SECRET,secure=True)# type: ignore
except Exception as e:
    # In ra lỗi nếu cấu hình bị sai key/secret
    print(f"LỖI CẤU HÌNH CLOUDINARY: {e}") 
    pass

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'webtruyen.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'webtruyen.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'webtruyen',      # Tên Database PostgreSQL bạn đã tạo
        'USER': 'postgres',        # Username của bạn (thường là 'postgres')
        'PASSWORD': '1234',    # Mật khẩu của PostgreSQL user
        'HOST': 'localhost',                # Hoặc địa chỉ IP nếu DB nằm trên server khác
        'PORT': '5432',                     # Port mặc định của PostgreSQL
    }
}

# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
import os

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
STATIC_URL = '/static/'
STATICFILES_DIRS = []
STATIC_ROOT = BASE_DIR / 'staticfiles'
