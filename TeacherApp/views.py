from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_control
from django.contrib import messages
from django.http import HttpResponse
from django.contrib.auth.hashers import check_password

from TeacherApp.models import Teacher, Course_Instructor, Special_Course_Instructor
from ResultApp.models import Course_Mark, Exam_Period, Semester_Result, Special_Repeat
from StudentApp.models import Student
from FacultyApp.models import Course

from .documentGenerator import PDF

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
    teacher = Teacher.objects.get(user=request.user)
    faculty = teacher.faculty
    
    exam_period = Exam_Period.objects.filter(faculty=faculty).first()
    special_repeat = Special_Repeat.objects.filter(faculty=faculty).first().special_period
    
    # Create response object with the rendered template
    response = render(request, 'teacher_dashboard.html', {
        'user': request.user, 
        'exam_period': exam_period.period,
        'special_repeat': special_repeat
    })
    
    # Add cache control headers to prevent caching
    response['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response['Pragma'] = 'no-cache'  # HTTP 1.0
    response['Expires'] = '0'  # Proxies
    
    return response


@login_required(login_url='TeacherApp:teacher_login')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def teacher_update_profile(request):
    teacher = Teacher.objects.get(user=request.user)
    faculty = teacher.faculty
    
    exam_period = Exam_Period.objects.filter(faculty=faculty).first()
    special_repeat = Special_Repeat.objects.filter(faculty=faculty).first().special_period
    
    if request.method == 'POST':
        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        
        
        # Check if current password matches the user's password
        if check_password(current_password, request.user.password):
            if new_password == confirm_password:
                # Set the new password
                request.user.set_password(new_password)
                request.user.save()
                
                # Update the session with the new password to keep the user logged in
                update_session_auth_hash(request, request.user)
                
                messages.success(request, 'Your password has been updated successfully.')
                return redirect('TeacherApp:teacher_update_profile')
            else:
                messages.error(request, 'New password and confirm password do not match.')
        else:
            messages.error(request, 'Current password is incorrect.')
            

    response = render(request, 'teacher_update_profile.html', {
        'user': request.user, 
        'exam_period': exam_period.period,
        'special_repeat': special_repeat
    })
    
    # Add cache control headers to prevent caching
    response['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response['Pragma'] = 'no-cache'  # HTTP 1.0
    response['Expires'] = '0'  # Proxies
    
    return response


@login_required(login_url='TeacherApp:teacher_login')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def myCourses(request):
    teacher = request.user.teacher
    faculty = teacher.faculty
    num_semesters = faculty.number_of_semseter
    exam_period = Exam_Period.objects.filter(faculty=faculty).first().period
    special_repeat = Special_Repeat.objects.filter(faculty=faculty).first().special_period
    assigned_courses = Course_Instructor.objects.filter(teacher_id=teacher).select_related('courseinfo')
    
    if exam_period == 'F-Removal':
        assigned_courses = assigned_courses.exclude(courseinfo__semester__semester_number=num_semesters)

    context = {
        'assigned_courses': assigned_courses,
        'teacher_name': teacher.user.get_full_name(),
        'exam_period':  exam_period,
        'special_repeat': special_repeat
    }

    # Add cache control headers to prevent caching
    response = render(request, 'myCourses.html', context)
    response['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response['Pragma'] = 'no-cache'  # HTTP 1.0 backward compatibility
    response['Expires'] = '0'  # Proxies

    return response


@login_required(login_url='TeacherApp:teacher_login')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def specialCourses(request):
    teacher = request.user.teacher
    faculty = teacher.faculty
    exam_period = Exam_Period.objects.filter(faculty=faculty).first().period
    special_repeat = Special_Repeat.objects.filter(faculty=faculty).first().special_period
    assigned_courses = Special_Course_Instructor.objects.filter(teacher_id=teacher).select_related('courseinfo')

    context = {
        'assigned_courses': assigned_courses,
        'teacher_name': teacher.user.get_full_name(),
        'exam_period':  exam_period,
        'special_repeat': special_repeat
    }

    # Add cache control headers to prevent caching
    response = render(request, 'specialCourses.html', context)
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
    
    
# For Regular and F-removal Exam (Special Repeat in given below)
@login_required(login_url='TeacherApp:teacher_login')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def enter_marks(request, course_code):
    try:
        teacher = Teacher.objects.get(user=request.user)
        course = Course.objects.get(course_code=course_code)
        faculty = teacher.faculty
        exam_period = Exam_Period.objects.filter(faculty=faculty).first().period
        special_repeat = Special_Repeat.objects.filter(faculty=faculty).first().special_period

        # Ensure the teacher is assigned to this course
        if not Course_Instructor.objects.filter(teacher_id=teacher, courseinfo=course).exists():
            messages.error(request, "You are not assigned to this course.")
            return redirect('TeacherApp:myCourses')

        # Get all students enrolled in this course and same faculty
        if exam_period == 'Regular':
            students = Student.objects.filter(faculty=teacher.faculty, curr_semester=course.semester, payment_status='Paid', graduation_status='Incomplete').order_by('student_id')
        elif exam_period == 'F-Removal':
            conditonal_pass_student = Semester_Result.objects.filter(semester=course.semester, remark='Conditional Passed')
            # students = [con.student_id for con in conditonal_pass_student]
            students = []
            for con in conditonal_pass_student:
                print(f"Conditonal Passed Students: {con.student_id}")
                if Course_Mark.objects.filter(student_id=con.student_id, course_id=course_code).first().total < 40.00:
                    students.append(con.student_id)

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

        existing_marks = existing_marks if existing_marks else {}

        if request.method == 'POST':
            # Process the marks entry form
            for student in students:
                # Allow all fields during Regular, restrict to only final_exam during F-Removal
                if exam_period == 'Regular':
                    attendance = float(request.POST.get(f'attendance_{student.id}', 0))
                    assignment = float(request.POST.get(f'assignment_{student.id}', 0))
                    mid_exam = float(request.POST.get(f'mid_exam_{student.id}', 0))
                else:
                    attendance = float(existing_marks.get(student.id, {}).get('attendance', 0))
                    assignment = float(existing_marks.get(student.id, {}).get('assignment', 0))
                    mid_exam = float(existing_marks.get(student.id, {}).get('mid_exam', 0))

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
                        'letter_grade': letter_grade,
                        'grade_point': grade_point
                    }
                )

            messages.success(request, "Marks entered successfully!")
            return redirect('TeacherApp:enter_marks', course_code=course_code)

        context = {
            'course': course,
            'students': students,
            'existing_marks': existing_marks,
            'exam_period': exam_period,
            'special_repeat': special_repeat
        }
        return render(request, 'enter_marks.html', context)

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
def special_repeat_enter_mark(request, course_code):
    try:
        teacher = Teacher.objects.get(user=request.user)
        course = Course.objects.get(course_code=course_code)
        faculty = teacher.faculty
        exam_period = Exam_Period.objects.filter(faculty=faculty).first().period
        special_repeat = Special_Repeat.objects.filter(faculty=faculty).first().special_period
        last_semester = faculty.number_of_semseter
        # Ensure the teacher is assigned to this course
        if not Special_Course_Instructor.objects.filter(teacher_id=teacher, courseinfo=course).exists():
            messages.error(request, "You are not assigned to this course.")
            print(f"You are not assigned to this course.")
            return redirect('TeacherApp:specialCourses')

        # Get all students enrolled in this course and same faculty
        conditonal_pass_student = Semester_Result.objects.filter(semester=last_semester)
        # students = [con.student_id for con in conditonal_pass_student]
        students = []
        for con in conditonal_pass_student:
            print(f"Conditonal Passed Students: {con.student_id}")
            if Course_Mark.objects.filter(student_id=con.student_id, course_id=course_code).first().total < 40.00:
                students.append(con.student_id)

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
        
        existing_marks = existing_marks if existing_marks else {}

        if request.method == 'POST':
            # Process the marks entry form
            for student in students:
                # Allow all fields during Regular, restrict to only final_exam during F-Removal
                attendance = float(existing_marks.get(student.id, {}).get('attendance', 0))
                assignment = float(existing_marks.get(student.id, {}).get('assignment', 0))
                mid_exam = float(existing_marks.get(student.id, {}).get('mid_exam', 0))

                final_exam = float(request.POST.get(f'final_exam_{student.id}', 0))

                # Server-side validation
                if attendance > 10 or attendance < 7 or assignment > 5 or mid_exam > 15 or final_exam > 70:
                    messages.error(request, f"Invalid marks for {student.student_id}: "
                                            f"Attendance must be between 7-10, Assignment <= 5, "
                                            f"Mid Exam <= 15, Final Exam <= 70.")
                    return redirect('TeacherApp:special_repeat_enter_mark', course_code=course_code)

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
                        'letter_grade': letter_grade,
                        'grade_point': grade_point
                    }
                )

            messages.success(request, "Marks entered successfully!")
            return redirect('TeacherApp:special_repeat_enter_mark', course_code=course_code)
        context = {
            'course': course,
            'students': students,
            'existing_marks': existing_marks,
            'exam_period': exam_period,
            'special_repeat': special_repeat
        }
        print(students)
        return render(request, 'special_repeat_enter_mark.html', context)

    except Teacher.DoesNotExist:
        messages.error(request, "You are not authorized to enter marks.")
        return redirect('TeacherApp:teacher_login')

    except Course.DoesNotExist:
        messages.error(request, "Course not found.")
        return redirect('TeacherApp:specialCourses')

    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")
        return redirect('TeacherApp:specialCourses')



@login_required(login_url='TeacherApp:teacher_login')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def generate_pdf(request, course_code):
    faculty = Teacher.objects.get(user=request.user).faculty
    print(f"\nTeacher Faculty: {faculty} \n")
    try:
        response = PDF(faculty, course_code)
        return response

    except Course.DoesNotExist:
        return HttpResponse("Course not found.", status=404)
