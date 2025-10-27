from django.shortcuts import render, get_object_or_404
from .models import Story, Chapter

# Trang chủ - hiển thị danh sách truyện
def story_list(request):
    stories = Story.objects.all()
    return render(request, 'story/story_list.html', {'stories': stories})

# Trang chi tiết truyện - hiển thị mô tả và chương
def story_detail(request, story_id):
    story = get_object_or_404(Story, id=story_id)
    chapters = story.chapters.all().order_by('number')
    return render(request, 'story/story_detail.html', {'story': story, 'chapters': chapters})

# Trang đọc chương
def chapter_detail(request, story_id, chapter_number):
    chapter = get_object_or_404(Chapter, story_id=story_id, number=chapter_number)
    return render(request, 'story/chapter_detail.html', {'chapter': chapter})
def home(request):
    stories = Story.objects.filter(thumbnail__isnull=False)  # Lấy stories có ảnh thumbnail
    return render(request, 'story/banner/banner.html', {'stories': stories})
