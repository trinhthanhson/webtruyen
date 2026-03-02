import os
from pathlib import Path
import dj_database_url
from django.utils.translation import gettext_lazy as _
BASE_DIR = Path(__file__).resolve().parent.parent


SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-15&9bm1ik@+8py!xjzxn&6k3_td#8mi79wq-#m4df%bz(0$3r7')

DEBUG = 'RENDER' not in os.environ

ALLOWED_HOSTS = ['localhost', '127.0.0.1']

RENDER_EXTERNAL_HOSTNAME = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)

INSTALLED_APPS = [
    'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'whitenoise.runserver_nostatic', 
    'django.contrib.staticfiles',
    'cloudinary', 
    'story',
]

LANGUAGES = [
    ('vi', _('Tiếng Việt')),
    ('en', _('English')),
    ('zh-hans', _('Chinese')), # Tiếng Trung giản thể
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware', 
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware', 
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'webtruyen.urls'

LOCALE_PATHS = [
    BASE_DIR / 'locale/',
]
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

DATABASES = {
    'default': dj_database_url.config(
        default='postgresql://postgres:1234@localhost:5432/webtruyen',
        conn_max_age=600
    )
}

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

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