from django.shortcuts import render, redirect,  get_object_or_404
from django.http import Http404,JsonResponse
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib import messages
from django.contrib.auth.models import User
from .models import Course, Yearlevel, Section, Student, Subject, Instructor, Semester
from django.db.models import Q
from django.utils import timezone 
from django.db import IntegrityError
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator
from django.contrib.auth.views import PasswordResetView
from django.contrib import messages
from django.shortcuts import redirect
import openpyxl
from datetime import datetime
from django.http import HttpResponse
from django import forms 
from django.template.loader import render_to_string
from weasyprint import HTML

def login(request):
    # Redirect authenticated users to the appropriate page
    if request.user.is_authenticated:
        if request.user.is_staff:  # Check if the user is a superuser/admin
            return redirect('/admin')  # Redirect superuser to admin panel
        return redirect('dashboard')  # Regular user to the dashboard

    if request.method == 'POST':
        # Get the login input (could be username or email)
        username_or_email = request.POST.get('username_or_email')
        password = request.POST.get('password')
        
        # Check if the input is an email or username
        if '@' in username_or_email:
            try:
                # Attempt to find the user by email
                user = User.objects.get(email=username_or_email)
                user = authenticate(request, username=user.username, password=password)
            except User.DoesNotExist:
                user = None
        else:
            # Attempt to authenticate with username
            user = authenticate(request, username=username_or_email, password=password)

        # If user is found and authentication is successful
        if user is not None:
            auth_login(request, user)  # Log the user in
            if user.is_staff:  # If the user is an admin
                return redirect('/admin')  # Redirect admin to the admin panel
            return redirect('dashboard')  # Redirect regular user to the dashboard
        else:
            messages.error(request, 'Invalid username/email or password.')
            return redirect('login')  # Redirect back to login after failed login attempt

    return render(request, 'registration/login.html')
def logout(request):
    # Clear all messages from the session manually before logging out
    if '_messages' in request.session:
        del request.session['_messages']  # This removes the stored messages from the session

    # Log the user out
    auth_logout(request)

    # Redirect back to the login page after logout
    return redirect('login')

class CustomPasswordResetView(PasswordResetView):
    def form_valid(self, form):
        email = form.cleaned_data.get('email')
        if not User.objects.filter(email=email).exists():
            messages.error(self.request, "No user with this email address was found.")
            return redirect('password_reset')  # Redirect to the same page
        return super().form_valid(form)

def dashboard(request):
    # Fetch all courses and year levels
    courses = Course.objects.all()  # Fetch all Course objects
    year_levels = Yearlevel.objects.all()  # Fetch all Yearlevel objects
    
    # Pass the data to the template context
    context = {
        'courses': courses,
        'year_levels': year_levels,
    }
    
    return render(request, 'dashboard.html', context)


def view_section(request, course_name, year_level):
    # Get the Course object by course_name
    course = get_object_or_404(Course, course_name=course_name)
    
    # Get the Yearlevel object by year_level
    year = get_object_or_404(Yearlevel, year_level=year_level)
    
    # Filter sections based on both course and year level
    sections = Section.objects.filter(course_name=course, year_level=year)
    
    # Check if there is a search query for section name or capacity
    search_query = request.GET.get('search', '')
    if search_query:
        sections = sections.filter(section_name__icontains=search_query)  # Search by section name

    # Check if there is a search query for capacity
    capacity_query = request.GET.get('capacity', '')
    if capacity_query:
        try:
            # If a valid number is provided for capacity, filter sections by capacity
            capacity_value = int(capacity_query)
            sections = sections.filter(capacity=capacity_value)  # Search by exact capacity
        except ValueError:
            # If the capacity query is not a valid number, don't apply the filter
            pass

    return render(request, 'section.html', {'course': course, 'year': year, 'sections': sections})

# Excel Upload Form
class ExcelUploadForm(forms.Form):
    file = forms.FileField()

