from django.shortcuts import render, get_object_or_404
from django.db.models import F, Min, Max, Count, Q
# Dấu .. để gọi models từ thư mục cha (story/)
from ..models import Story, Category, Chapter

def home(request):
    """Trang chủ hiển thị danh sách truyện mới cập nhật."""
    stories = Story.objects.all().order_by('-updated_at', '-created_at')
    categories = Category.objects.annotate(story_count=Count('stories'))
    
    context = {
        'stories': stories,
        'categories': categories
    }
    return render(request, 'story/home.html', context)

def story_list(request):
    """Danh sách tất cả truyện với tối ưu hóa query."""
    stories = Story.objects.prefetch_related('categories').order_by('-updated_at', '-created_at')
    categories = Category.objects.annotate(story_count=Count('stories'))
    
    context = {
        'stories': stories,
        'categories': categories
    }
    return render(request, 'story/story_list.html', context)

def story_detail(request, story_slug): 
    # 1. Tăng lượt xem (sử dụng F expression để tránh race condition)
    Story.objects.filter(slug=story_slug).update(views_count=F('views_count') + 1)

    # 2. Lấy thông tin truyện và tính toán chương đầu/cuối
    story = get_object_or_404(
        Story.objects.annotate(
            first_chapter_number=Min('chapters__chapter_number'),
            latest_chapter_number=Max('chapters__chapter_number'),
            chapter_count=Count('chapters')

        ), 
        slug=story_slug
    )

    # 3. Lấy truyện cùng thể loại (Related Stories)
    current_categories = story.categories.all()
    related_stories = Story.objects.filter(
        categories__in=current_categories
    ).exclude(story_id=story.story_id).distinct().order_by('-views_count')[:5]

    # 4. Lấy danh sách chương và danh mục sidebar
    chapters = story.chapters.all().order_by('chapter_number')
    all_categories = Category.objects.annotate(story_count=Count('stories'))
    
    context = {
        'story': story, 
        'chapters': chapters,
        'related_stories': related_stories,
        'page_title': story.title,
        'categories': all_categories
    }
    return render(request, 'story/story_detail.html', context)

def home_banner(request):
    """Lấy top 5 truyện có ảnh bìa nhiều view nhất cho banner."""
    stories_for_banner = Story.objects.exclude(cover_image_url='').order_by('-views_count')[:5]
    return render(request, 'story/banner/banner.html', {'stories': stories_for_banner})

def search_results(request):
    """Xử lý tìm kiếm truyện theo tên, tác giả hoặc mô tả."""
    query = request.GET.get('q', '')
    results = []
    page_title = "Kết Quả Tìm Kiếm"
    categories = Category.objects.annotate(story_count=Count('stories'))

    if query:
        results = Story.objects.filter(
            Q(title__icontains=query) | 
            Q(author__icontains=query) | 
            Q(description__icontains=query)
        ).distinct().order_by('-created_at')
        page_title = f"Kết Quả Tìm Kiếm cho: \"{query}\""
            
    context = {
        'query': query,
        'stories': results,
        'page_title': page_title,
        'categories': categories
    }
    return render(request, 'story/story_list.html', context)