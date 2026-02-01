from django.shortcuts import render, get_object_or_404
from django.db.models import Count
# Dấu .. để quay ra thư mục story lấy models
from ..models import Story, Category 

def category_detail(request, category_slug):
    """
    Hiển thị chi tiết một danh mục và tất cả các truyện thuộc danh mục đó.
    """
    # 1. Tìm Category dựa trên slug
    category = get_object_or_404(Category, slug=category_slug)

    # 2. Lấy danh sách truyện thuộc category này
    stories = category.stories.all().order_by('-views_count') 
    
    # 3. Lấy toàn bộ danh mục để hiển thị sidebar (nếu cần)
    categories = Category.objects.annotate(story_count=Count('stories')) 

    context = {
        'category': category,
        'stories': stories,
        'categories': categories
    }
    
    return render(request, 'story/category_detail.html', context)

def category_list(request):
    """Hiển thị danh sách tất cả các thể loại."""
    categories = Category.objects.annotate(story_count=Count('stories'))
    return render(request, 'story/category_list.html', {'categories': categories})