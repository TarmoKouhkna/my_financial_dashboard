from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('portfolio/', views.portfolio_list, name='portfolio_list'),
    path('portfolio/<int:pk>/', views.portfolio_detail, name='portfolio_detail'),
    path('portfolio/add/', views.portfolio_add, name='portfolio_add'),
    path('register/', views.register, name='register'),
]
