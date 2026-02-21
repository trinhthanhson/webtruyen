from django.contrib import admin
from .models import Story, Chapter, Category, Comment
from django.utils.html import format_html # Để hiển thị ảnh preview
from django import forms
import hashlib 
import cloudinary.uploader
from django.utils.text import slugify
import unicodedata 

# --- HELPER SLUG ---
def vietnamese_slugify(s):
    s = unicodedata.normalize('NFD', s).encode('ascii', 'ignore').decode("utf-8")
    s = s.replace('đ', 'd').replace('Đ', 'D')
    return slugify(s)

# --- FORM ---
class CategoryAdminForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = '__all__'
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'slug' in self.fields:
            self.fields['slug'].required = False

# --- TRANG ADMIN TRUYỆN ---
@admin.register(Story)
class StoryAdmin(admin.ModelAdmin):
    list_display = ('show_cover', 'title', 'author', 'translator', 'colored_status') 
    list_filter = ('status', 'categories', 'author')
    search_fields = ('title', 'author')
    filter_horizontal = ('categories',)
    readonly_fields = ('views_count', 'avg_rating', 'show_full_cover')

    # Hiển thị ảnh nhỏ ở danh sách
    def show_cover(self, obj):
        if obj.cover_image_url:
            return format_html('<img src="{}" style="width: 45px; height: 60px; border-radius: 4px; object-fit: cover;" />', obj.cover_image_url)
        return "No Image"
    show_cover.short_description = "Ảnh bìa"

    # Hiển thị ảnh lớn trong trang chi tiết
    def show_full_cover(self, obj):
        if obj.cover_image_url:
            return format_html('<img src="{}" style="max-width: 200px; border-radius: 8px;" />', obj.cover_image_url)
        return "Chưa có ảnh"
    show_full_cover.short_description = "Xem trước ảnh"

    # Làm màu cho cột Trạng thái
    def colored_status(self, obj):
        colors = {
            'ongoing': '#28a745', # Xanh lá
            'completed': '#007bff', # Xanh dương
            'dropped': '#dc3545', # Đỏ
        }
        return format_html(
            '<span style="color: white; background-color: {}; padding: 3px 10px; border-radius: 10px; font-size: 11px; font-weight: bold;">{}</span>',
            colors.get(obj.status, '#6c757d'),
            obj.get_status_display()
        )
    colored_status.short_description = "Trạng thái"

    # Giữ nguyên logic save_model của bạn
    def save_model(self, request, obj, form, change):
        if not obj.slug:
            obj.slug = vietnamese_slugify(obj.title)
        
        if 'upload_image_temp' in form.files:
            file_data = form.files['upload_image_temp']
            file_content = file_data.read()
            public_id_hash = hashlib.md5(file_content).hexdigest()
            file_data.seek(0)
            
            title_slug = vietnamese_slugify(obj.title)
            public_id_name = f"{title_slug}-{public_id_hash}"

            upload_result = cloudinary.uploader.upload(
                file_data,
                folder="webtruyen/story_covers",
                public_id=public_id_name,
                overwrite=True,
                resource_type="image"
            )
            obj.cover_image_url = upload_result["secure_url"]
            obj.upload_image_temp = None
        super().save_model(request, obj, form, change)

# --- CÁC TRANG ADMIN KHÁC ---
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    form = CategoryAdminForm
    list_display = ('category_name', 'slug')
    def save_model(self, request, obj, form, change):
        if not obj.slug or 'category_name' in form.changed_data:
            obj.slug = vietnamese_slugify(obj.category_name)
        super().save_model(request, obj, form, change)

@admin.register(Chapter)
class ChapterAdmin(admin.ModelAdmin):
    list_display = ('title', 'story', 'chapter_number')
    list_filter = ('story',)
    search_fields = ('title', 'story__title')

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'story', 'content', 'created_at')
    list_filter = ('created_at',)