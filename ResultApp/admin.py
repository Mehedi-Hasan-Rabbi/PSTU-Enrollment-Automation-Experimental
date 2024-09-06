from django.contrib import admin
from .models import Course_Mark, Semester_Result

@admin.register(Course_Mark)
class CourseMarkAdmin(admin.ModelAdmin):
    list_display = ('course_id', 'student_id', 'attendance', 'assignment', 'mid_exam', 'final_exam', 'total')
    search_fields = ('course_id__course_title', 'student_id__user__username')
    list_filter = ('course_id', 'student_id')

@admin.register(Semester_Result)
class SemesterResultAdmin(admin.ModelAdmin):
    list_display = ('student_id', 'semester', 'gpa', 'cgpa')
    search_fields = ('student_id__user__username', 'semester__semester_number')
    list_filter = ('semester', 'student_id')