# Upload Excel View
def upload_excel(request):
    if request.method == 'POST':
        form = ExcelUploadForm(request.POST, request.FILES)
        if form.is_valid():
            file = form.cleaned_data['file']
            try:
                # Load the workbook
                workbook = openpyxl.load_workbook(file)
                sheet = workbook.active

                # Containers for bulk creation
                course_to_create = []
                yearlevel_to_create = []
                semester_to_create = []
                instructor_to_create = []
                section_to_create = []
                subject_to_create = []
                student_to_create = []

                # Process rows from the Excel file
                for row in sheet.iter_rows(min_row=2, values_only=True):  # Skip the header row
                    try:
                        print(f"Row data: {row}") 
                        # Map columns to variables
                        (
                            student_first_name, student_middle_name, student_last_name, age, birthday, address, email_address,
                            school_year, enrollment_date, student_id, status, gender, course_name, year_level, semester_name,
                            instructor_first_name, instructor_middle_name, instructor_last_name, section_name, capacity,
                            subject_code, subject_name, subject_unit, section_time, section_day, section_room
                        ) = row

                        # Parse dates
                        enrollment_date = datetime.strptime(enrollment_date, "%b %d %Y").date()
                        birthday = datetime.strptime(birthday, "%b %d %Y").date()

                        # Course
                        course, _ = Course.objects.get_or_create(course_name=course_name)
                        
                        # Year Level
                        year_level_obj, _ = Yearlevel.objects.get_or_create(year_level=year_level)
                        
                        # Semester
                        semester_obj, _ = Semester.objects.get_or_create(semester_name=semester_name)
                        
                        # Section
                        section, _ = Section.objects.get_or_create(
                            section_name=section_name,
                            course_name=course,
                            year_level=year_level_obj,
                            defaults={'capacity': capacity},
                        )

                        # Skip if student already exists
                        if Student.objects.filter(student_id=student_id).exists():
                            print(f"Skipping existing student_id: {student_id}")
                            continue

                        # Prepare instructors for bulk creation
                        instructor_to_create.append(
                            Instructor(
                                first_name=instructor_first_name,
                                middle_name=instructor_middle_name,
                                last_name=instructor_last_name,
                            )
                        )

                        # Prepare subjects for bulk creation
                        subject_to_create.append(
                            Subject(
                                subject_code=subject_code,
                                subject_name=subject_name,
                                subject_unit=subject_unit,
                                section_time=section_time,
                                section_day=section_day,
                                section_room=section_room,
                                course_name=course,
                                year_level=year_level_obj,
                            )
                        )

                        # Prepare students for bulk creation
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
                                course_name=course,
                                section_name=section,
                                semester=semester_obj,
                                year_level=year_level_obj,
                            )
                        )
                    except Exception as e:
                        print(f"Error processing row: {row}, Error: {e}")
                        continue

                # Bulk create for efficiency
                Instructor.objects.bulk_create(instructor_to_create)
                Subject.objects.bulk_create(subject_to_create)
                Student.objects.bulk_create(student_to_create)

                return HttpResponse("File processed successfully!")

            except Exception as e:
                return HttpResponse(f"Error processing file: {e}")

    else:
        form = ExcelUploadForm()

    return render(request, 'upload_excel.html', {'form': form})


def view_students(request, course_name, year_level, section_name):
    # Get the Course, Yearlevel, and Section objects
    course = get_object_or_404(Course, course_name=course_name)
    year = get_object_or_404(Yearlevel, year_level=year_level)
    section = get_object_or_404(Section, section_name=section_name, course_name=course, year_level=year)

    # Get the search query from the request (if any)
    search_query = request.GET.get('search', '')
    
    # Filter students by course, year, and section
    students = Student.objects.filter(
        course_name=course,
        year_level=year,
        section_name=section
    )
    
    # If there's a search query, filter the students further
    if search_query:
        # Split the search query into individual words (in case it's a full name or ID)
        search_parts = search_query.split()
        
        # Create a Q object for the filter
        filter_query = Q()
        
        # For each part of the query, search across all relevant fields
        for part in search_parts:
            filter_query |= Q(first_name__icontains=part) | Q(middle_name__icontains=part) | Q(last_name__icontains=part) | Q(student_id__icontains=part) | Q(status__icontains=part)
        
        # Apply the filter to the students queryset
        students = students.filter(filter_query)

    # Get the total count of students (before pagination)
    students_count = students.count()

    # Pagination: show 5 students per page
    paginator = Paginator(students, 10)  # Show 5 students per page
    page_number = request.GET.get('page')  # Get the current page number from the URL
    page_obj = paginator.get_page(page_number)

    context = {
        'students': page_obj,  # Pass the paginated students
        'students_count': students_count,  # Pass the total number of students
        'course': course,
        'year': year,
        'section': section,
        'search_query': search_query,  # Pass the search query to retain it in the search bar
    }

    return render(request, 'student.html', context)

