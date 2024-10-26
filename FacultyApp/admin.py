from django.contrib import admin
from .models import Faculty, Semester, Course, Department, FacultyController, Cost

# Register your models here.
# admin.site.register(Faculty)
# admin.site.register(Semester)
# admin.site.register(Course)

@admin.register(Faculty)
class FacultyAdmin(admin.ModelAdmin):
    list_display = ('faculty_name', 'number_of_semseter') # Display these fields in the admin list view
    search_fields = ('faculty_name',) # Enable search by faculty_name
    list_filter = ('number_of_semseter',) # Enable filtering by number_of_semseter
    
@admin.register(FacultyController)
class FacultyControllerAdmin(admin.ModelAdmin):
    list_display = ('user', 'faculty')
    search_fields = ('user__username', 'faculty__faculty_name')
    list_filter = ('faculty',)

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
    list_display = ('course_code', 'course_title', 'semester', 'faculty_name')
    search_fields = ('course_code', 'course_title', 'semester', 'faculty_name')
    list_filter = ('course_code',)

@admin.register(Cost)
class CostAdmin(admin.ModelAdmin):
    list_display = ('admission_fee', 'enrollment_fee', 'cost_per_credit', 'electricity')
    list_display_links = ('admission_fee',)  # This makes 'admission_fee' clickable to view the detail page
    list_editable = ('enrollment_fee', 'cost_per_credit', 'electricity')
    search_fields = ('admission_fee', 'enrollment_fee', 'cost_per_credit', 'electricity')