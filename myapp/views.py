from django.shortcuts import render, redirect,  get_object_or_404
from django.http import Http404,JsonResponse
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib import messages
from django.contrib.auth.models import User
from .models import Course, Yearlevel, Section, Student, Subject, Instructor,Semester
from django.db.models import Q


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

    return render(request, 'login.html')
def logout(request):
    # Clear all messages from the session manually before logging out
    if '_messages' in request.session:
        del request.session['_messages']  # This removes the stored messages from the session

    # Log the user out
    auth_logout(request)

    # Redirect back to the login page after logout
    return redirect('login')

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
        # Split the search query into individual words (in case it's a full name)
        search_parts = search_query.split()
        
        # Create a Q object for the filter
        filter_query = Q()
        
        # For each part of the name (first, middle, last), search across all name fields
        for part in search_parts:
            filter_query |= Q(first_name__icontains=part) | Q(middle_name__icontains=part) | Q(last_name__icontains=part)
        
        # Apply the filter to the students queryset
        students = students.filter(filter_query)

    context = {
        'course': course,
        'year': year,
        'section': section,
        'students': students,
        'search_query': search_query,  # Pass the search query to retain it in the search bar
    }
    
    return render(request, 'student.html', context)
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


def add_student(request, course_id, year_level):
    # Retrieve the course and year_level from the database using the URL parameters
    course = get_object_or_404(Course, id=course_id)
    year_level_obj = get_object_or_404(Yearlevel, year_level=year_level)

    # Ensure that the selected course is associated with the selected year level
    if course not in year_level_obj.courses.all():
        raise Http404("Invalid course and year level combination.")

    # Fetch sections based on the selected course and year level
    sections = Section.objects.filter(course_name=course, year_level=year_level_obj)

    # If the form is submitted (POST request)
    if request.method == 'POST':
        first_name = request.POST.get('firstName')
        middle_name = request.POST.get('middleName')
        last_name = request.POST.get('lastName')
        age = request.POST.get('age')
        semester_id = request.POST.get('semester')  # Get the selected semester ID
        section_name = request.POST.get('section')
        status = request.POST.get('status')
        subject_ids = request.POST.getlist('subjects')

        # Get the selected semester and section
        semester = get_object_or_404(Semester, id=semester_id)  # Fetch by ID, not name
        section = get_object_or_404(Section, section_name=section_name, course_name=course, year_level=year_level_obj)

        # Create a new student instance
        student = Student.objects.create(
            first_name=first_name,
            middle_name=middle_name,
            last_name=last_name,
            age=age,
            course_name=course,
            year_level=year_level_obj,
            semester=semester,
            section_name=section,
            status=status
        )

        # Add subjects to the student
        for subject_id in subject_ids:
            subject = get_object_or_404(Subject, id=subject_id)
            student.subjects.add(subject)

        # Redirect to the view_students page after saving
        return redirect('view_students', course_name=course.course_name, year_level=year_level_obj.year_level, section_name=section.section_name)

    # Fetch all semesters and subjects for the form
    semesters = Semester.objects.all()
    subjects = Subject.objects.all()

    # Context data to pass to the template
    context = {
        'course': course,
        'year_level': year_level_obj,
        'sections': sections,
        'semesters': semesters,
        'subjects': subjects,
    }

    return render(request, 'add_student.html', context)


