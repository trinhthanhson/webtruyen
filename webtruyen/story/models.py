from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from django.contrib.postgres.fields import ArrayField # Có thể dùng JSONField thay thế nếu cần

# Giả định bạn đang sử dụng User Model mặc định của Django.
# Nếu bạn muốn tùy chỉnh, hãy thay đổi import và ForeignKey.
# class User (models.Model): # Nếu bạn muốn định nghĩa riêng
#     ... 

# --- 1. STORIES (Truyện) ---
class Story(models.Model):
    STATUS_CHOICES = [
        ('ongoing', 'Đang tiến hành'),
        ('completed', 'Hoàn thành'),
        ('paused', 'Tạm ngưng'),
    ]

    story_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255, verbose_name="Tên truyện")
    author = models.CharField(max_length=100, blank=True, null=True, verbose_name="Tác giả")
    description = models.TextField(blank=True, null=True, verbose_name="Tóm tắt")
    cover_image_url = models.ImageField(max_length=255, blank=True, null=True, verbose_name="Ảnh bìa URL")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ongoing', verbose_name="Trạng thái")
    views_count = models.BigIntegerField(default=0, verbose_name="Lượt xem")
    
    # NUMERIC(3, 2)
    avg_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00, verbose_name="Đánh giá TB") 
    
    created_at = models.DateTimeField(default=timezone.now, verbose_name="Thời gian đăng")
    updated_at = models.DateTimeField(blank=True, null=True, verbose_name="Thời gian cập nhật")

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Truyện"
        verbose_name_plural = "Truyện"
        db_table = 'stories'
        indexes = [
            models.Index(fields=['title']),
            models.Index(fields=['author']),
        ]

# --- 2. CATEGORIES (Thể loại) ---
class Category(models.Model):
    category_id = models.AutoField(primary_key=True)
    category_name = models.CharField(max_length=50, unique=True, verbose_name="Tên thể loại")
    slug = models.SlugField(max_length=50, unique=True, verbose_name="Slug") # Dùng SlugField cho URL thân thiện

    def __str__(self):
        return self.category_name
    
    class Meta:
        verbose_name = "Thể loại"
        verbose_name_plural = "Thể loại"

# Mối quan hệ Many-to-Many giữa Story và Category
# Django sẽ tự tạo bảng trung gian (StoryCategories) nếu bạn dùngManyToManyField.
Story.add_to_class('categories', models.ManyToManyField(Category, related_name='stories'))


# --- 3. CHAPTERS (Chương/Tập) ---
class Chapter(models.Model):
    chapter_id = models.AutoField(primary_key=True)
    
    # ForeignKey tới Story (ON DELETE CASCADE mặc định)
    story = models.ForeignKey(Story, on_delete=models.CASCADE, related_name='chapters', verbose_name="Truyện")
    
    # NUMERIC(10, 2)
    chapter_number = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Số chương")
    
    title = models.CharField(max_length=255, verbose_name="Tên chương")
    content = models.TextField(blank=True, null=True, verbose_name="Nội dung chữ")
    
    # Sử dụng JSONField cho danh sách URL ảnh (tương đương JSONB của Postgres)
    image_urls = models.JSONField(default=list, blank=True, null=True, verbose_name="Danh sách ảnh") 
    
    published_at = models.DateTimeField(default=timezone.now, verbose_name="Thời gian xuất bản")

    def __str__(self):
        return f"{self.story.title} - Chapter {self.chapter_number}"

    class Meta:
        verbose_name = "Chương truyện"
        verbose_name_plural = "Chương truyện"
        # Ràng buộc UNIQUE (story_id, chapter_number)
        unique_together = ('story', 'chapter_number')


# --- 4. RATINGS (Đánh giá - Sao) ---
class Rating(models.Model):
    # Sử dụng User model mặc định của Django
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ratings', verbose_name="Người dùng")
    story = models.ForeignKey(Story, on_delete=models.CASCADE, related_name='ratings', verbose_name="Truyện")
    
    # SMALLINT NOT NULL CHECK (score BETWEEN 1 AND 5)
    score = models.SmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name="Điểm đánh giá (1-5)"
    )
    
    created_at = models.DateTimeField(default=timezone.now, verbose_name="Thời gian đánh giá")

    class Meta:
        verbose_name = "Đánh giá"
        verbose_name_plural = "Đánh giá"
        # Ràng buộc UNIQUE (story_id, user_id)
        unique_together = ('story', 'user')


# --- 5. COMMENTS (Bình luận - Tích hợp AI) ---
class Comment(models.Model):
    # Sử dụng User model mặc định của Django
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments', verbose_name="Người dùng")
    story = models.ForeignKey(Story, on_delete=models.CASCADE, related_name='comments', verbose_name="Truyện")
    
    # Bình luận cha (parent_comment_id)
    parent_comment = models.ForeignKey(
        'self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies', verbose_name="Bình luận cha"
    )
    
    content = models.TextField(verbose_name="Nội dung bình luận")
    created_at = models.DateTimeField(default=timezone.now, verbose_name="Thời gian bình luận")
    
    # is_approved BOOLEAN NOT NULL DEFAULT FALSE
    is_approved = models.BooleanField(default=False, verbose_name="Đã được duyệt")
    
    # ai_score NUMERIC(5, 2)
    ai_score = models.DecimalField(max_digits=5, decimal_places=2, default=0.00, verbose_name="Điểm AI phản cảm")
    
    def __str__(self):
        return f"Comment by {self.user.username} on {self.story.title}"

    class Meta:
        verbose_name = "Bình luận"
        verbose_name_plural = "Bình luận"
        ordering = ['created_at'] # Sắp xếp theo thời gian
        indexes = [
            # Tối ưu truy vấn bình luận theo truyện và trạng thái duyệt
            models.Index(fields=['story', 'is_approved', '-created_at']), 
        ]


# --- 6. USER_FAVORITES (Truyện yêu thích) ---
class UserFavorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites', verbose_name="Người dùng")
    story = models.ForeignKey(Story, on_delete=models.CASCADE, related_name='favorited_by', verbose_name="Truyện")
    created_at = models.DateTimeField(default=timezone.now, verbose_name="Thời gian thêm")

    class Meta:
        verbose_name = "Truyện yêu thích"
        verbose_name_plural = "Truyện yêu thích"
        # Ràng buộc PRIMARY KEY (user_id, story_id)
        unique_together = ('user', 'story')


# --- 7. READING_HISTORY (Lịch sử đọc truyện) ---
class ReadingHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='history', verbose_name="Người dùng")
    story = models.ForeignKey(Story, on_delete=models.CASCADE, related_name='history', verbose_name="Truyện")
    
    # chapter_id REFERENCES chapters (NULL nếu chương đó bị xóa)
    chapter = models.ForeignKey(Chapter, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Chương đã đọc")
    
    last_read_at = models.DateTimeField(default=timezone.now, verbose_name="Lần đọc cuối")

    class Meta:
        verbose_name = "Lịch sử đọc"
        verbose_name_plural = "Lịch sử đọc"
        # Ràng buộc UNIQUE (user_id, story_id)
        unique_together = ('user', 'story')
        indexes = [
            models.Index(fields=['user', '-last_read_at']), 
        ]