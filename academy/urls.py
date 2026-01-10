"""
مسارات URL لتطبيق academy
=========================
"""

from django.urls import path
from . import views

urlpatterns = [
    # الصفحة الرئيسية
    path('', views.home, name='home'),
    
    # المصادقة
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('register/', views.user_register, name='register'),
    
    # لوحة التحكم
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # الملف الشخصي
    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('profile/change-password/', views.change_password, name='change_password'),
    
    # API
    path('api/specializations/', views.get_specializations, name='get_specializations'),
]