# Generated by Django 5.1.3 on 2024-12-07 02:27

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0013_student_address_student_birthday'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='student',
            name='birthday',
        ),
    ]
