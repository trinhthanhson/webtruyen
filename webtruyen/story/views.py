from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import F, Min, Max  # ĐÃ THÊM F, Min, Max
from .models import Story, Chapter, Category, Comment,ReadingHistory,Rating  # Đảm bảo import đúng Models
from decimal import Decimal
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages
from django.conf import settings  # Để sử dụng LOGIN_REDIRECT_URL
from .form import ProfileEditForm
from django.contrib.auth.decorators import login_required
from django.forms.models import model_to_dict
from django.db.models import Count, Q,Avg
from django.http import JsonResponse
from .models import Story, UserFavorite  # Giả sử các model nằm trong cùng app
from django.views.decorators.http import require_http_methods
from django.db import models
from django.utils import timezone
LOGIN_REDIRECT_URL = getattr(settings, "LOGIN_REDIRECT_URL", "/")


# Trang chủ - hiển thị danh sách truyện
def home(request):
    """Lấy và hiển thị danh sách truyện, sắp xếp theo thời gian cập nhật."""

    # Lấy tất cả truyện, sắp xếp theo thời gian cập nhật giảm dần
    stories = Story.objects.all().order_by("-updated_at", "-created_at")

    context = {
        "stories": stories,
        # Bạn có thể thêm các biến khác nếu cần, ví dụ: 'top_stories': ...
    }
    return render(request, "story/home.html", context)


def story_list(request):
    """
    Lấy và hiển thị danh sách truyện, sắp xếp theo thời gian cập nhật.
    Sử dụng select_related để tải trước Category, tránh lỗi N+1 query.
    """

    # Lấy tất cả truyện, sắp xếp theo thời gian cập nhật giảm dần
    # SỬA: Thêm .select_related('category')
    stories = Story.objects.prefetch_related("categories").order_by(
        "-updated_at", "-created_at"
    )

    context = {
        "stories": stories,
    }

    # Sau khi sửa, code của bạn sẽ chạy mượt mà khi sử dụng:
    # Thể loại: {{ story.category.category_name |default:"Chưa rõ" }}

    return render(request, "story/story_list.html", context)


# Trang chi tiết truyện - hiển thị mô tả và chương
def story_detail(request, story_slug):
    """
    Hiển thị thông tin chi tiết truyện, tăng lượt xem và danh sách chương.
    Đã thêm logic tính toán chương đầu tiên và chương mới nhất (dùng cho nút bấm).
    """
    
    # 1. TĂNG LƯỢT XEM: Tăng views_count lên 1.
    # Sử dụng F() và update() để đảm bảo tính nguyên vẹn (atomic update).
    Story.objects.filter(slug=story_slug).update(views_count=F("views_count") + 1)

    # 2. Lấy Story VÀ Annotate để tính toán số chương đầu/cuối
    # SỬA LỖI: Đã thay pk=story_id thành slug=story_slug.
    story = get_object_or_404(
        Story.objects.annotate(
            # Giả định related_name từ Chapter tới Story là 'chapters'
            first_chapter_number=Min("chapters__chapter_number"),
            latest_chapter_number=Max("chapters__chapter_number"),
        ),
        slug=story_slug,
    )
    is_favorited = False
    if request.user.is_authenticated:
        # Kiểm tra xem user đã lưu truyện này chưa
        is_favorited = UserFavorite.objects.filter(
            user=request.user, story=story, status=True
        ).exists()
    # 3. LẤY CHƯƠNG: Lấy tất cả chương, sắp xếp theo chapter_number (DecimalField/Int)
    chapters = story.chapters.all().order_by("chapter_number")
    approved_comments = (
        story.comments.filter(is_approved=True, parent_comment__isnull=True)
        .annotate(
            reply_count=Count("replies", filter=models.Q(replies__is_approved=True))
        )
        .order_by("-created_at")  # ⬅️ mới nhất lên đầu
    )
    
    context = {
        "story": story,
        "chapters": chapters,
        "page_title": story.title,
        "is_favorited": is_favorited,
        "comments": approved_comments,
        "total_comments": story.comments.filter(
            is_approved=True
        ).count(),  # Lấy title từ đối tượng story đã fetch
    }
    return render(request, "story/story_detail.html", context)


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
        Chapter.objects.select_related("story"),  # Select related story object
        story=story,
        chapter_number=chapter_number_decimal,
    )

    # 4. Lấy chương trước và sau để điều hướng
    # Chương trước (chapter_number < hiện tại, sắp xếp giảm dần, lấy cái đầu tiên)
    previous_chapter = (
        Chapter.objects.filter(story=story, chapter_number__lt=chapter_number_decimal)
        .order_by("-chapter_number")
        .only("chapter_number")  # Tối ưu hóa: chỉ cần lấy chapter_number
        .first()
    )

    # Chương sau (chapter_number > hiện tại, sắp xếp tăng dần, lấy cái đầu tiên)
    next_chapter = (
        Chapter.objects.filter(story=story, chapter_number__gt=chapter_number_decimal)
        .order_by("chapter_number")
        .only("chapter_number")  # Tối ưu hóa: chỉ cần lấy chapter_number
        .first()
    )
    chapter = get_object_or_404(Chapter, story=story, chapter_number=chapter_number)
    if request.user.is_authenticated:
            # Sử dụng update_or_create để đảm bảo chỉ có 1 bản ghi duy nhất
            # (do bạn đã thiết lập unique_together = ('user', 'story'))
            reading_history, created = ReadingHistory.objects.update_or_create(
                user=request.user,
                story=story,
                defaults={
                    'chapter': chapter,
                    'last_read_at': timezone.now() # Cập nhật thời gian đọc
                }
            )
    # 5. Truyền context sang template
    context = {
        "story": story,
        "chapter": current_chapter,
        "previous_chapter": previous_chapter,
        "next_chapter": next_chapter,
        "page_title": f"{story.title} - Chương {current_chapter.chapter_number}",
    }

    return render(request, "story/chapter_detail.html", context)


