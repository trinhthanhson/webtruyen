from django.shortcuts import render
from matplotlib.style import context
from ..models import Story, Chapter, Category, ReadingHistory

def hotline_views(request):
    # Lấy danh sách thể loại để hiển thị trên dropdown của Header
    categories = Category.objects.all()
    
    context = {
        'categories': categories,
        'title': 'Liên hệ & Hỗ trợ',
    }
    
    if request.method == "POST":
        # Tại đây bạn có thể xử lý gửi Email hoặc lưu tin nhắn vào Database
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        
        # Tạm thời trả về thông báo thành công (Logic gửi mail có thể thêm sau)
        context['success_msg'] = f"Cảm ơn {name}, tin nhắn của bạn đã được gửi đi!"
        
    return render(request, 'story/hotline/hotline.html', context)

def terms_view(request):
    categories = Category.objects.all()
    return render(request, 'story/terms/terms.html', {
        'categories': categories,
    })