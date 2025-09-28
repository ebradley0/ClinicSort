import os
import pygsheets
import csv
import SortProjects


home_directory = os.getcwd()
csvPath = home_directory + '\Student Clinic Request (Responses) - Form.csv'
Seniors = []
Juniors = []
failed_students = []
Students = []
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

def findStudents():
    pass

with open(csvPath, 'r', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)  # Skip the header row
        Students = []
        for row in reader:
            if len(row) > 1:  # Ensure the row is not empty
                if row[4] == "EET":
                    row[4] = "ECE"  # Change EET to ECE
                if row[4] == "MET":
                    row[4] = "ME"  # Change MET to ME
                Students.append(Student(row))

#Student class with fields for Timestamp	Email Address	First Name:	Last Name:	Major:	Year:	Project 1:	I have _________ on the above project before.	Project 2:	I have _________ on the above project before.	Project 3:	I have _________ on the above project before.	Project 4:	I have _________ on the above project before.	Project 5:	I have _________ on the above project before.	Project 6:	I have _________ on the above project before.	Project 7:	I have _________ on the above project before.	Project 8:	I have _________ on the above project before.	Electronic Signature:	Resume:	LinkedIn
Projects = SortProjects.get_project_data()


def normalize(s):
    return s.strip().lower().replace('\r', '').replace('\n', '').replace('\xa0', ' ')
def SortStudents():
    for student in Students:
    
        if student.year == 'SENIOR':
            Seniors.append(student)
        elif student.year == 'JUNIOR':
            Juniors.append(student)

def matchRequestedStudents():

    for project in Projects:
        #Handling Priority Student Requests
        requested_students = project.student_requests.split(',')
        for student in requested_students:
            student = student.strip()
            if student and len(project.current_students) <=  int(project.max_students_for_operation): # Ensure the project can still accept students
                # Add student to the project
                if student not in project.current_students:
                    student_object = next((s for s in Students if s.email == student + '@students.rowan.edu' or s.email == student + '@rowan.edu'), None)
                    
                    if student_object == None:
                        Warning(f"Student object for {student} not found.")
                        failed_students.append(student)
                        continue
                    first_choice = student_object.project_1
                    first_choice_number = int(first_choice.split(' ')[0].replace('-',''))
                    if first_choice_number != project.project_ID:
                        print(f"Student {student} did not request project {project.project_name} as their first choice.")
                        continue
                    project.current_students.append(student_object)
                #Check if student requested the project as #1
                    print(student)
                    student_object = next((s for s in Students if s.email == student + '@students.rowan.edu' or s.email == student + '@rowan.edu'), None)

                    if student_object.year == 'SENIOR':
                        for s in Seniors:
                            if s.email == student_object.email:
                                Seniors.remove(s)
                                break
                    if student_object.year == 'JUNIOR':
                        for j in Juniors:
                            if j.email == student_object.email:
                                Juniors.remove(j)
                                break
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
    #print(student_projects)

    
    
    for project_name in student_projects:
        project_name = project_name.strip()
        if project_name:

            projectJunk = project_name.split(' ')
            project_name = ' '.join(projectJunk[2:]).strip()  # Combine all parts after the first hyphen
            projectID = int(projectJunk[0].replace('-',''))
            project = next((p for p in Projects if (p.project_ID) == (projectID)), None)
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
                    'ME': "max_me_students",
                    'ChE': "max_che_students",
                    'ECE': "max_ece_students",
                    'CEE': "max_cee_students",
                    'EXE': "max_exe_students",
                    'BME': "max_bme_students",
                    'EET': "max_eet_students",
                    'MET': "max_met_students"
                    
                }

            currentAttribute = major_counts_map.get(student_major, None)
            RequiredAttribute = major_required_map.get(student_major, None)

            #print(project_name, student_major, currentAttribute, RequiredAttribute)
            if len(project.current_students) < int(project.max_students_for_operation):
                #Check if the students major matches the project requirements
                if int(getattr(project, currentAttribute)) < int(getattr(project, RequiredAttribute)): #Check if the project can accept more students of this major
                    # Check if the student is already in the project
                        # Add student to the project
                        if student not in project.current_students:
                            project.current_students.append(student)
                            setattr(project, currentAttribute, getattr(project, currentAttribute) + 1)
                            #print(f"Added {student.email} to project {project_name}")
                            return True
    
                        