# Hàm home() bị trùng lặp, logic của nó có thể gộp vào story_list hoặc banner
# Nếu bạn muốn một trang home riêng biệt cho banner:
def home_banner(request):
    """Lấy các truyện có ảnh bìa để hiển thị trên banner."""

    # Giả định ImageField cover_image_url KHÔNG NULL nếu có ảnh
    # Lưu ý: Django ImageField sẽ lưu chuỗi rỗng ('') nếu không có file,
    # nên kiểm tra bằng cách loại trừ chuỗi rỗng là cách an toàn hơn.
    stories_for_banner = Story.objects.exclude(cover_image_url="").order_by(
        "-views_count"
    )[:5]

    return render(request, "story/banner/banner.html", {"stories": stories_for_banner})


def category_list(request):
    """Lấy và hiển thị danh sách loại truyện."""

    # Lấy tất cả loại truyện
    categories = Category.objects.annotate(story_count=Count("stories"))
    context = {
        "categories": categories,
    }
    return render(request, "story/category_list.html", context)


from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.urls import reverse  # Cần import reverse
from django.conf import settings  # Cần import settings (để lấy LOGIN_REDIRECT_URL)

# Thiết lập đường dẫn chuyển hướng, mặc định là trang chủ
LOGIN_REDIRECT_URL = getattr(settings, "LOGIN_REDIRECT_URL", "/")


def register_view(request):
    """
    Xử lý logic cho trang Đăng ký (Register).
    Sử dụng UserCreationForm tích hợp sẵn của Django.
    """
    if request.method == "POST":
        # Khởi tạo form với dữ liệu POST
        form = UserCreationForm(request.POST)
        if form.is_valid():
            # Lưu người dùng mới vào database
            user = form.save()
            print(
                f"Người dùng mới đã được tạo: {user.username}"
            )  # In ra console khi thành công

            # Tùy chọn: Đăng nhập người dùng ngay sau khi đăng ký
            login(request, user)

            messages.success(request, f"Đăng ký thành công! Chào mừng {user.username}.")
            # Chuyển hướng người dùng
            return redirect(LOGIN_REDIRECT_URL)
        else:
            # --- ĐÃ SỬA: CHÈN THÊM LỆNH IN LỖI ---
            print("LỖI VALIDATION ĐĂNG KÝ:")
            print(form.errors)  # <-- In đối tượng lỗi ra console server
            messages.error(
                request, "Đăng ký không thành công. Vui lòng kiểm tra lại thông tin."
            )
            pass  # Lỗi sẽ được hiển thị qua form trong template
    else:
        # Nếu là request GET, hiển thị form trống
        form = UserCreationForm()

    context = {"form": form, "page_title": "Đăng Ký Tài Khoản"}
    # Sử dụng template 'story/account/register.html'
    return render(request, "story/account/register.html", context)


