from django.db import models
from django.contrib.auth.models import User
from FacultyApp.models import Faculty, Course

class Teacher(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    faculty = models.OneToOneField(Faculty, on_delete=models.CASCADE, null=True)
    
    
class Course_Instructor(models.Model):
    teacher_id = models.ForeignKey(Teacher, on_delete=models.CASCADE, null=True)
    courseinfo = models.ForeignKey(Course, on_delete=models.CASCADE, null=True)
    