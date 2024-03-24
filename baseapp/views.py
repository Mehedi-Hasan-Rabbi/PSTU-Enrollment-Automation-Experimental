from django.shortcuts import redirect, render
from baseapp.models import student, Faculty, Semester, Course
from django.contrib import messages
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse

# Create your views here.
def first(request):
    return render(request, 'index.html')

def faculty(request):
    return render(request, 'faculty.html')

def login(request):
    if request.method == 'POST':
        student_ID = request.POST.get('Student_ID')
        password = request.POST.get('password')    

        for i in student_ID:
            if i >= '0' and i <= '9':
                print()
            else:
                # messages.warning(request, "ID must be number")
                return render(request, 'login.html')

        print(f"\nStudent ID: {student_ID}")
        print(f"password: {password}")

        person = student.objects.filter(student_id=student_ID, password=password).first()
        print(f"Person: {person}")
        if person:
            print("\nLogin in successfull\n")
            x = student.objects.filter(student_id=student_ID).values()
            print(f"\nx: {x}\n")
            request.session['user_data'] = list(x)  # Store x in session
            return redirect('profile')
        else:
            print("\nLogin Failes\n")
            return render(request, 'login.html')

    else:
        return render(request, 'login.html')

def payment(request):
    return render(request, 'payment.html')

def profile(request):
    user = request.session.get('user_data')  # Retrieve x from session
    print(f"\npassed data: {user}\n")
    return render(request, 'profile.html', {'user': user})

def profileupdate(request):
    user = request.session.get('user_data')  # Retrieve x from session
    print(f"\npassed data in update: {user}\n")
    
    stuDBpass = [student['password'] for student in user]
    dbpassword = ''.join(stuDBpass)
    print(f"{dbpassword} --> {type(dbpassword)}")
    if request.method == 'POST':
        password = request.POST['current_password']
        new_password = request.POST['new_password']
        com_password = request.POST['confirm_password']
        print(f"{password} --> {type(password)}")
        if password == dbpassword:
            if new_password == com_password:
                stuDBid = [student['student_id'] for student in user]
                print(f"studentDBid: {stuDBid} --> {type(stuDBid)}")
                db_id = int(stuDBid[0])
                print(f"db_id: {db_id} --> {type(db_id)}")
                student.objects.filter(student_id = db_id).update(password = new_password)
                messages.error(request, "Password Updated")
                redirect('profileupdate.html')
            else:
                messages.error(request, "New Password not matched")
                redirect('profileupdate.html')

        else:
            messages.error(request, "Wrong Password")
            redirect('profileupdate.html')
    return render(request, 'profileupdate.html')


# Courses Retrive Section
def show_next_semester_courses(request):

    user = request.session.get('user_data')
    stuDBid = [student['student_id'] for student in user]
    student_id = int(stuDBid[0])
    print(f"student_id in next semester: {student_id} --> {type(student_id)}")

    # Retrieve the student object based on the provided student_id
    Student = get_object_or_404(student, pk=student_id)

    # Get the current semester of the student
    current_semester = Student.semester

    # Get the name of the current semester
    current_semester_name = current_semester.name

    # Determine the name of the next semester
    next_semester_name = get_next_semester_name(current_semester_name)

    # Find the next semester based on the name
    next_semester = Semester.objects.filter(name=next_semester_name).first()

    if next_semester:
        # Retrieve the courses for the next semester
        next_semester_courses = Course.objects.filter(semester=next_semester, faculty=Student.faculty)

        # Pass the data to the template
        return render(request, 'next_semester_courses.html', {'student': Student, 'next_semester_courses': next_semester_courses})
    else:
        # If there is no next semester, display a message or handle it as per your requirement
        return HttpResponse(request, 'No Course Found')

def get_next_semester_name(current_semester_name):
    # Map the current semester name to the next semester name
    semesters = ['Semester 1', 'Semester 2', 'Semester 3', 'Semester 4', 'Semester 5', 'Semester 6', 'Semester 7', 'Semester 8']
    try:
        current_semester_index = semesters.index(current_semester_name)
        next_semester_index = current_semester_index + 1
        if next_semester_index < len(semesters):
            return semesters[next_semester_index]
    except ValueError:
        pass  # Handle if the current semester name is not found in the list of semesters
    return None