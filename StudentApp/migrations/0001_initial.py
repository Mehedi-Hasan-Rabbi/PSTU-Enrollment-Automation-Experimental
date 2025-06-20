# Generated by Django 5.1.2 on 2025-06-15 16:19

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('FacultyApp', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Student',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('student_id', models.IntegerField(unique=True)),
                ('reg_no', models.IntegerField(default=0, unique=True)),
                ('phone_number', models.CharField(max_length=20, null=True, unique=True)),
                ('session', models.CharField(max_length=20, null=True)),
                ('payment_status', models.CharField(choices=[('Paid', 'Paid'), ('Unpaid', 'Unpaid')], default='Paid', max_length=20)),
                ('academic_status', models.CharField(choices=[('Regular', 'Regular'), ('Irregular', 'Irregular')], default='Regular', max_length=20)),
                ('graduation_status', models.CharField(choices=[('Complete', 'Complete'), ('Conditional Complete', 'Conditional Complete'), ('Incomplete', 'Incomplete')], default='Incomplete', max_length=20)),
                ('profile_pic', models.ImageField(upload_to='students_profile_pics/')),
                ('curr_semester', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='FacultyApp.semester')),
                ('faculty', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='FacultyApp.faculty')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Student_Transaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('trxID', models.CharField(max_length=50)),
                ('amount', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('semester', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='FacultyApp.semester')),
                ('student_id', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='StudentApp.student')),
            ],
        ),
        migrations.AddConstraint(
            model_name='student',
            constraint=models.UniqueConstraint(fields=('user', 'student_id', 'faculty'), name='unique_student'),
        ),
    ]
