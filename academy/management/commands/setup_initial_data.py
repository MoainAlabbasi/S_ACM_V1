"""
أمر لإنشاء البيانات الأولية
"""

from django.core.management.base import BaseCommand
from academy.models import Department, Specialization, RolePermission, User


class Command(BaseCommand):
    help = 'إنشاء البيانات الأولية للنظام'
    
    def handle(self, *args, **options):
        self.stdout.write('جاري إنشاء البيانات الأولية...')
        
        # إنشاء الأقسام
        departments_data = [
            {'name': 'قسم تقنية المعلومات', 'description': 'قسم تقنية المعلومات'},
            {'name': 'قسم علوم الحاسب', 'description': 'قسم علوم الحاسب'},
            {'name': 'قسم نظم المعلومات', 'description': 'قسم نظم المعلومات'},
        ]
        
        for dept_data in departments_data:
            dept, created = Department.objects.get_or_create(
                name=dept_data['name'],
                defaults={'description': dept_data['description']}
            )
            if created:
                self.stdout.write(f'  ✓ تم إنشاء القسم: {dept.name}')
        
        # إنشاء التخصصات
        it_dept = Department.objects.get(name='قسم تقنية المعلومات')
        specializations_data = [
            {'name': 'شبكات الحاسب', 'department': it_dept},
            {'name': 'تطوير البرمجيات', 'department': it_dept},
            {'name': 'قواعد البيانات', 'department': it_dept},
        ]
        
        for spec_data in specializations_data:
            spec, created = Specialization.objects.get_or_create(
                name=spec_data['name'],
                department=spec_data['department']
            )
            if created:
                self.stdout.write(f'  ✓ تم إنشاء التخصص: {spec.name}')
        
        # إنشاء صلاحيات الأدوار
        permissions_data = [
            {
                'role': 'student',
                'can_upload_files': False,
                'can_delete_files': False,
                'can_manage_users': False,
                'can_manage_courses': False,
                'can_send_notifications': False,
                'can_view_reports': False,
                'can_use_ai': True,
            },
            {
                'role': 'teacher',
                'can_upload_files': True,
                'can_delete_files': True,
                'can_manage_users': False,
                'can_manage_courses': False,
                'can_send_notifications': True,
                'can_view_reports': True,
                'can_use_ai': True,
            },
            {
                'role': 'admin',
                'can_upload_files': True,
                'can_delete_files': True,
                'can_manage_users': True,
                'can_manage_courses': True,
                'can_send_notifications': True,
                'can_view_reports': True,
                'can_use_ai': True,
            },
        ]
        
        for perm_data in permissions_data:
            perm, created = RolePermission.objects.get_or_create(
                role=perm_data['role'],
                defaults=perm_data
            )
            if created:
                self.stdout.write(f'  ✓ تم إنشاء صلاحيات: {perm.role}')
        
        self.stdout.write(self.style.SUCCESS('\n✅ تم إنشاء البيانات الأولية بنجاح!'))