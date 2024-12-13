from django.contrib import admin
from .models import Course, Yearlevel, Semester, Section, Instructor, Subject, Student

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
        'student_id',
        'enrollment_date',
        'status',
        'birthday',  # Added new field
        'address',  # Added new field
        'email_address',  # Added new field
        'school_year',  # Added new field
        'gender',  # Added gender field
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
