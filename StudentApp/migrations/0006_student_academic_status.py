# Generated by Django 5.1.2 on 2024-10-25 16:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('StudentApp', '0005_student_payment_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='student',
            name='academic_status',
            field=models.CharField(choices=[('Regular', 'Regular'), ('Irregular', 'Irregular')], default='Regular', max_length=20),
        ),
    ]
