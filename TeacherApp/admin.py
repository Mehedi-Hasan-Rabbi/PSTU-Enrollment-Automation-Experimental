from django.contrib import admin
from .models import Teacher, Course_Instructor

# Register your models here.
@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ('user', 'faculty')
    search_fields = ('user__username', 'faculty__faculty_name')
    list_filter = ('faculty',)
    
    # Display raw ID fields for better performance with related models
    raw_id_fields = ('user', 'faculty')

@admin.register(Course_Instructor)
class CourseInstructorAdmin(admin.ModelAdmin):
    list_display = ('get_teacher_first_name', 'get_teacher_last_name', 'courseinfo') # Display the teacher's first name, last name, and course title
    search_fields = ('teacher_id__user__first_name', 'teacher_id__user__last_name', 'courseinfo__course_title') # Allow searching by teacher's first name, last name, and course title
    list_filter = ('teacher_id', 'courseinfo') # Add filtering options for teachers and courses
    raw_id_fields = ('teacher_id', 'courseinfo') # Display raw ID fields for foreign keys to enhance performance
    
    # Custom method to display teacher's first name
    def get_teacher_first_name(self, obj):
        return obj.teacher_id.user.first_name
    get_teacher_first_name.short_description = 'First Name'
    
    # Custom method to display teacher's last name
    def get_teacher_last_name(self, obj):
        return obj.teacher_id.user.last_name
    get_teacher_last_name.short_description = 'Last Name'