def download_students_pdf(request, course_name, year_level, section_name):
    course = get_object_or_404(Course, course_name=course_name)
    year = get_object_or_404(Yearlevel, year_level=year_level)
    section = get_object_or_404(Section, section_name=section_name, course_name=course, year_level=year)
    
    # Fetch the students
    students = Student.objects.filter(course_name=course, year_level=year, section_name=section)
    
    # Render the HTML content for the PDF
    html_string = render_to_string('students_pdf_template.html', {
        'students': students,
        'course': course,
        'year': year,
        'section': section,
    })
    
    # Generate the PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{section.section_name}_students.pdf"'
    HTML(string=html_string).write_pdf(response)
    
    return response

def view_student_subjects(request, course_name, year_level, section_name, student_id):
    # Fetching the course, year_level, section, and student objects
    course = get_object_or_404(Course, course_name=course_name)
    year_level_obj = get_object_or_404(Yearlevel, year_level=year_level)  # Corrected variable name
    section = get_object_or_404(Section, section_name=section_name, course_name=course, year_level=year_level_obj)
    student = get_object_or_404(Student, id=student_id, section_name=section)

    # Get the search query from the request
    search_query = request.GET.get('search', '')

    # Get all subjects for the student
    subjects = student.subjects.all()

    # If a search query exists, filter subjects by subject_name or subject_code
    if search_query:
        subjects = subjects.filter(
            Q(subject_name__icontains=search_query) | Q(subject_code__icontains=search_query)
        )

    # Fetch all semesters (assuming you have a Semester model)
    semesters = Semester.objects.all()

    # Context data to pass to the template
    context = {
        'course': course,
        'year_level': year_level_obj,  # Corrected to pass the Yearlevel object
        'section': section,
        'student': student,
        'subjects': subjects,
        'search_query': search_query,  # Search query to filter subjects
        'semesters': semesters,  # Add semesters to context
    }

    return render(request, 'subject.html', context)


def view_instructor(request, course_name, year_level, section_name, student_id, subject_code):
    # Get the specific student, course, year level, and section
    student = get_object_or_404(Student, student_id=student_id)
    course = get_object_or_404(Course, course_name=course_name)
    year = get_object_or_404(Yearlevel, year_level=year_level)
    section = get_object_or_404(Section, section_name=section_name, course_name=course, year_level=year)
    subject = get_object_or_404(Subject, subject_code=subject_code)

    # Get the instructor for the given subject and section
    instructor = Instructor.objects.filter(subjects=subject, section=section).first()

    # If no instructor is found, handle the case accordingly
    instructor_info = instructor if instructor else None

    # Render the template with the student, subject, and instructor info
    context = {
        'student': student,
        'course': course,
        'year': year,
        'section': section,
        'subject': subject,
        'instructor_info': instructor_info,
    }

    return render(request, 'instructor.html', context)


def add_student(request, course_id, year_level, section_name):
    course = get_object_or_404(Course, id=course_id)
    year_level_obj = get_object_or_404(Yearlevel, year_level=year_level)

    if course not in year_level_obj.courses.all():
        raise Http404("Invalid course and year level combination.")

    # Fetch the specific section based on the course and year level
    selected_section = get_object_or_404(Section, course_name=course, year_level=year_level_obj, section_name=section_name)

    # Handle form submission
    error_message = None
    if request.method == 'POST':
        # Extract data from the form
        first_name = request.POST.get('firstName')
        middle_name = request.POST.get('middleName')
        last_name = request.POST.get('lastName')
        age = request.POST.get('age')
        semester_id = request.POST.get('semester')
        status = request.POST.get('status')
        student_id = request.POST.get('student_id')
        gender = request.POST.get('gender')  # Get gender
        birthday = request.POST.get('birthday')  # Get birthday
        address = request.POST.get('address')  # Get address
        email_address = request.POST.get('email_address')  # Get email address
        school_year = request.POST.get('school_year')  # Get school year

        # If no student ID is provided, auto-generate one
        if not student_id:
            student_id = generate_student_id(course, year_level_obj)

        # Check if student ID already exists
        if Student.objects.filter(student_id=student_id).exists():
            error_message = "The Student ID already exists."

        if not error_message:
            semester = get_object_or_404(Semester, id=semester_id)

            # Create the student instance
            student = Student(
                first_name=first_name,
                middle_name=middle_name,
                last_name=last_name,
                age=age,
                course_name=course,
                year_level=year_level_obj,
                semester=semester,
                section_name=selected_section,  # Use the selected section
                status=status,
                student_id=student_id,
                gender=gender,  # Set gender
                birthday=birthday,  # Save birthday
                address=address,  # Save address
                email_address=email_address,  # Save email address
                school_year=school_year,  # Save school year
            )

            try:
                # Save the student to the database
                student.save()


                return redirect('view_students', course_name=course.course_name, year_level=year_level_obj.year_level, section_name=selected_section.section_name)
            except IntegrityError:
                error_message = "Student ID already exist."

    # Fetch semesters and subjects for the form
    semesters = Semester.objects.all()
    subjects = Subject.objects.all()

    context = {
        'course': course,
        'year_level': year_level_obj,
        'selected_section': selected_section,  # Ensure you're passing the selected section
        'semesters': semesters,
        'subjects': subjects,
        'error_message': error_message,
        'student': Student(),  # Empty student object to render the form
    }

    return render(request, 'add_student.html', context)



