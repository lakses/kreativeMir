from django.urls import path
from . import views

urlpatterns = [
    path('', views.creators_list_view, name='creators_list'),

]