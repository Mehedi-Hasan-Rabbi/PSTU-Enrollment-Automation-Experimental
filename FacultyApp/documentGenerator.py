from .models import FacultyController, Semester, Course, Faculty, Department
from TeacherApp.models import Teacher, Course_Instructor
from StudentApp.models import Student
from ResultApp.views import get_student_mark

from django.http import HttpResponse
from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from StudentApp.models import Student
from ResultApp.models import Semester_Result, Course_Mark
from reportlab.lib.units import inch


def all_student_PDF(faculty, semester_number):
    students = Student.objects.filter(faculty=faculty, curr_semester=semester_number, payment_status='Paid')
           
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
        
        # Taking all failed course of a student
        failing_courses = Course_Mark.objects.filter(student_id=student, grade_point=0.00).select_related('course_id')
        failed_courses = []
        for course_mark in failing_courses:
            failed_courses.append(course_mark.course_id.course_code)
        
        if semester_result:
            print(f"\nGenerate Report PDF:{semester_result}\n")
            prev_sem_result = Semester_Result.objects.filter(student_id=student, semester=semester_number - 1).first()
            print(f"\nGenerate Report prev_sem_result:{prev_sem_result}\n")
            pcgpa = prev_sem_result.cgpa if prev_sem_result else 0
            pcch = prev_sem_result.cumulative_credit_earned if prev_sem_result else 0
            
            # All failed course append in PDF
            remark_with_failed_courses = semester_result.remark
            if failed_courses:
                formatted_failed_courses = []
                for i in range(0, len(failed_courses), 3):
                    formatted_failed_courses.append(", ".join(failed_courses[i:i+3]))
                remark_with_failed_courses += "\nFailed: " + "\n".join(formatted_failed_courses)
            
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
                remark_with_failed_courses # Remarks
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


def conditional_passed_student_PDF(faculty, semester_number):
    students = Student.objects.filter(faculty=faculty, curr_semester=semester_number, payment_status='Paid')
    conditional_students = []
    
    for student in students:
        if (Semester_Result.objects.filter(student_id=student, remark='Conditional Passed')):
            conditional_students.append(student)
            
    print(f'Conditional Students PDF: {conditional_students}')

    # Set up the HttpResponse with appropriate PDF headers
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="(Conditional Passed)Student_Report_Semester_{semester_number}_{faculty}.pdf"'

    # Create the PDF document object using ReportLab
    # doc = SimpleDocTemplate(response, pagesize=A4)
    doc = SimpleDocTemplate(response, pagesize=landscape(A4))
    elements = []

    # Title and semester information
    styles = getSampleStyleSheet()
    elements.append(Paragraph(f"(Conditional Passed) Student Report for Semester {semester_number} ({faculty})", styles['Title']))

    # Create table data (headers)
    data = [["SL No.", "Student ID", "Name", "Regi", "PCGPA", "PCCH", "GPA", "CGPA", "Earned Cr", "CCH", "Remarks"]]

    # Fetch semester results and add to table
    for index, student in enumerate(conditional_students, start=1):
        semester_result = Semester_Result.objects.filter(student_id=student, semester=semester_number).first()
        
        # Taking all failed course of a student
        failing_courses = Course_Mark.objects.filter(student_id=student, grade_point=0.00).select_related('course_id')
        failed_courses = []
        for course_mark in failing_courses:
            failed_courses.append(course_mark.course_id.course_code)
        
        if semester_result:
            prev_sem_result = Semester_Result.objects.filter(student_id=student, semester=semester_number - 1).first()
            pcgpa = prev_sem_result.cgpa if prev_sem_result else 0
            pcch = prev_sem_result.cumulative_credit_earned if prev_sem_result else 0
            
            # All failed course append in PDF
            remark_with_failed_courses = semester_result.remark
            if failed_courses:
                formatted_failed_courses = []
                for i in range(0, len(failed_courses), 3):
                    formatted_failed_courses.append(", ".join(failed_courses[i:i+3]))
                remark_with_failed_courses += "\nFailed: " + "\n".join(formatted_failed_courses)
            
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
                remark_with_failed_courses  # Remarks
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



