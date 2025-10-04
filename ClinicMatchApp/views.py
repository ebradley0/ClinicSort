from django.shortcuts import render

from ClinicMatchApp.models import ClinicNumberHandler
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