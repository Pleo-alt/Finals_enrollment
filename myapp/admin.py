from django.contrib import admin
from .models import Course, Yearlevel, Semester, Section, Instructor, Subject, Student, ExcelFile
from django import forms
import openpyxl  # or `import xlrd` if you're using `.xls`
from datetime import datetime

# Register your models here.
class ExcelFileAdminForm(forms.ModelForm):
    class Meta:
        model = ExcelFile
        fields = ['name', 'file']

    def clean_file(self):
        file = self.cleaned_data.get('file')
        if not file.name.endswith(('.xlsx', '.xls')):
            raise forms.ValidationError('Invalid file type. Only Excel files are supported.')
        return file

class ExcelFileAdmin(admin.ModelAdmin):
    form = ExcelFileAdminForm

    def save_model(self, request, obj, form, change):
        # Save the uploaded file
        super().save_model(request, obj, form, change)
        file_path = obj.file.path

        # Open the Excel file
        workbook = openpyxl.load_workbook(file_path)
        sheet = workbook.active

        course_to_create = []
        yearlevel_to_create = []
        semester_to_create = []
        instructor_to_create = []
        section_to_create = []
        subject_to_create = []
        student_to_create = []

        # Read the data from Excel and update the Student model
        for row in sheet.iter_rows(min_row=2, values_only=True):  # Skip the header row
            print(f"Row data: {row}") 
            student_first_name, student_middle_name, student_last_name, age, birthday, address, email_address, school_year, enrollment_date, student_id, status, gender, course_name, year_level, semester_name, instructor_first_name, instructor_middle_name, instructor_last_name, section_name, capacity, subject_code, subject_name, subject_unit, section_time, section_day, section_room  = row  # Map columns to fields
            
            try:
                enrollment_date = datetime.strptime(enrollment_date, "%b %d %Y").date()
            except ValueError:
                 print(f"Invalid date format: {enrollment_date}")
                 continue  # Skip rows with invalid dates
            
            try:
                birthday = datetime.strptime(birthday, "%b %d %Y").date()
            except ValueError:
                 print(f"Invalid date format for birthday: {birthday}")
                 continue  # Skip rows with invalid birthday
            
             # Check if the course already exists
            course, created = Course.objects.get_or_create(course_name=course_name)
            if created:
                course_to_create.append(course)

            # Check if the year_level already exists
            year_level_obj, created = Yearlevel.objects.get_or_create(year_level=year_level)
            if created:
                yearlevel_to_create.append(year_level_obj)

            # Semester
            semester_obj, created = Semester.objects.get_or_create(semester_name=semester_name)
            if created:
               semester_to_create.append(semester_obj)

              # Check if the section_name already exists
            section, created = Section.objects.get_or_create(
                section_name=section_name,
                course_name=course,  # Link to the correct course
                year_level=year_level_obj, # Link to the correct year level
                defaults={'capacity': capacity}, # Only applies when creating a new Section
            )
            if created:
                print(f"New Section created: {section.section_name} with capacity {section.capacity}")
        
            # Global check: Skip processing info for all the models if student_id exists in Member
            if Student.objects.filter(student_id=student_id).exists():
                print(f"Skipping existing student_id: {student_id}")
                continue

            instructor_to_create.append(
                Instructor(
                    first_name=instructor_first_name,
                    middle_name=instructor_middle_name,
                    last_name=instructor_last_name,
                )
            )

            subject_to_create.append(
                Subject(
                    subject_code=subject_code,
                    subject_name=subject_name,
                    subject_unit=subject_unit,
                    section_time=section_time,
                    section_day=section_day,
                    section_room=section_room,
                    course_name=course,  # Ensure the course is linked
                    year_level=year_level_obj,
                )
            )

            student_to_create.append(
                Student(
                    first_name=student_first_name,
                    middle_name=student_middle_name,
                    last_name=student_last_name,
                    age=age,
                    birthday=birthday,
                    address=address, 
                    email_address=email_address,
                    school_year=school_year,
                    enrollment_date=enrollment_date,
                    student_id=student_id,
                    status=status,
                    gender=gender,
                    course_name=course,  # Ensure the course is linked
                    section_name=section,
                    semester=semester_obj,
                    year_level=year_level_obj,
                )
            )

        # Bulk create for models
        Course.objects.bulk_create(course_to_create, ignore_conflicts=True)
        Yearlevel.objects.bulk_create(yearlevel_to_create)
        Semester.objects.bulk_create(semester_to_create)
        Instructor.objects.bulk_create(instructor_to_create)
        Section.objects.bulk_create(section_to_create)
        Subject.objects.bulk_create(subject_to_create)
        Student.objects.bulk_create(student_to_create)
         
        print(f"Added {len(course_to_create)} new course.")
        print(f"Added {len(yearlevel_to_create)} new year levels.")
        print(f"Added {len(yearlevel_to_create)} new Semester.")
        print(f"Added {len(instructor_to_create)} new Instructor.")
        print(f"Added {len(section_to_create)} new Section.")
        print(f"Added {len(subject_to_create)} new Subject.")
        print(f"Added {len(student_to_create)} new Student.") 

