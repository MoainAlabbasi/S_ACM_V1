"""
Decorators للتحقق من الصلاحيات
==============================
تستخدم لحماية الـ Views بناءً على دور المستخدم
"""

from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.core.exceptions import PermissionDenied


def role_required(allowed_roles):
    """
    Decorator للتحقق من دور المستخدم
    
    الاستخدام:
    @role_required(['teacher', 'admin'])
    def my_view(request):
        ...
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                messages.error(request, 'يجب تسجيل الدخول أولاً')
                return redirect('login')
            
            if request.user.role not in allowed_roles:
                messages.error(request, 'ليس لديك صلاحية للوصول إلى هذه الصفحة')
                raise PermissionDenied
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def student_required(view_func):
    """Decorator للطلاب فقط"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'يجب تسجيل الدخول أولاً')
            return redirect('login')
        
        if not request.user.is_student:
            messages.error(request, 'هذه الصفحة متاحة للطلاب فقط')
            raise PermissionDenied
        
        return view_func(request, *args, **kwargs)
    return wrapper


def teacher_required(view_func):
    """Decorator للمدرسين فقط"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'يجب تسجيل الدخول أولاً')
            return redirect('login')
        
        if not request.user.is_teacher:
            messages.error(request, 'هذه الصفحة متاحة للمدرسين فقط')
            raise PermissionDenied
        
        return view_func(request, *args, **kwargs)
    return wrapper


def admin_required(view_func):
    """Decorator للمسؤولين فقط"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'يجب تسجيل الدخول أولاً')
            return redirect('login')
        
        if not request.user.is_admin_user:
            messages.error(request, 'هذه الصفحة متاحة للمسؤولين فقط')
            raise PermissionDenied
        
        return view_func(request, *args, **kwargs)
    return wrapper


def teacher_or_admin_required(view_func):
    """Decorator للمدرسين أو المسؤولين"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'يجب تسجيل الدخول أولاً')
            return redirect('login')
        
        if not (request.user.is_teacher or request.user.is_admin_user):
            messages.error(request, 'هذه الصفحة متاحة للمدرسين والمسؤولين فقط')
            raise PermissionDenied
        
        return view_func(request, *args, **kwargs)
    return wrapper