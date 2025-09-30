from django import forms
from django.forms import ModelForm, inlineformset_factory, modelformset_factory
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
        
extraMajorCount = Major.objects.count() if Major.objects.count() > 0 else 1 # Calculate the amount of forms we need, 1 per major
            

ClinicNumbersFormset = inlineformset_factory(Clinic,  ClinicNumberHandler, form=ClinicNumbersForm, extra=extraMajorCount, can_delete=False,) #Formset for the major requirement numbers associated with a clinic

