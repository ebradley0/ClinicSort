from django.contrib import admin
from .models import Student, Clinic, Major, ClinicNumberHandler, Professor, Review

#Registering various models so admin can access them. This is useful for debugging
admin.site.register(Student)
#admin.site.register(Major)
# Register your models here.
admin.site.register(Professor)
admin.site.register(Review)

class ClinicNumberHandlerInline(admin.TabularInline): # Creating a table for the major requirement numbers to be displayed. This is attached to ClinicAdmin
    
    model = ClinicNumberHandler
    #Display the same number of rows as there are majors in the database
    #extra = Major.objects.count() if Major.objects.count() > 0 else 1
    extra = 1


class ClinicAdmin(admin.ModelAdmin):
    inlines = [ClinicNumberHandlerInline] #Creating a table to display the various requested numbers for each major
admin.site.register(Clinic, ClinicAdmin) #Register it now that we've made out adjustments



admin.site.register(Major)

