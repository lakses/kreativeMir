from django.urls import path
from . import views

urlpatterns = [
    path('upload/', views.upload_work, name='upload_work'),
    path('delete/<int:pk>/', views.delete_work, name='delete_work'),
    # ВОТ ЭТА СТРОКА ОТВЕЧАЕТ ЗА ЗАКРЕПЛЕНИЕ:
    path('pin/<int:pk>/', views.toggle_pin_work, name='toggle_pin_work'),
    path('<int:pk>/', views.work_detail, name='work_detail'),
]