from django.urls import path
from . import views

urlpatterns = [
    path('', views.first, name="first"),
    path('faculty/', views.faculty, name="faculty"),
    path('login/', views.login, name="login"),
    path('payment/', views.payment, name="payment"),
    path('profile/', views.profile, name="profile"),
    path('profileupdate/', views.profileupdate, name="profileupdate"),
    path('courses/', views.show_next_semester_courses, name='next_semester_courses'),
]
