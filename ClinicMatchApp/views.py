from multiprocessing import context
import random
import re
import os
import time
from re import S
# from tkinter import W
from django.db.models import Sum, Prefetch
from django.db.models.functions import Coalesce
from django.shortcuts import render, get_object_or_404, redirect
from ClinicMatchApp.models import ClinicNumberHandler, Clinic, Major, Professor, Student
from .forms import ClinicForm, get_ClinicNumbersFormset, StudentForm, StudentProfileForm, ProfessorProfileForm
from social_django.models import UserSocialAuth
from .models import Student as StudentModel
from django.db.models.fields import NOT_PROVIDED
from django.http import HttpResponse, JsonResponse
import csv
import io
from django.core.exceptions import ObjectDoesNotExist
from dotenv import load_dotenv
from .serializers import StudentSerializer
import logging
logger = logging.getLogger(__name__)
# Create your views here.

load_dotenv()

def login_check(request): #Runs post login. Import 
    code = request.session.pop('professor_code', None)
    user = request.user
    print(user)
    if user.is_anonymous:
        print("User is Anonymous")
        return
    if not user.email: #If the user is manually created then skip this process, this is mostly used for dev and won't be in production
        print("User has no email associated, cannot create Student object.")
        return
    
    # This is to allow admin panel access. Contact IRT to figure out a better way to do this later.
    try:
        UserAuthObject = UserSocialAuth.objects.get(user=user)
    except ObjectDoesNotExist:
        print(f"No UserSocialAuth found for {user.username} — probably a local/admin login. Skipping student sync.")
        return
    
    if code is None:
        print("Code DNE")
        #Student login post, return to index

        created, updated = Student.objects.get_or_create(userAuth=UserAuthObject, first_name=user.first_name,
                                                    last_name=user.last_name,
                                                    email=user.email)

        if created:
            print("Created new Student object for user:", user)
        else:
            print("Found existing Student object for user:", user)

        
    else:

        if code == os.getenv('PROFESSOR_KEY'):
            created, updated = Professor.objects.get_or_create(userAuth=UserAuthObject, first_name=user.first_name,
                                                        last_name=user.last_name,
                                                        email=user.email)
        else:
            return

def loginView(request):
    if request.method == "POST":
        code = request.POST.get('professor_code')
        request.session['professor_code'] = code
        
        return redirect('social:begin', backend='google-oauth2') # Proceed to the normal social auth screen, now that the code was saved
        

        pass
    else:
        return render(request, 'login.html')

def index(request):
    login_check(request) # Passing for profile verifcation, this might need to be relocated.
    context = {}
    try:
        user = request.user
    except:
        user = None
    if user and user.is_authenticated:
        #Since they're logged in, let them view the profile and Project View buttons

        #Checking whether its a student or professor
        userAuth = UserSocialAuth.objects.filter(user=user).first()

        if userAuth is None:
            context['status'] = "none"

        student_object = StudentModel.objects.filter(userAuth=userAuth).first()
        professor_object = Professor.objects.filter(userAuth=userAuth).first()

        if professor_object:
            context['status'] = "professor"
        else:
            context['status'] = "student"

        context['logged_in'] = True
    return render(request, 'index.html', context=context)

def clinicViewList(request): # Lists prfoessors clinics if edits are needed to be made, will connect directly to clinicView
    user = request.user
    userAuth = UserSocialAuth.objects.get(user=user)
    professor = Professor.objects.get(userAuth=userAuth)
    if request.method == "GET":
        print(professor)
        clinics = professor.current_clinic.all()
        context = {}
        context['clinics'] = clinics
        print(clinics)

        return render(request, 'clinicsubmitlist.html', context)

    pass

