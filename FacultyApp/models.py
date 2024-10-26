from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Faculty(models.Model):
    faculty_name = models.CharField(max_length=100, unique=True)
    number_of_semseter = models.IntegerField()

    def __str__(self):
        return f'{self.faculty_name}'
        # I am using Class to view fields in admin panel writen in admin.py
        # if i don't use class in admin.py then def __str__(self): return f'{self.faculty_name}' this will work
        # and also when i use this field as ForeignKey to others then this fields will show
        

class FacultyController(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE)
    
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'faculty'], name='unique_faculty_admin')
        ]


class Semester(models.Model):
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
        (13, 'Semester 13'),
        (14, 'Semester 14'),
        (15, 'Semester 15'),
    ]
    semester_number = models.IntegerField(choices=SEMESTER_CHOICES, default=1, primary_key=True)
       
    def __str__(self):
        return f'{self.semester_number}'


class Department(models.Model):
    dept_name = models.CharField(max_length=255, unique=True)
    faculty_name = models.ForeignKey(Faculty, on_delete=models.CASCADE, null=True)
    
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['dept_name', 'faculty_name'], name='unique_faculty_dept')
        ]
    
    def __str__(self):
        return f'{self.dept_name}'

class Course(models.Model):
    course_code = models.CharField(max_length=20, primary_key=True)
    course_title = models.CharField(max_length=255)
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE, null=True)
    faculty_name = models.ForeignKey(Faculty, on_delete=models.CASCADE, null=True)
    credit_hour = models.DecimalField(max_digits = 3, decimal_places = 2, default=0.0)
    
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['course_code', 'semester', 'faculty_name'], name='unique_course_code_semester')
        ]
    
    def __str__(self):
        return f'{self.course_code}'
    
    
class Cost(models.Model):
    admission_fee = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    enrollment_fee = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    cost_per_credit = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    electricity = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)

    def __str__(self):
        return f"Cost Details: Admission Fee - {self.admission_fee}, Enrollment Fee - {self.enrollment_fee}, " \
               f"Cost per Credit - {self.cost_per_credit}, Electricity - {self.electricity}"