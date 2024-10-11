from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_control
from django.contrib import messages
from django.http import HttpResponse

# PDF Generation Libraries
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, A3, LETTER
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.pdfgen import canvas

from TeacherApp.models import Teacher, Course_Instructor
from ResultApp.models import Course_Mark
from StudentApp.models import Student
from FacultyApp.models import Course

# Create your views here.
@cache_control(no_store=True, no_cache=True, must_revalidate=True)
def teacher_login(request):
    if request.user.is_authenticated:
        if Teacher.objects.filter(user=request.user).exists():
            return redirect('TeacherApp:teacher_dashboard')
        else:
            messages.error(request, 'You do not have the required permissions to access this page.')
            return redirect('FacultyApp:index')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Authenticate the user
        user = authenticate(request, username=username, password=password)

        if user is not None:
            try:
                teacher = Teacher.objects.get(user=user)
                login(request, user)
                return redirect('TeacherApp:teacher_dashboard')
            except Teacher.DoesNotExist:
                messages.error(request, 'You do not have the required permissions to log in.')
        else:
            messages.error(request, 'Invalid username or password')

    # Add cache control headers to prevent caching of the login page
    response = render(request, 'teacher_login.html')
    response['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response['Pragma'] = 'no-cache'  # HTTP 1.0
    response['Expires'] = '0'  # Proxies

    return response


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def teacher_logout(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')  # Optional success message

    # Clear Cache on Logout
    response = redirect('TeacherApp:teacher_login')
    response['Cache-Control'] = 'no-cache, no-store, must-revalidate'  # HTTP 1.1
    response['Pragma'] = 'no-cache'  # HTTP 1.0
    response['Expires'] = '0'  # Proxies

    return response


@login_required(login_url='TeacherApp:teacher_login')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def teacher_dashboard(request):
    # Create response object with the rendered template
    response = render(request, 'teacher_dashboard.html', {'user': request.user})
    
    # Add cache control headers to prevent caching
    response['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response['Pragma'] = 'no-cache'  # HTTP 1.0
    response['Expires'] = '0'  # Proxies
    
    return response


@login_required(login_url='TeacherApp:teacher_login')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def myCourses(request):
    teacher = request.user.teacher  # Assuming the user has a one-to-one relation with Teacher
    assigned_courses = Course_Instructor.objects.filter(teacher_id=teacher).select_related('courseinfo')

    context = {
        'assigned_courses': assigned_courses,
        'teacher_name': teacher.user.get_full_name(),
    }

    # Add cache control headers to prevent caching
    response = render(request, 'myCourses.html', context)
    response['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response['Pragma'] = 'no-cache'  # HTTP 1.0 backward compatibility
    response['Expires'] = '0'  # Proxies

    return response



def calculate_grade_point(marks):
    if marks >= 80:
        return [4.00, 'A+']
    elif marks >= 75:
        return [3.75, 'A']
    elif marks >= 70:
        return [3.50, 'A-']
    elif marks >= 65:
        return [3.25, 'B+']
    elif marks >= 60:
        return [3.00, 'B']
    elif marks >= 55:
        return [2.75, 'B-']
    elif marks >= 50:
        return [2.50, 'C+']
    elif marks >= 45:
        return [2.25, 'C']
    elif marks >= 40:
        return [2.00, 'D']
    else:
        return [0.00, 'F']  # F grade
    

@login_required(login_url='TeacherApp:teacher_login')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def enter_marks(request, course_code):
    try:
        teacher = Teacher.objects.get(user=request.user)
        course = Course.objects.get(course_code=course_code)

        # Ensure the teacher is assigned to this course
        if not Course_Instructor.objects.filter(teacher_id=teacher, courseinfo=course).exists():
            messages.error(request, "You are not assigned to this course.")
            return redirect('TeacherApp:myCourses')

        # Get all students enrolled in this course and same faculty
        students = Student.objects.filter(faculty=teacher.faculty, curr_semester=course.semester).order_by('student_id')

        # Fetch existing marks for the course and students
        existing_marks = {
            mark.student_id.id: {
                'attendance': mark.attendance,
                'assignment': mark.assignment,
                'mid_exam': mark.mid_exam,
                'final_exam': mark.final_exam,
                'total': mark.total,
                'letter_grade': mark.letter_grade,
                'grade_point': mark.grade_point,

            }
            for mark in Course_Mark.objects.filter(course_id=course, student_id__in=students)
        }

        # Ensure existing_marks is not None and default to an empty dict
        existing_marks = existing_marks if existing_marks else {}

        if request.method == 'POST':
            # Process the marks entry form
            for student in students:
                attendance = float(request.POST.get(f'attendance_{student.id}', 0))
                assignment = float(request.POST.get(f'assignment_{student.id}', 0))
                mid_exam = float(request.POST.get(f'mid_exam_{student.id}', 0))
                final_exam = float(request.POST.get(f'final_exam_{student.id}', 0))

                # Server-side validation
                if attendance > 10 or attendance < 7 or assignment > 5 or mid_exam > 15 or final_exam > 70:
                    messages.error(request, f"Invalid marks for {student.student_id}: "
                                            f"Attendance must be between 7-10, Assignment <= 5, "
                                            f"Mid Exam <= 15, Final Exam <= 70.")
                    return redirect('TeacherApp:enter_marks', course_code=course_code)

                total = attendance + assignment + mid_exam + final_exam
                
                grade_point, letter_grade = calculate_grade_point(total)
                
                # Create or update the student's marks
                Course_Mark.objects.update_or_create(
                    student_id=student,
                    course_id=course,
                    defaults={
                        'attendance': attendance,
                        'assignment': assignment,
                        'mid_exam': mid_exam,
                        'final_exam': final_exam,
                        'total': total,
                        'letter_grade' : letter_grade,
                        'grade_point' : grade_point
                    }
                )

            messages.success(request, "Marks entered successfully!")
            return redirect('TeacherApp:enter_marks', course_code=course_code)

        context = {
            'course': course,
            'students': students,
            'existing_marks': existing_marks,  # Always pass a dictionary to avoid None errors
        }
        response = render(request, 'enter_marks.html', context)
        response['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
        response['Pragma'] = 'no-cache'
        response['Expires'] = '0'

        return response

    except Teacher.DoesNotExist:
        messages.error(request, "You are not authorized to enter marks.")
        return redirect('TeacherApp:teacher_login')

    except Course.DoesNotExist:
        messages.error(request, "Course not found.")
        return redirect('TeacherApp:myCourses')

    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")
        return redirect('TeacherApp:myCourses')


@login_required(login_url='TeacherApp:teacher_login')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def generate_pdf(request, course_code):
    try:
        course = Course.objects.get(course_code=course_code)
        students = Student.objects.filter(curr_semester=course.semester)

        # Set up the HttpResponse with appropriate PDF headers
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{course.course_code}_marks.pdf"'

        # Create the PDF document object using ReportLab (Portrait A4 paper size)
        # doc = SimpleDocTemplate(response, pagesize=landscape(A4))
        doc = SimpleDocTemplate(response, pagesize=A4)
        elements = []

        # Title and course information
        styles = getSampleStyleSheet()
        elements.append(Paragraph(f"Marks Report for {course.course_title} ({course.course_code})", styles['Title']))

        # Create table data
        # data = [["Student ID", "Name", "Attendance", "Assignment", "Mid Exam", "Final Exam", "Total", "Letter Grade", "Grade Point"]]
        data = [["Student ID", "Name", "Attendance", "Assignment", "Mid", "Final", "Total", "Letter Grade", "Grade Point"]]

        # Fetch marks and add to table
        for student in students:
            mark = Course_Mark.objects.filter(course_id=course, student_id=student).first()
            if mark:
                # Add each student's data as a new row in the table
                data.append([
                    str(student.student_id),   # Convert student ID to string
                    f"{student.user.first_name} {student.user.last_name}",   # Student full name
                    str(mark.attendance),      # Attendance
                    str(mark.assignment),      # Assignment
                    str(mark.mid_exam),        # Mid Exam
                    str(mark.final_exam),      # Final Exam
                    str(mark.total),           # Total
                    mark.letter_grade,         # Letter Grade
                    str(mark.grade_point)      # Grade Point
                ])

        # Create a table object
        # table = Table(data)
        table = Table(data, colWidths=[60, 100, 60, 60, 50, 50, 50, 65, 65])  # Define column widths for better fit

        # Style the table
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),  # Header background color
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),  # Header text color
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),  # Align text to the center
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),  # Header font
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),  # Header padding
            ('GRID', (0, 0), (-1, -1), 1, colors.black),  # Add grid lines (borders)
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),  # Data rows background color
        ]))

        # Add table to the elements list
        elements.append(table)

        # Build the PDF with all the elements
        doc.build(elements)

        return response

    except Course.DoesNotExist:
        return HttpResponse("Course not found.", status=404)
