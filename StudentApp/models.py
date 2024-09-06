from django.db import models
from django.contrib.auth.models import User
from FacultyApp.models import Semester, Faculty

class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    student_id = models.IntegerField(unique=True)
    phone_number = models.CharField(max_length=20, unique=True, null=True)
    session = models.CharField(max_length=20, null=True)
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE, null=True)
    curr_semester = models.ForeignKey(Semester, on_delete=models.CASCADE, null=True)
    cgpa = models.DecimalField(max_digits = 4, decimal_places = 3, default=0.0)
    