def special_repeat_exam_pdf(faculty, semester_number):
    # Get all students in the last semester who failed at least one course
    students = Student.objects.filter(faculty=faculty, curr_semester=semester_number, payment_status='Paid')
    failed_students = []
    
    for student in students:
        failing_courses = Course_Mark.objects.filter(student_id=student, grade_point=0.00).select_related('course_id')
        if failing_courses:
            failed_students.append({
                'student': student,
                'failing_courses': failing_courses,
            })

    # Set up the HttpResponse with appropriate PDF headers
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Special_Repeat_Report_Semester_{semester_number}_{faculty}.pdf"'
    doc = SimpleDocTemplate(response, pagesize=A4)
    elements = []
    styles = getSampleStyleSheet()

    # Title and header for the special repeat exam
    elements.append(Paragraph(f"Student list of Special Repeat Examination for {semester_number}th Semester", styles['Title']))
    elements.append(Spacer(1, 12))

    # Loop through each failing course and create a table for each
    for entry in failed_students:
        student = entry['student']
        student_name = f"{student.user.first_name} {student.user.last_name}"
        
        sl_no = 1
        for course in entry['failing_courses']:
            semester = course.course_id.semester
            course_code = course.course_id.course_code
            course_title = course.course_id.course_title
            credit_hours = course.course_id.credit_hour
            
            # Course information for failed course table
            elements.append(Paragraph(f"{sl_no}.Semester: {semester}, Course Code: {course_code}, Credit.Hr.= {credit_hours}, Course Title: {course_title}", styles['Heading5']))
            elements.append(Paragraph(f"Number of Students: {len(failed_students)}\n", styles['Italic']))
            elements.append(Paragraph(f"", styles['Italic']))
            
            # Table headers and data for each student
            sl_no_student = 1
            data = [["SL No.", "Student ID", "Student Name", "Reg. No", "Remark"]]
            data.append([
                str(sl_no_student),
                student.student_id,
                student_name,
                student.reg_no,
                "S. Repeat"
            ])
            sl_no_student += 1
            sl_no += 1
            
            # Create table object and style it
            table = Table(data)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ]))

            elements.append(table)
            elements.append(Spacer(1, 12))

    # Build the PDF
    doc.build(elements)
    return response


def merit_list_PDF(faculty, semester_number):
    # Filter students in the given faculty and semester without any failed courses
    students = Student.objects.filter(faculty=faculty, curr_semester=semester_number, payment_status='Paid')
    
    # Collect students with no failing courses in the semester
    qualified_students = []
    for student in students:
        failed_courses = Course_Mark.objects.filter(student_id=student, grade_point=0.00)
        if not failed_courses:
            semester_result = Semester_Result.objects.filter(student_id=student, semester=semester_number).first()
            if semester_result and semester_result.remark == "Passed":
                qualified_students.append({
                    'student': student,
                    'cgpa': semester_result.cgpa,
                    'cumulative_credit_earned': semester_result.cumulative_credit_earned,
                })

    # Separate students based on academic status
    regular_students = sorted(
        [s for s in qualified_students if s['student'].academic_status == 'Regular'],
        key=lambda x: x['cgpa'],
        reverse=True
    )
    irregular_students = [s for s in qualified_students if s['student'].academic_status == 'Irregular']
    
    # Set up PDF response
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Merit_List_Semester_{semester_number}_{faculty}.pdf"'
    doc = SimpleDocTemplate(response, pagesize=landscape(A4))
    elements = []
    styles = getSampleStyleSheet()

    # Title and header
    elements.append(Paragraph(f"Merit List for {semester_number}th Semester - Faculty: {faculty}", styles['Title']))
    elements.append(Spacer(1, 12))
    
    # Header row for the table
    data = [["SL No.", "Student ID", "Name", "Reg. No", "CGPA", "Cumulative Credit Earned", "Merit Position"]]
    
    # Add regular students with merit position
    for i, entry in enumerate(regular_students, start=1):
        student = entry['student']
        student_name = f"{student.user.first_name} {student.user.last_name}"
        data.append([
            i,  # SL No. based on merit position
            student.student_id,
            student_name,
            student.reg_no,
            entry['cgpa'],
            entry['cumulative_credit_earned'],
            f"{i}th"  # Merit position
        ])
    
    # Add irregular students with merit position as "Passed"
    for entry in irregular_students:
        student = entry['student']
        student_name = f"{student.user.first_name} {student.user.last_name}"
        data.append([
            len(data),  # Next SL No.
            student.student_id,
            student_name,
            student.reg_no,
            entry['cgpa'],
            entry['cumulative_credit_earned'],
            "Passed"  # Merit position for irregular students
        ])
    
    # Create table with style
    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
    ]))

    elements.append(table)

    # Build the PDF
    doc.build(elements)
    return response