from django.apps import AppConfig
import sys
from django.contrib.auth.signals import user_logged_in


class ClinicMatchAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'ClinicMatchApp'
    verbose_name = "Clinic Match App"

    
    def ready(self):
        import ClinicMatchApp.signals
        # avoid DB access during migration, makemigrations, tests, etc.
        import ClinicMatchApp.signals  # Import the signals so theyre active for the app
        skip_commands = {"makemigrations", "migrate", "collectstatic", "test", "shell", "check"}
        if any(cmd in sys.argv for cmd in skip_commands):
            return
        try:
            from django.urls import path
            from . import views
            from .models import Major
            import importlib

            urls_module = importlib.import_module("ClinicMatchApp.urls")

            # for major in Major.objects.all():
            #     urls_module.urlpatterns.append(
            #         path(
            #             f"clinicManagementView/{major.major}/",
            #             views.clinicManagementView,
            #             {"title": f"{major.major}"},
            #             name=f"clinicManagementView_{major.major}"
            #         )
            #     )
        except Exception:
            # don't crash startup — optionally log the error
            pass
