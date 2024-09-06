from django.db import models
from django.contrib.auth.models import User, AbstractBaseUser, PermissionsMixin

# Create your models here.
class semester(models.Model):
    SEMESTER_CHOICES = [
        (1, 'Semester 1'),
        (2, 'Semester 2'),
        (3, 'Semester 3'),
        (4, 'Semester 4'),
        (5, 'Semester 5'),
        (6, 'Semester 6'),
        (7, 'Semester 7'),
        (8, 'Semester 8'),
        (9, 'Semester 9'),
        (10, 'Semester 10'),
        (11, 'Semester 11'),
        (12, 'Semester 12'),
        (12, 'Semester 13'),
        (14, 'Semester 14'),
        (15, 'Semester 15'),
    ]
    semester_number = models.IntegerField(choices=SEMESTER_CHOICES, unique=True)

class CSEStudents(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    student_id = models.IntegerField(unique=True, primary_key=True)
    semester = models.ForeignKey(semester, on_delete=models.CASCADE)
