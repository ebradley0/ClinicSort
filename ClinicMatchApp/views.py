from multiprocessing import context
import random
import re
import os
import time
from re import S
from django.db.models import Sum, Prefetch
from django.db.models.functions import Coalesce
from django.shortcuts import render, get_object_or_404
from ClinicMatchApp.models import ClinicNumberHandler, Clinic, Major, Professor
from .forms import ClinicForm, get_ClinicNumbersFormset, StudentForm, StudentProfileForm
from social_django.models import UserSocialAuth
from .models import Student as StudentModel
from django.db.models.fields import NOT_PROVIDED
from django.http import HttpResponse, JsonResponse
import csv
import io
from dotenv import load_dotenv
# Create your views here.

def index(request):
    context = {}
    try:
        user = request.user
    except:
        user = None
    if user and user.is_authenticated:
        #Since they're logged in, let them view the profile and Project View buttons
        context['logged_in'] = True
    load_dotenv()  # Load environment variables from a .env file if present
    print("HOME PAGE REQUESTED")
    print(os.getenv("GOOGLE_OAUTH2_KEY"))
    return render(request, 'index.html', context=context)


def clinicView(request):
    print("Doing stuff")
    if request.method == "GET":
        major_dict = [{'major': major} for major in ClinicNumberHandler.objects.all()] #Creating a dictionary of all the majors in the database to be used to populate the formset
        context = {}
        form = ClinicForm()
        context['form'] = form
        ClinicNumbersFormset = get_ClinicNumbersFormset()  # Get the formset class with the correct number of extra forms
        formset = ClinicNumbersFormset(initial=major_dict) #Populate the formset with a major field for each major in the database
        
        context['formset'] = formset
        

        return render(request, 'clinicsubmit.html', context)
    elif request.method == "POST":
        print("Posting Request Recieved")
        print(request.POST)
        form = ClinicForm(request.POST)
        ClinicNumbersFormset = get_ClinicNumbersFormset()  # Get the formset class with the correct number of extra forms
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
            if '_choice' in item:
                choices.append(request.POST[item])

        studentObject = form.instance
        studentObject.choices.set(choices) 
        studentObject.save() # Save the object now that their top choices have been saved
        context = {}
        context['form'] = form
        return render(request, 'studentsubmit.html', context)
    

import re
def extract_hyperlink_content(value):
    """
    Extracts the visible text from an Excel-style HYPERLINK formula.
    Example: =HYPERLINK("mailto:test@example.com", "John Doe") → 'John Doe'
    """
    if not isinstance(value, str):
        return value
    match = re.match(r'^\s*=HYPERLINK\("[^"]*",\s*"([^"]*)"\)\s*$', value)
    return match.group(1) if match else value

    for clinic in Clinic.objects.all():
        for manager in clinic.clinic_mgmt.all():
            manager.last_name = extract_hyperlink_content(manager.last_name)
            manager.save()



def projectView(request):
    user  = request.user
    user = UserSocialAuth.objects.get(user=user)
    studentObject = StudentModel.objects.filter(userAuth=user).first()
    selected_clinics = studentObject.choices.all() 
    majors = Major.objects.all()
    if request.method == "GET":
        clinics = []
        for clinic in Clinic.objects.all():
            if clinic in selected_clinics:
                continue
            clinics.append(clinic)
            
        
        print("PROJECT VIEW REQUESTED")
        context = {}
        context['clinics'] = clinics
        context['selected_clinics'] = selected_clinics
        context['majors'] = majors
        return render(request, "projectview.html", context=context)
    elif request.method == "POST":
        print(request.POST)
        clinicSelections = request.POST.getlist('clinic_name')
        studentObject.choices.clear()
        for clinic in clinicSelections: #Go through their choices in order, adding it to choices
            print("Clinic: ", clinic)
            clinic_object = Clinic.objects.get(title=clinic.strip())
            studentObject.choices.add(clinic_object)
        studentObject.save() # Save the instance
        selected_clinics = studentObject.choices.all()
        clinics = [] 
        for clinic in Clinic.objects.all(): #Only display clinics not selected in the clinic array. Selected clinics should auto populate into selection grid. This can probably be a helper function.
            if clinic in selected_clinics:
                continue
            clinics.append(clinic)
        return render(request, "projectview.html", context={'clinics': clinics, 'selected_clinics': selected_clinics, 'majors': Major.objects.all()})

