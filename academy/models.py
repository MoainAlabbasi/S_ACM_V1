"""
نماذج البيانات لنظام S-ACM
===========================
يحتوي هذا الملف على جميع نماذج قاعدة البيانات للمشروع.

الجداول:
- User: المستخدمون (طالب، مدرس، مسؤول)
- Department: الأقسام الأكاديمية
- Specialization: التخصصات
- Course: المقررات الدراسية
- Enrollment: تسجيل الطلاب في المقررات
- LectureFile: ملفات المحاضرات
- Notification: الإشعارات
- AISummary: ملخصات الذكاء الاصطناعي
- AIQuestion: أسئلة الذكاء الاصطناعي
"""

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import FileExtensionValidator
from django.utils import timezone


# =============================================================================
# 1. نموذج المستخدم المخصص (Custom User Model)
# =============================================================================

class User(AbstractUser):
    """
    نموذج المستخدم المخصص الذي يدعم ثلاثة أدوار:
    - طالب (student)
    - مدرس (teacher)
    - مسؤول (admin)
    """
    
    class Role(models.TextChoices):
        """أدوار المستخدمين في النظام"""
        STUDENT = 'student', 'طالب'
        TEACHER = 'teacher', 'مدرس'
        ADMIN = 'admin', 'مسؤول'
    
    # الحقول الإضافية
    role = models.CharField(
        max_length=10,
        choices=Role.choices,
        default=Role.STUDENT,
        verbose_name='الدور'
    )
    
    academic_id = models.CharField(
        max_length=20,
        unique=True,
        null=True,
        blank=True,
        verbose_name='الرقم الأكاديمي'
    )
    
    phone = models.CharField(
        max_length=15,
        blank=True,
        null=True,
        verbose_name='رقم الهاتف'
    )
    
    profile_image = models.ImageField(
        upload_to='profiles/',
        blank=True,
        null=True,
        verbose_name='صورة الملف الشخصي'
    )
    
    department = models.ForeignKey(
        'Department',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='users',
        verbose_name='القسم'
    )
    
    specialization = models.ForeignKey(
        'Specialization',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='users',
        verbose_name='التخصص'
    )
    
    # للطلاب فقط: المستوى الدراسي
    level = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        choices=[
            (1, 'المستوى الأول'),
            (2, 'المستوى الثاني'),
            (3, 'المستوى الثالث'),
            (4, 'المستوى الرابع'),
        ],
        verbose_name='المستوى الدراسي'
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='تاريخ الإنشاء'
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='تاريخ التحديث'
    )
    
    class Meta:
        verbose_name = 'مستخدم'
        verbose_name_plural = 'المستخدمون'
        ordering = ['-date_joined']
    
    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.get_role_display()})"
    
    # خصائص مساعدة للتحقق من الدور
    @property
    def is_student(self):
        """هل المستخدم طالب؟"""
        return self.role == self.Role.STUDENT
    
    @property
    def is_teacher(self):
        """هل المستخدم مدرس؟"""
        return self.role == self.Role.TEACHER
    
    @property
    def is_admin_user(self):
        """هل المستخدم مسؤول؟"""
        return self.role == self.Role.ADMIN


# =============================================================================
# 2. نموذج القسم (Department)
# =============================================================================

class Department(models.Model):
    """
    الأقسام الأكاديمية في الكلية
    مثال: قسم تقنية المعلومات، قسم علوم الحاسب
    """
    
    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name='اسم القسم'
    )
    
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name='الوصف'
    )
    
    head = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='headed_departments',
        verbose_name='رئيس القسم'
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='تاريخ الإنشاء'
    )
    
    class Meta:
        verbose_name = 'قسم'
        verbose_name_plural = 'الأقسام'
        ordering = ['name']
    
    def __str__(self):
        return self.name


# =============================================================================
# 3. نموذج التخصص (Specialization)
# =============================================================================

