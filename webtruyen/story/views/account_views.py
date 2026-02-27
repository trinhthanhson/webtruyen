from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.db.models import Count

from ..models import Category
from ..form import ProfileEditForm 

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
            messages.error(request, "Đăng nhập không thành công. Tên người dùng hoặc mật khẩu không đúng.")
    else:
        form = AuthenticationForm()
        
    context = {
        'form': form,
        'page_title': 'Đăng Nhập Tài Khoản'
    }
    return render(request, 'story/account/login.html', context)

@login_required
def profile_view(request):
    return render(request, 'story/account/profile.html')

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
def toggle_favorite(request, story_id):
    if request.method == "POST":
        story = Story.objects.get(id=story_id)
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