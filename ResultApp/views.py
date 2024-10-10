from django.shortcuts import render
from decimal import Decimal
from django.db.models import Sum, F

from StudentApp.models import Student
from ResultApp.models import Course_Mark, Semester_Result
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
    
    
def calculate_gpa(student, semester):
    # Get all courses for the given semester
    courses = Course.objects.filter(semester=semester, faculty_name=student.faculty)
    
    total_credit_hours = Decimal(0)
    total_grade_points = Decimal(0)
    student_marks = {}
    
    for course in courses:
        # Get course marks for this student and course
        course_mark = Course_Mark.objects.filter(student_id=student, course_id=course).first()

        if course_mark and course_mark.total:
            numerical_marks = course_mark.total
            grade_point = calculate_grade_point(numerical_marks)
            credit_hour = course.credit_hour

            # Multiply grade_point with credit_hour
            total_grade_points += Decimal(grade_point) * credit_hour
            total_credit_hours += credit_hour
            
            student_marks[course.course_code] = {
                'numerical_marks': numerical_marks,
                'grade_point': grade_point
            }
        else:
            # student_marks[course.course_code] = 'N/A'
            student_marks[course.course_code] = {
                'numerical_marks': 0.0,
                'grade_point': 0.0
            }
    
    # Calculate GPA
    if total_credit_hours > 0:
        gpa = total_grade_points / total_credit_hours
    else:
        gpa = Decimal(0.00)

    return round(gpa, 3), total_credit_hours, student_marks  # Return GPA and total credit hours earned in the semester



def calculate_cgpa(student, current_semester, current_gpa, current_credits):
    # Get previous semester results, excluding the current one
    previous_results = Semester_Result.objects.filter(student_id=student).exclude(semester=current_semester)
    
    # If there are no previous results, this is the first semester
    if not previous_results.exists():
        return current_gpa, current_credits  # CGPA = GPA for the first semester, and cumulative credits are current credits

    # Calculate cumulative credit hours and weighted GPA for previous semesters
    cumulative_credits = previous_results.aggregate(total=Sum('curr_sem_credit_earned'))['total'] or Decimal(0)
    weighted_gpa_sum = previous_results.aggregate(weighted_sum=Sum(F('gpa') * F('curr_sem_credit_earned')))['weighted_sum'] or Decimal(0)

    # Add current semester's GPA and credits to the cumulative totals
    cumulative_credits += current_credits
    weighted_gpa_sum += current_gpa * current_credits

    # Calculate CGPA
    if cumulative_credits > 0:
        cgpa = weighted_gpa_sum / cumulative_credits
    else:
        cgpa = Decimal(0.00)
    
    return round(cgpa, 3), cumulative_credits  # Return CGPA and cumulative credit hours



def get_student_mark(faculty, semester):
    students = Student.objects.filter(faculty=faculty, curr_semester=semester).order_by("student_id")
    course_codes = Course.objects.filter(semester=semester, faculty_name=faculty)

    results = []
    
    for student in students:
        # Calculate GPA for the current semester
        gpa, current_credits, student_marks = calculate_gpa(student, semester)
        
        # Calculate CGPA, considering previous semesters (or set CGPA = GPA for the first semester)
        cgpa, cumulative_credits = calculate_cgpa(student, semester, gpa, current_credits)

        # Save the result in Semester_Result model
        Semester_Result.objects.update_or_create(
            student_id=student,
            semester=semester,
            defaults={
                'gpa': gpa,
                'cgpa': cgpa,  # For first semester, CGPA = GPA
                'curr_sem_credit_earned': current_credits,
                'cumulative_credit_earned': cumulative_credits,
                'remark': 'Passed' if gpa >= 2.00 else 'Failed'
            }
        )
        
        # Prepare the results for the context
        results.append({
            'student_id': student.student_id,
            'marks': student_marks,
            'gpa': gpa,
            'cgpa': cgpa
        })

    context = {
        'semester': semester,
        'course_codes': course_codes,
        'results': results
    }
    
    return context


