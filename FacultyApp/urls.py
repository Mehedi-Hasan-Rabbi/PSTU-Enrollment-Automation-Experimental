from django.urls import path
from . import views

app_name = "FacultyApp"
urlpatterns = [
    path('', views.index, name="index"),
    
    path('faculty_admin/login/', views.faculty_admin_login, name="faculty_admin_login"),
    path('faculty_admin/logout/', views.faculty_admin_logout, name="faculty_admin_logout"),
    path('faculty_admin/dashboard/', views.dashboard, name="dashboard"),
    
    path('faculty_admin/addCourse/', views.addCourse, name="addCourse"),
    path('faculty_admin/deleteCourse/', views.deleteCourse, name="deleteCourse"),
    
    path('faculty_admin/addTeacher/', views.addTeacher, name="addTeacher"),
    path('faculty_admin/deleteTeacher/', views.deleteTeacher, name="deleteTeacher"),
    
    path('faculty_admin/addDepartment/', views.addDepartment, name="addDepartment"),
    path('faculty_admin/deleteDepartment/', views.deleteDepartment, name="deleteDepartment"),
]