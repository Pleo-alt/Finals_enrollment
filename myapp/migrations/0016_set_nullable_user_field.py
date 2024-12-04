from django.db import migrations


def set_nullable_user_for_students(apps, schema_editor):
    Student = apps.get_model('myapp', 'Student')

    # For all students that don't have a user set, we will set it to None (since the field is now nullable)
    students_without_user = Student.objects.filter(user__isnull=True)
    for student in students_without_user:
        student.user = None  # explicitly setting it to None
        student.save()


class Migration(migrations.Migration):
    dependencies = [
        # Add your dependency here (it should depend on the previous migration that added the 'user' field)
    ]

    operations = [
        migrations.RunPython(set_nullable_user_for_students),
    ]