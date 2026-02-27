from django.shortcuts import render, get_object_or_404
from django.db.models import F, Min, Max, Count, Q
from django.core.paginator import Paginator 
from ..models import Story, Category, Chapter, UserFavorite

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
    """Danh sách tất cả truyện với phân trang 50 mục/trang."""
    all_stories = Story.objects.prefetch_related('categories').order_by('-updated_at', '-created_at')
    categories = Category.objects.annotate(story_count=Count('stories'))
    
    paginator = Paginator(all_stories, 20) 
    page_number = request.GET.get('page') 
    page_obj = paginator.get_page(page_number)
    
    context = {
        'stories': page_obj, 
        'categories': categories,
        'page_obj': page_obj 
    }
    return render(request, 'story/story_list.html', context)

def story_detail(request, story_slug): 
    Story.objects.filter(slug=story_slug).update(views_count=F('views_count') + 1)
    
    story = get_object_or_404(
        Story.objects.annotate(
            first_chapter_number=Min('chapters__chapter_number'),
            latest_chapter_number=Max('chapters__chapter_number'),
            chapter_count=Count('chapters')

        ), 
        slug=story_slug
    )
    is_favorite = False
    if request.user.is_authenticated:
        is_favorite = UserFavorite.objects.filter(user=request.user, story=story).exists()
    current_categories = story.categories.all()
    related_stories = Story.objects.filter(
        categories__in=current_categories
    ).exclude(story_id=story.story_id).distinct().order_by('-views_count')[:5]

    chapters = story.chapters.all().order_by('chapter_number')
    all_categories = Category.objects.annotate(story_count=Count('stories'))
    
    context = {
        'story': story, 
        'chapters': chapters,
        'related_stories': related_stories,
        'page_title': story.title,
        'categories': all_categories,
        'is_favorite': is_favorite,
    }
    return render(request, 'story/story_detail.html', context)

def home_banner(request):
    """Lấy top 5 truyện có ảnh bìa nhiều view nhất cho banner."""
    stories_for_banner = Story.objects.exclude(cover_image_url='').order_by('-views_count')[:5]
    return render(request, 'story/banner/banner.html', {'stories': stories_for_banner})
def search_results(request):
    """Xử lý tìm kiếm truyện theo tên, tác giả, dịch giả, mô tả hoặc thể loại."""
    query = request.GET.get('q', '').strip()
    categories = Category.objects.annotate(story_count=Count('stories'))
    
    if query:
        results_list = Story.objects.filter(
            Q(title__icontains=query) |              # Tìm theo tiêu đề
            Q(author__icontains=query) |             # Tìm theo tác giả
            Q(translator__icontains=query) |         # Tìm theo dịch giả (MỚI)
            Q(description__icontains=query) |        # Tìm theo tóm tắt
            Q(categories__category_name__icontains=query) # Tìm theo thể loại
        ).distinct().order_by('-created_at')
        
        page_title = f"Kết Quả Tìm Kiếm cho: \"{query}\""
    else:
        results_list = Story.objects.none()
        page_title = "Vui lòng nhập từ khóa tìm kiếm"

    # Phân trang
    paginator = Paginator(results_list, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'query': query,
        'stories': page_obj,
        'page_obj': page_obj,
        'page_title': page_title,
        'categories': categories,
    }
    return render(request, 'story/story_list.html', context)