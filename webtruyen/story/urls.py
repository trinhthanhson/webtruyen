from django.urls import path
from . import views

urlpatterns = [
    path('', views.story_list, name='story_list'),
    path('<int:story_id>/', views.story_detail, name='story_detail'),
    path('<int:story_id>/chapter/<int:chapter_number>/', views.chapter_detail, name='chapter_detail'),
]
