from django.contrib import admin
from CSE.models import semester, CSEStudents

# Register your models here.
admin.site.register(CSEStudents)
admin.site.register(semester)