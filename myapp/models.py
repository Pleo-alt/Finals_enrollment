from django.db import models
from django.utils import timezone
from django.db.models import Max
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
    section = models.ForeignKey(Section, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.subject_name

# Student model, including student_id generation and handling of enrollment
class Student(models.Model):
    course_name = models.ForeignKey(Course, on_delete=models.CASCADE)
    year_level = models.ForeignKey(Yearlevel, on_delete=models.CASCADE)
    section_name = models.ForeignKey(Section, on_delete=models.CASCADE)
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE)
    subjects = models.ManyToManyField(Subject, related_name="students")
    first_name = models.CharField(max_length=200)
    middle_name = models.CharField(max_length=200, null=True, blank=True)
    last_name = models.CharField(max_length=200)
    age = models.IntegerField(null=True)
    enrollment_date = models.DateField(auto_now_add=True)

    student_id = models.CharField(max_length=9, unique=True, blank=True, null=True)
    status = models.CharField(max_length=100, blank=True, null=True)

    @property
    def full_name(self):
        return f"{self.first_name} {self.middle_name} {self.last_name}".strip()
    
    def __str__(self):
        return self.full_name

    def save(self, *args, **kwargs):
        # Generate student_id if not set (only for new students)
        if not self.student_id:
            year = timezone.now().year  # Get the current year
            last_student = Student.objects.filter(student_id__startswith=str(year)).aggregate(Max('student_id'))
            next_id = 1

            if last_student['student_id__max']:
                # Get the last ID for the current year and increment it
                last_id = int(last_student['student_id__max'][-5:])
                next_id = last_id + 1
            
            # Format the student_id as 'YYYYxxxxx' where xxxxx is the auto-incremented part
            self.student_id = f"{year}{next_id:05}"

        super().save(*args, **kwargs)  # Call the parent class's save method

    class Meta:
        ordering = ['last_name', 'first_name']  # Sort students by name