def login_view(request):
    """
    Xử lý logic cho trang Đăng nhập (Login).
    Sử dụng AuthenticationForm tích hợp sẵn của Django.
    """
    if request.method == "POST":
        # Khởi tạo form với dữ liệu POST
        # Lưu ý: AuthenticationForm cần request là tham số đầu tiên
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            # Lấy thông tin người dùng đã xác thực
            user = form.get_user()

            # Đăng nhập người dùng
            login(request, user)

            messages.success(
                request, f"Đăng nhập thành công! Chào mừng trở lại, {user.username}."
            )
            # Chuyển hướng người dùng đến trang họ muốn (nếu có next param) hoặc LOGIN_REDIRECT_URL
            return redirect(request.GET.get("next") or LOGIN_REDIRECT_URL)
        else:
            # Nếu form không hợp lệ
            messages.error(
                request,
                "Đăng nhập không thành công. Tên người dùng hoặc mật khẩu không đúng.",
            )

    # Nếu là request GET, hoặc form POST không hợp lệ
    else:
        form = AuthenticationForm()

    context = {"form": form, "page_title": "Đăng Nhập Tài Khoản"}
    # Sử dụng template 'account/login.html'
    return render(request, "story/account/login.html", context)


@login_required
def profile_view(request):
    """
    Hiển thị thông tin hồ sơ người dùng.
    Dữ liệu người dùng (request.user) đã có sẵn trong template.
    """
    return render(request, "story/account/profile.html")


# --- Hàm View cho Trang CHỈNH SỬA HỒ SƠ ---
@login_required
def profile_edit_view(request):
    """
    Cho phép người dùng chỉnh sửa thông tin cá nhân (First name, Last name, Email)
    sử dụng ProfileEditForm an toàn.
    """
    if request.method == "POST":
        # 1. SỬ DỤNG PROFILEEDITFORM TÙY CHỈNH để tránh hiển thị các trường admin
        form = ProfileEditForm(request.POST, instance=request.user)

        if form.is_valid():
            user = form.save()
            messages.success(request, "Hồ sơ đã được cập nhật thành công! (Chỉnh sửa)")
            return redirect("profile")  # Chuyển hướng về trang profile sau khi lưu
        else:
            messages.error(
                request,
                "Đã xảy ra lỗi khi cập nhật hồ sơ. Vui lòng kiểm tra lại thông tin.",
            )

    else:
        # Load dữ liệu hiện tại của user vào ProfileEditForm
        form = ProfileEditForm(instance=request.user)

    context = {"form": form}
    return render(request, "story/account/profile_edit.html", context)


def custom_logout_view(request):
    """
    Xử lý logic Đăng xuất.
    """
    logout(request)
    messages.info(request, "Bạn đã đăng xuất thành công.")
    # Chuyển hướng về trang chủ
    return redirect("home")


def search_results(request):
    """Xử lý logic tìm kiếm truyện."""

    query = request.GET.get("q")  # Lấy chuỗi tìm kiếm từ thanh header
    results = []
    page_title = "Kết Quả Tìm Kiếm"

    if query:
        try:
            # Truy vấn cơ sở dữ liệu: Tìm kiếm gần đúng (icontains)
            results = (
                Story.objects.filter(
                    Q(title__icontains=query)
                    | Q(author__icontains=query)
                    | Q(description__icontains=query)
                )
                .distinct()
                .order_by("-created_at")
            )

            page_title = f'Kết Quả Tìm Kiếm cho: "{query}"'
        except NameError:
            print("loi")
    context = {
        "query": query,
        "stories": results,
        "page_title": page_title,
    }

    # Sử dụng lại template hiển thị danh sách truyện
    return render(request, "story/story_list.html", context)


def category_detail(request, category_slug):
    """
    Hiển thị chi tiết một danh mục và tất cả các truyện thuộc danh mục đó.
    """
    # 1. Tìm Category dựa trên slug, nếu không tìm thấy thì trả về 404
    category = get_object_or_404(Category, slug=category_slug)

    # 2. Lấy tất cả các câu chuyện liên quan đến danh mục này.
    # Ta dùng related_name='stories' đã được định nghĩa trong ManyToManyField của Story.
    # Ví dụ: stories = Story.objects.filter(categories=category)
    stories = category.stories.all().order_by("-views_count")  # Sắp xếp theo lượt xem

    context = {
        "category": category,
        "stories": stories,
    }

    return render(request, "story/category_detail.html", context)


