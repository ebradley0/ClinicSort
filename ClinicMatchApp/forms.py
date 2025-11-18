from enum import auto
from django import forms
from django.forms import ModelForm, inlineformset_factory
from .models import Student, Major, Clinic, Professor, Review, ClinicNumberHandler



class ClinicForm(forms.ModelForm):

    

    class Meta:
        model = Clinic
        fields = '__all__' #Use all fields from the model
        
        


#Creating a basic form template to be sued by ClinicNumberHandler. These will be used by a formset to store them all together
class ClinicNumbersForm(forms.ModelForm):
    class Meta:
        model = ClinicNumberHandler
        fields = '__all__' #Use all fields from the model
    def __init__(self, *args, **kwargs):
        super(ClinicNumbersForm, self).__init__(*args, **kwargs)
        self.fields['major'].disabled = True #Disable the major field so users cant change it. It will still look like a dropdown, but we can handle this with css.
        #This is a very scuffed workaround for trying to dynamically populate a form, but it works
        
#extraMajorCount = Major.objects.count() if Major.objects.count() > 0 else 1 # Calculate the amount of forms we need, 1 per major
            

#ClinicNumbersFormset = inlineformset_factory(Clinic,  ClinicNumberHandler, form=ClinicNumbersForm, extra=extraMajorCount, can_delete=False,) #Formset for the major requirement numbers associated with a clinic

def get_ClinicNumbersFormset(extra=None):
    from .models import Major  # Local import to avoid circular issues
    if extra is None:
        try:
            extra = Major.objects.count()
            if extra == 0:
                extra = 1
        except:
            extra = 1  # Fallback during migrations or early stage
    return inlineformset_factory(
        Clinic,
        ClinicNumberHandler,
        form=ClinicNumbersForm,
        extra=extra,
        can_delete=False,
    )

class StudentProfileForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['banner_id', 'j_or_s', 'major', 'alternative_major'] 
        labels = {
            'banner_id': 'Banner ID',
            'j_or_s': 'Grade Level (J/S)',
            'major': 'Major',
            'alternative_major': 'EET/MET',
        }

class ProfessorProfileForm(forms.ModelForm):
    class Meta:
        model = Professor
        fields = ['department', 'crn']


class StudentForm(forms.ModelForm):
    first_choice = forms.ModelChoiceField(queryset=Clinic.objects.all(), required=True)
    second_choice = forms.ModelChoiceField(queryset=Clinic.objects.all(), required=True)
    third_choice = forms.ModelChoiceField(queryset=Clinic.objects.all(), required=True)
    fourth_choice = forms.ModelChoiceField(queryset=Clinic.objects.all(), required=True)
    fifth_choice = forms.ModelChoiceField(queryset=Clinic.objects.all(), required=True)
    sixth_choice = forms.ModelChoiceField(queryset=Clinic.objects.all(), required=True)
    seventh_choice = forms.ModelChoiceField(queryset=Clinic.objects.all(), required=True)
    eighth_choice = forms.ModelChoiceField(queryset=Clinic.objects.all(), required=True)
    class Meta:
        model = Student
        fields = ['first_name', 'last_name', 'email', 'banner_id', 'j_or_s', 'major', 'first_choice', 'second_choice', 'third_choice', 'fourth_choice', 'fifth_choice', 'sixth_choice', 'seventh_choice', 'eighth_choice'] #Use all fields from the model except choices, we'll handle that manually
    

