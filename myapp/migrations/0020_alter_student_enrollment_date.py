# Generated by Django 5.1.3 on 2024-12-11 05:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0019_student_gender'),
    ]

    operations = [
        migrations.AlterField(
            model_name='student',
            name='enrollment_date',
            field=models.DateField(auto_now=True),
        ),
    ]