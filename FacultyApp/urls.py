from django.urls import path
from . import views

app_name = "FacultyApp"
urlpatterns = [
    path('', views.index, name="index"),
    path('faculty_admin/', views.login, name='login'),
]