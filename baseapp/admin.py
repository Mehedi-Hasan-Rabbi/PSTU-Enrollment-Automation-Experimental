from django.contrib import admin
from baseapp.models import student, Semester, Course, Faculty, Cost


class StudentAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'student_id', 'faculty', 'semester')
    search_fields = ('first_name', 'last_name', 'student_id', 'faculty', 'semester')

# Register your models here.
admin.site.register(student, StudentAdmin)
admin.site.register(Faculty)
admin.site.register(Semester)
admin.site.register(Course)
admin.site.register(Cost)