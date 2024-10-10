from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_control
from django.contrib import messages

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
                'total': mark.total
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

                # Create or update the student's marks
                Course_Mark.objects.update_or_create(
                    student_id=student,
                    course_id=course,
                    defaults={
                        'attendance': attendance,
                        'assignment': assignment,
                        'mid_exam': mid_exam,
                        'final_exam': final_exam,
                        'total': total
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