def clinicManagementHomepage(request):
    context = {}
    context['majors'] = Major.objects.all()
    return render(request, "clinicmanagement.html", context=context)

def clinicManagementView(request, title='all'):
    """
    Clinic management view that:
    - Loads all clinics with assigned students.
    - Determines if a clinic is 'general' (has a general number handler).
    - Calculates the min/max capacity based on general or per-major settings.
    """

    # Prefetch assigned students for each clinic
    clinics_qs = Clinic.objects.prefetch_related(
        Prefetch(
            'Assigned_Output',
            queryset=StudentModel.objects.all(),
            to_attr='assigned_students'
        ),
        'numberHandler__major'  # prefetch major info for number handlers
    )

    clinics = list(clinics_qs)

    for clinic in clinics:
        handlers = clinic.numberHandler.all()
        general_handler = next((h for h in handlers if h.general), None)
        clinic.is_general = general_handler is not None

        if clinic.is_general:
            # General clinics always use the general handler or fallback to clinic's own
            clinic.total_min = int(general_handler.min or clinic.min or 0)
            clinic.total_max = int(general_handler.max or clinic.max or 0)

        else:
            # If a specific major filter is applied
            if title != 'all':
                # Find handler for that major
                major_handler = next(
                    (h for h in handlers if str(h.major.major).lower() == str(title).lower()), 
                    None
                )
                if major_handler:
                    clinic.total_min = int(major_handler.min or 0)
                    clinic.total_max = int(major_handler.max or 0)
                else:
                    # Fallback: if no matching major handler exists
                    clinic.total_min = int(clinic.min or 0)
                    clinic.total_max = int(clinic.max or 0)
            else:
                # When viewing all majors, sum across handlers
                clinic.total_min = sum(int(h.min or 0) for h in handlers)
                clinic.total_max = sum(int(h.max or 0) for h in handlers)

                if clinic.total_min == 0 and clinic.total_max == 0:
                    clinic.total_min = int(clinic.min or 0)
                    clinic.total_max = int(clinic.max or 0)

        # Filter assigned_students by major if title != 'all'
        if title != 'all':
            clinic.assigned_students = [
                student for student in clinic.assigned_students
                if student.major.major.lower() == title.lower()
            ]

    # Filter unassigned students by selected major
    if title != 'all':
        unassigned_students = StudentModel.objects.filter(
            assigned_clinic__isnull=True,
            major__major=title
        )
    else:
        unassigned_students = StudentModel.objects.filter(assigned_clinic__isnull=True)

    context = {
        'clinics': clinics,
        'unassigned_students': unassigned_students,
        'title': title,
        'majors': Major.objects.all(),
    }

    return render(request, "clinicmanagementview.html", context=context)

def profileView(request):
    user = request.user
    user = UserSocialAuth.objects.get(user=user)
    profile_object = StudentModel.objects.get(userAuth=user)

    if request.method == "POST":
        form = StudentProfileForm(request.POST, instance=profile_object) #"Binding" the form. This basically tells django to store all the data, and gives us the option to save it. It does this by automatically matching the request fields to the form fields if they match. The instance is added to cover stuff not included in the form
        context = {"user": request.user,
                "profile": profile_object,
                "profileForm": form,
                }
        if form.is_valid():
            form.save()
        return render(request, "profile.html", context=context)
    else:
        profile_form = StudentProfileForm(instance=profile_object) #Since the profile exists, automatically populate it from the existing data. The form should always be valid by default since its pulled stragiht from the model.
        context = {"user": request.user,
                "profile": profile_object,
                "profileForm": profile_form,
                }
        return render(request, "profile.html", context=context)


def logoutView(request):
    from django.contrib.auth import logout #Imported here just for cleanliness, shouldn't be needed outside of this function
    logout(request)
    return render(request, "index.html", {})