def clinicView(request):
    print("Doing stuff")
    if request.method == "GET":
        clinic_id = request.GET.get('clinic_id')
        if clinic_id:
            major_dict = [{'major': major} for major in ClinicNumberHandler.objects.all()] #Creating a dictionary of all the majors in the database to be used to populate the formset
            clinic = Clinic.objects.get(id=clinic_id)
            context = {}
            context['form'] = ClinicForm(instance=clinic)
            context['majors'] = Major.objects.all()        # <-- add this line
            ClinicNumbersFormset = get_ClinicNumbersFormset()  # Get the formset class with the correct number of extra forms
            formset = ClinicNumbersFormset(
                    initial=major_dict,
                    instance=clinic,
                    queryset=clinic.numberHandler.all()
                    )
            print(formset)
            
            context['formset'] = formset
            return render(request, 'clinicsubmit.html', context)
            pass
        else:

            major_dict = [{'major': major} for major in ClinicNumberHandler.objects.all()] #Creating a dictionary of all the majors in the database to be used to populate the formset
            context = {}
            form = ClinicForm()
            context['form'] = form
            context['majors'] = Major.objects.all()        # <-- add this line
            ClinicNumbersFormset = get_ClinicNumbersFormset()  # Get the formset class with the correct number of extra forms
            formset = ClinicNumbersFormset(initial=major_dict) #Populate the formset with a major field for each major in the database
            
            context['formset'] = formset
        

            return render(request, 'clinicsubmit.html', context)
    elif request.method == "POST":
        user = request.user
        userAuth = UserSocialAuth.objects.get(user=user)
        professor = Professor.objects.get(userAuth=userAuth)
        print("Posting Request Recieved")
        print(request.POST)
        form = ClinicForm(request.POST)
        ClinicNumbersFormset = get_ClinicNumbersFormset()  # Get the formset class with the correct number of extra forms
        if request.POST['clinic_type'] == "general":
            formset = None
        else:

            formset = ClinicNumbersFormset(request.POST)
        
        if form.is_valid() and (formset is None or formset.is_valid() ):
            clinic_instance = form.save() #Save the clinic instance first to get the foreign key relationship
            clinic_instance.clinic_mgmt.add(professor)
            professor.current_clinic.add(clinic_instance)
            clinic_instance.save()
            professor.save()
            if formset:
                formset.instance = clinic_instance
                formset.save()
            else:
                #general clinic, so take the min and max vals
                clinic_instance.min = request.POST['numberHandler-0-min'] 
                clinic_instance.max = request.POST['numberHandler-0-max']
                clinic_instance.save()
                pass
        else:
            print("Form or Formset Invalid")
            print("Form Errors:", form.errors)
            print("Formset Errors:", formset.non_form_errors())

        context = {}
        context['status'] = "professor"
        context['logged_in'] = True
        return render(request, 'index.html', context)


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
        for clinic in Clinic.objects.all(): #removes selected clinics from the main section
            if clinic in selected_clinics:
                continue
            clinics.append(clinic)

        print("PROJECT VIEW REQUESTED")
        context = {}
        context['clinics'] = clinics
        context['selected_clinics'] = selected_clinics
        context['majors'] = majors
        context['student'] = studentObject
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
        
        # Recalculate popularity index
        clinics = [] 
        for clinic in Clinic.objects.all(): 
            clinic.pop_index = 0  # Reset popularity index before recalculation
            clinic.save()
            if clinic in selected_clinics: #creates selected clinics list
                continue
            clinics.append(clinic)
        for student in StudentModel.objects.all():
            first_choice = Clinic.objects.get(title=student.choices.first().title) if student.choices.exists() else None
            if first_choice:
                first_choice.pop_index += 1
                first_choice.save()
        return render(request, "projectview.html", context={'clinics': clinics, 'selected_clinics': selected_clinics, 'majors': Major.objects.all()})

def clinicManagementHomepage(request):
    context = {}
    context['majors'] = Major.objects.all()
    return render(request, "clinicmanagement.html", context=context)

def clinicManagementView(request, title):
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

