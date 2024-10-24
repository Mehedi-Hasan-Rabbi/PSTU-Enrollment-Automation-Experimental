from django.db import models
from StudentApp.models import Student
from FacultyApp.models import Course, Semester, Faculty

# Create your models here.
class Course_Mark(models.Model):
    LETTER_GRADE_CHOICES = [
        ("A+", 'A+'),
        ("A", 'A'),
        ("A-", 'A-'),
        ("B+", 'B+'),
        ("B", 'B'),
        ("B-", 'B-'),
        ("C+", 'C+'),
        ("C", 'C'),
        ("D", 'D'),
        ("F", 'F'),
    ]
    
    course_id = models.ForeignKey(Course, on_delete=models.CASCADE, null=True)
    student_id = models.ForeignKey(Student, on_delete=models.CASCADE, null=True)
    attendance = models.DecimalField(max_digits=4, decimal_places=2, null=True)
    assignment = models.DecimalField(max_digits=4, decimal_places=2, null=True)
    mid_exam = models.DecimalField(max_digits=4, decimal_places=2, null=True)
    final_exam = models.DecimalField(max_digits=4, decimal_places=2, null=True)
    total = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    letter_grade = models.CharField(max_length=5, choices=LETTER_GRADE_CHOICES, default='F')
    grade_point = models.DecimalField(max_digits=3, decimal_places=2, default=0.0)
    

class Semester_Result(models.Model):
    REMARK_CHOICES = [
        ("Passed", 'Passed'),
        ("Failed", 'Failed'),
        ("Conditional Passed", 'Conditional Passed'),
    ]
    
    student_id = models.ForeignKey(Student, on_delete=models.CASCADE, null=True)
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE, null=True)
    gpa = models.DecimalField(max_digits = 4, decimal_places = 3, default=0.0)
    cgpa = models.DecimalField(max_digits = 4, decimal_places = 3, default=0.0)
    curr_sem_credit_earned = models.DecimalField(max_digits = 5, decimal_places = 2, default=0.0)
    cumulative_credit_earned = models.DecimalField(max_digits = 5, decimal_places = 2, default=0.0)
    remark = models.CharField(max_length=50, choices=REMARK_CHOICES, default="Failed")
    
    
class Exam_Period(models.Model):
    PERIOD_CHOICES = [
        ("Regular", 'Regular'),
        ("F-Removal", 'F-Removal')
    ]
    
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE, null=True)
    period = models.CharField(max_length=20, choices=PERIOD_CHOICES, default='Regular')
    
    
class Special_Repeat(models.Model):
    SPECIAL_REPEAT_CHOICES = [
        ("Enable", 'Enable'),
        ("Disable", 'Disable')
    ]
    
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE, null=True)
    special_period = models.CharField(max_length=20, choices=SPECIAL_REPEAT_CHOICES, default='Disable')