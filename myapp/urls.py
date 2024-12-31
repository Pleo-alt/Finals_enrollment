from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from .views import CustomPasswordResetView
from .views import upload_excel

urlpatterns = [
    # Authentication and Dashboard
    path('', views.login, name='login'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('student_dashboard/', views.student_dashboard, name='student_dashboard'),
    path('student/profile/', views.student_profile, name='student_profile'),
    path('logout/', views.logout, name='logout'),

    # Password reset URLs
    path('password_reset/', CustomPasswordResetView.as_view(template_name='registration/password_reset.html'), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='registration/password_reset_done.html'),name='password_reset_done',),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='registration/password_reset_confirm.html'),name='password_reset_confirm',),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete.html'),name='password_reset_complete',),
    
    # Student management
    path('add_student/<int:course_id>/<str:year_level>/<str:section_name>/', views.add_student, name='add_student'),
    path('edit_student/<int:student_id>/', views.edit_student, name='edit_student'),
    path('delete_student/<int:student_id>/', views.delete_student, name='delete_student'),
    path('get_year_levels/', views.get_year_levels, name='get_year_levels'),
    path('get_sections/', views.get_sections, name='get_sections'),
    path('add_section/<int:course_id>/<int:year_level_id>/', views.add_section, name='add_section'),
    path('edit_section/<int:section_id>/', views.edit_section, name='edit_section'),
    path('delete_section/<int:section_id>/', views.delete_section, name='delete_section'),
    path('search/', views.search_student, name='search_student'),
    
    # Course, Yearlevel, Section, and Student management
    path('<str:course_name>/<str:year_level>/', views.view_section, name='sections'),
    path('view_students/<str:course_name>/<str:year_level>/<str:section_name>/', views.view_students, name='view_students'),

    #Excels
    path('upload-excel/', upload_excel, name='upload_excel'),

    #Downloading pdf
    path('download_students_pdf/<str:course_name>/<str:year_level>/<str:section_name>/', views.download_students_pdf, name='download_students_pdf'),
    
    # Student subjects and instructor views
    path('view_student_subjects/<str:course_name>/<str:year_level>/<str:section_name>/<int:student_id>/', views.view_student_subjects, name='view_student_subjects'),
    path('<int:course_id>/<int:year_level_id>/student/<int:student_id>/add-subject/', views.add_subject, name='add_subject'),
    path('subject/<int:subject_id>/edit/', views.edit_subject, name='edit_subject'),
    path('subject/<int:subject_id>/delete/', views.delete_subject, name='delete_subject'),
    path('<str:course_name>/year/<str:year_level>/section/<str:section_name>/student/<int:student_id>/subject/<str:subject_code>/instructor/', views.view_instructor, name='view_instructor'),
]

# Serve media files during development (if applicable)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
