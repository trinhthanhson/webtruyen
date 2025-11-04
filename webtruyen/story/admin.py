from django.contrib import admin
from .models import Story, Chapter, Category, Comment
import hashlib 
import cloudinary.uploader
from django.utils.text import slugify
import re 
import unicodedata 
from django import forms # <-- THÊM IMPORT NÀY!

# =========================================================
# === HÀM HELPER XỬ LÝ SLUG TIẾNG VIỆT ===
# =========================================================

def vietnamese_slugify(s):
    """
    Chuyển đổi tiếng Việt có dấu thành không dấu sử dụng unicodedata.
    Ví dụ: 'Cổ đại' -> 'co-dai'
    """
    # 1. Chuẩn hóa Unicode và loại bỏ dấu
    s = unicodedata.normalize('NFD', s).encode('ascii', 'ignore').decode("utf-8")
    
    # 2. Xử lý trường hợp chữ 'Đ' viết hoa/thường (unicodedata không xử lý)
    s = s.replace('đ', 'd').replace('Đ', 'D')
    
    # 3. Áp dụng slugify
    return slugify(s)


# =========================================================
# === FORM TÙY CHỈNH CHO ADMIN (Giải quyết lỗi 'required') ===
# =========================================================
class CategoryAdminForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = '__all__'
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Vô hiệu hóa yêu cầu bắt buộc (required) trên Form Admin cho trường slug.
        # Điều này cho phép form vượt qua validation khi trường slug trống, 
        # sau đó hàm save_model sẽ điền giá trị chính xác.
        if 'slug' in self.fields:
            self.fields['slug'].required = False


# =========================================================
# === ADMIN CLASSES ===
# =========================================================

@admin.register(Story)
class StoryAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            'fields': (
                'title', 
                'slug', # Giữ slug trong fields để người dùng có thể tùy chỉnh
                'author', 
                'description',
                'upload_image_temp', 
                'cover_image_url', 
                'categories',  
                'status', 
                'views_count',
                'avg_rating'
            )
        }),
    )
    readonly_fields = ('views_count', 'avg_rating') 
    list_display = ('title', 'author', 'status','slug')
    list_filter = ('status', 'categories')  
    search_fields = ('title', 'author')
    filter_horizontal = ('categories',)  

    def save_model(self, request, obj, form, change):
        # 0. Logic Tự động tạo Slug dựa trên Title (trước khi lưu)
        # Chỉ tạo slug nếu đây là đối tượng mới (chưa có ID) HOẶC 
        # trường slug KHÔNG được điền (là chuỗi rỗng)
        # HOẶC bạn muốn tự động cập nhật slug MỖI KHI title thay đổi.
        
        # Nếu muốn người dùng CÓ THỂ chỉnh sửa slug, chỉ tạo khi nó rỗng (None hoặc rỗng)
        if not obj.slug:
            # SỬ DỤNG HÀM SLUGIFY CỦA BẠN CHO TIẾNG VIỆT
            obj.slug = vietnamese_slugify(obj.title) 
        
        # 1. Logic Tải ảnh lên Cloudinary
        if 'upload_image_temp' in form.files:
            file_data = form.files['upload_image_temp']
            file_content = file_data.read()
            public_id_hash = hashlib.md5(file_content).hexdigest()
            file_data.seek(0)
            
            # --- ÁP DỤNG SLUGIFY TIẾNG VIỆT CHO TÊN FILE ---
            title_slug = vietnamese_slugify(obj.title)
            public_id_name = f"{title_slug}-{public_id_hash}"
            print(f"Bắt đầu tải file: {file_data.name} lên Cloudinary...")

            upload_result = cloudinary.uploader.upload(
                file_data,
                folder="webtruyen/story_covers",
                public_id=public_id_name,
                overwrite=True,
                resource_type="image"
            )
            
            obj.cover_image_url = upload_result["secure_url"]
            obj.upload_image_temp = None
            form.files.pop('upload_image_temp')
            
        super().save_model(request, obj, form, change)

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    # Gán Form tùy chỉnh để tắt thuộc tính required cho slug
    form = CategoryAdminForm
    
    # list_display vẫn hiển thị slug trong danh sách, điều này là bình thường
    list_display = ('category_name', 'slug')
    
    # Đã xóa get_prepopulated_fields (Đúng!)
    
    def save_model(self, request, obj, form, change):
        """
        Ghi đè save_model để áp dụng hàm slugify tùy chỉnh (vietnamese_slugify).
        Hàm này chạy sau khi form validation đã pass.
        """
        # Python sẽ tự động tạo slug đúng co-dai khi lưu.
        if not obj.slug or 'category_name' in form.changed_data:
            obj.slug = vietnamese_slugify(obj.category_name)
            
        super().save_model(request, obj, form, change)


admin.site.register(Chapter)
admin.site.register(Comment)
