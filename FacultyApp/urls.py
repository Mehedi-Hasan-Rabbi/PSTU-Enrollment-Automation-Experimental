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
    
    path('faculty_admin/addStudent/', views.addStudent, name="addStudent"),
    path('faculty_admin/deleteStudent/', views.deleteStudent, name="deleteStudent"),
    
    path('faculty_admin/assignCourse/', views.assignCourse, name="assignCourse"),
    path('faculty_admin/deleteAllCourseInstructors/', views.deleteAllCourseInstructors, name="deleteAllCourseInstructors"),
    path('faculty_admin/specialCourseAssign/', views.specialCourseAssign, name="specialCourseAssign"),
    path('faculty_admin/deleteAllSpecialCourses/', views.deleteAllSpecialCourses, name="deleteAllSpecialCourses"),
    
    path('faculty_admin/updateExamPeriod/', views.updateExamPeriod, name="updateExamPeriod"),
    
    path('faculty_admin/calculate_result/', views.calculate_result, name='calculate_result'),
    path('faculty_admin/generate_result/<int:semester_number>/', views.generate_results, name='generate_results'),
    path('faculty_admin/generate_special_repeat_results/', views.generate_special_repeat_results, name='generate_special_repeat_results'),
    
    path('faculty_admin/all_student_PDF_generate/<int:semester_number>/', views.all_student_PDF_generate, name='all_student_PDF_generate'),
    path('faculty_admin/conditional_passed_student_PDF_generate/<int:semester_number>/', views.conditional_passed_student_PDF_generate, name='conditional_passed_student_PDF_generate'),
    path('faculty_admin/special_repeat_exam_PDF_generate/<int:semester_number>/', views.special_repeat_exam_PDF_generate, name='special_repeat_exam_PDF_generate'),
    
    path('faculty_admin/promote_to_next_semester/<int:semester_number>/', views.promote_to_next_semester, name='promote_to_next_semester'),
    
    path('faculty_admin/merit_list_PDF_generate/<int:semester_number>/', views.merit_list_PDF_generate, name='merit_list_PDF_generate'),
]
