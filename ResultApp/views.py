from django.shortcuts import render
from decimal import Decimal
from StudentApp.models import Student
from ResultApp.models import Course_Mark
from FacultyApp.models import Course


# Helper function to convert marks to grade point based on the given criteria
def calculate_grade_point(marks):
    if marks >= 80:
        return 4.00
    elif marks >= 75:
        return 3.75
    elif marks >= 70:
        return 3.50
    elif marks >= 65:
        return 3.25
    elif marks >= 60:
        return 3.00
    elif marks >= 55:
        return 2.75
    elif marks >= 50:
        return 2.50
    elif marks >= 45:
        return 2.25
    elif marks >= 40:
        return 2.00
    else:
        return 0.00  # F grade


def get_student_mark(faculty, semester):
    # Get all students in this faculty and semester
    students = Student.objects.filter(faculty=faculty, curr_semester=semester).order_by("student_id")

    # Get all courses for this semester and faculty
    course_codes = Course.objects.filter(semester=semester, faculty_name=faculty)

    results = []
    
    # Prepare a list of dictionaries for each student
    for student in students:
        student_marks = {}
        total_credit_hours = Decimal(0)  # Keep total credit hours
        total_grade_points = Decimal(0)  # Keep total grade points
        
        for course in course_codes:
            course_mark = Course_Mark.objects.filter(student_id=student, course_id=course).first()
            
            if course_mark:
                numerical_marks = course_mark.total
                grade_point = calculate_grade_point(numerical_marks)  # Your function to calculate grade point
                credit_hour = course.credit_hour
                
                # Multiply grade_point with credit_hour, convert grade_point to Decimal
                total_grade_points += Decimal(grade_point) * credit_hour
                total_credit_hours += credit_hour

                student_marks[course.course_code] = {
                    'numerical_marks': numerical_marks,
                    'grade_point': grade_point
                }
            else:
                student_marks[course.course_code] = 'N/A'

        # Calculate GPA for the student
        if total_credit_hours > 0:
            gpa = total_grade_points / total_credit_hours
        else:
            gpa = 0
        
        results.append({
            'student_id': student.student_id,
            'marks': student_marks,
            'gpa': round(gpa, 3)  # rounding the GPA to 2 decimal places
        })
    
    context = {
        'semester': semester,
        'course_codes': course_codes,
        'results': results
    }
    
    return context
