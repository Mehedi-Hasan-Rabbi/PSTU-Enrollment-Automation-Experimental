# Generated by Django 5.1.2 on 2024-10-26 17:10

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('StudentApp', '0007_student_transaction_delete_payment'),
    ]

    operations = [
        migrations.AddField(
            model_name='student_transaction',
            name='created_at',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
