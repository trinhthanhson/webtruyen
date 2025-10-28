from django.contrib import admin
from .models import Story, Chapter, Category, Comment

@admin.register(Story)
class StoryAdmin(admin.ModelAdmin):
    # Tạm thời chỉ giữ lại các trường đơn giản, loại bỏ 'categories' 
    # và các trường quan hệ khác (nếu có)
    fieldsets = (
        (None, {
            'fields': ('title', 'author', 'description', 'cover_image_url', 'status', 'views_count')
        }),
        # Tạm thời BỎ qua trường 'categories'
        # ('Phân loại', {
        #     'fields': ('categories',),
        # }),
    )
    list_display = ('title', 'author', 'status', 'views_count', 'avg_rating')
    list_filter = ('status',)
    search_fields = ('title', 'author')

# Đảm bảo bạn cũng đã định nghĩa Category:
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('category_name', 'slug')
    prepopulated_fields = {'slug': ('category_name',)}
admin.site.register(Chapter)

admin.site.register(Comment)
