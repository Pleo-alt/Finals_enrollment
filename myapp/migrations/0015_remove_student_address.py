# Generated by Django 5.1.3 on 2024-12-07 02:42

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0014_remove_student_birthday'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='student',
            name='address',
        ),
    ]