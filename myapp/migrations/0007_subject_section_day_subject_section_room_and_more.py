# Generated by Django 5.1.3 on 2024-12-04 09:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0006_alter_course_options_alter_student_options_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='subject',
            name='section_day',
            field=models.CharField(default='TBA', max_length=200),
        ),
        migrations.AddField(
            model_name='subject',
            name='section_room',
            field=models.CharField(default='TBA', max_length=200),
        ),
        migrations.AddField(
            model_name='subject',
            name='section_time',
            field=models.CharField(default='TBA', max_length=200),
        ),
    ]