admin.site.register(ExcelFile, ExcelFileAdmin)

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('course_name', 'background_image')
    search_fields = ('course_name',)


@admin.register(Yearlevel)
class YearlevelAdmin(admin.ModelAdmin):
    list_display = ('year_level', 'get_courses')
    search_fields = ('year_level',)

    def get_courses(self, obj):
        return ", ".join([course.course_name for course in obj.courses.all()])
    get_courses.short_description = 'Courses'


@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ('section_name', 'course_name', 'year_level', 'capacity')
    search_fields = ('section_name', 'course_name', 'year_level')
    list_filter = ('course_name', 'year_level')

    def get_queryset(self, request):
        # Optimize the queryset to avoid excessive database queries
        queryset = super().get_queryset(request)
        return queryset.select_related('course_name', 'year_level')  # Use select_related for ForeignKeys


@admin.register(Instructor)
class InstructorAdmin(admin.ModelAdmin):
    list_display = ('full_name',)
    
    def full_name(self, obj):
        return str(obj)  # Uses the __str__ method for the instructor's name
    full_name.short_description = 'Full Name'


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('subject_code', 'subject_name', 'course_name', 'year_level', 'subject_unit', 'section_time', 'section_day', 'section_room')
    list_filter = ('course_name', 'year_level')
    search_fields = ('subject_code', 'subject_name')
    ordering = ('course_name', 'year_level', 'subject_code')


@admin.register(Semester)
class SemesterAdmin(admin.ModelAdmin):
    list_display = ('semester_name',)
    search_fields = ('semester_name',)

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = (
        'first_name',
        'last_name',
        'middle_name',
        'age',
        'section_name',
        'year_level',
        'semester_enrolled',
        'subjects_display',
        'student_id',  # Display Student ID
        'enrollment_date',
        'status',
        'birthday',  # Added new field
        'address',  # Added new field
        'email_address',  # Added new field
        'school_year',  # Added new field
        'gender',  # Added gender field
        'cellphone_number',
        'civil_status',
        'nationality',
    )
    search_fields = (
        'first_name',
        'middle_name',
        'last_name',
        'age',
        'year_level',
        'course_name',
        'semester',
        'enrollment_date',
        'email_address',  # Added new field
        'school_year',  # Added new field
        'gender',  # Added gender field to search
        'student_id',  # Allow searching by student ID
    )
    list_filter = (
        'year_level',
        'course_name',
        'section_name',
        'school_year',  # Added new field
        'gender',  # Added gender field to filter
    )

    def subjects_display(self, obj):
        return ", ".join([subject.subject_name for subject in obj.subjects.all()])
    subjects_display.short_description = 'Subjects'

    def semester_enrolled(self, obj):
        return obj.semester.semester_name if obj.semester else "Not Assigned"
    semester_enrolled.short_description = 'Semester Enrolled'