@login_required
def toggle_favorite(request, story_slug):
    if request.method == "POST":
        story = get_object_or_404(Story, slug=story_slug)
        user = request.user

        try:
            # Nếu đã tồn tại, đảo trạng thái True <-> False
            favorite_entry = UserFavorite.objects.get(user=user, story=story)
            favorite_entry.status = not favorite_entry.status
            favorite_entry.save()
            is_favorited = favorite_entry.status
            print(is_favorited)
            message = (
                "Đã thêm vào mục yêu thích."
                if is_favorited
                else "Đã xoá khỏi mục yêu thích."
            )
        except UserFavorite.DoesNotExist:
            # Nếu chưa có thì tạo mới (mặc định là True)
            UserFavorite.objects.create(user=user, story=story, status=True)
            favorite_entry.status = True
            message = "Đã thêm vào mục yêu thích."

        # Nếu là AJAX request thì trả về JSON
        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            return JsonResponse(
                {
                    "success": True,
                    "is_favorited": favorite_entry.status,
                    "message": message,
                }
            )

        # Nếu không phải AJAX (ví dụ form POST), chuyển hướng về lại trang chi tiết
        return redirect("story_detail", story_slug=story_slug)
    # Nếu là GET hoặc method khác → redirect về chi tiết truyện
    return redirect("story_detail", story_slug=story_slug)


@login_required
def favorite_list(request):
    """Hiển thị danh sách truyện đã được người dùng lưu (status=True)."""

    # Lấy tất cả đối tượng UserFavorite của người dùng hiện tại
    # Lọc theo status=True (đã lưu) và sắp xếp theo thời gian mới nhất
    user_favorites = (
        UserFavorite.objects.filter(user=request.user, status=True)
        .select_related("story")
        .order_by("-created_at")
    )

    # Lấy danh sách các đối tượng Story từ user_favorites
    favorite_stories = [fav.story for fav in user_favorites]

    context = {
        "page_title": "Truyện Đã Lưu",
        "favorite_stories": favorite_stories,
        "user_favorites": user_favorites,  # Tùy chọn, nếu cần thông tin created_at
    }

    return render(request, "story/favorite.html", context)


@login_required  # Chỉ cho phép người dùng đã đăng nhập bình luận
@require_http_methods(["POST"])  # Chỉ chấp nhận phương thức POST từ form
def submit_comment(request, story_slug):
    """
    Xử lý việc gửi bình luận mới hoặc trả lời (reply) bình luận cũ bằng AJAX.
    """
    try:
        # 1. Lấy truyện
        story = get_object_or_404(Story, slug=story_slug)
    except Exception:
        # Trả về 404 nếu không tìm thấy truyện (chỉ cho AJAX)
        return JsonResponse({'success': False, 'message': 'Truyện không tồn tại.'}, status=404)

    # Lấy dữ liệu cần thiết
    comment_content = request.POST.get("content", "").strip()
    parent_id = request.POST.get("parent_id") # Lấy ID của bình luận cha (nếu có)
    
    # Kiểm tra xem có phải là AJAX request không
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

    # Kiểm tra nội dung bình luận
    if not comment_content:
        if is_ajax:
            return JsonResponse({'success': False, 'message': 'Nội dung không được để trống.'}, status=400)
        # Nếu không phải AJAX, chuyển hướng về trang chi tiết truyện (không xử lý logic lỗi phức tạp)
        return redirect("story_detail", story_slug=story.slug)
    
    # --- Xử lý Bình luận Cha (Parent Comment) ---
    parent_comment = None
    if parent_id:
        try:
            # Lấy đối tượng Comment cha, đảm bảo nó thuộc truyện hiện tại
            parent_comment = Comment.objects.get(pk=parent_id, story=story)
        except (Comment.DoesNotExist, ValueError):
            # Nếu ID cha không hợp lệ, vẫn cho phép tạo bình luận gốc (hoặc trả về lỗi tùy theo yêu cầu)
            # Ở đây, ta chọn bỏ qua parent_id không hợp lệ và tiếp tục như bình luận gốc.
            print(f"Lỗi: Bình luận cha ID {parent_id} không hợp lệ.")
            pass 

    # --- 2. Tạo đối tượng bình luận mới ---
    try:
        new_comment = Comment.objects.create(
            story=story,
            user=request.user,
            content=comment_content,
            parent_comment=parent_comment, # Gán bình luận cha
            is_approved=True, # Tạm thời cho phép hiển thị ngay
        )
    except Exception as e:
        # Xử lý các lỗi khác (ví dụ: lỗi database)
        print(f"Lỗi khi tạo bình luận: {e}")
        if is_ajax:
            return JsonResponse({'success': False, 'message': 'Lỗi máy chủ khi lưu bình luận.'}, status=500)
        return redirect("story_detail", story_slug=story.slug)


    # --- 3. Trả về Response ---
    if is_ajax:
        # Trả về JSON response
        comment_data = {
            'id': new_comment.id,
            'content': new_comment.content,
            'username': request.user.username,
            # Format thời gian theo định dạng cần thiết cho JavaScript
            'created_at': new_comment.created_at.isoformat(), 
            'is_reply': parent_comment is not None
        }
        return JsonResponse({
            'success': True,
            'message': 'Bình luận đã được gửi thành công.',
            'comment': comment_data,
        })
    else:
        # Chuyển hướng người dùng trở lại trang chi tiết truyện
        # Thêm neo #comments để nhảy đến khu vực bình luận sau khi post
        return redirect(f"{story.get_absolute_url()}#comments")
    