def generate_student_id(course, year_level):
    """Generate student ID for new students."""
    year = timezone.now().year
    last_student = Student.objects.filter(student_id__startswith=str(year)).order_by('-student_id').first()
    next_id = 1  # Default to the first student ID of the year

    if last_student:
        last_id = int(last_student.student_id[4:])  # Extract the last 5 digits
        next_id = last_id + 1  # Increment the ID

    return f"{year}{next_id:05}"





def edit_student(request, student_id):
    # Fetch the student object by its ID
    student = get_object_or_404(Student, student_id=student_id)

    # Fetch all necessary data
    courses = Course.objects.all()
    year_levels = Yearlevel.objects.all()
    sections = Section.objects.filter(course_name=student.course_name, year_level=student.year_level)
    semesters = Semester.objects.all()
    subjects = Subject.objects.all()

    if request.method == "POST":
        # Get form data (including student_id)
        student_id = request.POST.get("student_id")
        first_name = request.POST.get("firstName")
        middle_name = request.POST.get("middleName", "")  # Allow empty middle name
        last_name = request.POST.get("lastName")
        age = request.POST.get("age")
        semester_id = request.POST.get("semester")
        section_id = request.POST.get("section")
        status = request.POST.get("status")
        gender = request.POST.get("gender")  # Get gender
        subject_ids = request.POST.getlist("subjects")
        course_id = request.POST.get("course")
        year_level_id = request.POST.get("yearLevel")
        birthday = request.POST.get('birthday')  # Get birthday
        address = request.POST.get('address')  # Get address
        email_address = request.POST.get('email_address')  # Get email address
        school_year = request.POST.get('school_year')  # Get school year

        # Fetch related objects
        course = get_object_or_404(Course, id=course_id)
        year_level_obj = get_object_or_404(Yearlevel, id=year_level_id)
        semester = get_object_or_404(Semester, id=semester_id)
        section = get_object_or_404(Section, id=section_id, course_name=course, year_level=year_level_obj)

        # Update student information, including the student_id
        student.student_id = student_id  # Assign updated student_id
        student.first_name = first_name
        student.middle_name = middle_name
        student.last_name = last_name
        student.age = age
        student.course_name = course
        student.year_level = year_level_obj
        student.semester = semester
        student.section_name = section
        student.status = status
        student.gender = gender  # Update gender
        student.birthday = birthday  # Save birthday
        student.address = address  # Save address
        student.email_address = email_address  # Save email address
        student.school_year = school_year  # Save school year

        # Handle potential IntegrityError if student_id is not unique
        try:
            # Save the changes to the student
            student.save()

            # Update subjects (Many-to-Many relationship)
            student.subjects.set(subject_ids)

            # Redirect to the student list or detail view
            return redirect("view_students", course_name=course.course_name, year_level=year_level_obj.year_level, section_name=section.section_name)

        except IntegrityError:
            # Catch the IntegrityError if student_id is already taken and display an error message
            context = {
                'student': student,
                "courses": courses,
                "year_levels": year_levels,
                "sections": sections,
                "semesters": semesters,
                "subjects": subjects,
                'error': 'This Student ID is already taken. Please choose a different one.',
            }
            return render(request, "edit_student.html", context)

    # Prepare context data for the form
    context = {
        'student': student,
        "courses": courses,
        "year_levels": year_levels,
        "sections": sections,
        "semesters": semesters,
        "subjects": subjects,
    }

    return render(request, "edit_student.html", context)

