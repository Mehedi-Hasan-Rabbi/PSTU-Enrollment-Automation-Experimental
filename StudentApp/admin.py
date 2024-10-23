from django.contrib import admin
from .models import Student, Payment

# Register your models here.
@admin.register(Student)
class StudenAdmin(admin.ModelAdmin):
    list_display = ('user', 'student_id', 'faculty', 'curr_semester', 'payment_status')
    search_fields = ('user__username', 'student_id', 'faculty__faculty_name', 'semester__semester_number', 'payment_status')
    list_filter = ('faculty',)
    
    
@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('student_id', 'semester', 'payment')
    search_fields = ('student_id__student_id', 'semester__semester_number', 'payment')
    list_filter = ('payment', 'semester')