def student_detail_api(request, student_id):
    student = get_object_or_404(StudentModel, pk=student_id)
    return JsonResponse({
        'id': student.id,
        'name': student.first_name + ' ' + student.last_name,
        'major': str(student.major),
        'email': student.email,
        'banner_id': student.banner_id,
        'j_or_s': student.j_or_s,
        'choices': [clinic.title for clinic in student.choices.all()],
        'assigned_clinic': str(student.assigned_clinic.title) if student.assigned_clinic else None,
        'initial_assignment': str(student.initial_assignment.title) if student.initial_assignment else None,
        # Add more fields as needed
    })

def major_api(request, major_id):
    major = get_object_or_404(Major, pk=major_id)
    return JsonResponse({
        'id': major.id,
        'major': major.major,
        'color': major.color,
    })


from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt  # If you want to exempt CSRF for now
import json

@require_POST
@csrf_exempt  # You can remove this if you want CSRF protection and handle tokens on frontend
def update_student_assignments(request):
    try:
        data = json.loads(request.body)
        assignments = data.get('assignments', [])

        for assignment in assignments:
            student_id = assignment.get('student_id')
            clinic_id = assignment.get('clinic_id')

            if not student_id or not clinic_id:
                continue

            try:
                student = StudentModel.objects.get(pk=student_id)
                clinic = Clinic.objects.get(pk=clinic_id)
                student.assigned_clinic = clinic
                student.save()
            except StudentModel.DoesNotExist:
                continue
            except Clinic.DoesNotExist:
                continue

        return JsonResponse({'status': 'success'})

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)










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
    project_count = 0
    for project in projects:
        
        primaryManager = project.manager_last_names[0] 
        primaryManager = re.match(r'^\s*=HYPERLINK\("[^"]*",\s*"([^"]*)"\)\s*$', primaryManager).group(1)
        primaryManagerEmail = project.email
        links = []
        for link in project.project_url_links:
            print(link)
            link = re.match(r'=HYPERLINK\(\s*"([^"]+)"\s*,\s*"([^"]+)"\s*\)', link)
            if link  != None:
                link = link.group(1)
                links.append(link)
        
        clinic = Clinic(
            title=project.project_name.strip(),
            department= Major.objects.get(major=project.department) if Major.objects.filter(major=project.department).exists() else None,
            description=project.project_description,
            links= ','.join(links),
            requested_students= project.student_requests,
        )
        clinic.save()
        professor, created = Professor.objects.get_or_create(
            last_name=primaryManager,
            email=primaryManagerEmail,)
        
        if created:
                professor.save()
                clinic.clinic_mgmt.add(professor)
        else:
                clinic.clinic_mgmt.add(professor)
        clinic.save()
        
        for professorEntry in project.manager_last_names[1:]:
                
                professor, created = Professor.objects.get_or_create(
                last_name=professorEntry,
                email="None",
            )
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
            numberHandler = ClinicNumberHandler()
            numberHandler.clinic = clinic
            numberHandler.general = True
            numberHandler.major = Major.objects.get(major="ME")  #Assigning a default major since the field is required, but it won't be used since general is true
            numberHandler.min = project.min_students_required
            numberHandler.max = project.max_students_for_operation
            numberHandler.save()
            clinic.save()
            
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
    
import SortStudents
def loadStudentsFromCSV(request):
    Students = SortStudents.get_student_data()
    for student in Students:
        print(student.first_name, student.last_name, student.major, student.year)
        major = Major.objects.get(major=student.major.upper().strip())
        year = student.year[0].upper() # Mapping to J or S
        studentObj = StudentModel(
            first_name=student.first_name,
            last_name=student.last_name,
            email=student.email,
            banner_id=random.randint(100000000, 999999999), #Generating a random banner ID since we dont have that data
            j_or_s=year,
            major=major,
        )
        studentObj.save()
        choices = []
        for i in range(1, 9):
            project_attr = getattr(student, f"project_{i}", None)
            if not project_attr:
                continue

            parts = project_attr.split(" - ", 1)
            if len(parts) > 1:
                title = parts[1].strip()
                clinic = Clinic.objects.filter(title__iexact=title).first()
                if clinic:
                    choices.append(clinic)
                else:
                    print(f"⚠️ Clinic not found for '{title}'")
            else:
                print(f"⚠️ Malformed project entry: '{project_attr}'")

        # Deduplicate before saving
        studentObj.choices.set(set(choices))
        studentObj.save()


    return render(request, 'index.html', {})





