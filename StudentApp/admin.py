from django.contrib import admin
from .models import Student, Student_Transaction

# Register your models here.
@admin.register(Student)
class StudenAdmin(admin.ModelAdmin):
    list_display = ('user', 'student_id', 'faculty', 'curr_semester', 'payment_status', 'academic_status', 'graduation_status')
    search_fields = ('user__username', 'student_id', 'faculty__faculty_name', 'semester__semester_number', 'payment_status', 'academic_status', 'graduation_status')
    list_filter = ('faculty',)
    
    
@admin.register(Student_Transaction)
class StudentTransactionAdmin(admin.ModelAdmin):
    list_display = ('student_id', 'semester', 'trxID', 'amount', 'created_at')  # Added created_at
    search_fields = ('student_id__student_id', 'semester__semester_number', 'trxID', 'amount', 'created_at')  # Added created_at
    list_filter = ('student_id', 'semester', 'created_at')  # Added created_at

    # Optional: To make the list filter more user-friendly, you can format the created_at field
    # date_hierarchy = 'created_at'  # This will add a date filter in the admin panel
