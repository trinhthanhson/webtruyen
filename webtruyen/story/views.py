from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import F
from .models import Story, Chapter # Đảm bảo import đúng Models

# Trang chủ - hiển thị danh sách truyện
def story_list(request):
    """Lấy và hiển thị danh sách truyện, sắp xếp theo thời gian cập nhật."""
    
    # Lấy tất cả truyện, sắp xếp theo thời gian cập nhật giảm dần
    stories = Story.objects.all().order_by('-updated_at', '-created_at')
    
    context = {
        'stories': stories,
        # Bạn có thể thêm các biến khác nếu cần, ví dụ: 'top_stories': ...
    }
    return render(request, 'story/story_list.html', context)


# Trang chi tiết truyện - hiển thị mô tả và chương
def story_detail(request, story_id):
    """Hiển thị thông tin chi tiết truyện, tăng lượt xem và danh sách chương."""
    
    # Lấy Story theo Primary Key (pk)
    story = get_object_or_404(Story, pk=story_id)
    
    # 1. TĂNG LƯỢT XEM: Tăng views_count lên 1. Sử dụng F() để tránh race condition.
    story.views_count = F('views_count') + 1
    story.save(update_fields=['views_count'])
    
    # Lấy lại đối tượng Story sau khi save F() để đảm bảo views_count hiển thị đúng
    story.refresh_from_db() 
    
    # 2. LẤY CHƯƠNG: Lấy tất cả chương, sắp xếp theo chapter_number (DecimalField)
    # Tên related_name trong Story Model là 'chapters'
    chapters = story.chapters.all().order_by('chapter_number') 
    
    context = {
        'story': story, 
        'chapters': chapters
    }
    return render(request, 'story/story_detail.html', context)


# Trang đọc chương
def chapter_detail(request, story_id, chapter_number):
    """Hiển thị nội dung chương truyện."""
    
    # Tên trường số chương là chapter_number (NUMERIC/DecimalField)
    chapter = get_object_or_404(
        Chapter, 
        story_id=story_id, 
        chapter_number=chapter_number
    )
    
    # *Logic nâng cao: Xử lý ReadingHistory ở đây nếu cần*
    
    context = {
        'chapter': chapter,
        'story': chapter.story # Truy cập Story qua ForeignKey
    }
    return render(request, 'story/chapter_detail.html', context)


# Hàm home() bị trùng lặp, logic của nó có thể gộp vào story_list hoặc banner
# Nếu bạn muốn một trang home riêng biệt cho banner:
def home_banner(request):
    """Lấy các truyện có ảnh bìa để hiển thị trên banner."""
    
    # Giả định ImageField cover_image_url KHÔNG NULL nếu có ảnh
    # Lưu ý: Django ImageField sẽ lưu chuỗi rỗng ('') nếu không có file, 
    # nên kiểm tra bằng cách loại trừ chuỗi rỗng là cách an toàn hơn.
    stories_for_banner = Story.objects.exclude(cover_image_url='').order_by('-views_count')[:5]
    
    return render(request, 'story/banner/banner.html', {'stories': stories_for_banner})