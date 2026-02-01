from django.shortcuts import render, get_object_or_404
from django.db.models import Count
from decimal import Decimal
# Sử dụng .. để trỏ ra thư mục story lấy models
from ..models import Story, Chapter, Category

def chapter_detail(request, story_slug, chapter_number):
    """
    Hiển thị nội dung chương chi tiết của truyện.
    """
    # 1. Chuyển chapter_number thành Decimal an toàn
    try:
        chapter_number_decimal = Decimal(str(chapter_number))
    except (ValueError, TypeError):
        return get_object_or_404(Chapter, pk=None) 

    # 2. Lấy truyện theo slug
    story = get_object_or_404(Story, slug=story_slug)

    # 3. Lấy chương hiện tại (dùng select_related để tối ưu)
    current_chapter = get_object_or_404(
        Chapter.objects.select_related('story'), 
        story=story,
        chapter_number=chapter_number_decimal
    )

    # 4. Lấy chương trước và sau để điều hướng
    previous_chapter = (
        Chapter.objects.filter(story=story, chapter_number__lt=chapter_number_decimal)
        .order_by('-chapter_number')
        .first()
    )

    next_chapter = (
        Chapter.objects.filter(story=story, chapter_number__gt=chapter_number_decimal)
        .order_by('chapter_number')
        .first()
    )

    # 5. Lấy danh sách thể loại cho Sidebar
    categories = Category.objects.annotate(story_count=Count('stories'))

    # 6. Chuẩn bị context
    # Hiển thị số nguyên nếu chương là số chẵn (ví dụ 1.0 -> 1)
    chapter_display = int(current_chapter.chapter_number) if current_chapter.chapter_number % 1 == 0 else current_chapter.chapter_number

    context = {
        'story': story,
        'chapter': current_chapter,
        'previous_chapter': previous_chapter,
        'next_chapter': next_chapter,
        'page_title': f"{story.title} - Chương {chapter_display}",
        'categories': categories
    }

    return render(request, 'story/chapter_detail.html', context)