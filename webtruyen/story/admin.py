from django.contrib import admin
from .models import Story, Chapter, Category, Comment
import hashlib # Dùng để tạo public_id duy nhất, tránh trùng lặp
import cloudinary.uploader
from django.template.defaultfilters import slugify 
@admin.register(Story)
class StoryAdmin(admin.ModelAdmin):
    # Tạm thời chỉ giữ lại các trường đơn giản, loại bỏ 'categories' 
    # và các trường quan hệ khác (nếu có)
    fieldsets = (
        (None, {
            'fields': ('title', 'author', 'description','upload_image_temp', 'cover_image_url', 'status', 'views_count')
        }),
        # Tạm thời BỎ qua trường 'categories'
        # ('Phân loại', {
        #     'fields': ('categories',),
        # }),
    )
    list_display = ('title', 'author', 'status', 'views_count', 'avg_rating')
    list_filter = ('status',)
    search_fields = ('title', 'author')
    def save_model(self, request, obj, form, change):
        # 1. Kiểm tra xem có file ảnh được tải lên qua trường tạm thời không
        if 'upload_image_temp' in form.files:
            file_data = form.files['upload_image_temp']
            
            # --- TẠO ID DUY NHẤT VÀ TẢI LÊN CLOUDINARY ---
            
            # Tạo hash từ nội dung file và tên file để đảm bảo public_id duy nhất
            file_content = file_data.read()
            public_id_hash = hashlib.md5(file_content).hexdigest()
            file_data.seek(0) # Quay con trỏ về đầu file sau khi đọc
            title_slug = slugify(obj.title)
            public_id_name = f"{title_slug}-{public_id_hash}"
            print(f"Bắt đầu tải file: {file_data.name} lên Cloudinary...")

            # Thực hiện Tải lên
            upload_result = cloudinary.uploader.upload(
                file_data,
                folder="webtruyen/story_covers", # Thư mục lưu trữ trên Cloudinary
                public_id=public_id_name,
                overwrite=True, 
                resource_type="image"
            )
            
            # 2. Gán URL trả về từ Cloudinary vào trường cover_image_url chính thức
            obj.cover_image_url = upload_result["secure_url"]
            
            # 3. Xóa trường file tạm thời khỏi Model/Form để Django không lưu cục bộ
            obj.upload_image_temp = None
            form.files.pop('upload_image_temp')
        
        # 4. Lưu đối tượng Model vào Database
        super().save_model(request, obj, form, change)

# Đảm bảo bạn cũng đã định nghĩa Category:
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('category_name', 'slug')
    prepopulated_fields = {'slug': ('category_name',)}
admin.site.register(Chapter)

admin.site.register(Comment)