def delete_student(request, student_id):
    # Fetch the student record by its ID
    student = get_object_or_404(Student, id=student_id)

    # Get related information to redirect after deletion
    course_name = student.course_name.course_name  # Assuming course_name is a ForeignKey to Course model
    year_level = student.year_level.year_level  # Assuming year_level is a ForeignKey to Yearlevel model
    section_name = student.section_name.section_name  # Assuming section_name is a ForeignKey to Section model

    # Check if the request method is POST before deleting
    if request.method == 'POST':
        # Perform the deletion
        student.delete()
        messages.success(request, "Student deleted successfully!")
        
        # Redirect to the student list or a relevant page after deletion
        return redirect('view_students', course_name=course_name, year_level=year_level, section_name=section_name)

    # If not POST request, just redirect (optionally, you could display a confirmation page)
    return redirect('view_students', course_name=course_name, year_level=year_level, section_name=section_name)


def get_year_levels(request):
    course_id = request.GET.get('course_id')
    year_levels = Yearlevel.objects.filter(course_name_id=course_id)

    # Prepare year levels to send back as a response
    year_level_data = [{"id": year.id, "year_level": year.year_level} for year in year_levels]
    
    return JsonResponse({'year_levels': year_level_data})

# View to fetch sections based on the selected course and year level
def get_sections(request):
    course_id = request.GET.get('course_id')
    year_level_id = request.GET.get('year_level_id')
    sections = Section.objects.filter(course_name_id=course_id, year_level_id=year_level_id)

    # Prepare sections to send back as a response
    section_data = [{"id": section.id, "section_name": section.section_name} for section in sections]
    
    return JsonResponse({'sections': section_data})

def add_section(request, course_id, year_level_id):
    # Get the course and year level from the database
    course = get_object_or_404(Course, id=course_id)
    year_level = get_object_or_404(Yearlevel, id=year_level_id)

    if request.method == 'POST':
        # Handle form submission
        section_name = request.POST.get('sectionName')
        capacity = request.POST.get('capacity')

        # Create the new section object
        new_section = Section(
            section_name=section_name,
            capacity=capacity,
            course_name=course,
            year_level=year_level
        )
        new_section.save()

        # Redirect back to the sections page or any other desired page
        return redirect('sections', course_name=course.course_name, year_level=year_level.year_level)

    return render(request, 'add_section.html', {
        'course': course,
        'year_level': year_level
    })

def edit_section(request, section_id):
    # Fetch the section object by its ID
    section = get_object_or_404(Section, id=section_id)
    course = section.course_name
    year_level_obj = section.year_level

    # Fetch all courses and year levels
    courses = Course.objects.all()
    year_levels = Yearlevel.objects.all()

    if request.method == "POST":
        # Get form data
        section_name = request.POST.get("sectionName")
        course_id = request.POST.get("course")
        year_level_id = request.POST.get("yearLevel")

        # Validation for section name
        if not section_name:
            messages.error(request, "Section name is required.")
            return render(
                request, "edit_section.html", {
                    "section": section,
                    "courses": courses,
                    "year_levels": year_levels,
                }
            )

        # Fetch related objects for course and year level
        try:
            course = get_object_or_404(Course, id=course_id)
            year_level_obj = get_object_or_404(Yearlevel, id=year_level_id)
        except (Course.DoesNotExist, Yearlevel.DoesNotExist):
            messages.error(request, "Invalid course or year level.")
            return render(
                request, "edit_section.html", {
                    "section": section,
                    "courses": courses,
                    "year_levels": year_levels,
                }
            )

        # Update section information
        section.section_name = section_name
        section.course_name = course
        section.year_level = year_level_obj
        section.save()

        # Redirect to the section list or detail view
        return redirect("view_sections", course_name=course.course_name, year_level=year_level_obj.year_level)

    # Prepare context data for the form
    context = {
        "section": section,
        "courses": courses,
        "year_levels": year_levels,
    }
    return render(request, "edit_section.html", context)


def delete_section(request, section_id):
    # Fetch the section object by its ID
    section = get_object_or_404(Section, id=section_id)

    # Get the course_name and year_level from the section object
    course_name = section.course_name.course_name  # Assuming course_name is a ForeignKey to Course model
    year_level = section.year_level.year_level  # Assuming year_level is a ForeignKey to Yearlevel model

    # Perform the deletion
    section.delete()

    # Redirect to the view_section page with course_name and year_level
    return redirect('sections', course_name=course_name, year_level=year_level)