def studentManagementView(request):
    context = {}
    context['majors'] = Major.objects.all()
    return render(request, "studentmanagement.html", context=context)

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

    # Prepare student email representations for matching
    student_email = (student.email or "").strip().lower()
    student_ref = student_email.split('@')[0] if student_email else ""

    requested_by = []
    # Find clinics that mention this student in their requested_students field
    for clinic in Clinic.objects.all():
        rs = clinic.requested_students

        if not rs:
            continue

        # Normalize requested_students into a list of strings
        if isinstance(rs, (list, tuple)):
            candidates = [str(x).strip().lower() for x in rs if x]
        else:
            # If stored as a comma-separated string
            candidates = [s.strip().lower() for s in str(rs).split(',') if s.strip()]

        # Check whether any candidate matches either the local-part or full email
        matched = False
        for cand in candidates:
            # Remove any mailto: prefix if present
            cand_norm = cand.replace('mailto:', '').strip().lower()
            if cand_norm == student_ref or cand_norm == student_email:
                matched = True
                break

        if matched:
            requested_by.append(
                clinic.title
            )

    return JsonResponse({
        'id': student.id,
        'name': (student.first_name or '') + ' ' + (student.last_name or ''),
        'major': str(student.major) if student.major else None,
        'email': student.email,
        'banner_id': student.banner_id,
        'j_or_s': student.j_or_s,
        'choices': [clinic.title for clinic in student.choices.all()],
        'assigned_clinic': str(student.assigned_clinic.title) if student.assigned_clinic else None,
        'initial_assignment': str(student.initial_assignment.title) if student.initial_assignment else None,
        'requested_by': requested_by if requested_by else [],
        'alternative_major': student.alternative_major,
    })

def major_api(request, major_id):
    major = get_object_or_404(Major, pk=major_id)
    return JsonResponse({
        'id': major.id,
        'major': major.major,
        'color': major.color,
    })

def mapStudentsToClinics(request):
    students = StudentModel.objects.all()
    clinics = Clinic.objects.all()
    student_clinic_map = {}

    for clinic in clinics:
        clinic.current_students.clear()  # Clear current students for each clinic
        clinic.save()
    try:
        for student in students:
            assigned_clinic = student.assigned_clinic
            if assigned_clinic:
                assigned_clinic.current_students.add(student)
                assigned_clinic.save()
        return JsonResponse({'status': 'success'})
    except Exception as e:
        print("Error mapping students to clinics:", str(e))
        return JsonResponse({'error': str(e)}, status=500) 

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import JSONParser

from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt  # If you want to exempt CSRF for now