def edit_student(request, student_id):
    # Fetch the student object by its ID
    student = get_object_or_404(Student, id=student_id)
    course = student.course_name
    year_level_obj = student.year_level
    section = student.section_name

    # Fetch all courses, year levels, semesters, and subjects
    courses = Course.objects.all()
    year_levels = Yearlevel.objects.all()
    semesters = Semester.objects.all()
    subjects = Subject.objects.all()

    # Filter the sections based on the student's course and year level
    sections = Section.objects.filter(course_name=course, year_level=year_level_obj)

    if request.method == "POST":
        # Get form data
        first_name = request.POST.get("firstName")
        middle_name = request.POST.get("middleName") or None  # Allow empty middle name
        last_name = request.POST.get("lastName")
        age = request.POST.get("age")
        semester_id = request.POST.get("semester")
        section_id = request.POST.get("section")
        status = request.POST.get("status")
        subject_ids = request.POST.getlist("subjects")
        course_id = request.POST.get("course")
        year_level_id = request.POST.get("yearLevel")

        # Validation for age
        if not age:
            messages.error(request, "Age is required.")
            return render(
                request, "edit_student.html", {
                    "student": student,
                    "courses": courses,
                    "year_levels": year_levels,
                    "sections": sections,
                    "semesters": semesters,
                    "subjects": subjects,
                }
            )
        try:
            age = int(age)
            if age <= 0:
                raise ValueError("Age must be a positive number.")
        except ValueError as e:
            messages.error(request, str(e))
            return render(
                request, "edit_student.html", {
                    "student": student,
                    "courses": courses,
                    "year_levels": year_levels,
                    "sections": sections,
                    "semesters": semesters,
                    "subjects": subjects,
                }
            )

        # Fetch related objects
        course = get_object_or_404(Course, id=course_id)
        year_level_obj = get_object_or_404(Yearlevel, id=year_level_id)
        semester = get_object_or_404(Semester, id=semester_id)
        section = get_object_or_404(Section, id=section_id, course_name=course, year_level=year_level_obj)

        # Update student information
        student.first_name = first_name
        student.middle_name = middle_name  # Now allows None if middle name is empty
        student.last_name = last_name
        student.age = age
        student.course_name = course
        student.year_level = year_level_obj
        student.semester = semester
        student.section_name = section
        student.status = status
        student.save()

        # Update subjects (Many-to-Many relationship)
        student.subjects.set(subject_ids)

        # Redirect to the student list or detail view
        return redirect("view_students", course_name=course.course_name, year_level=year_level_obj.year_level, section_name=section.section_name)

    # Prepare context data for the form
    context = {
        "student": student,
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

def add_subject(request, course_id, year_level_id, student_id):
    # Get the course, year level, and student objects
    course = get_object_or_404(Course, id=course_id)
    year_level = get_object_or_404(Yearlevel, id=year_level_id)
    student = get_object_or_404(Student, id=student_id, course_name=course, year_level=year_level)

    if request.method == 'POST':
        # Get selected subject from the form
        subject_code = request.POST.get('subject_code')
        subject_name = request.POST.get('subject_name')
        subject_unit = request.POST.get('subject_unit')
        section_time = request.POST.get('section_time', 'TBA')
        section_day = request.POST.get('section_day', 'TBA')
        section_room = request.POST.get('section_room', 'TBA')

        # Create the new subject object
        new_subject = Subject(
            course_name=course,
            year_level=year_level,
            subject_code=subject_code,
            subject_name=subject_name,
            subject_unit=subject_unit,
            section_time=section_time,
            section_day=section_day,
            section_room=section_room
        )
        new_subject.save()

        # Add subject to student
        student.subjects.add(new_subject)

        # Redirect back to the student subject page or any other desired page
        return redirect('view_student_subjects', 
                        course_name=course.course_name, 
                        year_level=year_level.year_level,
                        section_name=student.section_name.section_name,
                        student_id=student.id)

    return render(request, 'add_subject.html', {
        'course': course,
        'year_level': year_level,
        'student': student
    })

def edit_subject(request, subject_id):
    subject = get_object_or_404(Subject, id=subject_id)

    if request.method == 'POST':
        # Handle the form submission, update the subject
        subject.subject_code = request.POST.get('subject_code')
        subject.subject_name = request.POST.get('subject_name')
        subject.subject_unit = request.POST.get('subject_unit')
        subject.section_time = request.POST.get('section_time')
        subject.section_day = request.POST.get('section_day')
        subject.section_room = request.POST.get('section_room')
        subject.save()

        return redirect('view_student_subjects', 
                        course_name=subject.course_name.course_name, 
                        year_level=subject.year_level.year_level, 
                        section_name=subject.section_name.section_name, 
                        student_id=subject.student.id)

    return render(request, 'edit_subject.html', {'subject': subject})