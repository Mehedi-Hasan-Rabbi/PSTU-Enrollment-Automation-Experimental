from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_control
from django.contrib.auth.models import User
from TeacherApp.models import Teacher, Course_Instructor
from ResultApp.models import Course_Mark
from StudentApp.models import Student
from FacultyApp.models import Course


# PDF Generation Libraries
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, A3, LETTER
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.pdfgen import canvas


def PDF (faculty, course_code):
    course = Course.objects.get(course_code=course_code)
    students = Student.objects.filter(faculty=faculty, curr_semester=course.semester, payment_status='Paid', graduation_status='Incomplete')

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