class Specialization(models.Model):
    """
    التخصصات داخل كل قسم
    مثال: شبكات، برمجيات، قواعد بيانات
    """
    
    name = models.CharField(
        max_length=100,
        verbose_name='اسم التخصص'
    )
    
    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        related_name='specializations',
        verbose_name='القسم'
    )
    
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name='الوصف'
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='تاريخ الإنشاء'
    )
    
    class Meta:
        verbose_name = 'تخصص'
        verbose_name_plural = 'التخصصات'
        ordering = ['department', 'name']
        unique_together = ['name', 'department']
    
    def __str__(self):
        return f"{self.name} - {self.department.name}"


# =============================================================================
# 4. نموذج المقرر (Course)
# =============================================================================

class Course(models.Model):
    """
    المقررات الدراسية
    """
    
    class Semester(models.TextChoices):
        """الفصول الدراسية"""
        FIRST = 'first', 'الفصل الأول'
        SECOND = 'second', 'الفصل الثاني'
        SUMMER = 'summer', 'الفصل الصيفي'
    
    name = models.CharField(
        max_length=200,
        verbose_name='اسم المقرر'
    )
    
    code = models.CharField(
        max_length=20,
        unique=True,
        verbose_name='رمز المقرر'
    )
    
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name='الوصف'
    )
    
    specialization = models.ForeignKey(
        Specialization,
        on_delete=models.CASCADE,
        related_name='courses',
        verbose_name='التخصص'
    )
    
    level = models.PositiveSmallIntegerField(
        choices=[
            (1, 'المستوى الأول'),
            (2, 'المستوى الثاني'),
            (3, 'المستوى الثالث'),
            (4, 'المستوى الرابع'),
        ],
        verbose_name='المستوى'
    )
    
    semester = models.CharField(
        max_length=10,
        choices=Semester.choices,
        default=Semester.FIRST,
        verbose_name='الفصل الدراسي'
    )
    
    academic_year = models.CharField(
        max_length=9,
        default='2025/2026',
        verbose_name='العام الأكاديمي'
    )
    
    credit_hours = models.PositiveSmallIntegerField(
        default=3,
        verbose_name='الساعات المعتمدة'
    )
    
    # المدرس المسؤول عن المقرر
    teacher = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='taught_courses',
        limit_choices_to={'role': 'teacher'},
        verbose_name='المدرس'
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name='نشط'
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='تاريخ الإنشاء'
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='تاريخ التحديث'
    )
    
    class Meta:
        verbose_name = 'مقرر'
        verbose_name_plural = 'المقررات'
        ordering = ['specialization', 'level', 'name']
    
    def __str__(self):
        return f"{self.code} - {self.name}"
    
    @property
    def enrolled_students_count(self):
        """عدد الطلاب المسجلين في المقرر"""
        return self.enrollments.count()


# =============================================================================
# 5. نموذج تسجيل المقررات (Enrollment)
# =============================================================================

class Enrollment(models.Model):
    """
    تسجيل الطلاب في المقررات
    """
    
    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='enrollments',
        limit_choices_to={'role': 'student'},
        verbose_name='الطالب'
    )
    
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='enrollments',
        verbose_name='المقرر'
    )
    
    enrolled_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='تاريخ التسجيل'
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name='نشط'
    )
    
    class Meta:
        verbose_name = 'تسجيل'
        verbose_name_plural = 'التسجيلات'
        unique_together = ['student', 'course']
        ordering = ['-enrolled_at']
    
    def __str__(self):
        return f"{self.student.get_full_name()} - {self.course.name}"


# =============================================================================
# 6. نموذج ملفات المحاضرات (LectureFile)
# =============================================================================

