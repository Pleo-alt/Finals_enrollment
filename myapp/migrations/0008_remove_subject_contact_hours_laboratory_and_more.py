# Generated by Django 5.1.3 on 2024-12-04 09:54

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0007_subject_section_day_subject_section_room_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='subject',
            name='contact_hours_laboratory',
        ),
        migrations.RemoveField(
            model_name='subject',
            name='contact_hours_lecture',
        ),
    ]