import os
from pathlib import Path
import dj_database_url

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# --- SECURITY ---
# Sử dụng biến môi trường để bảo mật Secret Key trên Render
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-15&9bm1ik@+8py!xjzxn&6k3_td#8mi79wq-#m4df%bz(0$3r7')

# Tự động tắt DEBUG khi chạy trên Render (môi trường Production)
DEBUG = 'RENDER' not in os.environ

# --- TỰ ĐỘNG CẤU HÌNH HOST ---
ALLOWED_HOSTS = ['localhost', '127.0.0.1']

# Lấy hostname từ Render (ví dụ: web-story-deployment-new.onrender.com)
RENDER_EXTERNAL_HOSTNAME = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)

# --- APPLICATION DEFINITION ---
INSTALLED_APPS = [
    'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'whitenoise.runserver_nostatic', # Hỗ trợ static file
    'django.contrib.staticfiles',
    'cloudinary', 
    'story',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware', # QUAN TRỌNG: Phải nằm sau SecurityMiddleware
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

# --- DATABASE (Tự động chuyển đổi Local <-> Render) ---
DATABASES = {
    'default': dj_database_url.config(
        # Nếu không thấy biến môi trường DATABASE_URL, nó sẽ dùng Database ở localhost
        default='postgresql://postgres:1234@localhost:5432/webtruyen',
        conn_max_age=600
    )
}

# --- STATIC & MEDIA FILES ---
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Cấu hình lưu trữ file tĩnh tối ưu cho Render
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# --- CLOUDINARY CONFIG ---
CLOUDINARY_CLOUD_NAME = 'dqb9trxs4'
CLOUDINARY_API_KEY = '526277124128331'
CLOUDINARY_API_SECRET = 'lBNZfs38GP1iGvMKXCRzjDzZcss'

import cloudinary
cloudinary.config(
    cloud_name=CLOUDINARY_CLOUD_NAME,
    api_key=CLOUDINARY_API_KEY,
    api_secret=CLOUDINARY_API_SECRET,
    secure=True
)

# --- JAZZMIN SETTINGS ---
JAZZMIN_SETTINGS = {
    "site_title": "Thiên Mộng Hành Admin",
    "site_header": "Thiên Mộng Hành",
    "site_brand": "Quản trị Nguyệt Mộng",
    "welcome_sign": "Chào mừng bạn đến với hệ thống quản trị truyện",
    "copyright": "Thiên Mộng Hành Ltd",
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
    "theme": "flatly",
    "navbar_variant": "navbar-dark",
    "accent": "accent-primary",
}

# --- OTHERS ---
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'