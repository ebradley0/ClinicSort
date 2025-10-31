from django.urls import path

from . import views
from .models import Major

urlpatterns = [
    path("", views.index, name="index"),
    path("clinicsubmission/", views.clinicView, name="clinicView"),
    path("studentsubmission/", views.studentView, name="studentView"),
    path("loadProjectsFromCSV/", views.loadProjectsFromCSV, name="loadProjectsFromCSV"),
    path("loadStudentsFromCSV/", views.loadStudentsFromCSV, name="loadStudentsFromCSV"),
    path("projectView/", views.projectView, name="projectView" ),
    path("clinicManagementView/", views.clinicManagementHomepage, name="clinicManagementView"), # for testing, will change later
    path("clinicManagementView/all/", views.clinicManagementView, {'title': 'all'}, name="clinicManagementView_all"),
    path("profile/", views.profileView, name="profile"),
    path("logout/", views.logoutView, name="logout"),
    path('api/student/<int:student_id>/', views.student_detail_api, name='student-detail-api'),
    path('api/update-student-assignments/', views.update_student_assignments, name='update_student_assignments'),
    path('MatchingProcess/', views.runMatchingAlgorithm, name='runMatchingAlgorithm'),
    path('createMajor/', views.createMajor, name='createMajor'),
    path('api/major/<int:major_id>/', views.major_api, name='major-api'),
]
""" 
for major in Major.objects.all():
    urlpatterns.append(path(f"clinicManagementView/{major.major}/", views.clinicManagementView, {'title': f'{major.major}'}, name=f"clinicManagementView_{major.major}")) """