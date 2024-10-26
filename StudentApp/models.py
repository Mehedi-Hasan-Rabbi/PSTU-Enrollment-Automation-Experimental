from django.utils import timezone
from django.db import models
from django.contrib.auth.models import User
from FacultyApp.models import Semester, Faculty

class Student(models.Model):
    PAYMENT_CHOICES = [
        ("Paid", 'Paid'),
        ("Unpaid", 'Unpaid'),
    ]
    ACADEMIC_STATUS_CHOICES = [
        ("Regular", 'Regular'),
        ("Irregular", 'Irregular'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    student_id = models.IntegerField(unique=True)
    reg_no = models.IntegerField(unique=True, default=0)
    phone_number = models.CharField(max_length=20, unique=True, null=True)
    session = models.CharField(max_length=20, null=True)
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE, null=True)
    curr_semester = models.ForeignKey(Semester, on_delete=models.CASCADE, null=True)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_CHOICES, default='Paid')
    academic_status = models.CharField(max_length=20, choices=ACADEMIC_STATUS_CHOICES, default='Regular')
    profile_pic = models.ImageField(upload_to='students_profile_pics/')
    
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'student_id', 'faculty'], name='unique_student')
        ]
    
    
class Student_Transaction(models.Model):    
    student_id = models.ForeignKey(Student, on_delete=models.CASCADE, null=True)
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE, null=True)
    trxID = models.CharField(max_length=50)
    amount = models.DecimalField(max_digits = 10, decimal_places = 2, default=0.0)
    created_at = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return f"{self.trxID} - {self.amount} - {self.created_at.strftime('%Y-%m-%d %H:%M:%S')}"
    