import os
import pygsheets
import csv
import SortProjects


home_directory = os.getcwd()
csvPath = home_directory + '\Student Clinic Request (Responses) [Spring 2025] - Form (1).csv'
Seniors = []
Juniors = []
failed_students = []
class Student:
    def __init__(self, row):
        self.timestamp = row[0]
        self.email = row[1]
        self.first_name = row[2]
        self.last_name = row[3]
        self.major = row[4]
        self.year = row[5]
        self.project_1 = row[6]
        self.project_1_experience = row[7]
        self.project_2 = row[8]
        self.project_2_experience = row[9]
        self.project_3 = row[10]
        self.project_3_experience = row[11]
        self.project_4 = row[12]
        self.project_4_experience = row[13]
        self.project_5 = row[14]
        self.project_5_experience = row[15]
        self.project_6 = row[16]
        self.project_6_experience = row[17]
        self.project_7 = row[18]
        self.project_7_experience = row[19]
        self.project_8 = row[20]
        self.project_8_experience = row[21]
        self.electronic_signature = row[22]
        self.resume = row[23]
        self.linkedin = row[24]


with open(csvPath, 'r', encoding='utf-8') as csvfile:
    reader = csv.reader(csvfile)
    next(reader)  # Skip the header row
    Students = []
    for row in reader:
        if len(row) > 1:  # Ensure the row is not empty
            Students.append(Student(row))

#Student class with fields for Timestamp	Email Address	First Name:	Last Name:	Major:	Year:	Project 1:	I have _________ on the above project before.	Project 2:	I have _________ on the above project before.	Project 3:	I have _________ on the above project before.	Project 4:	I have _________ on the above project before.	Project 5:	I have _________ on the above project before.	Project 6:	I have _________ on the above project before.	Project 7:	I have _________ on the above project before.	Project 8:	I have _________ on the above project before.	Electronic Signature:	Resume:	LinkedIn
Projects = SortProjects.get_project_data()


def normalize(s):
    return s.strip().lower().replace('\r', '').replace('\n', '').replace('\xa0', ' ')

for student in Students:
   
    if student.year == 'SENIOR':
        Seniors.append(student)
    elif student.year == 'JUNIOR':
        Juniors.append(student)

for project in Projects:
    #Handling Priority Student Requests
    requested_students = project.student_requests.split(',')
    for student in requested_students:
        student = student.strip()
        
        if project.max_students_for_operation == '':
            project.max_students_for_operation = 9999
        if student and len(project.current_students) <=  int(project.max_students_for_operation): # Ensure the project can still accept students
            # Add student to the project
            if student not in project.current_students:
                student_object = next((s for s in Students if s.email == student + '@students.rowan.edu' or s.email == student + '@rowan.edu'), None)
                project.current_students.append(student_object)
            #Check if student requested the project as #1
            student_object = next((s for s in Students if s.email == student + '@students.rowan.edu' or s.email == student + '@rowan.edu'), None)
            if student_object is None:
            
                failed_students.append(student)
                continue
            if student_object.year == 'Senior':
                Seniors.remove(student_object)
            elif student_object.year == 'Junior':
                Juniors.remove(student_object)
            student_major = student_object.major
            if student_major == 'ME':
                project.current_me_students += 1
            elif student_major == 'ChE':
                project.current_che_students += 1
            elif student_major == 'ECE': 
                project.current_ece_students += 1
            elif student_major == 'CEE':
                project.current_cee_students += 1
            elif student_major == 'EXE':
                project.current_exe_students += 1
            elif student_major == 'BME':
                project.current_bme_students += 1
            elif student_major == 'EET':
                project.current_eet_students += 1
         


def filter_student(student):
    print(f"Filtering student: {student.email}")
    #Filter through the students projects based on priority, trying to slot them into their top choices
    student_projects = [
        student.project_1,
        student.project_2,
        student.project_3,
        student.project_4,
        student.project_5,
        student.project_6,
        student.project_7,
        student.project_8]
    student_major = student.major
    print(student_projects)

    
    
    for project_name in student_projects:
        project_name = project_name.strip()
        if project_name:
           
            projectJunk = project_name.split(' - ')
            
            project_name = projectJunk[1].strip()
            
            project = next((p for p in Projects if (p.project_name.strip()) == (project_name.strip())), None)

            major_counts_map = {
                    'ME': 'current_me_students',
                    'ChE': 'current_che_students',
                    'ECE': 'current_ece_students',
                    'CEE': 'current_cee_students',
                    'EXE': 'current_exe_students',
                    'BME': 'current_bme_students',
                    'EET': 'current_eet_students',
                    'MET': 'current_met_students'
                }
            major_required_map = {
                    'ME': "me_students",
                    'ChE': "che_students",
                    'ECE': "ece_students",
                    'CEE': "cee_students",
                    'EXE': "exe_students",
                    'BME': "bme_students",
                    'EET': "eet_students",
                    'MET': "met_students"
                    
                }

            currentAttribute = major_counts_map.get(student_major, None)
            RequiredAttribute = major_required_map.get(student_major, None)

            print(student_major, currentAttribute, RequiredAttribute)
            if project and len(project.current_students) < int(project.max_students_for_operation):
                #Check if the students major matches the project requirements
                if int(getattr(project, currentAttribute)) < int(getattr(project, RequiredAttribute)): #Check if the project can accept more students of this major
                    # Check if the student is already in the project
                    
                    # Check if the project can still accept students
                    if len(project.current_students) < int(project.max_students_for_operation):
                        # Add student to the project
                        if student not in project.current_students:
                            project.current_students.append(student)
                            getattr(project, currentAttribute) + 1
                            print(f"Added {student.email} to project {project_name}")
                            return True
    
                        



for senior in Seniors:
    
    print(f"Filtering senior: {senior.email}")   
    if not filter_student(senior):
        print(f"Could not add Senior {senior} to any project.")
        failed_students.append(senior.email)

for junior in Juniors:
    if not filter_student(junior):
        print(f"Could not add Junior {junior} to any project.")
        failed_students.append(junior.email)



for project in Projects:
    print(f"Project: {project.project_name},\n Current Students: {[s.email for s in project.current_students if s]},\n Max Students: {project.max_students_for_operation}\n, Current Student Count: {len(project.current_students)}\n")


for student in failed_students:
    print(f"Failed to add student: " + student)


print("Total Failed Students: ", len(failed_students)  )