@api_view(['POST'])
#@permission_classes([IsAuthenticatedOrReadOnly])
@csrf_exempt
def importStudents(request):
    if request.method == "POST":
        serializer = StudentSerializer(data=request.data, many=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            for student_data in serializer.validated_data:
                studentExists = StudentModel.objects.get(email=student_data['email']) if StudentModel.objects.filter(email=student_data['email']).exists() else None
                if studentExists:
                    continue
                student = StudentModel(first_name=student_data['first_name'],
                                       last_name=student_data['last_name'],
                                       email=student_data['email'],
                                       banner_id=int(student_data['banner_id']),
                                       j_or_s=student_data['j_or_s'],
                                       major=student_data['major'],
                                       alternative_major=student_data['alternative_major'])
                student.save()
            return JsonResponse({'status': 'success'})
            
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt  # If you want to exempt CSRF for now
from django.db import transaction
import json

@require_POST
@csrf_exempt
def update_student_assignments(request):
    """
    Accepts JSON: { "assignments": [ { "student_id": <id>, "clinic_id": <id|null> }, ... ] }
    Updates student.assigned_clinic (allows clinic_id null to unassign).
    Returns summary of updates and any errors.
    """
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    assignments = data.get('assignments', [])
    if not isinstance(assignments, (list, tuple)):
        return JsonResponse({'error': 'assignments must be a list'}, status=400)

    results = {'updated': [], 'skipped': [], 'errors': []}

    # Use a transaction so either all succeed or none (optional)
    with transaction.atomic():
        for a in assignments:
            try:
                student_id = a.get('student_id')
                clinic_id = a.get('clinic_id', None)

                if student_id is None:
                    results['skipped'].append({'reason': 'missing student_id', 'assignment': a})
                    continue

                # Try to coerce numeric strings to ints
                try:
                    student_pk = int(student_id)
                except (ValueError, TypeError):
                    student_pk = student_id

                student = StudentModel.objects.get(pk=student_pk)

                # Handle unassign (null / None / "null")
                if clinic_id is None or clinic_id == 'null' or clinic_id == '':
                    student.assigned_clinic = None
                    student.save()
                    results['updated'].append({'student_id': student.id, 'clinic_id': None})
                    continue

                # Coerce clinic id
                try:
                    clinic_pk = int(clinic_id)
                except (ValueError, TypeError):
                    clinic_pk = clinic_id

                clinic = Clinic.objects.get(pk=clinic_pk)
                student.assigned_clinic = clinic
                student.save()

                results['updated'].append({'student_id': student.id, 'clinic_id': clinic.id})

            except StudentModel.DoesNotExist:
                results['errors'].append({'assignment': a, 'error': 'Student does not exist'})
                continue
            except Clinic.DoesNotExist:
                results['errors'].append({'assignment': a, 'error': 'Clinic does not exist'})
                continue
            except Exception as e:
                # catch unexpected errors but keep processing
                results['errors'].append({'assignment': a, 'error': str(e)})
                continue

    return JsonResponse(results)
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
        primaryManager = re.match(r'^\s*=HYPERLINK\("[^"]*",\s*"([^"]*)"\)\s*$', primaryManager).group(1) #Regex generated via CHATGPT
        primaryManagerEmail = project.email
        links = []
        for link in project.project_url_links:
            print(link)
            link = re.match(r'=HYPERLINK\(\s*"([^"]+)"\s*,\s*"([^"]+)"\s*\)', link) #Regex generated via CHATGPT
            if link  != None:
                link = link.group(1)
                links.append(link)
        
        clinic = Clinic(
            title=project.project_name.strip(),
            department= Major.objects.get(major=project.department.upper()) if Major.objects.filter(major=project.department.upper()).exists() else None,
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
        professor.current_clinic.add(clinic)
        professor.save()
        
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
        print("Row:", student.first_name, student.last_name, "raw major:", repr(student.major))
        # Defensive normalization
        raw_major = (student.major or "").strip()
        major_token = raw_major.upper()

        # default
        alt_major = False

        # Map special cases (EET→ECE, MET→ME)
        if major_token == "EET":
            mapped_major_code = "ECE"
            alt_major = True
        elif major_token == "MET":
            mapped_major_code = "ME"
            alt_major = True
        else:
            # Use the token as-is for lookup (ME, ECE, CHE, etc.)
            mapped_major_code = major_token

        # Try to find a Major row robustly (case-insensitive)
        major_obj = Major.objects.filter(major__iexact=mapped_major_code).first()
        if not major_obj:
            # Fallback: if mapped didn't match, try original token
            major_obj = Major.objects.filter(major__iexact=raw_major).first()

        if not major_obj:
            # Still no major found — print warning and skip or decide fallback policy
            print(f"⚠️ Major not found for student {student.first_name} {student.last_name}: "
                  f"raw='{raw_major}', mapped='{mapped_major_code}'")
            # Option A: continue (skip this student)
            # continue
            # Option B: set major_obj to None and allow student.major null in DB
            major_obj = None

        year = (student.year or "J")[0].upper()  # default to J if missing
        studentObj = StudentModel(
            first_name=student.first_name,
            last_name=student.last_name,
            email=student.email,
            banner_id=random.randint(100000000, 999999999),
            j_or_s=year,
            major=major_obj,
            alternative_major=alt_major,
        )
        # Debug print before save
        print("Saving student:", studentObj.first_name, studentObj.last_name,
              "major:", getattr(major_obj, 'major', None), "alternative_major:", alt_major)
        studentObj.save()

        # choices handling (unchanged)
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

        studentObj.choices.set(set(choices))
        studentObj.save()


    return render(request, 'index.html', {})





def profileView(request):
    user = request.user
    user = UserSocialAuth.objects.get(user=user)
    student_object = StudentModel.objects.filter(userAuth=user).first()
    professor_object = Professor.objects.filter(userAuth=user).first()

    if request.method == "POST":
        if student_object:
            form = StudentProfileForm(request.POST, instance=student_object) #"Binding" the form. This basically tells django to store all the data, and gives us the option to save it. It does this by automatically matching the request fields to the form fields if they match. The instance is added to cover stuff not included in the form
            context = {"user": request.user,
                    "profile": student_object,
                    "profileForm": form,
                    "status": "student"
                    }
            if form.is_valid():
                form.save()
            return render(request, "profile.html", context=context)
        elif professor_object:
            form = ProfessorProfileForm(request.POST, instance=professor_object)
            context = {
                "user": request.user,
                "profile": professor_object,
                "profileForm": form,
                "status": "professor"
            }
            if form.is_valid():
                form.save()
            return render(request, "profile.html", context=context)
    
    else:
        if student_object:
            profile_form = StudentProfileForm(request.GET, instance=student_object) #Since the profile exists, automatically populate it from the existing data. The form should always be valid by default since its pulled stragiht from the model.
            context = {"user": request.user,
                    "profile": student_object,
                    "profileForm": profile_form,
                    "status": "student",
                    }
            return render(request, "profile.html", context=context)
        elif professor_object:
            form = ProfessorProfileForm(request.GET, instance=professor_object)
            context = {
                "user": request.user,
                "profile": professor_object,
                "profileForm": form,
                "status": "professor"
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
                        student.initial_assignment = clinic
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
    return JsonResponse({'status': 'success'})




def matchStudent(student):
    for choice in student.choices.all(): #Going through their choices
        clinic = choice
        clinicNumberHandlers = clinic.numberHandler.all()
        for handler in clinicNumberHandlers:
            if handler.general:
                if clinic.current_students.count() < handler.max:
                    student.assigned_clinic = clinic
                    student.initial_assignment = clinic
                    clinic.current_students.add(student)
                    clinic.save()
                    student.save()
                    break
            else:
                if student.major == handler.major:
                    if clinic.current_students.count() < handler.max:
                        student.assigned_clinic = clinic
                        student.initial_assignment = clinic
                        clinic.current_students.add(student)
                        clinic.save()
                        student.save()
                        break
        if student.assigned_clinic is not None:
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
    # eet= Major(major="EET", color="#F9CB9C")
    # eet.save()
    # met= Major(major="MET", color="#A4C2F4")
    # met.save()
    return render(request, "index.html", {})





# Statistic APIs
def mostPopularClinics(request):
    clinics = Clinic.objects.all()
    data = []
    for clinic in clinics:
        data.append({
            'title': clinic.title,
            'requests': StudentModel.objects.filter(choices=clinic).count(),
            'major_color': clinic.department.color if clinic.department else "#ffffff",
        })
    return JsonResponse(data, safe=False)

def mostPopularProfessors(request):
    profs = Professor.objects.all()
    data = []
    for prof in profs:
        request = 0
        current_clinics = prof.current_clinic.all()
        for clinic in current_clinics:
            request += StudentModel.objects.filter(choices=clinic).count()
        data.append({
            'name': prof.last_name,
            'requests': request,
        })
    return JsonResponse(data, safe=False)

def mostPopularDepartment(request):
    majors = Major.objects.all()
    data = []
    for major in majors:
        request = 0
        for student in StudentModel.objects.all():
            for choice in student.choices.all():
                if major.major == choice.department.major:
                    request += 1
        data.append({
            'major': major.major,
            'color': major.color,
            'requests': request,
        })
    return JsonResponse(data, safe=False)

def proposedProjectsByDepartment(request):
    majors = Major.objects.all()
    clinics = Clinic.objects.all()
    data = []
    for major in majors:
        data.append({
            'major': major.major,
            'color': major.color,
            'proposed': clinics.filter(department=major).count(),
        })
    return JsonResponse(data, safe=False)

def studentSignupsByDepartment(request):
    majors = Major.objects.all()
    students = StudentModel.objects.all()
    data = []
    for major in majors:
        data.append({
            'major': major.major,
            'color': major.color,
            'signups': students.filter(major=major).filter(alternative_major=False).count(),
        })
        #dealing with MET/EET
        if major.major == 'ME':
            data.append({
                'major': 'MET',
                'color': '#A4C2F4',
                'signups': students.filter(major=major).filter(alternative_major=True).count(),
            })
        elif major.major == 'ECE':
            data.append({
                'major': 'EET',
                'color': '#F9CB9C',
                'signups': students.filter(major=major).filter(alternative_major=True).count(),
            })

    return JsonResponse(data, safe=False)

from num2words import num2words
def studentChoiceDistribution(request):
    students = StudentModel.objects.all()
    data = []
    for i in range(1,9):
        data.append({
            'choice': num2words(i, ordinal=True),
            'count': 0,
        })
    data.append({
        'choice': 'none',
        'count': 0,
    })
    for student in students:
        i = 0
        foundClinic = False
        for choice in student.choices.all():
            if student.assigned_clinic:
                if choice.title == student.assigned_clinic.title:
                    data[i]['count'] += 1
                    foundClinic = True
                    break
                i += 1
            else:
                break

        if not foundClinic:
            data[8]['count'] += 1
    
    return JsonResponse(data, safe=False)
