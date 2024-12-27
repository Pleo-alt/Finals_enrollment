from django.db import models
from django.db import transaction
from django.utils import timezone
from django.contrib.auth.models import User

# Course model
class Course(models.Model):
    course_name = models.CharField(max_length=50, unique=True)
    background_image = models.ImageField(upload_to='images/', blank=True, null=True)

    def __str__(self):
        return self.course_name

    class Meta:
        ordering = ['course_name']  # Order courses alphabetically

# Yearlevel model
class Yearlevel(models.Model):
    YEAR_CHOICES = [
        ('1st Year', '1st Year'),
        ('2nd Year', '2nd Year'),
        ('3rd Year', '3rd Year'),
        ('4th Year', '4th Year'),
    ]
    year_level = models.CharField(max_length=30, choices=YEAR_CHOICES, default='1st Year')
    courses = models.ManyToManyField(Course, related_name='year_levels')

    def __str__(self):
        return self.year_level

    class Meta:
        verbose_name = 'Year Level'
        verbose_name_plural = 'Year Levels'

# Semester model to store semester data
class Semester(models.Model):
    semester_name = models.CharField(max_length=200)

    def __str__(self):
        return self.semester_name

# Instructor model for teachers/lecturers
class Instructor(models.Model):
    first_name = models.CharField(max_length=200)
    middle_name = models.CharField(max_length=200, null=True, blank=True)
    last_name = models.CharField(max_length=200)

    def __str__(self):
        if self.middle_name:
            return f"{self.first_name} {self.middle_name} {self.last_name}"
        return f"{self.first_name} {self.last_name}"




# Section model for dividing students into classes
class Section(models.Model):
    course_name = models.ForeignKey(Course, on_delete=models.CASCADE)
    year_level = models.ForeignKey(Yearlevel, on_delete=models.CASCADE)
    section_name = models.CharField(max_length=200)
    capacity = models.IntegerField(null=False, default=0)  # Ensure capacity is non-null

    def __str__(self):
        return self.section_name
    
class Subject(models.Model):
    course_name = models.ForeignKey(Course, on_delete=models.CASCADE)
    year_level = models.ForeignKey(Yearlevel, on_delete=models.CASCADE)
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE, null=True)
    subject_code = models.CharField(max_length=200)
    subject_name = models.CharField(max_length=200)
    subject_unit = models.IntegerField(null=True)
    section_time = models.CharField(max_length=200, default="TBA", null=True)
    section_day = models.CharField(max_length=200, default="TBA", null=True)
    section_room = models.CharField(max_length=200, default="TBA", null=True)

    def __str__(self):
        return self.subject_name

class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, blank=True, null=True)
    course_name = models.ForeignKey(Course, on_delete=models.CASCADE)
    year_level = models.ForeignKey(Yearlevel, on_delete=models.CASCADE)
    section_name = models.ForeignKey(Section, on_delete=models.CASCADE)
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE)
    subjects = models.ManyToManyField(Subject, related_name="students")
    first_name = models.CharField(max_length=200)
    middle_name = models.CharField(max_length=200, null=True, blank=True)
    last_name = models.CharField(max_length=200)
    age = models.IntegerField(null=True)
    birthday = models.DateField(null=True, blank=True)  # New field
    address = models.CharField(max_length=500, null=True, blank=True)  # Changed to CharField
    email_address = models.EmailField(unique=True, null=True, blank=True)  # New field
    school_year = models.CharField(max_length=9, null=True, blank=True)  # New field
    enrollment_date = models.DateField(auto_now=True)

    student_id = models.CharField(max_length=9, unique=True, blank=True, null=True, db_index=True)
    status = models.CharField(max_length=100, blank=True, null=True)

    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
    ]
    
    # Add the gender field
    gender = models.CharField(
        max_length=6,
        choices=GENDER_CHOICES,
        default='Male',  # Default to Male
    )

    @property
    def full_name(self):
        return f"{self.first_name} {self.middle_name} {self.last_name}".strip()

    def __str__(self):
        return self.full_name

    def save(self, *args, **kwargs):
        # Only auto-generate student_id for new students (if it's not manually provided)
        if not self.student_id:
            year = timezone.now().year  # Get the current year

            # Use a transaction to ensure thread safety and avoid race conditions
            with transaction.atomic():
                # Get the last student_id for the current year, ordered by the most recent ID
                last_student = Student.objects.filter(
                    student_id__startswith=str(year)
                ).last()  # Fetch the most recent student with the same year prefix

                next_id = 1  # Default to the first student ID of the year

                if last_student:
                    # Extract and increment the numeric part of the last student_id (e.g., '20230001' -> '0001')
                    last_id = int(last_student.student_id[4:])  # Extract the last 5 digits
                    next_id = last_id + 1  # Increment the ID

                # Format the student_id as 'YYYYxxxxx' where xxxxx is the auto-incremented part
                self.student_id = f"{year}{next_id:05}"

        # If student_id is provided (for Old students), no changes will be made.
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['last_name', 'first_name']  # Sort students by name