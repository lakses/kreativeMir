from django.urls import path
from . import views

urlpatterns = [
    path('profile/', views.profile_view, name='profile'),
    path('register/', views.register_view, name='register'),
    path('profile/<str:username>/', views.profile_view, name='profile_detail'),
    path('chat/', views.chat_list_view, name='chat_list'),
    path('chat/<int:chat_id>/', views.chat_detail_view, name='chat_detail'),
    path('chat/start/<int:user_id>/', views.start_chat_view, name='start_chat'),
    path('chat/<int:chat_id>/messages/', views.get_new_messages_api, name='get_new_messages'),
    
    path('quiz/<int:user_id>/', views.quiz_view, name='quiz'),
    path('quiz/manage/', views.manage_quiz_view, name='manage_quiz')
]