def assign_subjects(request, student_id):
    # Get the student and all available subjects
    student = get_object_or_404(Student, student_id=student_id) 
    all_subjects = Subject.objects.all()

    if request.method == "POST":
        # Get the selected subjects from the form
        subject_ids = request.POST.getlist("subjects")
        # Assign selected subjects to the student
        student.subjects.set(subject_ids)
        student.save()  # Save the updated student data

        # Redirect back to the edit_student page with the correct student ID
        return redirect('edit_student', student_id=student.id)

    context = {
        'student': student,
        'all_subjects': all_subjects,
    }

    return render(request, 'assign_subject.html', context)

def add_subject(request, course_id, year_level_id, student_id):
    course = get_object_or_404(Course, id=course_id)
    year_level = get_object_or_404(Yearlevel, id=year_level_id)
    student = get_object_or_404(Student, id=student_id, course_name=course, year_level=year_level)

    error_message = None  # Variable to hold the error message

    if request.method == 'POST':
        # Get selected subject details from the form
        subject_code = request.POST.get('subject_code')
        subject_name = request.POST.get('subject_name')
        subject_unit = request.POST.get('subject_unit')
        section_time = request.POST.get('section_time', 'TBA')
        section_day = request.POST.get('section_day', 'TBA')
        section_room = request.POST.get('section_room', 'TBA')

        # Check if the subject already exists
        if Subject.objects.filter(subject_code=subject_code, course_name=course, year_level=year_level).exists():
            error_message = "The subject code already exists for this course and year level."
        else:
            # If no error, proceed to create or update the subject
            subject = Subject(
                subject_code=subject_code,
                subject_name=subject_name,
                subject_unit=subject_unit,
                section_time=section_time,
                section_day=section_day,
                section_room=section_room,
                course_name=course,
                year_level=year_level,
            )

            try:
                subject.save()  # Save the new subject
                student.subjects.add(subject)  # Add the subject to the student's subjects
                return redirect('view_student_subjects', course_name=course.course_name, year_level=year_level.year_level, section_name=student.section_name.section_name, student_id=student.id)
            except IntegrityError:
                error_message = "An error occurred while saving the subject."  # Handle any database errors (e.g. unique constraints)

    return render(request, 'add_subject.html', {
        'course': course,
        'year_level': year_level,
        'student': student,
        'error_message': error_message,  # Pass error message to the template
    })

def edit_subject(request, subject_id):
    # Fetch the subject
    subject = get_object_or_404(Subject, id=subject_id)

    # Get the first associated student
    student = subject.students.first()  # Adjust this based on the correct related_name
    if not student:
        return render(request, 'edit_subject.html', {
            'subject': subject,
            'error': 'No student is associated with this subject.'
        })

    # Get associated course, year level, and section
    course = subject.course_name
    year_level = subject.year_level
    section = student.section_name

    if request.method == 'POST':
        # Update subject fields
        subject.subject_code = request.POST.get('subject_code', '').strip()
        subject.subject_name = request.POST.get('subject_name', '').strip()
        subject.subject_unit = request.POST.get('subject_unit', '').strip()
        subject.section_time = request.POST.get('section_time', '').strip() or 'TBA'
        subject.section_day = request.POST.get('section_day', '').strip() or 'TBA'
        subject.section_room = request.POST.get('section_room', '').strip() or 'TBA'

        try:
            subject.save()
            # Redirect to view_student_subjects
            return redirect('view_student_subjects',
                            course_name=course.course_name,
                            year_level=year_level.year_level,
                            section_name=section.section_name,
                            student_id=student.id)
        except ValidationError as e:
            return render(request, 'edit_subject.html', {'subject': subject, 'error': str(e)})

    return render(request, 'edit_subject.html', {'subject': subject})

def delete_subject(request, subject_id):
    # Fetch the subject object by its ID
    subject = get_object_or_404(Subject, id=subject_id)

    # Get the related course and year level
    course_name = subject.course_name.course_name
    year_level = subject.year_level.year_level

    # Fetch the first student associated with this subject
    first_student = subject.students.first()

    # Check if there are students associated with the subject
    if first_student:
        # Delete the subject
        subject.delete()

        # Redirect to the first student's subject page
        return redirect('view_student_subjects', 
                        course_name=course_name, 
                        year_level=year_level,
                        section_name=first_student.section_name.section_name,  # Assuming section_name is in the student model
                        student_id=first_student.id)
    else:
        # If no students are associated, just delete the subject and redirect
        subject.delete()
        return redirect('subject_list')  # Redirect to subject list or wherever you want