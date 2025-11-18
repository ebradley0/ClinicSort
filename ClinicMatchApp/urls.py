from django.urls import path

from . import views
from .models import Major

urlpatterns = [
    path("ClinicMatch", views.index, name="index"),
    path("clinicsubmission/", views.clinicView, name="clinicView"),
    path("studentsubmission/", views.studentView, name="studentView"),
    path("loadProjectsFromCSV/", views.loadProjectsFromCSV, name="loadProjectsFromCSV"),
    path("loadStudentsFromCSV/", views.loadStudentsFromCSV, name="loadStudentsFromCSV"),
    path("projectView/", views.projectView, name="projectView" ),
    path("clinicManagementView/", views.clinicManagementHomepage, name="clinicManagementViewHomepage"), # for testing, will change later
    path("clinicManagementView/<str:title>/", views.clinicManagementView, name="clinicManagementView"),
    path("profile/", views.profileView, name="profile"),
    path("logout/", views.logoutView, name="logout"),
    path('api/student/<int:student_id>/', views.student_detail_api, name='student-detail-api'),
    path('api/update-student-assignments/', views.update_student_assignments, name='update_student_assignments'),
    path('MatchingProcess/', views.runMatchingAlgorithm, name='runMatchingAlgorithm'),
    path('createMajor/', views.createMajor, name='createMajor'),
    path('api/major/<int:major_id>/', views.major_api, name='major-api'),
    path('api/mapStudentsToClinics/', views.mapStudentsToClinics, name='map_students_to_clinics'),
    path('login/', views.loginView, name="loginView"),
    path('login-check/', views.login_check, name=""),
    path('studentmanagement/', views.studentManagementView, name='studentManagementView'),
    path('importStudents/', views.importStudents, name='importStudents'),

    # Statistics APIs
    path('api/statistics/mostPopularClinics/', views.mostPopularClinics, name='mostPopularClinics'),
    path('api/statistics/mostPopularProfessors/', views.mostPopularProfessors, name='mostPopularProfessors'),
    path('api/statistics/mostPopularDepartment/', views.mostPopularDepartment, name='mostPopularDepartment'),
    path('api/statistics/proposedProjectsByDepartment/', views.proposedProjectsByDepartment, name='proposedProjectsByDepartment'),
    path('api/statistics/studentSignupsByDepartment/', views.studentSignupsByDepartment, name='studentSignupsByDepartment'),
    path('api/statistics/studentChoiceDistribution/', views.studentChoiceDistribution, name='studentChoiceDistribution'),

    path('', views.index, name='index' ), #Remove this when migrating to etr, this is just done for testing sake to maintain consistency.
]
""" 
for major in Major.objects.all():
    urlpatterns.append(path(f"clinicManagementView/{major.major}/", views.clinicManagementView, {'title': f'{major.major}'}, name=f"clinicManagementView_{major.major}")) """