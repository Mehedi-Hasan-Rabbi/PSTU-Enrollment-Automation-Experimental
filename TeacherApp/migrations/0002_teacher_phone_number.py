# Generated by Django 5.1.1 on 2024-09-29 01:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('TeacherApp', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='teacher',
            name='phone_number',
            field=models.CharField(max_length=20, null=True, unique=True),
        ),
    ]