def profileView(request):
    user = request.user
    user = UserSocialAuth.objects.get(user=user)
    profile_object = StudentModel.objects.get(userAuth=user)

    if request.method == "POST":
        form = StudentProfileForm(request.POST, instance=profile_object) #"Binding" the form. This basically tells django to store all the data, and gives us the option to save it. It does this by automatically matching the request fields to the form fields if they match. The instance is added to cover stuff not included in the form
        context = {"user": request.user,
                "profile": profile_object,
                "profileForm": form,
                }
        if form.is_valid():
            form.save()
        return render(request, "profile.html", context=context)
    else:
        profile_form = StudentProfileForm(instance=profile_object) #Since the profile exists, automatically populate it from the existing data. The form should always be valid by default since its pulled stragiht from the model.
        context = {"user": request.user,
                "profile": profile_object,
                "profileForm": profile_form,
                }
        return render(request, "profile.html", context=context)



def runMatchingAlgorithm(request):



    students = StudentModel.objects.all()
    clinics = Clinic.objects.all()

    #Clearing all assignments
    for student in students:
        student.assigned_clinic = None
    for clinic in clinics:
        clinic.current_students.clear()

    juniors = []
    seniors = []
    for student in students:
        match student.j_or_s:
            case 'J':
                juniors.append(student)
            case 'S':
                seniors.append(student)
    #Doing requested student matching

    for clinic in clinics:
        requested_students = clinic.requested_students.split(',')
        if requested_students is not []:
            for student in students:
                
                student_ref = student.email.split('@')[0].strip().lower()
                for requested_student in requested_students:
                    if student_ref == requested_student.strip().lower():
                        student.assigned_clinic = clinic
                        #Removing from juniors and seniors
                        match student.j_or_s:
                            case 'J':
                                juniors = [j for j in juniors if j.id != student.id]
                            case 'S':
                                seniors = [s for s in seniors if s.id != student.id]
                        clinic.current_students.add(student)
                        student.save()
    for student in seniors:
        matchStudent(student)
    for student in juniors:
        matchStudent(student)
    return render(request, "index.html", {})




def matchStudent(student):
    for choice in student.choices.all(): #Going through their choices
            clinic = choice
            clinicNumberHandlers = clinic.numberHandler.all()
            for handler in clinicNumberHandlers:
                if handler.general:
                    if clinic.current_students.count() < handler.max:
                        student.assigned_clinic = clinic
                        clinic.current_students.add(student)
                        clinic.save()
                        student.save()
                        break
                else:
                    if student.major == handler.major:
                        if clinic.current_students.count() < handler.max:
                            student.assigned_clinic = clinic
                            clinic.current_students.add(student)
                            clinic.save()
                            student.save()
                            break

        

def logoutView(request):
    from django.contrib.auth import logout #Imported here just for cleanliness, shouldn't be needed outside of this function
    logout(request)
    return render(request, "index.html", {})

def createMajor(request):
    me= Major(major="ME", color="#C9DAF8")
    me.save()
    ece= Major(major="ECE", color="#FCE5CD")
    ece.save()
    che= Major(major="CHE", color="#D9D2E9")
    che.save()
    cee= Major(major="CEE", color="#D9EAD3")
    cee.save()
    exe= Major(major="EXE", color="#80F2EB")
    exe.save()
    bme= Major(major="BME", color="#E6B8AF")
    bme.save()
    eet= Major(major="EET", color="#F9CB9C")
    eet.save()
    met= Major(major="MET", color="#A4C2F4")
    met.save()
    return render(request, "index.html", {})