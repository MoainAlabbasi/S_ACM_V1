"""
Views لنظام S-ACM
=================
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Q
from django.http import JsonResponse

from .models import (
    User, Department, Specialization, Course,
    Enrollment, LectureFile, Notification
 )
from .forms import (
    LoginForm, StudentRegistrationForm, TeacherRegistrationForm,
    UserProfileForm, ChangePasswordForm
)
from .decorators import (
    student_required, teacher_required, admin_required,
    teacher_or_admin_required, role_required
)


# =============================================================================
# صفحات عامة
# =============================================================================

def home(request):
    """الصفحة الرئيسية"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'academy/home.html')


# =============================================================================
# المصادقة (Authentication)
# =============================================================================

def user_login(request):
    """تسجيل الدخول"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            
            # تذكرني
            if not form.cleaned_data.get('remember_me'):
                request.session.set_expiry(0)
            
            messages.success(request, f'مرحباً {user.get_full_name() or user.username}!')
            
            # توجيه حسب الدور
            next_url = request.GET.get('next', 'dashboard')
            return redirect(next_url)
        else:
            messages.error(request, 'اسم المستخدم أو كلمة المرور غير صحيحة')
    else:
        form = LoginForm()
    
    return render(request, 'registration/login.html', {'form': form})


def user_logout(request):
    """تسجيل الخروج"""
    logout(request)
    messages.info(request, 'تم تسجيل الخروج بنجاح')
    return redirect('login')


def user_register(request):
    """تسجيل طالب جديد"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = StudentRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'تم إنشاء حسابك بنجاح!')
            return redirect('dashboard')
        else:
            messages.error(request, 'يرجى تصحيح الأخطاء أدناه')
    else:
        form = StudentRegistrationForm()
    
    return render(request, 'registration/register.html', {'form': form})


# =============================================================================
# لوحة التحكم (Dashboard)
# =============================================================================

@login_required
def dashboard(request):
    """لوحة التحكم الرئيسية - توجيه حسب الدور"""
    user = request.user
    
    if user.is_student:
        return student_dashboard(request)
    elif user.is_teacher:
        return teacher_dashboard(request)
    elif user.is_admin_user:
        return admin_dashboard(request)
    
    return render(request, 'academy/dashboard.html')


@login_required
@student_required
def student_dashboard(request):
    """لوحة تحكم الطالب"""
    user = request.user
    
    # المقررات المسجل بها
    enrollments = Enrollment.objects.filter(
        student=user, is_active=True
    ).select_related('course', 'course__teacher')
    
    # الإشعارات غير المقروءة
    notifications = Notification.objects.filter(
        Q(recipient=user) | Q(course__enrollments__student=user),
        is_read=False
    ).distinct()[:5]
    
    # آخر الملفات المرفوعة في مقرراته
    recent_files = LectureFile.objects.filter(
        course__enrollments__student=user,
        is_active=True
    ).order_by('-uploaded_at')[:5]
    
    context = {
        'enrollments': enrollments,
        'notifications': notifications,
        'notifications_count': notifications.count(),
        'recent_files': recent_files,
    }
    
    return render(request, 'academy/student/dashboard.html', context)


@login_required
@teacher_required
def teacher_dashboard(request):
    """لوحة تحكم المدرس"""
    user = request.user
    
    # المقررات التي يدرسها
    courses = Course.objects.filter(
        teacher=user, is_active=True
    ).annotate(
        students_count=Count('enrollments'),
        files_count=Count('lecture_files')
    )
    
    # إحصائيات
    total_students = Enrollment.objects.filter(
        course__teacher=user, is_active=True
    ).values('student').distinct().count()
    
    total_files = LectureFile.objects.filter(
        uploaded_by=user
    ).count()
    
    # آخر الملفات المرفوعة
    recent_files = LectureFile.objects.filter(
        uploaded_by=user
    ).order_by('-uploaded_at')[:5]
    
    context = {
        'courses': courses,
        'total_students': total_students,
        'total_files': total_files,
        'recent_files': recent_files,
    }
    
    return render(request, 'academy/teacher/dashboard.html', context)


@login_required
@admin_required
def admin_dashboard(request):
    """لوحة تحكم المسؤول"""
    
    # إحصائيات عامة
    stats = {
        'total_users': User.objects.count(),
        'total_students': User.objects.filter(role='student').count(),
        'total_teachers': User.objects.filter(role='teacher').count(),
        'total_courses': Course.objects.filter(is_active=True).count(),
        'total_departments': Department.objects.count(),
        'total_files': LectureFile.objects.count(),
    }
    
    # آخر المستخدمين المسجلين
    recent_users = User.objects.order_by('-date_joined')[:5]
    
    # آخر الملفات المرفوعة
    recent_files = LectureFile.objects.order_by('-uploaded_at')[:5]
    
    context = {
        'stats': stats,
        'recent_users': recent_users,
        'recent_files': recent_files,
    }
    
    return render(request, 'academy/admin/dashboard.html', context)


# =============================================================================
# الملف الشخصي
# =============================================================================

@login_required
def profile(request):
    """عرض الملف الشخصي"""
    return render(request, 'academy/profile.html', {'user': request.user})


@login_required
def edit_profile(request):
    """تعديل الملف الشخصي"""
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'تم تحديث الملف الشخصي بنجاح')
            return redirect('profile')
    else:
        form = UserProfileForm(instance=request.user)
    
    return render(request, 'academy/edit_profile.html', {'form': form})


@login_required
def change_password(request):
    """تغيير كلمة المرور"""
    if request.method == 'POST':
        form = ChangePasswordForm(request.POST)
        if form.is_valid():
            if not request.user.check_password(form.cleaned_data['old_password']):
                messages.error(request, 'كلمة المرور الحالية غير صحيحة')
            else:
                request.user.set_password(form.cleaned_data['new_password1'])
                request.user.save()
                update_session_auth_hash(request, request.user)
                messages.success(request, 'تم تغيير كلمة المرور بنجاح')
                return redirect('profile')
    else:
        form = ChangePasswordForm()
    
    return render(request, 'academy/change_password.html', {'form': form})


# =============================================================================
# API للتخصصات (AJAX)
# =============================================================================

def get_specializations(request):
    """جلب التخصصات حسب القسم (AJAX)"""
    department_id = request.GET.get('department_id')
    
    if department_id:
        specializations = Specialization.objects.filter(
            department_id=department_id
        ).values('id', 'name')
        return JsonResponse(list(specializations), safe=False)
    
    return JsonResponse([], safe=False)