from django.db import models
from django.contrib.auth.models import User
from FacultyApp.models import Semester, Faculty

class Student(models.Model):
    PAYMENT_CHOICES = [
        ("Paid", 'Paid'),
        ("Unpaid", 'Unpaid'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    student_id = models.IntegerField(unique=True)
    reg_no = models.IntegerField(unique=True, default=0)
    phone_number = models.CharField(max_length=20, unique=True, null=True)
    session = models.CharField(max_length=20, null=True)
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE, null=True)
    curr_semester = models.ForeignKey(Semester, on_delete=models.CASCADE, null=True)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_CHOICES, default='Paid')
    # cgpa = models.DecimalField(max_digits = 4, decimal_places = 3, default=0.0)
    profile_pic = models.ImageField(upload_to='students_profile_pics/')
    
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'student_id', 'faculty'], name='unique_student')
        ]
    
    
class Payment(models.Model):
    PAYMENT_CHOICES = [
        ("Paid", 'Paid'),
        ("Unpaid", 'Unpaid'),
    ]
    
    student_id = models.ForeignKey(Student, on_delete=models.CASCADE, null=True)
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE, null=True)
    payment = models.CharField(max_length=50, choices=PAYMENT_CHOICES, default="Paid")
    
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['student_id', 'semester', 'payment'], name='unique_payment')
        ]