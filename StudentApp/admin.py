from django.contrib import admin
from .models import Student

# Register your models here.
@admin.register(Student)
class StudenAdmin(admin.ModelAdmin):
    list_display = ('user', 'student_id', 'faculty', 'curr_semester')
    search_fields = ('user__username', 'student_id', 'faculty__faculty_name', 'semester__semester_number')
    list_filter = ('faculty',)