@login_required
def history_view(request):
    # Lấy 10 bản ghi lịch sử đọc gần nhất của người dùng hiện tại, 
    # sắp xếp theo 'last_read_at' giảm dần.
    recent_history = ReadingHistory.objects.filter(user=request.user).select_related(
        'story', 'chapter' # Tối ưu truy vấn
    ).order_by('-last_read_at')[:10]

    context = {
        'recent_history': recent_history,
    }
    return render(request, 'story/reading_history.html', context)
@login_required  # Chỉ cho phép người dùng đã đăng nhập đánh giá
@require_http_methods(["POST"])  # Chỉ chấp nhận phương thức POST từ AJAX
def submit_rating(request, story_slug):
    """
    Xử lý việc gửi hoặc cập nhật điểm đánh giá (1-5 sao) bằng AJAX.
    """
    # 1. Lấy truyện
    try:
        story = get_object_or_404(Story, slug=story_slug)
    except Exception:
        return JsonResponse({'success': False, 'message': 'Truyện không tồn tại.'}, status=404)

    # Lấy dữ liệu cần thiết
    score_str = request.POST.get('score', '')
    
    # Kiểm tra xem có phải là AJAX request không (chủ yếu là AJAX cho rating)
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

    # 2. Xử lý và kiểm tra điểm số
    try:
        score = int(score_str)
        if not (1 <= score <= 5):
            raise ValueError("Điểm phải là số nguyên từ 1 đến 5.")
    except ValueError as e:
        if is_ajax:
            return JsonResponse({'success': False, 'message': f"Lỗi đầu vào: {e}"}, status=400)
        # Nếu không phải AJAX, chuyển hướng về trang chi tiết
        return redirect("story_detail", story_slug=story.slug)

    # --- 3. Lưu hoặc Cập nhật đánh giá ---
    try:
        # Sử dụng update_or_create để đảm bảo mỗi người dùng chỉ có 1 đánh giá cho mỗi truyện
        rating, created = Rating.objects.update_or_create(
            user=request.user,
            story=story,
            defaults={'score': score}
        )
    except Exception as e:
        print(f"Lỗi khi lưu/cập nhật đánh giá: {e}")
        if is_ajax:
            return JsonResponse({'success': False, 'message': 'Lỗi máy chủ khi lưu đánh giá.'}, status=500)
        return redirect("story_detail", story_slug=story.slug)
    
    # --- 4. Tính toán lại thống kê ---
    # Sử dụng Aggregate để lấy điểm trung bình và tổng số lượt đánh giá
    stats = Rating.objects.filter(story=story).aggregate(
        avg_score=Avg('score'),
        total_count=Count('id')
    )
    
    average_rating = stats['avg_score'] if stats['avg_score'] is not None else 0.0
    total_ratings = stats['total_count']
    
    # --- 5. Trả về Response ---
    if is_ajax:
        # Trả về JSON response
        return JsonResponse({
            'success': True,
            'message': 'Đánh giá đã được lưu/cập nhật thành công.',
            'score': rating.score,
            # Định dạng điểm trung bình thành chuỗi có 1 chữ số thập phân
            'average_rating': f"{average_rating:.1f}", 
            'total_ratings': total_ratings
        })
    else:
        # Chuyển hướng người dùng trở lại trang chi tiết truyện
        return redirect(f"{story.get_absolute_url()}#rating-widget")