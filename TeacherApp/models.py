from django.db import models
from django.contrib.auth.models import User
from FacultyApp.models import Faculty, Course, Department

class Teacher(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE, null=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, null=True)
    phone_number = models.CharField(max_length=20, unique=True, null=True)    
    profile_pic = models.ImageField(upload_to='teachers_profile_pics/')
    
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'faculty', 'department'], name='unique_teacher')
        ]
    
    
class Course_Instructor(models.Model):
    teacher_id = models.ForeignKey(Teacher, on_delete=models.CASCADE, null=True)
    courseinfo = models.ForeignKey(Course, on_delete=models.CASCADE, null=True)
    
    