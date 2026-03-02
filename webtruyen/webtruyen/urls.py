from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns 
urlpatterns = [
    path('admin/', admin.site.urls),
    path('i18n/', include('django.conf.urls.i18n')),
    path('', include('story.urls')),  # Trang chủ sẽ trỏ vào story
]

# Chỉ phục vụ file media (ảnh bìa, v.v.) trong môi trường DEBUG (phát triển)
# Trong môi trường production, một Web Server chuyên dụng (như Nginx/Apache) sẽ xử lý việc này.
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)