class LectureFile(models.Model):
    """
    ملفات المحاضرات والمواد التعليمية
    """
    
    class FileType(models.TextChoices):
        """أنواع الملفات"""
        PDF = 'pdf', 'PDF'
        WORD = 'word', 'Word'
        POWERPOINT = 'ppt', 'PowerPoint'
        VIDEO = 'video', 'فيديو'
        AUDIO = 'audio', 'صوت'
        IMAGE = 'image', 'صورة'
        OTHER = 'other', 'أخرى'
    
    title = models.CharField(
        max_length=255,
        verbose_name='عنوان الملف'
    )
    
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name='الوصف'
    )
    
    file = models.FileField(
        upload_to='lectures/%Y/%m/',
        validators=[
            FileExtensionValidator(
                allowed_extensions=['pdf', 'doc', 'docx', 'ppt', 'pptx', 'mp4', 'mp3', 'jpg', 'png', 'zip']
            )
        ],
        verbose_name='الملف'
    )
    
    file_type = models.CharField(
        max_length=10,
        choices=FileType.choices,
        default=FileType.PDF,
        verbose_name='نوع الملف'
    )
    
    file_size = models.PositiveIntegerField(
        default=0,
        verbose_name='حجم الملف (بايت)'
    )
    
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='lecture_files',
        verbose_name='المقرر'
    )
    
    chapter = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='الفصل/الوحدة'
    )
    
    uploaded_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='uploaded_files',
        verbose_name='رفع بواسطة'
    )
    
    uploaded_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='تاريخ الرفع'
    )
    
    download_count = models.PositiveIntegerField(
        default=0,
        verbose_name='عدد التحميلات'
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name='نشط'
    )
    
    class Meta:
        verbose_name = 'ملف محاضرة'
        verbose_name_plural = 'ملفات المحاضرات'
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return f"{self.title} - {self.course.name}"
    
    def save(self, *args, **kwargs):
        """حفظ حجم الملف تلقائياً"""
        if self.file:
            self.file_size = self.file.size
        super().save(*args, **kwargs)


# =============================================================================
# 7. نموذج الإشعارات (Notification)
# =============================================================================

class Notification(models.Model):
    """
    إشعارات النظام
    """
    
    class NotificationType(models.TextChoices):
        """أنواع الإشعارات"""
        GENERAL = 'general', 'عام'
        COURSE = 'course', 'مقرر'
        FILE = 'file', 'ملف جديد'
        EXAM = 'exam', 'اختبار'
        ANNOUNCEMENT = 'announcement', 'إعلان'
    
    class Priority(models.TextChoices):
        """أولوية الإشعار"""
        LOW = 'low', 'منخفضة'
        NORMAL = 'normal', 'عادية'
        HIGH = 'high', 'عالية'
        URGENT = 'urgent', 'عاجلة'
    
    title = models.CharField(
        max_length=255,
        verbose_name='العنوان'
    )
    
    content = models.TextField(
        verbose_name='المحتوى'
    )
    
    notification_type = models.CharField(
        max_length=15,
        choices=NotificationType.choices,
        default=NotificationType.GENERAL,
        verbose_name='نوع الإشعار'
    )
    
    priority = models.CharField(
        max_length=10,
        choices=Priority.choices,
        default=Priority.NORMAL,
        verbose_name='الأولوية'
    )
    
    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sent_notifications',
        verbose_name='المرسل'
    )
    
    # الإشعار يمكن أن يكون لمقرر معين أو عام
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='notifications',
        verbose_name='المقرر'
    )
    
    # أو لمستخدم محدد
    recipient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='received_notifications',
        verbose_name='المستلم'
    )
    
    is_read = models.BooleanField(
        default=False,
        verbose_name='تمت القراءة'
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='تاريخ الإنشاء'
    )
    
    expiry_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='تاريخ الانتهاء'
    )
    
    class Meta:
        verbose_name = 'إشعار'
        verbose_name_plural = 'الإشعارات'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
    
    @property
    def is_expired(self):
        """هل انتهت صلاحية الإشعار؟"""
        if self.expiry_date:
            return timezone.now() > self.expiry_date
        return False


