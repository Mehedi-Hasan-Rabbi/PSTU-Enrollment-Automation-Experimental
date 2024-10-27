import random
import string
import pytz
from django.conf import settings
from django.utils import timezone
from django.core.mail import send_mail
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_control
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.http import HttpResponse
from django.urls import reverse

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle
from django.shortcuts import get_object_or_404

from StudentApp.models import Student, Student_Transaction
from FacultyApp.models import Cost, Course

from sslcommerz_lib import SSLCOMMERZ 


# Create your views here.
@cache_control(no_store=True, no_cache=True, must_revalidate=True)
def student_login(request):
    if request.user.is_authenticated:
        if Student.objects.filter(user=request.user).exists():
            return redirect('StudentApp:student_dashboard')
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
                student = Student.objects.get(user=user)
                login(request, user)
                return redirect('StudentApp:student_dashboard')
            except Student.DoesNotExist:
                messages.error(request, 'You do not have the required permissions to log in.')
        else:
            messages.error(request, 'Invalid username or password')

    # Add cache control headers to prevent caching of the login page
    response = render(request, 'student_login.html')
    response['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response['Pragma'] = 'no-cache'  # HTTP 1.0
    response['Expires'] = '0'  # Proxies

    return response


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def student_logout(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')  # Optional success message

    # Clear Cache on Logout
    response = redirect('StudentApp:student_login')
    response['Cache-Control'] = 'no-cache, no-store, must-revalidate'  # HTTP 1.1
    response['Pragma'] = 'no-cache'  # HTTP 1.0
    response['Expires'] = '0'  # Proxies

    return response


@login_required(login_url='StudentApp:student_login')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def student_dashboard(request):
    student = Student.objects.get(user=request.user)
    faculty = student.faculty
    
    # Create response object with the rendered template
    response = render(request, 'student_dashboard.html', {
        'user': request.user,
    })
    
    # Add cache control headers to prevent caching
    response['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response['Pragma'] = 'no-cache'  # HTTP 1.0
    response['Expires'] = '0'  # Proxies
    
    return response


@login_required(login_url='StudentApp:student_login')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def student_enrollment(request):
    # Get the student and their faculty details
    student = Student.objects.get(user=request.user)
    faculty = student.faculty
    cost = Cost.objects.first()  # Assuming there is only one Cost record to use

    # Retrieve the courses for the student's current semester and faculty
    courses = Course.objects.filter(semester=student.curr_semester, faculty_name=faculty)

    # Calculate course amounts and the total cost
    course_data = []
    total_course_cost = 0
    for index, course in enumerate(courses, start=1):
        course_amount = course.credit_hour * cost.cost_per_credit
        total_course_cost += course_amount
        course_data.append({
            'sl_no': index,
            'course_code': course.course_code,
            'course_title': course.course_title,
            'credit_hour': course.credit_hour,
            'amount': course_amount,
        })

    # Calculate total amount with additional fees
    total_amount = total_course_cost + cost.admission_fee + cost.enrollment_fee + cost.electricity
    
    if request.method == 'POST':
        settings = {
            'store_id': 'patua671a59b3b6059',
            'store_pass': 'patua671a59b3b6059@ssl',
            'issandbox': True  # Set to False for production
        }

        sslcz = SSLCOMMERZ(settings)
        random_code_1 = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        random_code_2 = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        post_body = {
            'total_amount': total_amount,
            'currency': "BDT",
            'tran_id': "TXN" + str(request.user.id) + str(total_amount) + str(random_code_1) + str(random_code_2),
            'success_url': request.build_absolute_uri(reverse('StudentApp:payment_success', args=[student.student_id])),
            'fail_url': request.build_absolute_uri(reverse('StudentApp:payment_failure', args=[student.student_id])),
            'cancel_url': request.build_absolute_uri(reverse('StudentApp:payment_cancel', args=[student.student_id])),
            'emi_option': 0,
            'cus_name': request.user.get_full_name(),
            'cus_email': request.user.email,
            'cus_phone': request.user.student.phone_number,
            'cus_add1': 'PSTU, Dumki',
            'cus_city': "Patuakhali",
            'cus_country': "Bangladesh",
            'shipping_method': "NO",
            'multi_card_name': "",
            'num_of_item': 1,
            'product_name': "Semester Enrollment",
            'product_category': "Enrollment Fees",
            'product_profile': "general"
        }

        response = sslcz.createSession(post_body)  # API response

        # Redirect user to payment page
        return redirect(response['GatewayPageURL'])

    # Render response
    response = render(request, 'student_enrollment.html', {
        'student': student,
        'course_data': course_data,
        'cost': cost,
        'total_amount': total_amount,
        'payment_status': student.payment_status
    })
    
    # Add cache control headers to prevent caching
    response['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'
    
    return response


@csrf_exempt
def payment_success(request, student_id):
    try:
        student = Student.objects.get(student_id=student_id)
        student.payment_status = 'Paid'
        student.save()
        
        transaction_id = request.POST.get('tran_id')
        amount = request.POST.get('amount')

        bangladesh_timezone = pytz.timezone('Asia/Dhaka')
        current_time_bst = timezone.now().astimezone(bangladesh_timezone)
        print(current_time_bst)

        Student_Transaction.objects.create(
            student_id=student,
            semester=student.curr_semester,
            trxID=transaction_id,
            amount=amount,
            created_at=current_time_bst
        )

        subject = 'Payment Confirmation'
        message = (
            f"Dear {student.user.first_name} {student.user.last_name},\n\n"
            f"Your payment has been received successfully. Here are the details:\n\n"
            f"Student ID: {student.student_id}\n"
            f"Reg. No.: {student.reg_no}\n"
            f"Semester: {student.curr_semester}\n"
            f"Transaction ID: {transaction_id}\n"
            f"Amount Paid: BDT {amount}\n"
            f"Date & Time: {current_time_bst.strftime('%Y-%m-%d %H:%M:%S')} BST\n\n"
            f"Thank you for your payment.\n\nBest regards,\nYour University Team"
        )
        
        # Ensure to use the email field from the user's profile
        send_mail(
            subject,
            message,
            settings.EMAIL_HOST_USER,
            [student.user.email],
            fail_silently=False,
        )
        
        # Return HTML with redirect and styling
        return HttpResponse("""
            <html>
            <head>
                <meta http-equiv="refresh" content="5; url=/student/enrollment/" />
                <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.6.0/css/all.min.css" integrity="sha384-k6RqeWeci5ZR/Lv4MR0sA0FfDOMYZGzGJ8V+I5c7jz5d0cPHNf6EMzvWpVJWSsyg" crossorigin="anonymous">
                <style>
                    body {
                        background-color: #e0ffe0; /* Light green background */
                        display: flex;
                        justify-content: center;
                        align-items: center;
                        height: 100vh;
                        margin: 0;
                        font-family: Arial, sans-serif;
                    }
                    .message-box {
                        text-align: center;
                        font-size: 1.5em;
                        color: #155724; /* Dark green text */
                    }
                    .message-box h2 {
                        margin-top: 0;
                        font-size: 2em;
                    }
                    .message-box .icon {
                        font-size: 3em;
                        color: #28a745; /* Green color for success */
                    }
                </style>
            </head>
            <body>
                <div class="message-box">
                    <div class="icon"><i class="fas fa-check-circle"></i></div>
                    <h2>Payment Successful!</h2>
                    <p>You will be redirected to the enrollment page in 5 seconds.</p>
                </div>
            </body>
            </html>
        """)
    except Student.DoesNotExist:
        return HttpResponse("Error: Student does not exist.", status=404)
    except Exception as e:
        return HttpResponse(f"An error occurred: {str(e)}", status=500)

@csrf_exempt
def payment_failure(request, student_id):
    return HttpResponse("""
        <html>
        <head>
            <meta http-equiv="refresh" content="5; url=/student/enrollment/" />
            <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" integrity="sha384-k6RqeWeci5ZR/Lv4MR0sA0FfDOMYZGzGJ8V+I5c7jz5d0cPHNf6EMzvWpVJWSsyg" crossorigin="anonymous">
            <style>
                body {
                    background-color: #ffe0e0; /* Light red background */
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 100vh;
                    margin: 0;
                    font-family: Arial, sans-serif;
                }
                .message-box {
                    text-align: center;
                    font-size: 1.5em;
                    color: #721c24; /* Dark red text */
                }
                .message-box h2 {
                    margin-top: 0;
                    font-size: 2em;
                }
                .message-box .icon {
                    font-size: 3em;
                    color: #dc3545; /* Red color for failure */
                }
            </style>
        </head>
        <body>
            <div class="message-box">
                <div class="icon"><i class="fas fa-times-circle"></i></div>
                <h2>Payment Failed. Please try again.</h2>
                <p>You will be redirected to the enrollment page in 5 seconds.</p>
            </div>
        </body>
        </html>
    """)

@csrf_exempt
def payment_cancel(request, student_id):
    return HttpResponse("""
        <html>
        <head>
            <meta http-equiv="refresh" content="5; url=/student/enrollment/" />
            <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.6.0/css/all.min.css" integrity="sha384-k6RqeWeci5ZR/Lv4MR0sA0FfDOMYZGzGJ8V+I5c7jz5d0cPHNf6EMzvWpVJWSsyg" crossorigin="anonymous">
            <style>
                body {
                    background-color: #f9e5e1; /* Light peach background */
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 100vh;
                    margin: 0;
                    font-family: Arial, sans-serif;
                }
                .message-box {
                    text-align: center;
                    font-size: 1.5em;
                    color: #856404; /* Dark orange text */
                }
                .message-box h2 {
                    margin-top: 0;
                    font-size: 2em;
                }
                .message-box .icon {
                    font-size: 3em;
                    color: #fd7e14; /* Orange color for cancel */
                }
            </style>
        </head>
        <body>
            <div class="message-box">
                <div class="icon"><i class="fas fa-exclamation-circle"></i></div>
                <h2>Payment Cancelled.</h2>
                <p>You will be redirected to the enrollment page in 5 seconds.</p>
            </div>
        </body>
        </html>
    """)
    
    
@login_required(login_url='StudentApp:student_login')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def payment_history(request):
    student = request.user.student
    transactions = Student_Transaction.objects.filter(student_id=student)


    response = render(request, 'payment_history.html', {
        'transactions': transactions
    })
    
    response['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'
    
    return response


from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Image
from django.shortcuts import get_object_or_404
from .models import Student_Transaction  # Make sure you import your Transaction model
import os

def download_invoice(request, trx_id):
    # Get the transaction object
    transaction = get_object_or_404(Student_Transaction, trxID=trx_id)

    # Create a response object and set the appropriate content type for PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="invoice_{transaction.trxID}.pdf"'

    # Create the PDF object
    pdf = SimpleDocTemplate(response, pagesize=letter)
    elements = []

    # Styles
    styles = getSampleStyleSheet()

    # Title
    elements.append(Paragraph(f"Invoice of {transaction.student_id.curr_semester} semester", styles['Title']))
    elements.append(Paragraph(""))

    # Adding student picture
    student_image_path = transaction.student_id.profile_pic.path  # Adjust this path according to your model
    if os.path.exists(student_image_path):
        student_image = Image(student_image_path, width=100, height=100)  # Adjust width and height as needed
        elements.append(student_image)

    # Adding space
    elements.append(Paragraph("<br/>", styles['Normal']))

    # Adding a table for transaction details
    data = [
        ['Item', 'Details'],
        ['Student Name:', transaction.student_id.user.get_full_name()],
        ["Student ID:" , transaction.student_id.student_id],
        ["Reg. No.:" , transaction.student_id.reg_no],
        ["Semester:" , transaction.student_id.curr_semester],
        ["Faculty:" , transaction.student_id.faculty],
        ["Session:" , transaction.student_id.session],
        ['Amount', f"{transaction.amount} BDT"],
        ['TrxID', transaction.trxID],
        ['Date', transaction.created_at.strftime('%Y-%m-%d')],
        ['Time', transaction.created_at.strftime('%H:%M:%S')],
    ]

    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))

    elements.append(table)

    # Build the PDF
    pdf.build(elements)

    return response
