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
    ]
    name = models.CharField(max_length=20, choices=SEMESTER_CHOICES)

    def __str__(self):
        return self.name

class student(models.Model):
    # FACULTY = (
    #     ('AG', 'Agricalture'),
    #     ('CSE', 'Computer Science and Engineering'),
    #     ('FBA', 'Business Administation'),
    # )
    # # SEMESTER = (
    # #     ('1', 'First'),
    # #     ('2', 'Second'),
    # #     ('3', 'Third'),
    # #     ('4', 'Fourth'),
    # #     ('5', 'Fifth'),
    # #     ('6', 'Sixth'),
    # #     ('7', 'Seventh'),
    # #     ('8', 'Eighth'),
    # # )

    student_id = models.IntegerField(unique = True, primary_key=True)
    reg_id = models.IntegerField(unique = True)
    first_name = models.CharField(max_length = 50)
    last_name = models.CharField(max_length = 50)
    email = models.EmailField(unique = True)
    # faculty = models.CharField(max_length = 50, choices = FACULTY)
    # semester = models.CharField(Semester, max_length = 10, choices = SEMESTER)
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE)
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE)
    password = models.CharField(max_length = 100)
    phone_number = models.CharField(max_length = 50, unique = True)
    img = models.ImageField(upload_to = 'pics')


class Course(models.Model):
    course_code = models.CharField(max_length=20)
    course_title = models.CharField(max_length=100)
    credit = models.PositiveIntegerField()
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE)
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.course_code} - {self.course_title}"