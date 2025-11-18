from django.db import models
from django.forms import ValidationError
from django.db.models.signals import m2m_changed
from sortedm2m.fields import SortedManyToManyField
from colorfield.fields import ColorField
from social_django.models import UserSocialAuth

from django.contrib.auth import get_user_model

CustomUser = get_user_model()

# Models are Stored here.

# Useful Information Below
#######################################
# Anything that ends in Field() is an input method. Users can supply information which will be used when creating an item from a given model
# Methods ending in handler are not their own unique models, rather they are owned and used by other models. Look at ClinicNumberHandler for example. This has its own fields, but is only accessed through a Clinic instance. This was done to ensure dynamic allocation of majors for futureproofing.
# Within all field() methods, you can pass various settings. These include things like whether it can be empty, blank, or maximum input length. Additionally, on_delete=models.CASCADE is used on all modelFields (foreignKeysFields) to ensure the reference will be deleted to prevent issues if a referenced object is deleted.
# related_name is used to define internal names for SortedManyToManyFieldFields. This is done in case of things like the Professor Model, where you have multiple M2M Fields pointing to the same Model. Django uses these names internally to differentiate between the two.
# Fill in more as need #
#######################################
class Major(models.Model):
    major = models.CharField()
    color = ColorField(default='#FFFFFF') #Color associated with the major, used for visualizations

    def __str__(self): #This defines how the models items will be displayed, think of it like toString. Without this it will just say 'model' Object (n) where n is the number assigned to it internally
        return self.major


class Clinic(models.Model):
    title = models.CharField()
    department = models.ForeignKey(Major, on_delete=models.CASCADE, null=True)
    clinic_mgmt = SortedManyToManyField('Professor', related_name="professor_list", null=True, blank=True) #Connects to professor objects
    description = models.TextField(max_length=500, null=True)
    min = models.PositiveIntegerField(null=True, blank=True) # Minimum number of students required for the clinic to run
    max = models.PositiveIntegerField(null=True, blank=True) # Maximum number of students that can be accepted into the clinic
    links = models.CharField(null=True, blank=True) # CSV of links related to the clinic
    requested_students = models.CharField(null=True, blank=True) # CSV of requested students
    current_students = SortedManyToManyField('Student', related_name="current_students_in_clinic", null=True, blank=True) #Connects to student objects
    image = models.FileField(null=True, blank=True, upload_to="clinicImages/")
    links = models.JSONField(default=list, blank=True, null=True)
    pop_index = models.PositiveIntegerField(default=0) #Used to store popularity index during matching process.
    def __init__(self, *args, **kwargs):
        super(Clinic, self).__init__(*args, **kwargs)
        #Create a major field for each major in the database using ClinicNumberHandler
    def __str__(self):
        return f"{self.title} ({self.department})"
    
    def links_list(self): #Helper function to convert the list of links into something the Django HTML can iterate through
        if self.links:
            return [link.strip() for link in self.links.split(',')]
        return []
        
                

class ClinicNumberHandler(models.Model): #Used for dynamically select numbers for each major. Clinic Owns this model via the "major_requirements" related_name trait from the foreignkey
    clinic = models.ForeignKey(Clinic, on_delete=models.CASCADE, related_name="numberHandler", null=True) #Which clinic this min max requirement is related to.
    major = models.ForeignKey(Major, on_delete=models.CASCADE) #Which major this min max requirement is related to.
    general = models.BooleanField(default=False) #If this is a general requirement, not tied to a specific major
    min = models.PositiveIntegerField(null=True, blank=True) #This can be blank or null if this major isnt needed
    max = models.PositiveIntegerField(null=True, blank=True)
    class Meta:
        unique_together = ('clinic', 'major') #Ensure that each clinic can only have one entry per major

class Review(models.Model):
    professor = models.ForeignKey('Professor', on_delete=models.CASCADE, related_name='reviews') # Connect each review to a professor object
    review_text = models.TextField(max_length=500) # Limit the maximum number of characters to 500.
    

class Professor(models.Model):
    userAuth = models.OneToOneField(UserSocialAuth, on_delete=models.CASCADE, null=True, blank=True) #Connects to the UserSocialAuth object created by the social auth library.
    first_name = models.CharField()
    last_name = models.CharField()
    department = models.ForeignKey(Major, on_delete=models.CASCADE, null=True)
    email = models.CharField()
    crn = models.PositiveIntegerField(null=True, blank=True)
    current_clinic = SortedManyToManyField(Clinic, related_name="Active_Clinic", null=True, blank=True) # Connect to a clinic objects
    prev_clinics = SortedManyToManyField(Clinic, related_name="Previous_Clinics", null=True, blank=True) # Connects to clinic objects that previously were ran. When a clinic is done for the semester, it is moved to here.
    prof_reviews = SortedManyToManyField(Review, related_name='prof_review_history', null=True, blank=True)
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"

    
class Student(models.Model):
    userAuth = models.OneToOneField(UserSocialAuth, on_delete=models.CASCADE, null=True, blank=True) #Connects to the UserSocialAuth object created by the social auth library.
    CHOICES = [ #Predefining the choices for students to ensure consistency.
        ('J', 'Junior'),
        ('S', 'Senior'),
    ]
    first_name = models.CharField(null=True)
    last_name = models.CharField(null=True)
    email = models.CharField(null=True)
    banner_id = models.PositiveIntegerField(null=True)
    j_or_s = models.CharField(choices=CHOICES, null=True, blank=True, max_length=1) #Junior or Senior
    major = models.ForeignKey(Major, on_delete=models.CASCADE, null=True)

    choices = SortedManyToManyField(Clinic, related_name='Students_top_8_Choices')
    assigned_clinic = models.ForeignKey(Clinic, on_delete=models.CASCADE, related_name='Assigned_Output', null=True, blank=True)
    initial_assignment = models.ForeignKey(Clinic, on_delete=models.CASCADE, related_name='Initial_Assignments', null=True, blank=True)
    alternative_major = models.BooleanField(default=False) #Used to handle majors like MET/EET who's students are treated as a different major but need to be differentiated in the database
    link = models.CharField(blank=False, null=True)
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.major})"



def choicesChanged(sender, **kwargs):
    if kwargs['instance'].choices.count() > 8: #Check if the amount of selected clinics is > 8. This function is triggered when the m2m signal is raised, see below.
        raise ValidationError("Cannot choose more than 8 clinics.")

m2m_changed.connect(choicesChanged, sender = Student.choices.through) #Connecting the m2m_changed signal to the choicesChanged function. This will trigger whenever the major field is changed or saved.
