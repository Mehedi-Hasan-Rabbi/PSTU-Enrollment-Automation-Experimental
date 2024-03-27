from django.db import models

# Create your models here.
class Faculty(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Semester(models.Model):
    SEMESTER_CHOICES = [
        ('Semester 1', 'Semester 1'),
        ('Semester 2', 'Semester 2'),
        ('Semester 3', 'Semester 3'),
        ('Semester 4', 'Semester 4'),
        ('Semester 5', 'Semester 5'),
        ('Semester 6', 'Semester 6'),
        ('Semester 7', 'Semester 7'),
        ('Semester 8', 'Semester 8'),
        ('Semester 9', 'Semester 9'),
        ('Semester 10', 'Semester 10'),
        ('Semester 11', 'Semester 11'),
        ('Semester 12', 'Semester 12'),
        ('Semester 13', 'Semester 13'),
        ('Semester 14', 'Semester 14'),
        ('Semester 15', 'Semester 15'),
    ]
    name = models.CharField(max_length=20, choices=SEMESTER_CHOICES)

    def __str__(self):
        return self.name

class student(models.Model):

    student_id = models.IntegerField(unique = True, primary_key=True)
    reg_id = models.IntegerField(unique = True)
    first_name = models.CharField(max_length = 50)
    last_name = models.CharField(max_length = 50)
    email = models.EmailField(unique = True)
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE)
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE)
    password = models.CharField(max_length = 100)
    phone_number = models.CharField(max_length = 50, unique = True)
    img = models.ImageField(upload_to = 'pics')


class Course(models.Model):
    course_code = models.CharField(max_length=20, unique = True)
    course_title = models.CharField(max_length=100, unique = True)
    credit = models.PositiveIntegerField()
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE)
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.course_code} - {self.course_title}"
    
class Cost(models.Model):
    cost_per_credit = models.IntegerField(default=0)
    electricity = models.IntegerField(default=0)

    def __str__(self):
        return f"All Costs"