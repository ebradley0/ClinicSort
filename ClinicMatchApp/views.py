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
    
def projectView(request):
    user  = request.user
    user = UserSocialAuth.objects.get(user=user)
    studentObject = StudentModel.objects.filter(userAuth=user).first()
    selected_clinics = studentObject.choices.all() 
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
        return render(request, "projectview.html", context={'clinics': clinics, 'selected_clinics': selected_clinics})

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

    for project in projects:
        primaryManager = project.manager_last_names[0] 
        primaryManagerEmail = project.email

        
        clinic = Clinic(
            title=project.project_name,
            department= Major.objects.get(major=project.department) if Major.objects.filter(major=project.department).exists() else None,
            description=project.project_description,
            links= project.project_url_links,
            requested_students= project.student_requests,
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
    
import SortStudents
def loadStudentsFromCSV(request):
    Students = SortStudents.get_student_data()
    for student in Students:
        major = Major.objects.get(major=student.major) if Major.objects.filter(major=student.major).exists() else None
        studentObj = SortStudents.Student(
            first_name=student.first_name,
            last_name=student.last_name,
            email=student.email,
            banner_id=random.randint(100000000, 999999999), #Generating a random banner ID since we dont have that data
            j_or_s=student.year,
            major=major,
        )
        studentObj.save()
        choices = []
        for choice in student.choices:
            if Clinic.objects.filter(title=choice).exists():
                choices.append(Clinic.objects.get(title=choice).id)
        studentObj.choices.set(choices)
        studentObj.save()

    return render(request, 'index.html', {})

def loadStudentsFromCSV(request):
    Students = SortStudents.get_student_data()
    for student in Students:
        # studentObj = SortStudents.Student(row) ... studentObj.save()
        # avoid double-wrapping if `student` is already a SortStudents.Student
        if isinstance(student, SortStudents.Student):
            studentObj = student
        else:
            studentObj = SortStudents.Student(student)

        # Build kwargs from parsed Student object (keep only known fields)
        student_kwargs = {}
        for fld in ("email", "first_name", "last_name", "year", "linkedin", "resume", "major"):
            val = getattr(studentObj, fld, None)
            if val not in (None, ""):
                student_kwargs[fld] = val

        # Try to resolve major to a Major instance if your Student model uses a FK
        try:
            student_model_field = StudentModel._meta.get_field("major")
            major_is_fk = getattr(student_model_field, "many_to_one", False)
        except Exception:
            major_is_fk = False

        if major_is_fk and getattr(studentObj, "major", None):
            try:
                major_obj = Major.objects.get(major=studentObj.major)
            except Major.DoesNotExist:
                major_obj = None
            student_kwargs["major"] = major_obj

        # keep only concrete fields present on model
        allowed_fields = {
            f.name for f in StudentModel._meta.get_fields()
            if getattr(f, "concrete", False) and not getattr(f, "many_to_many", False)
        }
        filtered_kwargs = {k: v for k, v in student_kwargs.items() if k in allowed_fields}

        # --- ensure banner_id exists: try extract numeric suffix from email, else generate random unique id ---
        if 'banner_id' in allowed_fields and 'banner_id' not in filtered_kwargs:
            banner_val = None
            email_val = filtered_kwargs.get("email") or getattr(studentObj, "email", None)
            if email_val and "@" in email_val:
                local = email_val.split("@", 1)[0]
                m = re.search(r"(\d+)$", local)
                if m:
                    try:
                        banner_val = int(m.group(1))
                    except Exception:
                        banner_val = None
            # generate a random numeric banner_id if extraction failed
            if banner_val is None:
                # try a few times to avoid collisions
                for _ in range(10):
                    candidate = random.randint(1000000, 9999999)
                    if not StudentModel.objects.filter(banner_id=candidate).exists():
                        banner_val = candidate
                        break
                # last-resort deterministic fallback
                if banner_val is None:
                    banner_val = int(time.time()) % 10000000
            filtered_kwargs['banner_id'] = banner_val
        # --- end banner_id handling ---

        # --- derive j_or_s (Junior/Senior) fallback from year if present ---
        # only set if student model expects 'j_or_s' but CSV did not provide it
        if 'j_or_s' not in filtered_kwargs:
            j_or_s_val = None
            # prefer an explicit attribute if SortStudents set it
            if getattr(studentObj, 'j_or_s', None):
                j_or_s_val = studentObj.j_or_s
            # fall back to year parsing: look for "senior"/"junior" or digit year
            elif getattr(studentObj, 'year', None):
                yr = str(studentObj.year).strip().lower()
                if 'senior' in yr or yr.startswith('s') or yr in ('4','4th'):
                    j_or_s_val = 'S'
                elif 'junior' in yr or yr.startswith('j') or yr in ('3','3rd'):
                    j_or_s_val = 'J'
                else:
                    # numeric fallback (treat >=4 as Senior)
                    try:
                        n = int(yr)
                        j_or_s_val = 'S' if n >= 4 else 'J'
                    except Exception:
                        j_or_s_val = None
            if j_or_s_val is not None and 'j_or_s' in allowed_fields:
                filtered_kwargs['j_or_s'] = j_or_s_val
        # --- end j_or_s derivation ---

        # required field check (same as earlier)
        required_fields = []
        from django.db.models.fields import NOT_PROVIDED
        for f in StudentModel._meta.get_fields():
            if not getattr(f, "concrete", False) or getattr(f, "many_to_many", False) or getattr(f, "auto_created", False):
                continue
            if getattr(f, "primary_key", False):
                continue
            # field is required if null is False and no default provided
            if not getattr(f, "null", False) and getattr(f, "default", NOT_PROVIDED) is NOT_PROVIDED:
                required_fields.append(f.name)

        missing = [name for name in required_fields if name not in filtered_kwargs]

        # Try to derive a banner_id from email (local-part) if banner_id is required
        if "banner_id" in missing:
            email_val = filtered_kwargs.get("email") or getattr(studentObj, "email", None)
            if email_val and "@" in email_val:
                filtered_kwargs["banner_id"] = email_val.split("@", 1)[0]
                missing.remove("banner_id")

        # If required fields remain missing, skip this student and log for review
        if missing:
            print(f"Skipping student import — missing required fields: {missing} — parsed: {getattr(studentObj,'email',None)}")
            continue

        # Try create and handle DB errors gracefully
        try:
            StudentModel.objects.create(**filtered_kwargs)
        except Exception as e:
            print("Failed to create Student:", e, "data:", filtered_kwargs)
            continue

    return render(request, 'index.html', {})

def loadStudentsFromCSV(request):
    # Adjust this path or file source to match your current implementation
    csv_path = '/Users/r0n0than/Documents/ClinicSort/ClinicSort/Student Clinic Request (Responses) - Form.csv'

    created = 0
    skipped = 0
    errors = []
    skipped_examples = []

    try:
        with open(csv_path, newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            rows = list(reader)
    except Exception as e:
        return HttpResponse(f"Failed to open CSV: {e}", status=500)

    # if there's a header row, skip it (adjust as needed)
    if rows and any(cell.lower().startswith('timestamp') or cell.lower().startswith('email') for cell in rows[0]):
        rows = rows[1:]

    for i, row in enumerate(rows, start=1):
        try:
            # If your code already wraps rows into SortStudents.Student, keep that.
            studentObj = SortStudents.Student(row)

            # Build kwargs as before
            student_kwargs = {}
            for fld in ("email", "first_name", "last_name", "year", "linkedin", "resume", "major"):
                val = getattr(studentObj, fld, None)
                if val not in (None, ""):
                    student_kwargs[fld] = val

            # resolve major -> Major instance if needed (same logic you used)
            try:
                student_model_field = StudentModel._meta.get_field("major")
                major_is_fk = getattr(student_model_field, "many_to_one", False)
            except Exception:
                major_is_fk = False

            if major_is_fk and getattr(studentObj, "major", None):
                try:
                    major_obj = Major.objects.get(major=studentObj.major)
                except Major.DoesNotExist:
                    major_obj = None
                student_kwargs["major"] = major_obj

            # keep only concrete fields present on model
            allowed_fields = {
                f.name for f in StudentModel._meta.get_fields()
                if getattr(f, "concrete", False) and not getattr(f, "many_to_many", False)
            }
            filtered_kwargs = {k: v for k, v in student_kwargs.items() if k in allowed_fields}

            # --- ensure banner_id exists: try extract numeric suffix from email, else generate random unique id ---
            if 'banner_id' in allowed_fields and 'banner_id' not in filtered_kwargs:
                banner_val = None
                email_val = filtered_kwargs.get("email") or getattr(studentObj, "email", None)
                if email_val and "@" in email_val:
                    local = email_val.split("@", 1)[0]
                    m = re.search(r"(\d+)$", local)
                    if m:
                        try:
                            banner_val = int(m.group(1))
                        except Exception:
                            banner_val = None
                # generate a random numeric banner_id if extraction failed
                if banner_val is None:
                    # try a few times to avoid collisions
                    for _ in range(10):
                        candidate = random.randint(1000000, 9999999)
                        if not StudentModel.objects.filter(banner_id=candidate).exists():
                            banner_val = candidate
                            break
                    # last-resort deterministic fallback
                    if banner_val is None:
                        banner_val = int(time.time()) % 10000000
                filtered_kwargs['banner_id'] = banner_val
            # --- end banner_id handling ---

            # --- derive j_or_s (Junior/Senior) fallback from year if present ---
            # only set if student model expects 'j_or_s' but CSV did not provide it
            if 'j_or_s' not in filtered_kwargs:
                j_or_s_val = None
                # prefer an explicit attribute if SortStudents set it
                if getattr(studentObj, 'j_or_s', None):
                    j_or_s_val = studentObj.j_or_s
                # fall back to year parsing: look for "senior"/"junior" or digit year
                elif getattr(studentObj, 'year', None):
                    yr = str(studentObj.year).strip().lower()
                    if 'senior' in yr or yr.startswith('s') or yr in ('4','4th'):
                        j_or_s_val = 'S'
                    elif 'junior' in yr or yr.startswith('j') or yr in ('3','3rd'):
                        j_or_s_val = 'J'
                    else:
                        # numeric fallback (treat >=4 as Senior)
                        try:
                            n = int(yr)
                            j_or_s_val = 'S' if n >= 4 else 'J'
                        except Exception:
                            j_or_s_val = None
                if j_or_s_val is not None and 'j_or_s' in allowed_fields:
                    filtered_kwargs['j_or_s'] = j_or_s_val
            # --- end j_or_s derivation ---

            # required field check (same as earlier)
            required_fields = []
            from django.db.models.fields import NOT_PROVIDED
            for f in StudentModel._meta.get_fields():
                if not getattr(f, "concrete", False) or getattr(f, "many_to_many", False) or getattr(f, "auto_created", False):
                    continue
                if getattr(f, "primary_key", False):
                    continue
                if not getattr(f, "null", False) and getattr(f, "default", NOT_PROVIDED) is NOT_PROVIDED:
                    required_fields.append(f.name)
            missing = [name for name in required_fields if name not in filtered_kwargs]

            if missing:
                skipped += 1
                if len(skipped_examples) < 5:
                    skipped_examples.append({"row_index": i, "missing": missing, "parsed": {k: getattr(studentObj, k, None) for k in ("email","first_name","last_name")}})
                continue

            # create
            try:
                StudentModel.objects.create(**filtered_kwargs)
                created += 1
            except Exception as e:
                errors.append({"row": i, "error": str(e), "data": filtered_kwargs})
        except Exception as e:
            errors.append({"row": i, "error": str(e)})
            skipped += 1

    summary = {
        "total_rows": len(rows),
        "created": created,
        "skipped": skipped,
        "errors_count": len(errors),
        "skipped_examples": skipped_examples[:5],
        "errors": errors[:10],
    }
    return HttpResponse(f"Import summary: {summary}")



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