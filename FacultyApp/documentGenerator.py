from .models import FacultyController, Semester, Course, Faculty, Department
from TeacherApp.models import Teacher, Course_Instructor
from StudentApp.models import Student
from ResultApp.views import get_student_mark

from django.http import HttpResponse
from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from StudentApp.models import Student
from ResultApp.models import Semester_Result
from reportlab.lib.units import inch


def PDF(faculty, semester_number):
    students = Student.objects.filter(faculty=faculty, curr_semester=semester_number)

    # Set up the HttpResponse with appropriate PDF headers
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Student_Report_Semester_{semester_number}_{faculty}.pdf"'

    # Create the PDF document object using ReportLab
    # doc = SimpleDocTemplate(response, pagesize=A4)
    doc = SimpleDocTemplate(response, pagesize=landscape(A4))
    elements = []

    # Title and semester information
    styles = getSampleStyleSheet()
    elements.append(Paragraph(f"Student Report for Semester {semester_number} ({faculty})", styles['Title']))

    # Create table data (headers)
    data = [["SL No.", "Student ID", "Name", "Regi", "PCGPA", "PCCH", "GPA", "CGPA", "Earned Cr", "CCH", "Remarks"]]
    print(f"{data}")

    # Fetch semester results and add to table
    for index, student in enumerate(students, start=1):
        semester_result = Semester_Result.objects.filter(student_id=student, semester=semester_number).first()
        
        
        if semester_result:
            print(f"\nGenerate Report PDF:{semester_result}\n")
            prev_sem_result = Semester_Result.objects.filter(student_id=student, semester=semester_number - 1).first()
            print(f"\nGenerate Report prev_sem_result:{prev_sem_result}\n")
            pcgpa = prev_sem_result.cgpa if prev_sem_result else 0
            pcch = prev_sem_result.cumulative_credit_earned if prev_sem_result else 0
            
            data.append([
                str(index),  # SL No.
                student.student_id,  # Student ID
                f"{student.user.first_name} {student.user.last_name}",  # Name
                student.reg_no,  # Regi (Registration Number)
                str(pcgpa),  # PCGPA (Previous Semester CGPA)
                str(pcch),  # PCCH (Previous Semester Cumulative Credit Hours)
                str(semester_result.gpa),  # GPA (Current Semester GPA)
                str(semester_result.cgpa),  # CGPA (Current Semester CGPA)
                str(semester_result.curr_sem_credit_earned),  # Earned Credit
                str(semester_result.cumulative_credit_earned),  # Cumulative Credit Earned
                semester_result.remark  # Remarks
            ])
            print(f"{data}")

    # Create a table object
    # table = Table(data, colWidths=[40, 60, 120, 60, 50, 50, 50, 50, 60, 60, 80])
    table = Table(data)

    # Style the table
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),  # Header background color
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),  # Header text color
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),  # Center text
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),  # Header font
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),  # Header padding
        ('GRID', (0, 0), (-1, -1), 1, colors.black),  # Add borders
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),  # Data row background color
    ]))

    # Add the table to the PDF elements
    elements.append(table)

    # Build the PDF
    doc.build(elements)

    return response