from django.urls import path
from . import views

urlpatterns = [
    # Сначала конкретные пути (upload и delete)
    path('upload/', views.upload_work, name='upload_work'),
    path('delete/<int:pk>/', views.delete_work, name='delete_work'),
    # Потом общий путь для просмотра работы (он перехватывает любые ID)
    path('<int:pk>/', views.work_detail, name='work_detail'),
]