# =============================================================================
# 8. نموذج ملخصات الذكاء الاصطناعي (AISummary)
# =============================================================================

class AISummary(models.Model):
    """
    ملخصات المحاضرات المولدة بالذكاء الاصطناعي
    """
    
    lecture_file = models.ForeignKey(
        LectureFile,
        on_delete=models.CASCADE,
        related_name='ai_summaries',
        verbose_name='ملف المحاضرة'
    )
    
    summary_text = models.TextField(
        verbose_name='نص الملخص'
    )
    
    generated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='generated_summaries',
        verbose_name='طلب بواسطة'
    )
    
    generated_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='تاريخ التوليد'
    )
    
    # للتخزين المؤقت (Caching)
    is_cached = models.BooleanField(
        default=True,
        verbose_name='مخزن مؤقتاً'
    )
    
    class Meta:
        verbose_name = 'ملخص ذكاء اصطناعي'
        verbose_name_plural = 'ملخصات الذكاء الاصطناعي'
        ordering = ['-generated_at']
    
    def __str__(self):
        return f"ملخص: {self.lecture_file.title}"


# =============================================================================
# 9. نموذج أسئلة الذكاء الاصطناعي (AIQuestion)
# =============================================================================

class AIQuestion(models.Model):
    """
    أسئلة مولدة بالذكاء الاصطناعي من المحاضرات
    """
    
    lecture_file = models.ForeignKey(
        LectureFile,
        on_delete=models.CASCADE,
        related_name='ai_questions',
        verbose_name='ملف المحاضرة'
    )
    
    question_text = models.TextField(
        verbose_name='نص السؤال'
    )
    
    # الخيارات (JSON format)
    options = models.JSONField(
        default=list,
        verbose_name='الخيارات'
    )
    
    correct_answer = models.CharField(
        max_length=255,
        verbose_name='الإجابة الصحيحة'
    )
    
    explanation = models.TextField(
        blank=True,
        null=True,
        verbose_name='الشرح'
    )
    
    generated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='generated_questions',
        verbose_name='طلب بواسطة'
    )
    
    generated_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='تاريخ التوليد'
    )
    
    class Meta:
        verbose_name = 'سؤال ذكاء اصطناعي'
        verbose_name_plural = 'أسئلة الذكاء الاصطناعي'
        ordering = ['-generated_at']
    
    def __str__(self):
        return f"سؤال: {self.question_text[:50]}..."


# =============================================================================
# 10. نموذج الصلاحيات (Permission) - اختياري للتوسع
# =============================================================================

class RolePermission(models.Model):
    """
    صلاحيات الأدوار في النظام
    يمكن استخدامه للتحكم الدقيق في الصلاحيات
    """
    
    role = models.CharField(
        max_length=10,
        choices=User.Role.choices,
        unique=True,
        verbose_name='الدور'
    )
    
    can_upload_files = models.BooleanField(
        default=False,
        verbose_name='يمكنه رفع الملفات'
    )
    
    can_delete_files = models.BooleanField(
        default=False,
        verbose_name='يمكنه حذف الملفات'
    )
    
    can_manage_users = models.BooleanField(
        default=False,
        verbose_name='يمكنه إدارة المستخدمين'
    )
    
    can_manage_courses = models.BooleanField(
        default=False,
        verbose_name='يمكنه إدارة المقررات'
    )
    
    can_send_notifications = models.BooleanField(
        default=False,
        verbose_name='يمكنه إرسال الإشعارات'
    )
    
    can_view_reports = models.BooleanField(
        default=False,
        verbose_name='يمكنه عرض التقارير'
    )
    
    can_use_ai = models.BooleanField(
        default=False,
        verbose_name='يمكنه استخدام الذكاء الاصطناعي'
    )
    
    class Meta:
        verbose_name = 'صلاحية دور'
        verbose_name_plural = 'صلاحيات الأدوار'
    
    def __str__(self):
        return f"صلاحيات: {self.get_role_display()}"