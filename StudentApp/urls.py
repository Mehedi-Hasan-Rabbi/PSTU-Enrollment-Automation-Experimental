from django.urls import path
from . import views

app_name = "StudentApp"
urlpatterns = [    
    path('login/', views.student_login, name="student_login"),
    path('logout/', views.student_logout, name="student_logout"),
    path('dashboard/', views.student_dashboard, name="student_dashboard"),
    path('update_profile/', views.update_profile, name="update_profile"),
    
    path('enrollment/', views.student_enrollment, name="student_enrollment"),
    path('payment_success/<int:student_id>/', views.payment_success, name='payment_success'),
    path('payment_failure/<int:student_id>/', views.payment_failure, name='payment_failure'),
    path('payment_cancel/<int:student_id>/', views.payment_cancel, name='payment_cancel'),
    
    path('payment_history/', views.payment_history, name='payment_history'),
    path('invoice_download/<str:trx_id>/', views.download_invoice, name='download_invoice'),
    # path('download/invoice/<int:transaction_id>/', views.download_invoice, name='download_invoice'),
]