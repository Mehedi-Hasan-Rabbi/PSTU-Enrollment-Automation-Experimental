from django.urls import path
from . import views

app_name = "TeacherApp"
urlpatterns = [    
    path('login/', views.teacher_login, name="teacher_login"),
    path('logout/', views.teacher_logout, name="teacher_logout"),
    path('dashboard/', views.teacher_dashboard, name="teacher_dashboard"),
    
    path('myCourses/', views.myCourses, name="myCourses"),
    path('specialCourses/', views.specialCourses, name="specialCourses"),
    
    path('enterMarks/<str:course_code>/', views.enter_marks, name="enter_marks"),
    path('special_repeat_enter_mark/<str:course_code>/', views.special_repeat_enter_mark, name="special_repeat_enter_mark"),
    path('generate_pdf/<str:course_code>/', views.generate_pdf, name='generate_pdf'),
]