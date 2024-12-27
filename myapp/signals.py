import random
import string
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Student

def generate_temp_password(length=12):
    """Generate a random temporary password."""
    characters = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.choice(characters) for _ in range(length))

@receiver(post_save, sender=Student)
def create_student_user(sender, instance, created, **kwargs):
    if created:
        # Generate a temporary password
        temp_password = generate_temp_password()

        # Create a user with the temporary password
        user = User.objects.create_user(
            username=instance.student_id,
            password=temp_password,  # Temporary password
            first_name=instance.first_name,
            last_name=instance.last_name,
            email=instance.email_address,
        )
        instance.user = user
        instance.save()

        # Optionally, you could email the student with their temporary password
        # send_mail(...)

