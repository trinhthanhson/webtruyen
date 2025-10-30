from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import F, Min, Max # ĐÃ THÊM F, Min, Max
from .models import Story, Chapter,Category # Đảm bảo import đúng Models
from decimal import Decimal
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages
from django.conf import settings # Để sử dụng LOGIN_REDIRECT_URL
from .form import ProfileEditForm
from django.contrib.auth.decorators import login_required
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
    """
    Hiển thị thông tin chi tiết truyện, tăng lượt xem và danh sách chương.
    Đã thêm logic tính toán chương đầu tiên và chương mới nhất (dùng cho nút bấm).
    """
    
    try:
        # 1. TĂNG LƯỢT XEM: Tăng views_count lên 1. 
        # Sử dụng QuerySet.update() với F() để đảm bảo tính nguyên vẹn (atomic update)
        # Giả định Model Story đã được import ở đầu file.
        Story.objects.filter(pk=story_id).update(views_count=F('views_count') + 1)
        
        # 2. Lấy Story VÀ Annotate để tính toán số chương đầu/cuối
        # Sử dụng get_object_or_404 trên QuerySet đã annotate
        story = get_object_or_404(
            Story.objects.annotate(
                # Giả định related_name từ Chapter tới Story là 'chapters'
                first_chapter_number=Min('chapters__chapter_number'),
                latest_chapter_number=Max('chapters__chapter_number')
            ), 
            pk=story_id
        )

        # 3. LẤY CHƯƠNG: Lấy tất cả chương, sắp xếp theo chapter_number (DecimalField)
        # Tên related_name trong Story Model là 'chapters'
        chapters = story.chapters.all().order_by('chapter_number')
        
    except NameError:
        # Xử lý nếu Model (Story, Chapter) chưa được định nghĩa
        story = None
        chapters = []
        
    context = {
        'story': story, 
        'chapters': chapters,
        'page_title': story.title if story else 'Chi tiết truyện'
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

from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.urls import reverse # Cần import reverse
from django.conf import settings # Cần import settings (để lấy LOGIN_REDIRECT_URL)

# Thiết lập đường dẫn chuyển hướng, mặc định là trang chủ
LOGIN_REDIRECT_URL = getattr(settings, 'LOGIN_REDIRECT_URL', '/') 

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
            print(f"Người dùng mới đã được tạo: {user.username}") # In ra console khi thành công

            # Tùy chọn: Đăng nhập người dùng ngay sau khi đăng ký
            login(request, user)
            
            messages.success(request, f'Đăng ký thành công! Chào mừng {user.username}.')
            # Chuyển hướng người dùng
            return redirect(LOGIN_REDIRECT_URL)
        else:
            # --- ĐÃ SỬA: CHÈN THÊM LỆNH IN LỖI ---
            print("LỖI VALIDATION ĐĂNG KÝ:")
            print(form.errors) # <-- In đối tượng lỗi ra console server
            messages.error(request, "Đăng ký không thành công. Vui lòng kiểm tra lại thông tin.")
            pass # Lỗi sẽ được hiển thị qua form trong template
    else:
        # Nếu là request GET, hiển thị form trống
        form = UserCreationForm()
        
    context = {
        'form': form,
        'page_title': 'Đăng Ký Tài Khoản'
    }
    # Sử dụng template 'story/account/register.html'
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
@login_required
def profile_view(request):
    """
    Hiển thị thông tin hồ sơ người dùng.
    Dữ liệu người dùng (request.user) đã có sẵn trong template.
    """
    return render(request, 'story/account/profile.html')


# --- Hàm View cho Trang CHỈNH SỬA HỒ SƠ ---
@login_required
def profile_edit_view(request):
    """
    Cho phép người dùng chỉnh sửa thông tin cá nhân (First name, Last name, Email)
    sử dụng ProfileEditForm an toàn.
    """
    if request.method == 'POST':
        # 1. SỬ DỤNG PROFILEEDITFORM TÙY CHỈNH để tránh hiển thị các trường admin
        form = ProfileEditForm(request.POST, instance=request.user) 
        
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Hồ sơ đã được cập nhật thành công! (Chỉnh sửa)')
            return redirect('profile') # Chuyển hướng về trang profile sau khi lưu
        else:
            messages.error(request, 'Đã xảy ra lỗi khi cập nhật hồ sơ. Vui lòng kiểm tra lại thông tin.')
            
    else:
        # Load dữ liệu hiện tại của user vào ProfileEditForm
        form = ProfileEditForm(instance=request.user) 
        
    context = {'form': form}
    return render(request, 'story/account/profile_edit.html', context)
def custom_logout_view(request):
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