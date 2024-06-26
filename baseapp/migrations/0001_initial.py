# Generated by Django 5.0.2 on 2024-03-27 02:56

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Cost',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cost_per_credit', models.IntegerField(default=0)),
                ('electricity', models.IntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='Faculty',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Semester',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(choices=[('Semester 1', 'Semester 1'), ('Semester 2', 'Semester 2'), ('Semester 3', 'Semester 3'), ('Semester 4', 'Semester 4'), ('Semester 5', 'Semester 5'), ('Semester 6', 'Semester 6'), ('Semester 7', 'Semester 7'), ('Semester 8', 'Semester 8'), ('Semester 9', 'Semester 9'), ('Semester 10', 'Semester 10'), ('Semester 11', 'Semester 11'), ('Semester 12', 'Semester 12'), ('Semester 13', 'Semester 13'), ('Semester 14', 'Semester 14'), ('Semester 15', 'Semester 15')], max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='Course',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('course_code', models.CharField(max_length=20, unique=True)),
                ('course_title', models.CharField(max_length=100, unique=True)),
                ('credit', models.PositiveIntegerField()),
                ('faculty', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='baseapp.faculty')),
                ('semester', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='baseapp.semester')),
            ],
        ),
        migrations.CreateModel(
            name='student',
            fields=[
                ('student_id', models.IntegerField(primary_key=True, serialize=False, unique=True)),
                ('reg_id', models.IntegerField(unique=True)),
                ('first_name', models.CharField(max_length=50)),
                ('last_name', models.CharField(max_length=50)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('password', models.CharField(max_length=100)),
                ('phone_number', models.CharField(max_length=50, unique=True)),
                ('img', models.ImageField(upload_to='pics')),
                ('faculty', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='baseapp.faculty')),
                ('semester', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='baseapp.semester')),
            ],
        ),
    ]
