import os
from django.conf import settings
from django.core.mail import send_mail
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_control
from django.core.exceptions import ValidationError
from django.views.decorators.cache import never_cache
from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect

from .models import FacultyController, Semester, Course, Faculty, Department
from TeacherApp.models import Teacher, Course_Instructor, Special_Course_Instructor
from StudentApp.models import Student
from ResultApp.views import get_student_mark, calculate_cgpa, calculate_gpa
from ResultApp.models import Exam_Period, Semester_Result, Special_Repeat, Course_Mark
from FacultyApp.documentGenerator import all_student_PDF, conditional_passed_student_PDF, special_repeat_exam_pdf, merit_list_PDF



# Create your views here.
def index(request):    
    return render(request, 'index.html')

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def faculty_admin_login(request):
    if request.user.is_authenticated:
        if FacultyController.objects.filter(user=request.user).exists():
            return redirect('FacultyApp:dashboard')
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
                faculty_controller = FacultyController.objects.get(user=user)
                login(request, user)
                return redirect('FacultyApp:dashboard')
            except FacultyController.DoesNotExist:
                messages.error(request, 'You do not have the required permissions to log in.')
        else:
            messages.error(request, 'Invalid username or password')

    # Add cache control headers to prevent caching of the login page
    response = render(request, 'login.html')
    response['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response['Pragma'] = 'no-cache'  # HTTP 1.0
    response['Expires'] = '0'  # Proxies

    return response

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def faculty_admin_logout(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')  # Optional success message
    
    # Clear Cache on Logout
    response = redirect('FacultyApp:faculty_admin_login')
    response['Cache-Control'] = 'no-cache, no-store, must-revalidate'  # HTTP 1.1
    response['Pragma'] = 'no-cache'  # HTTP 1.0
    response['Expires'] = '0'  # Proxies
    
    return response


@login_required(login_url='FacultyApp:faculty_admin_login')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def dashboard(request):
    faculty_controller = FacultyController.objects.get(user=request.user)
    faculty = faculty_controller.faculty
    
    # Calculate total numbers for dashboard
    total_students = Student.objects.filter(faculty=faculty, graduation_status='Incomplete').count()
    total_teachers = Teacher.objects.filter(faculty=faculty).count()
    total_courses = Course.objects.filter(faculty_name=faculty).count()
    total_departments = Department.objects.filter(faculty_name=faculty).count()
    total_exam_periods = Exam_Period.objects.filter(faculty=faculty).count()
    total_special_repeats = Special_Course_Instructor.objects.filter(teacher_id__faculty=faculty).count()

    # Get the current exam period and special repeat period if available
    exam_period = Exam_Period.objects.filter(faculty=faculty).first()
    special_repeat = Special_Repeat.objects.filter(faculty=faculty).first().special_period

    # Render the dashboard template with context
    response = render(request, 'dashboard.html', {
        'user': request.user,
        'total_students': total_students,
        'total_teachers': total_teachers,
        'total_courses': total_courses,
        'total_departments': total_departments,
        'total_exam_periods': total_exam_periods,
        'total_special_repeats': total_special_repeats,
        'exam_period': exam_period.period if exam_period else 'Not Set',
        'special_repeat': special_repeat if special_repeat else 'Not Set',
    })
    
    # Add cache control headers
    response['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'
    
    return response


@login_required(login_url='FacultyApp:faculty_admin_login')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def addCourse(request):
    faculty_controller = FacultyController.objects.get(user=request.user)
    faculty = faculty_controller.faculty
    semesters = Semester.objects.all()

    exam_period = Exam_Period.objects.filter(faculty=faculty).first()
    special_repeat = Special_Repeat.objects.filter(faculty=faculty).first().special_period
    
    if request.method == 'POST':
        course_code = request.POST.get('course_code')
        course_title = request.POST.get('course_title')
        semester_number = request.POST.get('semester')
        credit_hour = request.POST.get('credit_hour')

        if course_code and course_title and semester_number and credit_hour:
            try:
                semester = Semester.objects.get(semester_number=semester_number)
                
                if Course.objects.filter(course_code=course_code, semester=semester, faculty_name=faculty).exists():
                    messages.error(request, 'This course already exists for the selected semester and faculty.')
                else:
                    # Create the new course
                    Course.objects.create(
                        course_code=course_code,
                        course_title=course_title,
                        semester=semester,
                        faculty_name=faculty,
                        credit_hour=credit_hour
                    )
                    # Success message
                    messages.success(request, 'Course added successfully!')
                    return redirect('FacultyApp:addCourse')

            except Semester.DoesNotExist:
                messages.error(request, 'Invalid semester selection.')
        else:
            messages.error(request, 'Please fill out all fields.')

    return render(request, 'addCourse.html', {
        'faculty_name': faculty.faculty_name,
        'semester_number': semesters,
        'exam_period': exam_period.period,
        'special_repeat': special_repeat
    })
    

@login_required(login_url='FacultyApp:faculty_admin_login')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def deleteCourse(request):
    faculty_controller = FacultyController.objects.get(user=request.user)
    faculty = faculty_controller.faculty
    all_course = Course.objects.filter(faculty_name=faculty)
    
    exam_period = Exam_Period.objects.filter(faculty=faculty).first()
    special_repeat = Special_Repeat.objects.filter(faculty=faculty).first().special_period
    
    print(f"{faculty}")
    
    if request.method == 'POST':
        course_code = request.POST.get('course_code')
        print(f"{course_code, faculty.faculty_name}")
        try:
            # Try to find and delete the course
            course = Course.objects.get(course_code=course_code, faculty_name=faculty)
            course.delete()
            messages.success(request, f'Course {course_code} has been deleted successfully.')
            return redirect('FacultyApp:deleteCourse')
        except Course.DoesNotExist:
            messages.error(request, f'Course {course_code} does not exist or you are not authorized to delete it.')

    
    return render(request, 'deleteCourse.html', {
        'faculty_name': faculty.faculty_name,
        'all_course': all_course,
        'exam_period': exam_period.period,
        'special_repeat': special_repeat
    })
    

@login_required(login_url='FacultyApp:faculty_admin_login')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def addTeacher(request):
    faculty_controller = FacultyController.objects.get(user=request.user)
    faculty = faculty_controller.faculty
    
    exam_period = Exam_Period.objects.filter(faculty=faculty).first()
    special_repeat = Special_Repeat.objects.filter(faculty=faculty).first().special_period
    
    departments = Department.objects.filter(faculty_name=faculty)
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        password_confirmation = request.POST.get('password_confirmation')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        phone_number = request.POST.get('phone_number')
        # faculty_id = request.POST.get('faculty')
        department_id = request.POST.get('department')
        profile_pic = request.FILES.get('profile_pic')

        # Validate that passwords match
        if password != password_confirmation:
            messages.error(request, "Passwords do not match.")
            return redirect('FacultyApp:addTeacher')

        # Ensure all required fields are filled out
        if not (username and password and first_name and last_name and email and phone_number and department_id):
            messages.error(request, "Please fill out all required fields.")
            return redirect('FacultyApp:addTeacher')

        try:
            # Check if the username is already taken
            if User.objects.filter(username=username).exists():
                messages.error(request, 'Username already exists. Please choose a different username.')
                return redirect('FacultyApp:addTeacher')

            # Check if the email is already taken
            if User.objects.filter(email=email).exists():
                messages.error(request, 'A user with this email already exists.')
                return redirect('FacultyApp:addTeacher')

            # Create the user
            user = User.objects.create_user(
                username=username,
                password=password,
                first_name=first_name,
                last_name=last_name,
                email=email
            )

            # Get the selected faculty and department
            department = Department.objects.get(id=department_id)

            # Create the Teacher profile
            Teacher.objects.create(
                user=user,
                faculty=faculty,
                department=department,
                phone_number=phone_number,
                profile_pic=profile_pic
            )
            
            # Send email to the new teacher
            subject = "Welcome to the Faculty"
            message = f"Hello {first_name} {last_name},\n\nYour teacher profile has been created.\n\nUsername: {username}\nPassword: {password}\nFaculty: {faculty.faculty_name}\nDepartment: {department.dept_name}\n\nPlease log in and change your password upon first login.\n\nBest regards,\nFaculty Administration"
            send_mail(
                subject,
                message,
                settings.EMAIL_HOST_USER,
                [email],
                fail_silently=False,
            )

            messages.success(request, 'Teacher added successfully!')
            return redirect('FacultyApp:addTeacher')

        except Faculty.DoesNotExist:
            messages.error(request, 'Selected faculty does not exist.')
        except Department.DoesNotExist:
            messages.error(request, 'Selected department does not exist.')
        except ValidationError as e:
            messages.error(request, e.message)

    return render(request, 'addTeacher.html', {
        'departments': departments,
        'faculty_name': faculty.faculty_name,
        'exam_period': exam_period.period,
        'special_repeat': special_repeat
    })


@login_required(login_url='FacultyApp:faculty_admin_login')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def deleteTeacher(request):
    faculty_controller = FacultyController.objects.get(user=request.user)
    faculty = faculty_controller.faculty
    
    exam_period = Exam_Period.objects.filter(faculty=faculty).first()
    special_repeat = Special_Repeat.objects.filter(faculty=faculty).first().special_period
    
    # Get the list of teachers for the faculty
    all_teachers = Teacher.objects.filter(faculty=faculty).select_related('department')  # Use select_related for efficiency

    if request.method == 'POST':
        teacher_id = request.POST.get('teacher_id')

        try:
            # Get the teacher object
            teacher = Teacher.objects.get(id=teacher_id)

            # Delete the profile picture file if it exists
            if teacher.profile_pic:
                profile_pic_path = os.path.join(settings.MEDIA_ROOT, str(teacher.profile_pic))
                if os.path.isfile(profile_pic_path):
                    os.remove(profile_pic_path)

            # Delete the associated user
            user = teacher.user
            user.delete()  # Deletes the user, which cascades to delete the Teacher instance

            messages.success(request, f'Teacher {user.username} deleted successfully!')
        except Teacher.DoesNotExist:
            messages.error(request, 'Teacher does not exist.')
        except Exception as e:
            messages.error(request, str(e))

        # Redirect after deletion
        return redirect('FacultyApp:deleteTeacher')  # Ensure to define this URL pattern

    return render(request, 'deleteTeacher.html', {
        'faculty_name': faculty.faculty_name,
        'all_teachers': all_teachers,
        'exam_period': exam_period.period,
        'special_repeat': special_repeat
    })
    
    
@login_required(login_url='FacultyApp:faculty_admin_login')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def addDepartment(request):
    faculty_controller = FacultyController.objects.get(user=request.user)
    faculty = faculty_controller.faculty
    
    exam_period = Exam_Period.objects.filter(faculty=faculty).first()
    special_repeat = Special_Repeat.objects.filter(faculty=faculty).first().special_period

    if request.method == 'POST':
        dept_name = request.POST.get('dept_name')

        # Ensure the department name is provided
        if not dept_name:
            messages.error(request, "Please fill out the department name.")
            return redirect('FacultyApp:addDepartment')

        # Check if the department already exists
        if Department.objects.filter(dept_name=dept_name, faculty_name=faculty).exists():
            messages.error(request, f'Department "{dept_name}" already exists under faculty "{faculty.faculty_name}".')
            return redirect('FacultyApp:addDepartment')

        try:
            # Create a new department
            Department.objects.create(
                dept_name=dept_name,
                faculty_name=faculty  # Associate with the logged-in faculty
            )
            messages.success(request, f'Department "{dept_name}" added successfully!')
            return redirect('FacultyApp:addDepartment')  # Redirect to the same page or a different page
        except Exception as e:
            messages.error(request, str(e))

    return render(request, 'addDepartment.html', {
        'faculty_name': faculty.faculty_name,
        'exam_period': exam_period.period,
        'special_repeat': special_repeat
    })
    
    
@login_required(login_url='FacultyApp:faculty_admin_login')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def deleteDepartment(request):
    faculty_controller = FacultyController.objects.get(user=request.user)
    faculty = faculty_controller.faculty
    
    special_repeat = Special_Repeat.objects.filter(faculty=faculty).first().special_period
    
    # Get the list of departments for the faculty
    all_departments = Department.objects.filter(faculty_name=faculty)

    if request.method == 'POST':
        department_id = request.POST.get('department_id')

        try:
            # Get the department object
            department = Department.objects.get(id=department_id)

            # Get all teachers in this department
            teachers_in_department = Teacher.objects.filter(department=department)

            # Delete profile pictures and associated user accounts
            for teacher in teachers_in_department:
                # Delete the profile picture if it exists
                if teacher.profile_pic:
                    profile_pic_path = os.path.join(settings.MEDIA_ROOT, str(teacher.profile_pic))
                    if os.path.isfile(profile_pic_path):
                        os.remove(profile_pic_path)  # Delete the file from the filesystem
                
                # Delete the user associated with the teacher
                user = teacher.user
                user.delete()  # Deletes the associated user

            # Now delete the department itself
            department.delete()
            messages.success(request, f'Department of {department.dept_name} and all associated teachers deleted successfully!')

        except Department.DoesNotExist:
            messages.error(request, 'Department does not exist.')
        except Exception as e:
            messages.error(request, str(e))

        # Redirect after deletion
        return redirect('FacultyApp:deleteDepartment')  # Ensure to define this URL pattern

    return render(request, 'deleteDepartment.html', {
        'faculty_name': faculty.faculty_name,
        'all_departments': all_departments,
        'exam_period':  Exam_Period.objects.filter(faculty=faculty).first().period,
        'special_repeat': special_repeat
    })



@login_required(login_url='FacultyApp:faculty_admin_login')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def addStudent(request):
    faculty_controller = FacultyController.objects.get(user=request.user)
    faculty = faculty_controller.faculty
    
    special_repeat = Special_Repeat.objects.filter(faculty=faculty).first().special_period

    if request.method == 'POST':
        # Get form data
        username = request.POST.get('username')
        password = request.POST.get('password')
        password_confirmation = request.POST.get('password_confirmation')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        student_id = request.POST.get('student_id')
        reg_no = request.POST.get('reg_no')
        phone_number = request.POST.get('phone_number')
        session = request.POST.get('session')
        curr_semester = Semester.objects.get(semester_number=request.POST.get('curr_semester'))
        # cgpa = request.POST.get('cgpa')
        profile_pic = request.FILES.get('profile_pic')

        # Validate password confirmation
        if password != password_confirmation:
            messages.error(request, "Passwords do not match!")
            return redirect('FacultyApp:addStudent')

        # Check if username, email, or phone number already exists
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return redirect('FacultyApp:addStudent')

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists.")
            return redirect('FacultyApp:addStudent')

        if Student.objects.filter(phone_number=phone_number).exists():
            messages.error(request, "Phone number already exists.")
            return redirect('FacultyApp:addStudent')

        # Create user and student profile
        try:
            user = User.objects.create_user(
                username=username,
                password=password,
                first_name=first_name,
                last_name=last_name,
                email=email
            )
            student = Student.objects.create(
                user=user,
                student_id=student_id,
                reg_no=reg_no,
                phone_number=phone_number,
                session=session,
                faculty=faculty,
                curr_semester=curr_semester,
                # cgpa=cgpa,
                profile_pic=profile_pic
            )
            
            subject = "Welcome to the University"
            message = (
                f"Hello {first_name} {last_name},\n\nYour student profile has been created.\n\n"
                f"Username: {username}\nPassword: {password}\nFaculty: {faculty.faculty_name}\n"
                f"Session: {session}\nCurrent Semester: {curr_semester.semester_number}\n\n"
                "Please log in and change your password upon first login.\n\nBest regards,\nFaculty Administration"
            )
            send_mail(
                subject,
                message,
                settings.EMAIL_HOST_USER,
                [email],
                fail_silently=False,
            )
            
            messages.success(request, "Student added successfully!")
        except Exception as e:
            messages.error(request, str(e))

        return redirect('FacultyApp:addStudent')

    semesters = Semester.objects.all()
    return render(request, 'addStudent.html', {
        'semesters': semesters, 
        'faculty_name': faculty.faculty_name,
        'exam_period':  Exam_Period.objects.filter(faculty=faculty).first().period,
        'special_repeat': special_repeat
    })


@login_required(login_url='FacultyApp:faculty_admin_login')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def deleteStudent(request):
    faculty_controller = FacultyController.objects.get(user=request.user)
    faculty = faculty_controller.faculty
    
    special_repeat = Special_Repeat.objects.filter(faculty=faculty).first().special_period
    
    # Get the list of students for the faculty
    all_students = Student.objects.filter(faculty=faculty).select_related('curr_semester')  # Use select_related for efficiency

    if request.method == 'POST':
        student_id = request.POST.get('student_id')

        try:
            # Get the student object
            student = Student.objects.get(id=student_id)

            # Delete the profile picture file if it exists
            if student.profile_pic:
                profile_pic_path = os.path.join(settings.MEDIA_ROOT, str(student.profile_pic))
                if os.path.isfile(profile_pic_path):
                    os.remove(profile_pic_path)

            # Delete the associated user
            user = student.user
            user.delete()  # Deletes the user, which cascades to delete the Student instance

            messages.success(request, f'Student {user.username} deleted successfully!')
        except Student.DoesNotExist:
            messages.error(request, 'Student does not exist.')
        except Exception as e:
            messages.error(request, str(e))

        # Redirect after deletion
        return redirect('FacultyApp:deleteStudent')  # Ensure to define this URL pattern

    return render(request, 'deleteStudent.html', {
        'faculty_name': faculty.faculty_name,
        'all_students': all_students,
        'exam_period':  Exam_Period.objects.filter(faculty=faculty).first().period,
        'special_repeat': special_repeat
    })
    
    
@login_required(login_url='FacultyApp:faculty_admin_login')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def assignCourse(request):
    faculty_controller = FacultyController.objects.get(user=request.user)
    faculty = faculty_controller.faculty
    
    special_repeat = Special_Repeat.objects.filter(faculty=faculty).first().special_period
    
    # Fetch all teachers and courses related to the faculty
    all_teachers = Teacher.objects.filter(faculty=faculty).select_related('department')
    all_courses = Course.objects.filter(faculty_name=faculty)
    
    if request.method == 'POST':
        teacher_id = request.POST.get('teacher_id')
        course_id = request.POST.get('course_id')

        try:
            teacher = Teacher.objects.get(id=teacher_id)
            course = Course.objects.get(course_code=course_id)

            # Check if the course is already assigned
            if Course_Instructor.objects.filter(teacher_id=teacher, courseinfo=course).exists():
                messages.warning(request, f'This course is already assigned to {teacher.user.username}.')
            else:
                # Create a new Course_Instructor record
                Course_Instructor.objects.create(teacher_id=teacher, courseinfo=course)
                messages.success(request, f'Course {course.course_code} assigned to {teacher.user.username} successfully!')

        except Teacher.DoesNotExist:
            messages.error(request, 'Selected teacher does not exist.')
        except Course.DoesNotExist:
            messages.error(request, 'Selected course does not exist.')
        except Exception as e:
            messages.error(request, str(e))

        return redirect('FacultyApp:assignCourse')

    return render(request, 'assignCourse.html', {
        'faculty_name': faculty.faculty_name,
        'all_teachers': all_teachers,
        'all_courses': all_courses,
        'exam_period':  Exam_Period.objects.filter(faculty=faculty).first().period,
        'special_repeat': special_repeat
    })


    
@login_required(login_url='FacultyApp:faculty_admin_login')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def deleteAllCourseInstructors(request):
    if request.method == 'POST':
        Course_Instructor.objects.all().delete()
        messages.success(request, 'All Course Instructor data has been deleted successfully.')
    return redirect('FacultyApp:assignCourse')



@login_required(login_url='FacultyApp:faculty_admin_login')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def specialCourseAssign(request):
    faculty_controller = FacultyController.objects.get(user=request.user)
    faculty = faculty_controller.faculty
    
    special_repeat = Special_Repeat.objects.filter(faculty=faculty).first().special_period
    
    # Fetch all teachers and courses related to the faculty
    all_teachers = Teacher.objects.filter(faculty=faculty).select_related('department')
    all_courses = Course.objects.filter(faculty_name=faculty)
    
    if request.method == 'POST':
        teacher_id = request.POST.get('teacher_id')
        course_id = request.POST.get('course_id')

        try:
            teacher = Teacher.objects.get(id=teacher_id)
            course = Course.objects.get(course_code=course_id)

            # Check if the course is already assigned
            if Special_Course_Instructor.objects.filter(teacher_id=teacher, courseinfo=course).exists():
                messages.warning(request, f'This course is already assigned to {teacher.user.username}.')
            else:
                # Create a new Course_Instructor record
                Special_Course_Instructor.objects.create(teacher_id=teacher, courseinfo=course)
                messages.success(request, f'Course {course.course_code} assigned to {teacher.user.username} successfully!')

        except Teacher.DoesNotExist:
            messages.error(request, 'Selected teacher does not exist.')
        except Course.DoesNotExist:
            messages.error(request, 'Selected course does not exist.')
        except Exception as e:
            messages.error(request, str(e))

        return redirect('FacultyApp:specialCourseAssign')

    return render(request, 'specialCourseAssign.html', {
        'faculty_name': faculty.faculty_name,
        'all_teachers': all_teachers,
        'all_courses': all_courses,
        'exam_period':  Exam_Period.objects.filter(faculty=faculty).first().period,
        'special_repeat': special_repeat
    })
    
    
@login_required(login_url='FacultyApp:faculty_admin_login')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def deleteAllSpecialCourses(request):
    if request.method == 'POST':
        Special_Course_Instructor.objects.all().delete()
        messages.success(request, 'All special course assignments have been deleted.')
    return redirect('FacultyApp:specialCourseAssign')


@login_required(login_url='FacultyApp:faculty_admin_login')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def updateExamPeriod(request):
    faculty_controller = FacultyController.objects.get(user=request.user)
    faculty = faculty_controller.faculty
    
    # Fetch current exam period and special repeat, or create defaults if not present
    exam_period = Exam_Period.objects.filter(faculty=faculty).first()
    special_repeat = Special_Repeat.objects.filter(faculty=faculty).first()

    if request.method == 'POST':
        selected_period = request.POST.get('exam_period')
        selected_repeat = request.POST.get('special_repeat')
        
        # Update or create exam period
        if exam_period:
            exam_period.period = selected_period
            exam_period.save()
        else:
            Exam_Period.objects.create(faculty=faculty, period=selected_period)
        
        # Update or create special repeat
        if special_repeat:
            special_repeat.special_period = selected_repeat
            special_repeat.save()
        else:
            Special_Repeat.objects.create(faculty=faculty, special_period=selected_repeat)
        
        messages.success(request, 'Exam Period and Special Repeat updated successfully!')
        return redirect('FacultyApp:updateExamPeriod')

    # Render the template with the current exam period and special repeat
    return render(request, 'updateExamPeriod.html', {
        'faculty': faculty,
        'exam_period': exam_period.period if exam_period else 'Regular',
        'special_repeat': special_repeat.special_period if special_repeat else 'Disable'
    })


# ------------------ New Views for Semester Results ------------------

@login_required(login_url='FacultyApp:faculty_admin_login')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def calculate_result(request):
    faculty_controller = FacultyController.objects.get(user=request.user)
    faculty = faculty_controller.faculty
    num_semesters = faculty.number_of_semseter
    exam_period =  Exam_Period.objects.filter(faculty=faculty).first().period
    special_repeat = Special_Repeat.objects.filter(faculty=faculty).first().special_period
         
    semesters = []
    if exam_period == 'F-Removal':
        semesters = Semester.objects.filter(semester_number__lte=num_semesters).exclude(semester_number=num_semesters)
    else:
        semesters = Semester.objects.filter(semester_number__lte=num_semesters)
    
    for semester in semesters:
        semester.student_count = Student.objects.filter(curr_semester=semester, faculty=faculty, payment_status='Paid', graduation_status='Incomplete').count()
            

    context = {
        'semesters': semesters,
        'exam_period':  exam_period,
        'special_repeat': special_repeat
    }

    return render(request, 'calculate_result.html', context)


@login_required(login_url='FacultyApp:faculty_admin_login')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def generate_results(request, semester_number):
    faculty_controller = FacultyController.objects.get(user=request.user)
    faculty = faculty_controller.faculty
    exam_period = Exam_Period.objects.filter(faculty=faculty).first().period
    special_repeat = Special_Repeat.objects.filter(faculty=faculty).first().special_period
    last_semester = faculty.number_of_semseter

    # Get the semester object
    semester = Semester.objects.get(semester_number=semester_number)
    # print(f"FacultyApp(view.py) generate_result:{Faculty}")
    context = get_student_mark(faculty, semester, exam_period, request)
    
    # If get_student_mark returns a redirect (i.e., missing marks), exit early
    if isinstance(context, HttpResponseRedirect):
        return context
    
    context['exam_period'] =  exam_period  # Add exam period to context
    context['special_repeat'] = special_repeat
    context['last_semester'] = last_semester

    return render(request, 'results_table.html', context)


@login_required(login_url='FacultyApp:faculty_admin_login')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def generate_special_repeat_results(request):
    faculty_controller = FacultyController.objects.get(user=request.user)
    faculty = faculty_controller.faculty
    exam_period = Exam_Period.objects.filter(faculty=faculty).first().period
    special_repeat = Special_Repeat.objects.filter(faculty=faculty).first().special_period
    
    results = []
    last_semester = faculty.number_of_semseter
    students_in_last_semester = Student.objects.filter(curr_semester__semester_number=last_semester, payment_status='Paid', graduation_status='Incomplete').order_by("student_id")
    
    for student in students_in_last_semester:
        
        for semester_number in range(1, last_semester + 1):
            semester = Semester.objects.get(semester_number=semester_number)
            
            gpa, current_credits, student_marks = calculate_gpa(student, semester, request)
            
            if gpa is None and current_credits is None and student_marks is None:
                messages.error(request, f"Marks are incomplete for student {student.user.get_full_name()} in semester {semester_number}.")
                return redirect('FacultyApp:generate_special_repeat_results')
            
            cgpa, cumulative_credits = calculate_cgpa(student, semester, gpa, current_credits)
            
            # Determine remark based on updated rule: Conditional Passed if any course is failed
            f_grade_count = sum(1 for mark in student_marks.values() if mark['grade_point'] == 0.00)
            if f_grade_count > 0:
                student_remark = "Conditional Passed"
                student.graduation_status = "Conditional Complete"
                student.save()
            else:
                student_remark = "Passed"
                student.graduation_status = "Complete"
                student.save()
            
            
            # All Failed Course
            failing_courses = Course_Mark.objects.filter(student_id=student, grade_point=0.00).select_related('course_id')
            failed_courses = []
            for course_mark in failing_courses:
                failed_courses.append(course_mark.course_id.course_code)

            # Save the result in Semester_Result model
            Semester_Result.objects.update_or_create(
                student_id=student,
                semester=semester,
                defaults={
                    'gpa': gpa,
                    'cgpa': cgpa,  # For first semester, CGPA = GPA
                    'curr_sem_credit_earned': current_credits,
                    'cumulative_credit_earned': cumulative_credits,
                    'remark': student_remark,
                }
            )
            
            # Prepare the results for the context
            if semester_number == last_semester:
                results.append({
                    'student_id': student.student_id,
                    'marks': student_marks,
                    'gpa': gpa,
                    'cgpa': cgpa,
                    'remark': student_remark,
                    'failed_courses' : failed_courses
                })
                
    
    context = {
        'semester': semester,
        'course_codes': Course.objects.filter(semester=last_semester, faculty_name=faculty),
        'results': results
    }
    
    context['exam_period'] =  exam_period
    context['special_repeat'] = special_repeat
    context['last_semester'] = last_semester

    return render(request, 'results_table.html', context)


@login_required(login_url='FacultyApp:faculty_admin_login')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def promote_to_next_semester(request, semester_number):
    faculty_controller = FacultyController.objects.get(user=request.user)
    faculty = faculty_controller.faculty
    exam_period = Exam_Period.objects.filter(faculty=faculty).first().period
    special_repeat = Special_Repeat.objects.filter(faculty=faculty).first().special_period

    # Get the current semester and the next semester
    current_semester = Semester.objects.get(semester_number=semester_number)
    next_semester = Semester.objects.filter(semester_number=semester_number + 1).first()

    if not next_semester:
        # Handle the case when the next semester does not exist
        messages.error(request, f"Semester {semester_number + 1} does not exist.")
        return redirect('FacultyApp:dashboard')

    # Get all students in the current semester and faculty
    students = Student.objects.filter(curr_semester=current_semester, faculty=faculty, payment_status='Paid', generate_results="Incomplete")

    promoted_students = []
    for student in students:
        # Get the semester result for the student in the specified semester
        semester_result = Semester_Result.objects.filter(student_id=student, semester=current_semester).first()

        if semester_result:
            # Check if the student has passed or conditionally passed
            if semester_result.remark in ["Passed", "Conditional Passed"]:
                # Update the student's current semester to the next semester
                student.curr_semester = next_semester
                student.payment_status = 'Unpaid'
                student.save()

                promoted_students.append(student)
                
            elif semester_result.remark == "Failed":
                Course_Mark.objects.filter(student_id=student, course_id__semester=current_semester).delete()
                semester_result.delete()
                student.payment_status = 'Unpaid'
                student.save()

    if promoted_students:
        messages.success(request, f"Successfully promoted {len(promoted_students)} students to semester {next_semester.semester_number}.")
    else:
        messages.info(request, "No students were promoted.")

    return redirect('FacultyApp:generate_results', semester_number)


@login_required(login_url='FacultyApp:faculty_admin_login')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def all_student_PDF_generate(request, semester_number):
    print(f"\nGenerate Report PDF:{semester_number}\n")
    
    faculty_controller = FacultyController.objects.get(user=request.user)
    faculty = faculty_controller.faculty
    try:
        response = all_student_PDF(faculty, semester_number)
        return response

    except Exception as e:
        return HttpResponse(f"An error occurred: {str(e)}", status=500)
    
    
@login_required(login_url='FacultyApp:faculty_admin_login')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def conditional_passed_student_PDF_generate(request, semester_number):
    print(f"\nGenerate Report PDF:{semester_number}\n")
    
    faculty_controller = FacultyController.objects.get(user=request.user)
    faculty = faculty_controller.faculty
    try:
        response = conditional_passed_student_PDF(faculty, semester_number)
        return response

    except Exception as e:
        return HttpResponse(f"An error occurred: {str(e)}", status=500)
    
    
@login_required(login_url='FacultyApp:faculty_admin_login')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def special_repeat_exam_PDF_generate(request, semester_number):    
    faculty_controller = FacultyController.objects.get(user=request.user)
    faculty = faculty_controller.faculty
    
    try:
        response = special_repeat_exam_pdf(faculty, semester_number)
        return response

    except Exception as e:
        return HttpResponse(f"An error occurred: {str(e)}", status=500)
    

@login_required(login_url='FacultyApp:faculty_admin_login')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def merit_list_PDF_generate(request, semester_number):    
    faculty_controller = FacultyController.objects.get(user=request.user)
    faculty = faculty_controller.faculty
    
    try:
        response = merit_list_PDF(faculty, semester_number)
        return response

    except Exception as e:
        return HttpResponse(f"An error occurred: {str(e)}", status=500)
