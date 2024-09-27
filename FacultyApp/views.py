from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.contrib import messages
from .models import FacultyController, Semester, Course

# Create your views here.
def index(request):    
    return render(request, 'index.html')


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
def dashboard(request):
    # Create response object with the rendered template
    response = render(request, 'dashboard.html', {'user': request.user})
    
    # Add cache control headers to prevent caching
    response['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response['Pragma'] = 'no-cache'  # HTTP 1.0
    response['Expires'] = '0'  # Proxies
    
    return response


@login_required(login_url='FacultyApp:faculty_admin_login')
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
def deleteCourse(request):
    return render(request, 'deleteCourse.html', {
        
    })