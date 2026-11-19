from django.urls import path
from . import views

urlpatterns = [
    path('profile/', views.profile_view, name='profile'),
    path('register/', views.register_view, name='register'),
    path('profile/<str:username>/', views.profile_view, name='profile_detail'),
    
    # --- ЧАТЫ ---
    path('chat/', views.chat_list_view, name='chat_list'),
    # ВАЖНО: здесь теперь views.chat_list_view, а не chat_detail_view
    path('chat/<int:chat_id>/', views.chat_list_view, name='chat_detail'), 
    path('chat/start/<int:user_id>/', views.start_chat_view, name='start_chat'),
    path('chat/<int:chat_id>/messages/', views.get_new_messages_api, name='get_new_messages'),
    
    # --- ОСТАЛЬНОЕ ---
    path('quiz/<int:user_id>/', views.quiz_view, name='quiz'),
    path('quiz/manage/', views.manage_quiz_view, name='manage_quiz'),
    path('feed/', views.feed_view, name='feed'),
    path('feed/post/<int:post_id>/like/', views.toggle_post_like_view, name='toggle_post_like'),
    path('feed/post/<int:post_id>/comment/', views.add_post_comment_view, name='add_post_comment'),
    
    # ДОБАВЬ ВОТ ЭТУ СТРОКУ (для страницы поста, которую мы делали ранее):
    path('post/<int:pk>/', views.post_detail, name='post_detail'),
]