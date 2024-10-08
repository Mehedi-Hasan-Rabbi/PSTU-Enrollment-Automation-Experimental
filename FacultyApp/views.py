import os
from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_control
from django.core.exceptions import ValidationError
from django.views.decorators.cache import never_cache
from django.contrib import messages
from .models import FacultyController, Semester, Course, Faculty, Department
from TeacherApp.models import Teacher, Course_Instructor
from StudentApp.models import Student
from ResultApp.models import Course_Mark

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


@login_required(login_url='FacultyApp:faculty_admin_login')  # Redirect to login if not authenticated
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def dashboard(request):
    # Create response object with the rendered template
    response = render(request, 'dashboard.html', {'user': request.user})
    
    # Add cache control headers to prevent caching
    response['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response['Pragma'] = 'no-cache'  # HTTP 1.0
    response['Expires'] = '0'  # Proxies
    
    return response


@login_required(login_url='FacultyApp:faculty_admin_login')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def addCourse(request):
    faculty_controller = FacultyController.objects.get(user=request.user)
    faculty = faculty_controller.faculty
    semesters = Semester.objects.all()

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
    })
    

@login_required(login_url='FacultyApp:faculty_admin_login')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def deleteCourse(request):
    faculty_controller = FacultyController.objects.get(user=request.user)
    faculty = faculty_controller.faculty
    all_course = Course.objects.filter(faculty_name=faculty)
    
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
    })
    

@login_required(login_url='FacultyApp:faculty_admin_login')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def addTeacher(request):
    faculty_controller = FacultyController.objects.get(user=request.user)
    faculty = faculty_controller.faculty
    
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
    })


@login_required(login_url='FacultyApp:faculty_admin_login')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def deleteTeacher(request):
    faculty_controller = FacultyController.objects.get(user=request.user)
    faculty = faculty_controller.faculty
    
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
    })
    
    
@login_required(login_url='FacultyApp:faculty_admin_login')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def addDepartment(request):
    faculty_controller = FacultyController.objects.get(user=request.user)
    faculty = faculty_controller.faculty

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
    })
    
    
@login_required(login_url='FacultyApp:faculty_admin_login')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def deleteDepartment(request):
    faculty_controller = FacultyController.objects.get(user=request.user)
    faculty = faculty_controller.faculty
    
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
    })



@login_required(login_url='FacultyApp:faculty_admin_login')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def addStudent(request):
    faculty_controller = FacultyController.objects.get(user=request.user)
    faculty = faculty_controller.faculty

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
        cgpa = request.POST.get('cgpa')
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
                cgpa=cgpa,
                profile_pic=profile_pic
            )
            messages.success(request, "Student added successfully!")
        except Exception as e:
            messages.error(request, str(e))

        return redirect('FacultyApp:addStudent')

    semesters = Semester.objects.all()
    return render(request, 'addStudent.html', {
        'semesters': semesters, 
        'faculty_name': faculty.faculty_name
    })


@login_required(login_url='FacultyApp:faculty_admin_login')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def deleteStudent(request):
    faculty_controller = FacultyController.objects.get(user=request.user)
    faculty = faculty_controller.faculty
    
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
    })
    
    
@login_required(login_url='FacultyApp:faculty_admin_login')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def assignCourse(request):
    faculty_controller = FacultyController.objects.get(user=request.user)
    faculty = faculty_controller.faculty
    
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
    })



# ------------------ New Views for Semester Results ------------------

@login_required(login_url='FacultyApp:faculty_admin_login')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def calculate_result(request):
    faculty_controller = FacultyController.objects.get(user=request.user)
    faculty = faculty_controller.faculty
    num_semesters = faculty.number_of_semseter

    # Get all semesters up to the number of semesters for this faculty
    semesters = Semester.objects.filter(semester_number__lte=num_semesters)

    # Add student count for each semester
    for semester in semesters:
        semester.student_count = Student.objects.filter(curr_semester=semester, faculty=faculty).count()

    context = {
        'semesters': semesters
    }

    return render(request, 'calculate_result.html', context)


@login_required(login_url='FacultyApp:faculty_admin_login')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def generate_results(request, semester_number):
    faculty_controller = FacultyController.objects.get(user=request.user)
    faculty = faculty_controller.faculty

    # Get the semester object
    semester = Semester.objects.get(semester_number=semester_number)
    
    # Get all students in this faculty and semester
    students = Student.objects.filter(faculty=faculty, curr_semester=semester).order_by("student_id")

    # Get all courses for this semester and faculty
    course_codes = Course.objects.filter(semester=semester, faculty_name=faculty)

    results = []
    
    # Prepare a list of dictionaries for each student
    for student in students:
        student_marks = {}
        for course in course_codes:
            course_mark = Course_Mark.objects.filter(student_id=student, course_id=course).first()
            student_marks[course.course_code] = course_mark.final_exam if course_mark else 'N/A'
        results.append({
            'student_id': student.student_id,
            'marks': student_marks
        })
    
    # print(f"{course_codes}")
    # print(f"{results}")
    context = {
        'semester': semester,
        'course_codes': course_codes,
        'results': results
    }

    return render(request, 'results_table.html', context)
