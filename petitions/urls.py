from django.urls import path
from . import views

urlpatterns = [
    path('', views.petition_list, name='petition_list'),
    path('create/', views.petition_create, name='petition_create'),
    path('<int:pk>/', views.petition_detail, name='petition_detail'),
]