def matchStudents():
    SortStudents()
    matchRequestedStudents()
    for senior in Seniors:
        if not filter_student(senior):
        
            failed_students.append(senior.email)

    for junior in Juniors:
        if not filter_student(junior):
            failed_students.append(junior.email)





    totalStudentSlots = 0
    for project in Projects:
        totalStudentSlots += int(project.max_students_for_operation)
        print('===========================================================================')
        print("Project: ", project.project_name, " has ", len(project.current_students), " students assigned out of ", project.max_students_for_operation)
        for student in project.current_students:
            print(" - ", student.first_name, student.last_name, " (", student.email, ")")
        print('===========================================================================')


    print("Total Failed Students: ", len(failed_students) / len(Students) * 100, "%")



ME_color = (
     0.788235294117647,
     0.8549019607843137,
    0.9725490196
)

ChE_color = (
     0.8509803921568627,
     0.8235294117647058,
    0.9137254901960784
)
ECE_color = (
    0.9882352941176471,
     0.8980392156862745,
     0.803921568627451
)
CEE_color = (
  0.8509803921568627,
    0.9176470588235294,
  0.8274509803921568
)
EXE_color = (
    0.5019607843137255,
    0.9490196078431372,
   0.9215686274509803
)
BME_color = (
    0.9019607843137255,
    0.7215686274509804,
    0.6862745098039216
)


def SelectColor(department):
    if department == "ME":
        return {
            "red": ME_color[0],
            "green": ME_color[1],
            "blue": ME_color[2],
        }
    elif department == "ChE":
        return {
            "red": ChE_color[0],
            "green": ChE_color[1],
            "blue": ChE_color[2],
        }
    elif department == "ECE":
        return {
            "red": ECE_color[0],
            "green": ECE_color[1],
            "blue": ECE_color[2],
        }
    elif department == "CEE":
        return {
            "red": CEE_color[0],
            "green": CEE_color[1],
            "blue": CEE_color[2],
        }
    elif department == "EXE":
        return {
            "red": EXE_color[0],
            "green": EXE_color[1],
            "blue": EXE_color[2],
        }
    elif department == "BME":
        return {
            "red": BME_color[0],
            "green": BME_color[1],
            "blue": BME_color[2],
        }
    else:
        return (1, 1, 1)  # Default to white if department not recognized


    
    

