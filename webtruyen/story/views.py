from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import F
from .models import Story, Chapter,Category # Đảm bảo import đúng Models
from decimal import Decimal
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages
from django.conf import settings # Để sử dụng LOGIN_REDIRECT_URL
LOGIN_REDIRECT_URL = getattr(settings, 'LOGIN_REDIRECT_URL', '/')

# Trang chủ - hiển thị danh sách truyện
def home(request):
    """Lấy và hiển thị danh sách truyện, sắp xếp theo thời gian cập nhật."""
    
    # Lấy tất cả truyện, sắp xếp theo thời gian cập nhật giảm dần
    stories = Story.objects.all().order_by('-updated_at', '-created_at')
    
    context = {
        'stories': stories,
        # Bạn có thể thêm các biến khác nếu cần, ví dụ: 'top_stories': ...
    }
    return render(request, 'story/home.html', context)

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
    # 1. Chuyển đổi số chương từ string (URL) sang Decimal để query database
    try:
        chapter_number_decimal = Decimal(chapter_number)
    except Exception:
        # Xử lý lỗi nếu chapter_number không phải là số hợp lệ
        # Hoặc trả về 404
        return render(request, 'error_page.html', {'message': 'Số chương không hợp lệ.'}) 

    # 2. Truy vấn đối tượng Chapter
    # Chúng ta sử dụng get_object_or_404 để tự động trả về lỗi 404 nếu không tìm thấy
    current_chapter = get_object_or_404(
        Chapter.objects.select_related('story'), # Dùng select_related để tối ưu truy vấn Story
        story_id=story_id,
        chapter_number=chapter_number_decimal
    )

    # 3. Tạo context để truyền dữ liệu sang template
    context = {
        'story_chapter': current_chapter, # Tên biến này sẽ được sử dụng trong template
        # Bạn có thể thêm các logic cho nút chương trước/sau ở đây
        # 'previous_chapter': ...,
        # 'next_chapter': ...,
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
def category_list(request):
    """Lấy và hiển thị danh sách loại truyện."""
    
    # Lấy tất cả loại truyện
    categories = Category.objects.all()
    
    context = {
        'categories': categories,
    }
    return render(request, 'story/category_list.html', context)

def register_view(request):
    """
    Xử lý logic cho trang Đăng ký (Register).
    Sử dụng UserCreationForm tích hợp sẵn của Django.
    """
    if request.method == 'POST':
        # Khởi tạo form với dữ liệu POST
        form = UserCreationForm(request.POST)
        if form.is_valid():
            # Lưu người dùng mới vào database
            user = form.save()
            
            # Tùy chọn: Đăng nhập người dùng ngay sau khi đăng ký
            login(request, user)
            
            messages.success(request, f'Đăng ký thành công! Chào mừng {user.username}.')
            # Chuyển hướng người dùng đến trang được định nghĩa trong settings.LOGIN_REDIRECT_URL (hoặc trang chủ)
            return redirect(LOGIN_REDIRECT_URL)
        else:
            # Nếu form không hợp lệ, hiển thị lại trang đăng ký cùng với lỗi
            # messages.error(request, "Đăng ký không thành công. Vui lòng kiểm tra các lỗi dưới đây.")
            pass # Lỗi sẽ được hiển thị qua form
    else:
        # Nếu là request GET, hiển thị form trống
        form = UserCreationForm()
        
    context = {
        'form': form,
        'page_title': 'Đăng Ký Tài Khoản'
    }
    # Sử dụng template 'account/register.html'
    return render(request, 'story/account/register.html', context)

def login_view(request):
    """
    Xử lý logic cho trang Đăng nhập (Login).
    Sử dụng AuthenticationForm tích hợp sẵn của Django.
    """
    if request.method == 'POST':
        # Khởi tạo form với dữ liệu POST
        # Lưu ý: AuthenticationForm cần request là tham số đầu tiên
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            # Lấy thông tin người dùng đã xác thực
            user = form.get_user()
            
            # Đăng nhập người dùng
            login(request, user)
            
            messages.success(request, f'Đăng nhập thành công! Chào mừng trở lại, {user.username}.')
            # Chuyển hướng người dùng đến trang họ muốn (nếu có next param) hoặc LOGIN_REDIRECT_URL
            return redirect(request.GET.get('next') or LOGIN_REDIRECT_URL)
        else:
            # Nếu form không hợp lệ
            messages.error(request, "Đăng nhập không thành công. Tên người dùng hoặc mật khẩu không đúng.")
    
    # Nếu là request GET, hoặc form POST không hợp lệ
    else:
        form = AuthenticationForm()
        
    context = {
        'form': form,
        'page_title': 'Đăng Nhập Tài Khoản'
    }
    # Sử dụng template 'account/login.html'
    return render(request, 'story/account/login.html', context)

def logout_view(request):
    """
    Xử lý logic Đăng xuất.
    """
    logout(request)
    messages.info(request, "Bạn đã đăng xuất thành công.")
    # Chuyển hướng về trang chủ
    return redirect('home') 

def search_results(request):
    """Xử lý logic tìm kiếm truyện."""
    
    query = request.GET.get('q') # Lấy chuỗi tìm kiếm từ thanh header
    results = []
    page_title = "Kết Quả Tìm Kiếm"
    
    if query:
        try:
            # Truy vấn cơ sở dữ liệu: Tìm kiếm gần đúng (icontains)
            results = Story.objects.filter(
                Q(title__icontains=query) | 
                Q(author__icontains=query) | 
                Q(description__icontains=query)
            ).distinct().order_by('-published_at')
            
            page_title = f"Kết Quả Tìm Kiếm cho: \"{query}\""
        except NameError:
             # Xử lý nếu Model Story chưa được định nghĩa
            pass 
        
    context = {
        'query': query,
        'stories': results,
        'page_title': page_title,
    }
    
    # Sử dụng lại template hiển thị danh sách truyện
    return render(request, 'story/story_list.html', context)