from django.urls import path

from . import views
from .models import Major

urlpatterns = [
    path("", views.index, name="index"),
    path("clinicsubmission/", views.clinicView, name="clinicView"),
    path("studentsubmission/", views.studentView, name="studentView"),
    path("loadProjectsFromCSV/", views.loadProjectsFromCSV, name="loadProjectsFromCSV"),
    path("projectView/", views.projectView, name="projectView" ),
    path("clinicManagementView/", views.clinicManagementHomepage, name="clinicManagementView"), # for testing, will change later
    path("clinicManagementView/all/", views.clinicManagementView, {'title': 'all'}, name="clinicManagementView_all"),
]
""" 
for major in Major.objects.all():
    urlpatterns.append(path(f"clinicManagementView/{major.major}/", views.clinicManagementView, {'title': f'{major.major}'}, name=f"clinicManagementView_{major.major}")) """