"""
نماذج الإدخال (Forms) لنظام S-ACM
==================================
"""

from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.core.exceptions import ValidationError
from .models import User, Department, Specialization


class LoginForm(AuthenticationForm):
    """نموذج تسجيل الدخول"""
    
    username = forms.CharField(
        label='اسم المستخدم',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'أدخل اسم المستخدم',
            'autofocus': True
        })
    )
    
    password = forms.CharField(
        label='كلمة المرور',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'أدخل كلمة المرور'
        })
    )
    
    remember_me = forms.BooleanField(
        required=False,
        label='تذكرني',
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )


class StudentRegistrationForm(UserCreationForm):
    """نموذج تسجيل طالب جديد"""
    
    class Meta:
        model = User
        fields = [
            'username', 'email', 'first_name', 'last_name',
            'academic_id', 'phone', 'department', 'specialization',
            'level', 'password1', 'password2'
        ]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # تخصيص الحقول
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'اسم المستخدم'
        })
        self.fields['email'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'البريد الإلكتروني'
        })
        self.fields['first_name'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'الاسم الأول'
        })
        self.fields['last_name'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'اسم العائلة'
        })
        self.fields['academic_id'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'الرقم الأكاديمي'
        })
        self.fields['phone'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'رقم الهاتف'
        })
        self.fields['department'].widget.attrs.update({
            'class': 'form-select'
        })
        self.fields['specialization'].widget.attrs.update({
            'class': 'form-select'
        })
        self.fields['level'].widget.attrs.update({
            'class': 'form-select'
        })
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'كلمة المرور'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'تأكيد كلمة المرور'
        })
        
        # تسميات عربية
        self.fields['username'].label = 'اسم المستخدم'
        self.fields['email'].label = 'البريد الإلكتروني'
        self.fields['first_name'].label = 'الاسم الأول'
        self.fields['last_name'].label = 'اسم العائلة'
        self.fields['academic_id'].label = 'الرقم الأكاديمي'
        self.fields['phone'].label = 'رقم الهاتف'
        self.fields['department'].label = 'القسم'
        self.fields['specialization'].label = 'التخصص'
        self.fields['level'].label = 'المستوى الدراسي'
        self.fields['password1'].label = 'كلمة المرور'
        self.fields['password2'].label = 'تأكيد كلمة المرور'
        
        # حقول مطلوبة
        self.fields['email'].required = True
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
        self.fields['academic_id'].required = True
        self.fields['level'].required = True
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = User.Role.STUDENT
        if commit:
            user.save()
        return user


class TeacherRegistrationForm(UserCreationForm):
    """نموذج تسجيل مدرس جديد (يستخدمه المسؤول)"""
    
    class Meta:
        model = User
        fields = [
            'username', 'email', 'first_name', 'last_name',
            'academic_id', 'phone', 'department',
            'password1', 'password2'
        ]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})
        
        self.fields['department'].widget.attrs.update({'class': 'form-select'})
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = User.Role.TEACHER
        if commit:
            user.save()
        return user


class UserProfileForm(forms.ModelForm):
    """نموذج تعديل الملف الشخصي"""
    
    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'email',
            'phone', 'profile_image'
        ]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        for field_name, field in self.fields.items():
            if field_name == 'profile_image':
                field.widget.attrs.update({'class': 'form-control'})
            else:
                field.widget.attrs.update({'class': 'form-control'})


class ChangePasswordForm(forms.Form):
    """نموذج تغيير كلمة المرور"""
    
    old_password = forms.CharField(
        label='كلمة المرور الحالية',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'كلمة المرور الحالية'
        })
    )
    
    new_password1 = forms.CharField(
        label='كلمة المرور الجديدة',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'كلمة المرور الجديدة'
        })
    )
    
    new_password2 = forms.CharField(
        label='تأكيد كلمة المرور الجديدة',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'تأكيد كلمة المرور الجديدة'
        })
    )
    
    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('new_password1')
        password2 = cleaned_data.get('new_password2')
        
        if password1 and password2 and password1 != password2:
            raise ValidationError('كلمتا المرور غير متطابقتين')
        
        return cleaned_data