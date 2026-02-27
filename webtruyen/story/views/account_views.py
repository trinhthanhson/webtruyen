from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.db.models import Count

from ..models import Category, Story, UserFavorite , ReadingHistory
from ..form import ProfileEditForm 
from django.http import JsonResponse


LOGIN_REDIRECT_URL = getattr(settings, 'LOGIN_REDIRECT_URL', '/')

def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect(LOGIN_REDIRECT_URL)
        else:
            print("LỖI VALIDATION ĐĂNG KÝ:", form.errors)
            messages.error(request, "Đăng ký không thành công. Vui lòng kiểm tra lại thông tin.")
    else:
        form = UserCreationForm()
        
    context = {
        'form': form,
        'page_title': 'Đăng Ký Tài Khoản'
    }
    return render(request, 'story/account/register.html', context)

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Đăng nhập thành công! Chào mừng trở lại, {user.username}.')
            return redirect(request.GET.get('next') or LOGIN_REDIRECT_URL)
        else:
            messages.error(request, "")
    else:
        form = AuthenticationForm()
        
    context = {
        'form': form,
        'page_title': 'Đăng Nhập Tài Khoản'
    }
    return render(request, 'story/account/login.html', context)

@login_required
def profile_view(request):
    # 1. Lấy 10 truyện đã đọc gần đây nhất (sắp xếp theo thời gian mới nhất)
    recent_history = ReadingHistory.objects.filter(user=request.user)\
        .select_related('story', 'chapter')\
        .order_by('-last_read_at')[:10]

    # 2. Lấy danh sách tất cả truyện yêu thích của người dùng
    favorite_stories = UserFavorite.objects.filter(user=request.user)\
        .select_related('story')\
        .order_by('-created_at') # Giả sử bạn có trường created_at, nếu không thì bỏ order_by
    categories = Category.objects.annotate(story_count=Count('stories'))
    context = {
        'user': request.user,
        'recent_history': recent_history,
        'favorite_stories': favorite_stories,
        'page_title': f"Hồ sơ của {request.user.username}",
        'categories':categories
    }
    
    return render(request, 'story/account/profile.html', context)

@login_required
def profile_edit_view(request):
    if request.method == 'POST':
        form = ProfileEditForm(request.POST, instance=request.user) 
        if form.is_valid():
            form.save()
            messages.success(request, 'Hồ sơ đã được cập nhật thành công!')
            return redirect('profile')
        else:
            messages.error(request, 'Đã xảy ra lỗi khi cập nhật hồ sơ.')
    else:
        form = ProfileEditForm(instance=request.user) 
    
    return render(request, 'story/account/profile_edit.html', {'form': form})

def custom_logout_view(request):
    logout(request)
    return redirect('home')

@login_required
def toggle_favorite(request, story_slug):
    if request.method == "POST":
        story = Story.objects.get(slug=story_slug)
        favorite, created = UserFavorite.objects.get_or_create(user=request.user, story=story)
        
        if not created:
            favorite.delete()
            is_favorite = False
        else:
            is_favorite = True
            
        return JsonResponse({
            'status': 'success',
            'is_favorite': is_favorite,
        })
    return JsonResponse({'status': 'error'}, status=400)