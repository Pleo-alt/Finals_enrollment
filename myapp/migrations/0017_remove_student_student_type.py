# Generated by Django 5.1.3 on 2024-12-07 02:59

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0016_student_address_student_birthday_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='student',
            name='student_type',
        ),
    ]
