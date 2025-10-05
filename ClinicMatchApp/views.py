from django.shortcuts import render

from ClinicMatchApp.models import ClinicNumberHandler, Clinic, Major, Professor
from .forms import ClinicForm, ClinicNumbersFormset, StudentForm

# Create your views here.

def index(request):
    print("HOME PAGE REQUESTED")
    return render(request, 'index.html')


def clinicView(request):
    print("Doing stuff")
    if request.method == "GET":
        major_dict = [{'major': major} for major in ClinicNumberHandler.objects.all()] #Creating a dictionary of all the majors in the database to be used to populate the formset
        context = {}
        form = ClinicForm()
        context['form'] = form
        formset = ClinicNumbersFormset(initial=major_dict) #Populate the formset with a major field for each major in the database
        
        context['formset'] = formset
        

        return render(request, 'clinicsubmit.html', context)
    elif request.method == "POST":
        print("Posting Request Recieved")
        print(request.POST)
        form = ClinicForm(request.POST)
        formset = ClinicNumbersFormset(request.POST)
        if form.is_valid() and formset.is_valid():
            clinic_instance = form.save() #Save the clinic instance first to get the foreign key relationship
            formset.instance = clinic_instance
            formset.save()
        else:
            print("Form or Formset Invalid")
            print("Form Errors:", form.errors)
            print("Formset Errors:", formset.non_form_errors())

        context = {}
        return render(request, 'clinicsubmit.html', context)


def studentView(request):
    if request.method == "GET":
        context = {}
        form = StudentForm()
        context['form'] = form
        return render(request, 'studentsubmit.html', context)
    elif request.method == "POST":
        print(request.POST)
        form = StudentForm(request.POST)
        
        if form.is_valid():
            form.save()
        else:
            print("Form Errors:", form.errors)
        #Getting the form to adjust the top 8 choices
        choices =  []

        for item in request.POST: # Grabbing the 8 choices from the request
            if 'Choice' in item:
                choices.append(request.POST[item])

        studentObject = form.instance
        studentObject.choices.set(choices) 
        studentObject.save() # Save the object now that their top choices have been saved
        context = {}
        context['form'] = form
        return render(request, 'studentsubmit.html', context)
















# TESTING STUFF
import SortProjects

def loadProjectsFromCSV(request):
    projects = SortProjects.get_project_data()
    """self.timestamp = row[0]
        self.email = row[1]
        self.manager_last_names = row[2].split(',') if row[2] else []
        self.department = row[3]
        self.project_name = row[4]
        self.project_description = row[5]
        self.is_externally_funded = row[6]
        self.project_url_links = row[7].split(',') if row[7] else []
        self.project_image = row[8]
        self.external_funding_source = row[9]
        self.student_requests = row[10]
        self.request_classification = row[11]
        self.min_students_required = (row[12])
        self.max_students_for_operation = (row[13])
        self.me_students = (row[14])
        self.che_students = (row[15])
        self.ece_students = (row[16])
        self.cee_students = (row[17])
        self.exe_students = (row[18])
        self.bme_students = (row[19])
        self.eet_students =  99999  # Default to a large number if not provided
        self.met_students =  99999  # Default to a large number if not provided
        self.max_me_students = (row[20])
        self.max_che_students = (row[21])
        self.max_ece_students = (row[22])
        self.max_cee_students = (row[23])
        self.max_exe_students = (row[24])
        self.max_bme_students = (row[25])
        self.max_eet_students = 99999  # Default to a large number if not provided
        self.max_met_students = 99999
        self.project_type = row[26]
        self.project_justification = row[27]
        self.current_students = []
        self.current_me_students = 0
        self.current_che_students = 0
        self.current_ece_students = 0
        self.current_cee_students = 0
        self.current_exe_students = 0
        self.current_bme_students = 0
        self.current_eet_students = 0
        self.current_met_students = 0
        self.project_ID = 0"""

    for project in projects:
        primaryManager = project.manager_last_names[0] 
        primaryManagerEmail = project.email

        
        clinic = Clinic(
            title=project.project_name,
            department= Major.objects.get(major=project.department) if Major.objects.filter(major=project.department).exists() else None,
            description=project.project_description,
            links= project.project_url_links,
            requestedStudents= project.student_requests,
        )
        professor, created = Professor.objects.get_or_create(
            last_name=primaryManager,
            email=primaryManagerEmail,
        )
        clinic.save()
        if created:
            professor.save()
            clinic.clinic_mgmt.add(professor)
        else:
            clinic.clinic_mgmt.add(professor)

        #Handling The ClinicNumberHandler entries for each major

        if 'General:' in project.request_classification :
            clinic.general = True
            clinic.min = project.min_students_required
            clinic.max = project.max_students_for_operation
            
        else:
            clinic.general = False
            clinic.min = project.me_students + project.che_students + project.ece_students + project.cee_students + project.exe_students + project.bme_students
            clinic.max = project.max_me_students + project.max_che_students + project.max_ece_students + project.max_cee_students + project.max_exe_students + project.max_bme_students

            for major in Major.objects.all():
                numberHandler = ClinicNumberHandler()
                numberHandler.clinic = clinic
                numberHandler.major = major
                
                match major.major:
                    case "ME":
                        numberHandler.max = int(project.max_me_students) or 0
                        numberHandler.min = int(project.me_students) or 0
                    case "ECE":
                        numberHandler.max = int(project.max_ece_students) or 0
                        numberHandler.min = int(project.ece_students) or 0
                    case "CHE":
                        numberHandler.max = int(project.max_che_students) or 0
                        numberHandler.min = int(project.che_students) or 0
                    case "CEE":
                        numberHandler.max = int(project.max_cee_students) or 0
                        numberHandler.min = int(project.cee_students) or 0
                    case "BME":
                        numberHandler.max = int(project.max_bme_students) or 0
                        numberHandler.min = int(project.bme_students) or 0
                    case "EXE":
                        numberHandler.max = int(project.max_exe_students) or 0
                        numberHandler.min = int(project.exe_students) or 0
                    #Add other cases here as more majors appear.
                numberHandler.save()

            clinic.save()

    return render(request, 'index.html', {})