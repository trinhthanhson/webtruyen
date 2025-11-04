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
from django.db.models import Count
from django.forms.models import model_to_dict
from django.db.models import Q

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
    """
    Lấy và hiển thị danh sách truyện, sắp xếp theo thời gian cập nhật.
    Sử dụng select_related để tải trước Category, tránh lỗi N+1 query.
    """
    
    # Lấy tất cả truyện, sắp xếp theo thời gian cập nhật giảm dần
    # SỬA: Thêm .select_related('category')
    stories = Story.objects.prefetch_related('categories').order_by('-updated_at', '-created_at')
    
    context = {
        'stories': stories,
    }


    # Sau khi sửa, code của bạn sẽ chạy mượt mà khi sử dụng:
    # Thể loại: {{ story.category.category_name |default:"Chưa rõ" }}
    
    return render(request, 'story/story_list.html', context)

# Trang chi tiết truyện - hiển thị mô tả và chương
def story_detail(request, story_slug): 
    """
    Hiển thị thông tin chi tiết truyện, tăng lượt xem và danh sách chương.
    Đã thêm logic tính toán chương đầu tiên và chương mới nhất (dùng cho nút bấm).
    """
    
    # 1. TĂNG LƯỢT XEM: Tăng views_count lên 1. 
    # Sử dụng F() và update() để đảm bảo tính nguyên vẹn (atomic update).
    Story.objects.filter(slug=story_slug).update(views_count=F('views_count') + 1)

    # 2. Lấy Story VÀ Annotate để tính toán số chương đầu/cuối
    # SỬA LỖI: Đã thay pk=story_id thành slug=story_slug.
    story = get_object_or_404(
        Story.objects.annotate(
            # Giả định related_name từ Chapter tới Story là 'chapters'
            first_chapter_number=Min('chapters__chapter_number'),
            latest_chapter_number=Max('chapters__chapter_number')
        ), 
        slug=story_slug
    )

    # 3. LẤY CHƯƠNG: Lấy tất cả chương, sắp xếp theo chapter_number (DecimalField/Int)
    chapters = story.chapters.all().order_by('chapter_number')
        
    context = {
        'story': story, 
        'chapters': chapters,
        'page_title': story.title # Lấy title từ đối tượng story đã fetch
    }
    return render(request, 'story/story_detail.html', context)

# Trang đọc chương
def chapter_detail(request, story_slug, chapter_number):
    """
    Hiển thị nội dung chương chi tiết của truyện, dựa theo slug truyện và số chương.
    """
    # 1. Chuyển chapter_number thành Decimal để match với DecimalField trong model
    try:
        # Chuyển số chương thành string trước khi tạo Decimal để tránh lỗi precision
        chapter_number_decimal = Decimal(str(chapter_number))
    except Exception:
        # Trả về lỗi 404 Not Found nếu số chương không hợp lệ (Không phải là số)
        return get_object_or_404(Story, pk=None) 

    # 2. Lấy truyện theo slug. Dùng select_related để lấy thông tin tác giả nếu cần
    story = get_object_or_404(Story, slug=story_slug)

    # 3. Lấy chương hiện tại
    current_chapter = get_object_or_404(
        Chapter.objects.select_related('story'), # Select related story object
        story=story,
        chapter_number=chapter_number_decimal
    )

    # 4. Lấy chương trước và sau để điều hướng
    # Chương trước (chapter_number < hiện tại, sắp xếp giảm dần, lấy cái đầu tiên)
    previous_chapter = (
        Chapter.objects.filter(story=story, chapter_number__lt=chapter_number_decimal)
        .order_by('-chapter_number')
        .only('chapter_number') # Tối ưu hóa: chỉ cần lấy chapter_number
        .first()
    )

    # Chương sau (chapter_number > hiện tại, sắp xếp tăng dần, lấy cái đầu tiên)
    next_chapter = (
        Chapter.objects.filter(story=story, chapter_number__gt=chapter_number_decimal)
        .order_by('chapter_number')
        .only('chapter_number') # Tối ưu hóa: chỉ cần lấy chapter_number
        .first()
    )

    # 5. Truyền context sang template
    context = {
        'story': story,
        'chapter': current_chapter,
        'previous_chapter': previous_chapter,
        'next_chapter': next_chapter,
        'page_title': f"{story.title} - Chương {current_chapter.chapter_number}",
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
    categories = Category.objects.annotate(story_count=Count('stories'))    
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
            ).distinct().order_by('-created_at')
            
            page_title = f"Kết Quả Tìm Kiếm cho: \"{query}\""
        except NameError:
             print("loi")
    context = {
        'query': query,
        'stories': results,
        'page_title': page_title,
    }
    
    # Sử dụng lại template hiển thị danh sách truyện
    return render(request, 'story/story_list.html', context)
def category_detail(request, category_slug):
    """
    Hiển thị chi tiết một danh mục và tất cả các truyện thuộc danh mục đó.
    """
    # 1. Tìm Category dựa trên slug, nếu không tìm thấy thì trả về 404
    category = get_object_or_404(Category, slug=category_slug)

    # 2. Lấy tất cả các câu chuyện liên quan đến danh mục này.
    # Ta dùng related_name='stories' đã được định nghĩa trong ManyToManyField của Story.
    # Ví dụ: stories = Story.objects.filter(categories=category)
    stories = category.stories.all().order_by('-views_count') # Sắp xếp theo lượt xem

    context = {
        'category': category,
        'stories': stories,
    }
    
    return render(request, 'story/category_detail.html', context)   