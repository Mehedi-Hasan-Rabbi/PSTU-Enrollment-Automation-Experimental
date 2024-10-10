from django.db import models
from StudentApp.models import Student
from FacultyApp.models import Course, Semester

# Create your models here.
class Course_Mark(models.Model):
    course_id = models.ForeignKey(Course, on_delete=models.CASCADE, null=True)
    student_id = models.ForeignKey(Student, on_delete=models.CASCADE, null=True)
    attendance = models.DecimalField(max_digits=4, decimal_places=2, null=True)
    assignment = models.DecimalField(max_digits=4, decimal_places=2, null=True)
    mid_exam = models.DecimalField(max_digits=4, decimal_places=2, null=True)
    final_exam = models.DecimalField(max_digits=4, decimal_places=2, null=True)
    total = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    

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