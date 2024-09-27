from django.contrib import admin
from .models import Student

# Register your models here.
@admin.register(Student)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ('user', 'student_id', 'faculty', 'curr_semester', 'cgpa')
    search_fields = ('user__username', 'student_id', 'faculty__faculty_name', 'semester__semester_number', 'cgpa')
    list_filter = ('faculty',)

