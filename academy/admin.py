"""
إعدادات لوحة تحكم المدير لنظام S-ACM
=====================================
تخصيص عرض وإدارة النماذج في لوحة تحكم Django Admin
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from django.db.models import Count
from .models import (
    User, Department, Specialization, Course,
    Enrollment, LectureFile, Notification,
    AISummary, AIQuestion, RolePermission
)


# =============================================================================
# تخصيص عنوان لوحة التحكم
# =============================================================================

admin.site.site_header = "نظام إدارة المحتوى الأكاديمي الذكي"
admin.site.site_title = "S-ACM Admin"
admin.site.index_title = "لوحة التحكم الرئيسية"


# =============================================================================
# 1. إدارة المستخدمين (User Admin)
# =============================================================================

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """إدارة المستخدمين مع الحقول المخصصة"""
    
    list_display = [
        'username', 'email', 'full_name_display', 'role_badge',
        'department', 'level', 'is_active', 'date_joined'
    ]
    
    list_filter = ['role', 'is_active', 'department', 'level', 'date_joined']
    
    search_fields = ['username', 'email', 'first_name', 'last_name', 'academic_id']
    
    ordering = ['-date_joined']
    
    # تقسيم الحقول في صفحة التعديل
    fieldsets = (
        ('معلومات الحساب', {
            'fields': ('username', 'password')
        }),
        ('المعلومات الشخصية', {
            'fields': ('first_name', 'last_name', 'email', 'phone', 'profile_image')
        }),
        ('المعلومات الأكاديمية', {
            'fields': ('role', 'academic_id', 'department', 'specialization', 'level')
        }),
        ('الصلاحيات', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
            'classes': ('collapse',)
        }),
        ('التواريخ', {
            'fields': ('last_login', 'date_joined'),
            'classes': ('collapse',)
        }),
    )
    
    # حقول إضافة مستخدم جديد
    add_fieldsets = (
        ('معلومات الحساب', {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2'),
        }),
        ('المعلومات الأكاديمية', {
            'fields': ('role', 'first_name', 'last_name', 'academic_id', 'department', 'level'),
        }),
    )
    
    def full_name_display(self, obj):
        """عرض الاسم الكامل"""
        return obj.get_full_name() or '-'
    full_name_display.short_description = 'الاسم الكامل'
    
    def role_badge(self, obj):
        """عرض الدور بشكل ملون"""
        colors = {
            'student': '#28a745',  # أخضر
            'teacher': '#007bff',  # أزرق
            'admin': '#dc3545',    # أحمر
        }
        color = colors.get(obj.role, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; '
            'border-radius: 3px; font-size: 11px;">{}</span>',
            color, obj.get_role_display()
        )
    role_badge.short_description = 'الدور'


# =============================================================================
# 2. إدارة الأقسام (Department Admin)
# =============================================================================

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    """إدارة الأقسام الأكاديمية"""
    
    list_display = ['name', 'head', 'specializations_count', 'users_count', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name', 'description']
    
    def specializations_count(self, obj):
        """عدد التخصصات في القسم"""
        return obj.specializations.count()
    specializations_count.short_description = 'عدد التخصصات'
    
    def users_count(self, obj):
        """عدد المستخدمين في القسم"""
        return obj.users.count()
    users_count.short_description = 'عدد المستخدمين'


# =============================================================================
# 3. إدارة التخصصات (Specialization Admin)
# =============================================================================

@admin.register(Specialization)
class SpecializationAdmin(admin.ModelAdmin):
    """إدارة التخصصات"""
    
    list_display = ['name', 'department', 'courses_count', 'created_at']
    list_filter = ['department', 'created_at']
    search_fields = ['name', 'description']
    
    def courses_count(self, obj):
        """عدد المقررات في التخصص"""
        return obj.courses.count()
    courses_count.short_description = 'عدد المقررات'


# =============================================================================
# 4. إدارة المقررات (Course Admin)
# =============================================================================

class EnrollmentInline(admin.TabularInline):
    """عرض التسجيلات داخل صفحة المقرر"""
    model = Enrollment
    extra = 0
    readonly_fields = ['enrolled_at']
    autocomplete_fields = ['student']


class LectureFileInline(admin.TabularInline):
    """عرض الملفات داخل صفحة المقرر"""
    model = LectureFile
    extra = 0
    readonly_fields = ['uploaded_at', 'file_size', 'download_count']
    fields = ['title', 'file', 'file_type', 'chapter', 'uploaded_at']


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    """إدارة المقررات الدراسية"""
    
    list_display = [
        'code', 'name', 'specialization', 'level', 'semester',
        'teacher', 'enrolled_count', 'files_count', 'is_active'
    ]
    
    list_filter = [
        'specialization__department', 'specialization', 'level',
        'semester', 'is_active', 'academic_year'
    ]
    
    search_fields = ['name', 'code', 'description']
    
    autocomplete_fields = ['teacher', 'specialization']
    
    inlines = [LectureFileInline, EnrollmentInline]
    
    fieldsets = (
        ('معلومات المقرر', {
            'fields': ('name', 'code', 'description')
        }),
        ('التصنيف', {
            'fields': ('specialization', 'level', 'semester', 'academic_year')
        }),
        ('التفاصيل', {
            'fields': ('teacher', 'credit_hours', 'is_active')
        }),
    )
    
    def enrolled_count(self, obj):
        """عدد الطلاب المسجلين"""
        count = obj.enrollments.count()
        return format_html('<strong>{}</strong> طالب', count)
    enrolled_count.short_description = 'المسجلون'
    
    def files_count(self, obj):
        """عدد الملفات"""
        return obj.lecture_files.count()
    files_count.short_description = 'الملفات'


# =============================================================================
# 5. إدارة التسجيلات (Enrollment Admin)
# =============================================================================

@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    """إدارة تسجيل الطلاب في المقررات"""
    
    list_display = ['student', 'course', 'enrolled_at', 'is_active']
    list_filter = ['is_active', 'course__specialization', 'enrolled_at']
    search_fields = ['student__username', 'student__first_name', 'course__name']
    autocomplete_fields = ['student', 'course']
    date_hierarchy = 'enrolled_at'


# =============================================================================
# 6. إدارة ملفات المحاضرات (LectureFile Admin)
# =============================================================================

@admin.register(LectureFile)
class LectureFileAdmin(admin.ModelAdmin):
    """إدارة ملفات المحاضرات"""
    
    list_display = [
        'title', 'course', 'file_type_badge', 'chapter',
        'uploaded_by', 'file_size_display', 'download_count', 'uploaded_at'
    ]
    
    list_filter = ['file_type', 'course__specialization', 'uploaded_at', 'is_active']
    
    search_fields = ['title', 'description', 'course__name']
    
    autocomplete_fields = ['course', 'uploaded_by']
    
    readonly_fields = ['file_size', 'download_count', 'uploaded_at']
    
    date_hierarchy = 'uploaded_at'
    
    fieldsets = (
        ('معلومات الملف', {
            'fields': ('title', 'description', 'file', 'file_type')
        }),
        ('التصنيف', {
            'fields': ('course', 'chapter')
        }),
        ('معلومات الرفع', {
            'fields': ('uploaded_by', 'uploaded_at', 'file_size', 'download_count'),
            'classes': ('collapse',)
        }),
        ('الحالة', {
            'fields': ('is_active',)
        }),
    )
    
    def file_type_badge(self, obj):
        """عرض نوع الملف بشكل ملون"""
        colors = {
            'pdf': '#dc3545',
            'word': '#007bff',
            'ppt': '#fd7e14',
            'video': '#6f42c1',
            'audio': '#20c997',
            'image': '#17a2b8',
            'other': '#6c757d',
        }
        color = colors.get(obj.file_type, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 8px; '
            'border-radius: 3px; font-size: 10px;">{}</span>',
            color, obj.get_file_type_display()
        )
    file_type_badge.short_description = 'النوع'
    
    def file_size_display(self, obj):
        """عرض حجم الملف بشكل مقروء"""
        size = obj.file_size
        if size < 1024:
            return f"{size} B"
        elif size < 1024 * 1024:
            return f"{size / 1024:.1f} KB"
        else:
            return f"{size / (1024 * 1024):.1f} MB"
    file_size_display.short_description = 'الحجم'


# =============================================================================
# 7. إدارة الإشعارات (Notification Admin)
# =============================================================================

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    """إدارة الإشعارات"""
    
    list_display = [
        'title', 'notification_type', 'priority_badge', 'sender',
        'course', 'is_read', 'created_at'
    ]
    
    list_filter = ['notification_type', 'priority', 'is_read', 'created_at']
    
    search_fields = ['title', 'content']
    
    autocomplete_fields = ['sender', 'course', 'recipient']
    
    date_hierarchy = 'created_at'
    
    def priority_badge(self, obj):
        """عرض الأولوية بشكل ملون"""
        colors = {
            'low': '#6c757d',
            'normal': '#17a2b8',
            'high': '#fd7e14',
            'urgent': '#dc3545',
        }
        color = colors.get(obj.priority, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 8px; '
            'border-radius: 3px; font-size: 10px;">{}</span>',
            color, obj.get_priority_display()
        )
    priority_badge.short_description = 'الأولوية'


# =============================================================================
# 8. إدارة ملخصات الذكاء الاصطناعي (AISummary Admin)
# =============================================================================

@admin.register(AISummary)
class AISummaryAdmin(admin.ModelAdmin):
    """إدارة ملخصات الذكاء الاصطناعي"""
    
    list_display = ['lecture_file', 'generated_by', 'generated_at', 'is_cached']
    list_filter = ['is_cached', 'generated_at']
    search_fields = ['lecture_file__title', 'summary_text']
    readonly_fields = ['generated_at']
    date_hierarchy = 'generated_at'


# =============================================================================
# 9. إدارة أسئلة الذكاء الاصطناعي (AIQuestion Admin)
# =============================================================================

@admin.register(AIQuestion)
class AIQuestionAdmin(admin.ModelAdmin):
    """إدارة أسئلة الذكاء الاصطناعي"""
    
    list_display = ['question_preview', 'lecture_file', 'generated_by', 'generated_at']
    list_filter = ['generated_at']
    search_fields = ['question_text', 'lecture_file__title']
    readonly_fields = ['generated_at']
    date_hierarchy = 'generated_at'
    
    def question_preview(self, obj):
        """معاينة السؤال"""
        return obj.question_text[:50] + '...' if len(obj.question_text) > 50 else obj.question_text
    question_preview.short_description = 'السؤال'


# =============================================================================
# 10. إدارة صلاحيات الأدوار (RolePermission Admin)
# =============================================================================

@admin.register(RolePermission)
class RolePermissionAdmin(admin.ModelAdmin):
    """إدارة صلاحيات الأدوار"""
    
    list_display = [
        'role', 'can_upload_files', 'can_delete_files',
        'can_manage_users', 'can_manage_courses',
        'can_send_notifications', 'can_use_ai'
    ]
    
    list_editable = [
        'can_upload_files', 'can_delete_files',
        'can_manage_users', 'can_manage_courses',
        'can_send_notifications', 'can_use_ai'
    ]