def resultOutput():
    findStudents()
    matchStudents()
    client = pygsheets.authorize(client_secret='client_secret.json')
    sheet = client.open('Assignment Output').sheet1  # Select the first page of the sheet
    dataChunk = []
    
    row = 2 #Starting at row 2 to make room for headers
    factor = 0
    meChunks, cheChunks, eceChunks, ceeChunks, exeChunks, bmeChunks = ([] for _ in range(6))
    for project in Projects:
        
        currentStudents = []
        studentString = ''
        for student in project.current_students:
            studentString = student.last_name + ', ' + student.first_name + ' | ' + student.year + ' | ' + student.major + ' | ' + student.email 
            currentStudents.append(studentString)
        #Fix manager_last_names[0] to no longer be a hyperlink
        project.manager_last_names[0] = project.email.split('@')[0]
        minString = project.me_students + ',' + project.che_students + ',' + project.ece_students + ',' + project.cee_students + ',' + project.exe_students + ',' + project.bme_students
        maxString = project.max_me_students + ',' + project.max_che_students + ',' + project.max_ece_students + ',' + project.max_cee_students + ',' + project.max_exe_students + ',' + project.max_bme_students
        dataChunk = [[str(project.project_ID)] + [project.project_name ]+ [','.join(project.manager_last_names)] + [project.department] + [project.is_externally_funded] + [project.request_classification] + [minString ]+ [maxString] + currentStudents]
        #sheet.update_values('A' + str(row), dataChunk)
        
        deptDataChunk = [[str(project.project_ID)] + [project.project_name ]+ [','.join(project.manager_last_names)] + [project.department] + [project.is_externally_funded] + [project.request_classification] + [minString ]+ [maxString] ]

        if project.department == "ME":
            color = {
                "red": ME_color[0] + (1 - ME_color[0]) * factor,  # Slightly lighter
                "green": ME_color[1] + (1 - ME_color[1]) * factor,
                "blue": ME_color[2] + (1 - ME_color[2]) * factor,
    
            }
            meChunks.append(deptDataChunk)

            
        elif project.department == "ChE":
            color = {
                "red": ChE_color[0] + (1 - ChE_color[0]) * factor,
                "green": ChE_color[1] + (1 - ChE_color[1]) * factor,
                "blue": ChE_color[2] + (1 - ChE_color[2]) * factor,
            }
            cheChunks.append(deptDataChunk)
           
        elif project.department == "ECE":
            color = {
                "red": ECE_color[0] + (1 - ECE_color[0]) * factor,
                "green": ECE_color[1] + (1 - ECE_color[1]) * factor,
                "blue": ECE_color[2] + (1 - ECE_color[2]) * factor,
            }
            eceChunks.append(deptDataChunk)
        elif  project.department == "CEE":
            color = {
                "red": CEE_color[0] + (1 - CEE_color[0]) * factor,
                "green": CEE_color[1] + (1 - CEE_color[1]) * factor,
                "blue": CEE_color[2] + (1 - CEE_color[2]) * factor,
            }
            ceeChunks.append(deptDataChunk)
            
        elif project.department == "EXE":
            color = {
                "red": EXE_color[0] + (1 - EXE_color[0]) * factor,
                "green": EXE_color[1] + (1 - EXE_color[1]) * factor,
                "blue": EXE_color[2] + (1 - EXE_color[2]) * factor,
            }
            exeChunks.append(deptDataChunk)
           
        elif project.department == "BME":
            color = {
                "red": BME_color[0] + (1 - BME_color[0]) * factor,
                "green": BME_color[1] + (1 - BME_color[1]) * factor,
                "blue": BME_color[2] + (1 - BME_color[2]) * factor,
            }
            bmeChunks.append(deptDataChunk)
            
       
        currentStudents = []
        format = {
            "numberFormat": {
                
            },
            "backgroundColor": color,
            "backgroundColorStyle":{ "rgbColor": color},
            "borders": {

            },
            "padding": {

            },
            "horizontalAlignment": "CENTER",
            "verticalAlignment": "MIDDLE",
            "textFormat": {
            },
            "textRotation": {
            }
        }




        row += 1
        #sheet.apply_format('A' + str(row) + ':H' + str(row), format)

    #Ordering by dept:
    sheet = client.open('Assignment Output') # Select the first page of the sheet
    sheet = sheet.worksheet('index', 1)
    print("Ordering by dept")
    row = 2
    ProjectsOrdered = []
    for chunk in meChunks:
        color = {
                "red": ME_color[0] + (1 - ME_color[0]) * factor,  # Slightly lighter
                "green": ME_color[1] + (1 - ME_color[1]) * factor,
                "blue": ME_color[2] + (1 - ME_color[2]) * factor,
    
            }
        format = {
            "numberFormat": {
                
            },
            "backgroundColor": color,
            "backgroundColorStyle":{ "rgbColor": color},
            "borders": {

            },
            "padding": {

            },
            "horizontalAlignment": "CENTER",
            "verticalAlignment": "MIDDLE",
            "textFormat": {
            },
            "textRotation": {
            }
        }
        #sheet.update_values('A' + str(row), chunk)
        #sheet.apply_format('A' + str(row) + ':H' + str(row), format)
        row += 1
        project = next((p for p in Projects if p.project_ID == int(chunk[0][0])), None)
        ProjectsOrdered.append(project)
    for chunk in cheChunks:
        color = {
                "red": ChE_color[0] + (1 - ChE_color[0]) * factor,
                "green": ChE_color[1] + (1 - ChE_color[1]) * factor,
                "blue": ChE_color[2] + (1 - ChE_color[2]) * factor,
            }
        format = {
            "numberFormat": {
                
            },
            "backgroundColor": color,
            "backgroundColorStyle":{ "rgbColor": color},
            "borders": {

            },
            "padding": {

            },
            "horizontalAlignment": "CENTER",
            "verticalAlignment": "MIDDLE",
            "textFormat": {
            },
            "textRotation": {
            }
        }
        #sheet.update_values('A' + str(row), chunk)
        #sheet.apply_format('A' + str(row) + ':H' + str(row), format)
        row += 1
        project = next((p for p in Projects if p.project_ID == int(chunk[0][0])), None)
        ProjectsOrdered.append(project)
    for chunk in eceChunks:
        color = {
                "red": ECE_color[0] + (1 - ECE_color[0]) * factor,
                "green": ECE_color[1] + (1 - ECE_color[1]) * factor,
                "blue": ECE_color[2] + (1 - ECE_color[2]) * factor,
            }
        format = {
            "numberFormat": {
                
            },
            "backgroundColor": color,
            "backgroundColorStyle":{ "rgbColor": color},
            "borders": {

            },
            "padding": {

            },
            "horizontalAlignment": "CENTER",
            "verticalAlignment": "MIDDLE",
            "textFormat": {
            },
            "textRotation": {
            }
        }
        #sheet.update_values('A' + str(row), chunk)
        #sheet.apply_format('A' + str(row) + ':H' + str(row), format)
        row += 1
        project = next((p for p in Projects if p.project_ID == int(chunk[0][0])), None)
        ProjectsOrdered.append(project)
    for chunk in ceeChunks:
        color = {
                "red": CEE_color[0] + (1 - CEE_color[0]) * factor,
                "green": CEE_color[1] + (1 - CEE_color[1]) * factor,
                "blue": CEE_color[2] + (1 - CEE_color[2]) * factor,
            }
        format = {
            "numberFormat": {
                
            },
            "backgroundColor": color,
            "backgroundColorStyle":{ "rgbColor": color},
            "borders": {

            },
            "padding": {

            },
            "horizontalAlignment": "CENTER",
            "verticalAlignment": "MIDDLE",
            "textFormat": {
            },
            "textRotation": {
            }
        }
        #sheet.update_values('A' + str(row), chunk)
        #sheet.apply_format('A' + str(row) + ':H' + str(row), format)
        row += 1
        project = next((p for p in Projects if p.project_ID == int(chunk[0][0])), None)
        ProjectsOrdered.append(project)

    for chunk in exeChunks:
        
        color = {
                "red": EXE_color[0] + (1 - EXE_color[0]) * factor,
                "green": EXE_color[1] + (1 - EXE_color[1]) * factor,
                "blue": EXE_color[2] + (1 - EXE_color[2]) * factor,
            }
        format = {
            "numberFormat": {
                
            },
            "backgroundColor": color,
            "backgroundColorStyle":{ "rgbColor": color},
            "borders": {

            },
            "padding": {

            },
            "horizontalAlignment": "CENTER",
            "verticalAlignment": "MIDDLE",
            "textFormat": {
            },
            "textRotation": {
            }
        }
        #sheet.update_values('A' + str(row), chunk)
        #sheet.apply_format('A' + str(row) + ':H' + str(row), format)
        row += 1
        project = next((p for p in Projects if p.project_ID == int(chunk[0][0])), None)
        ProjectsOrdered.append(project)
    for chunk in bmeChunks:
        color = {
                "red": BME_color[0] + (1 - BME_color[0]) * factor,
                "green": BME_color[1] + (1 - BME_color[1]) * factor,
                "blue": BME_color[2] + (1 - BME_color[2]) * factor,
            }
        format = {
            "numberFormat": {
                
            },
            "backgroundColor": color,
            "backgroundColorStyle":{ "rgbColor": color},
            "borders": {

            },
            "padding": {

            },
            "horizontalAlignment": "CENTER",
            "verticalAlignment": "MIDDLE",
            "textFormat": {
            },
            "textRotation": {
            }
        }
        #sheet.update_values('A' + str(row), chunk)
        #sheet.apply_format('A' + str(row) + ':H' + str(row), format)
        row += 1
        project = next((p for p in Projects if p.project_ID == int(chunk[0][0])), None)
        ProjectsOrdered.append(project)
    #Load failed students into the bottom of the sheet
    row += 2
    sheet.update_value(f'A{row}', 'Failed Students:')
    row += 1
 
    try:
        MESheet = sheet.copy_to(sheet.spreadsheet.id)
        MESheet.title = "ME"
        CHESheet = sheet.copy_to(sheet.spreadsheet.id)
        CHESheet.title = "CHE"
        ECESheet = sheet.copy_to(sheet.spreadsheet.id)
        ECESheet.title = "ECE"
        CEESheet = sheet.copy_to(sheet.spreadsheet.id)
        CEESheet.title = "CEE"
        EXESheet = sheet.copy_to(sheet.spreadsheet.id)
        EXESheet.title = "EXE"
        BMESheet = sheet.copy_to(sheet.spreadsheet.id)
        BMESheet.title = "BME"
    except Exception as e:
        print("Error copying sheet: ", e)
    
    for failed_student in failed_students:
        sheet.update_value(f'A{row}', failed_student)
        student_object = next((s for s in Students if s.email == failed_student + '@students.rowan.edu' or s.email == failed_student + '@rowan.edu' or s.email == failed_student or s.email == failed_student + 'students.rowan.edu' or s.email == failed_student + '.rowan.edu'), None)
        if student_object == None:
            failed_student_string = failed_student + ' | No additional info found for ' + failed_student
            row += 1
        else:
            failed_student_string = student_object.last_name + ', ' + student_object.first_name + ' | ' + student_object.year + ' | ' + student_object.major + ' | ' + student_object.email 
        sheet.update_value(f'A{row}', failed_student_string)
        row += 1

    #Select ME Sheet
    sheet = MESheet
    row = 2
    for project in ProjectsOrdered:
        column = 9
        currentStudents = project.current_students
        for student in currentStudents:
            student_object = student
            if student_object.major == "ME":
                studentString = student_object.last_name + ', ' + student_object.first_name + ' | ' + student_object.year + ' | ' + student_object.major + ' | ' + student_object.email 
                if column > 26:
                    column -= 25
                    sheet.update_value(f'A{chr(64+column)}{row}', studentString)
                else:
                    sheet.update_value(f'{chr(64+column)}{row}', studentString)
                color = SelectColor(student_object.major)
                format = {
                    "backgroundColor": color,
                    "backgroundColorStyle":{ "rgbColor": color},
                }
                sheet.apply_format(f'{chr(64+column)}{row}:{chr(64+column)}{row}', format)
                print(f'Updating {chr(64+column)}{row} with {studentString} with color {color}')
                column += 1
            else:
                column += 1

            pass
        row += 1
    #Loading failed Students into the bottom of the ME sheet
    row += 2
    sheet.update_value(f'A{row}', 'Failed Students:')
    row += 1
    for failed_student in failed_students:
        student_object = next((s for s in Students if s.email == failed_student + '@students.rowan.edu' or s.email == failed_student + '@rowan.edu' or s.email == failed_student or s.email == failed_student + 'students.rowan.edu' or s.email == failed_student + '.rowan.edu'), None)
        if student_object == None:
                failed_student_string = failed_student + ' | No additional info found for ' + failed_student
                row += 1
        else: 
            if student_object.major != "ME":
                continue
            failed_student_string = student_object.last_name + ', ' + student_object.first_name + ' | ' + student_object.year + ' | ' + student_object.major + ' | ' + student_object.email 
            sheet.update_value(f'A{row}', failed_student_string)
        row += 1
    #Select CHE Sheet
    sheet = CHESheet
    row = 2
    
    for project in ProjectsOrdered:
        column = 9
        currentStudents = project.current_students
        for student in currentStudents:
            student_object = student
            if student_object.major == "ChE":
                studentString = student_object.last_name + ', ' + student_object.first_name + ' | ' + student_object.year + ' | ' + student_object.major + ' | ' + student_object.email 
                if column > 26:
                    column -= 25
                    sheet.update_value(f'A{chr(64+column)}{row}', studentString)
                else:
                    sheet.update_value(f'{chr(64+column)}{row}', studentString)
                color = SelectColor(student_object.major)
                format = {
                    "backgroundColor": color,
                    "backgroundColorStyle":{ "rgbColor": color},
                }
                sheet.apply_format(f'{chr(64+column)}{row}:{chr(64+column)}{row}', format)
                column += 1
            else:
                column += 1

            pass
        row += 1
    #Loading failed Students into the bottom of the CHE sheet
    row += 2
    sheet.update_value(f'A{row}', 'Failed Students:')
    row += 1
    for failed_student in failed_students:
        student_object = next((s for s in Students if s.email == failed_student + '@students.rowan.edu' or s.email == failed_student + '@rowan.edu' or s.email == failed_student or s.email == failed_student + 'students.rowan.edu' or s.email == failed_student + '.rowan.edu'), None)
        if student_object == None:
                failed_student_string = failed_student + ' | No additional info found for ' + failed_student
                row += 1
        else:
            if student_object.major != "ChE":
                continue
            failed_student_string = student_object.last_name + ', ' + student_object.first_name + ' | ' + student_object.year + ' | ' + student_object.major + ' | ' + student_object.email 
            sheet.update_value(f'A{row}', failed_student_string)
        row += 1
    #Select ECE Sheet
    sheet = ECESheet
    row = 2
    for project in ProjectsOrdered:
        column = 9
        currentStudents = project.current_students
        for student in currentStudents:
            student_object = student
            if student_object.major == "ECE":
                studentString = student_object.last_name + ', ' + student_object.first_name + ' | ' + student_object.year + ' | ' + student_object.major + ' | ' + student_object.email 
                if column > 26:
                    column -= 25
                    sheet.update_value(f'A{chr(64+column)}{row}', studentString)
                else:
                    sheet.update_value(f'{chr(64+column)}{row}', studentString)
                color = SelectColor(student_object.major)
                format = {
                    "backgroundColor": color,
                    "backgroundColorStyle":{ "rgbColor": color},
                }
                sheet.apply_format(f'{chr(64+column)}{row}:{chr(64+column)}{row}', format)
                column += 1
            else:
                column += 1

            pass
        row += 1
    #Loading failed Students into the bottom of the ECE sheet
    row += 2
    sheet.update_value(f'A{row}', 'Failed Students:')
    row += 1
    for failed_student in failed_students:
        student_object = next((s for s in Students if s.email == failed_student + '@students.rowan.edu' or s.email == failed_student + '@rowan.edu' or s.email == failed_student or s.email == failed_student + 'students.rowan.edu' or s.email == failed_student + '.rowan.edu'), None)
        if student_object == None:
                failed_student_string = failed_student + ' | No additional info found for ' + failed_student
                row += 1
        else:
            if student_object.major != "ECE":
                continue
            failed_student_string = student_object.last_name + ', ' + student_object.first_name + ' | ' + student_object.year + ' | ' + student_object.major + ' | ' + student_object.email 
            sheet.update_value(f'A{row}', failed_student_string)
        row += 1
    #Select CEE Sheet
    sheet = CEESheet
    row = 2
    for project in ProjectsOrdered:
        column = 9
        currentStudents = project.current_students
        for student in currentStudents:
            student_object = student
            if student_object.major == "CEE":
                studentString = student_object.last_name + ', ' + student_object.first_name + ' | ' + student_object.year + ' | ' + student_object.major + ' | ' + student_object.email 
                if column > 26:
                    column -= 25
                    sheet.update_value(f'A{chr(64+column)}{row}', studentString)
                else:
                    sheet.update_value(f'{chr(64+column)}{row}', studentString)
                color = SelectColor(student_object.major)
                format = {
                    "backgroundColor": color,
                    "backgroundColorStyle":{ "rgbColor": color},
                }
                sheet.apply_format(f'{chr(64+column)}{row}:{chr(64+column)}{row}', format)
                column += 1
            else:
                column += 1

            pass
        row += 1
    #Loading failed Students into the bottom of the CEE sheet
    row += 2
    sheet.update_value(f'A{row}', 'Failed Students:')
    row += 1
    for failed_student in failed_students:
        student_object = next((s for s in Students if s.email == failed_student + '@students.rowan.edu' or s.email == failed_student + '@rowan.edu' or s.email == failed_student or s.email == failed_student + 'students.rowan.edu' or s.email == failed_student + '.rowan.edu'), None)
        if student_object == None:
                failed_student_string = failed_student + ' | No additional info found for ' + failed_student
                row += 1
        else:
            if student_object.major != "CEE":
                continue
            failed_student_string = student_object.last_name + ', ' + student_object.first_name + ' | ' + student_object.year + ' | ' + student_object.major + ' | ' + student_object.email 
            sheet.update_value(f'A{row}', failed_student_string)
        row += 1
    #Select EXE Sheet
    sheet = EXESheet
    row = 2
    for project in ProjectsOrdered:
        column = 9
        currentStudents = project.current_students
        for student in currentStudents:
            student_object = student
            if student_object.major == "EXE":
                studentString = student_object.last_name + ', ' + student_object.first_name + ' | ' + student_object.year + ' | ' + student_object.major + ' | ' + student_object.email 
                if column > 26:
                    column -= 25
                    sheet.update_value(f'A{chr(64+column)}{row}', studentString)
                else:
                    sheet.update_value(f'{chr(64+column)}{row}', studentString)
                color = SelectColor(student_object.major)
                format = {
                    "backgroundColor": color,
                    "backgroundColorStyle":{ "rgbColor": color},
                }
                sheet.apply_format(f'{chr(64+column)}{row}:{chr(64+column)}{row}', format)
                column += 1
            else:
                column += 1

            pass
        row += 1
    #Loading failed Students into the bottom of the EXE sheet
    row += 2
    sheet.update_value(f'A{row}', 'Failed Students:')
    row += 1
    for failed_student in failed_students:
        student_object = next((s for s in Students if s.email == failed_student + '@students.rowan.edu' or s.email == failed_student + '@rowan.edu' or s.email == failed_student or s.email == failed_student + 'students.rowan.edu' or s.email == failed_student + '.rowan.edu'), None)
        if student_object == None:
                failed_student_string = failed_student + ' | No additional info found for ' + failed_student
                row += 1
        else:
            if student_object.major != "EXE":
                continue
            failed_student_string = student_object.last_name + ', ' + student_object.first_name + ' | ' + student_object.year + ' | ' + student_object.major + ' | ' + student_object.email 
            sheet.update_value(f'A{row}', failed_student_string)
        row += 1
    #Select BME Sheet
    sheet = BMESheet
    row = 2 
    for project in ProjectsOrdered:
        column = 9
        currentStudents = project.current_students
        for student in currentStudents:
            student_object = student
            if student_object.major == "BME":
                studentString = student_object.last_name + ', ' + student_object.first_name + ' | ' + student_object.year + ' | ' + student_object.major + ' | ' + student_object.email 
                if column > 26:
                    column -= 25
                    sheet.update_value(f'A{chr(64+column)}{row}', studentString)
                else:
                    sheet.update_value(f'{chr(64+column)}{row}', studentString)
                color = SelectColor(student_object.major)
                format = {
                    "backgroundColor": color,
                    "backgroundColorStyle":{ "rgbColor": color},
                }
                sheet.apply_format(f'{chr(64+column)}{row}:{chr(64+column)}{row}', format)
                column += 1
            else:
                column += 1

            pass
        row += 1
    #Loading failed Students into the bottom of the BME sheet
    row += 2
    sheet.update_value(f'A{row}', 'Failed Students:')
    row += 1
    for failed_student in failed_students:
        student_object = next((s for s in Students if s.email == failed_student + '@students.rowan.edu' or s.email == failed_student + '@rowan.edu' or s.email == failed_student or s.email == failed_student + 'students.rowan.edu' or s.email == failed_student + '.rowan.edu'), None)
        if student_object == None:
                failed_student_string = failed_student + ' | No additional info found for ' + failed_student
                row += 1
        else:
            if student_object.major != "BME":
                continue
            failed_student_string = student_object.last_name + ', ' + student_object.first_name + ' | ' + student_object.year + ' | ' + student_object.major + ' | ' + student_object.email 
            sheet.update_value(f'A{row}', failed_student_string)
        row += 1
    
    pass

