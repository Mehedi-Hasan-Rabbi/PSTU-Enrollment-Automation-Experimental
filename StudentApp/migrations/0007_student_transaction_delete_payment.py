# Generated by Django 5.1.2 on 2024-10-26 16:00

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('FacultyApp', '0004_cost'),
        ('StudentApp', '0006_student_academic_status'),
    ]

    operations = [
        migrations.CreateModel(
            name='Student_Transaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('trxID', models.CharField(max_length=50)),
                ('amount', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
                ('semester', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='FacultyApp.semester')),
                ('student_id', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='StudentApp.student')),
            ],
        ),
        migrations.DeleteModel(
            name='Payment',
        ),
    ]
