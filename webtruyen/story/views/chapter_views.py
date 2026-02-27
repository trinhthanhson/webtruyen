from django.shortcuts import render, get_object_or_404
from django.db.models import Count
from decimal import Decimal
from ..models import Story, Chapter, Category, ReadingHistory
from django.utils import timezone 
def chapter_detail(request, story_slug, chapter_number):
    """
    Hiển thị nội dung chương chi tiết và lưu lịch sử đọc.
    """
    try:
        chapter_number_decimal = Decimal(str(chapter_number))
    except (ValueError, TypeError):
        return get_object_or_404(Chapter, pk=None) 

    story = get_object_or_404(Story, slug=story_slug)

    current_chapter = get_object_or_404(
        Chapter.objects.select_related('story'), 
        story=story,
        chapter_number=chapter_number_decimal
    )

    # --- LOGIC LƯU LỊCH SỬ ĐỌC TẠI ĐÂY ---
    if request.user.is_authenticated:
        ReadingHistory.objects.update_or_create(
            user=request.user,
            story=story,
            defaults={
                'chapter': current_chapter,
                'last_read_at': timezone.now()
            }
        )
    # -------------------------------------

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

    categories = Category.objects.annotate(story_count=Count('stories'))

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