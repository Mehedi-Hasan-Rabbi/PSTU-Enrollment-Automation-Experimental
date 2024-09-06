from django.contrib import admin
from .models import Faculty, Semester, Course, AssignCourse, Department

# Register your models here.
# admin.site.register(Faculty)
# admin.site.register(Semester)
# admin.site.register(Course)
# admin.site.register(AssignCourse)

@admin.register(Faculty)
class FacultyAdmin(admin.ModelAdmin):
    list_display = ('faculty_name', 'number_of_semseter') # Display these fields in the admin list view
    search_fields = ('faculty_name',) # Enable search by faculty_name
    list_filter = ('number_of_semseter',) # Enable filtering by number_of_semseter

@admin.register(Semester)
class SemesterAdmin(admin.ModelAdmin):
    list_display = ('semester_number',)
    search_fields = ('semester_number',)
    list_filter = ('semester_number',)
    
@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('dept_name', 'faculty_name')
    search_fields = ('dept_name', 'faculty_name')
    list_filter = ('dept_name', 'faculty_name')

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('course_code', 'course_title')
    search_fields = ('course_code', 'course_title')
    list_filter = ('course_code',)

@admin.register(AssignCourse)
class AssignCourseAdmin(admin.ModelAdmin):
    list_display = ('faculty_name', 'semester_number', 'course')
    search_fields = ('faculty_name__faculty_name', 'semester_number__semester_number', 'course__course_code')
    list_filter = ('faculty_name', 'semester_number', 'course')
