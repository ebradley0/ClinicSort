import csv
import os
import pygsheets
import requests



home_directory = os.getcwd()
csvPath = home_directory + '/Professor Clinic Request (Responses) - Form.csv'
AddedProjectsPath = home_directory + '/AddedProjects.csv'

client = pygsheets.authorize(client_secret='client_secret.json')

black_rgb = {
    "red": 0,
    "green": 0,
    "blue": 0
}

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
ME_text_color = (
    0.23529411764705882,
    0.47058823529411764,
    0.8470588235294118,
)
ChE_text_color = (
    0.403921568627451,
    0.3058823529411765,
    0.6549019607843137,
)
ECE_text_color = (
    0.9019607843137255,
    0.5686274509803921,
    0.2196078431372549,
)
CEE_text_color = (
    0.41568627450980394,
    0.6588235294117647,
    0.30980392156862746
)
EXE_text_color = (    
    0.12941176470588237,
    0.4666666666666667,
    0.4470588235294118
)
BME_text_color = (
    0.6509803921568628,
    0.10980392156862745,
    0,
)

sheet = client.open('Clinic Project View Fall FY26').sheet1 #Select the first page of the sheet
project_counter = 0
def initialize_sheet():
    client = pygsheets.authorize(client_secret='client_secret.json')
    sheet = client.open('Clinic Project View Fall FY26').sheet1  # Select the first page of the sheet

#Project class for filtering through the CSV.

class Project:
    def __init__(self, row):
        self.timestamp = row[0]
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
        self.project_ID = 0
        self.manager_last_names[0] = f'=HYPERLINK("mailto:{self.email}", "{self.manager_last_names[0].strip()}")'  # Make the first manager a mailto link
        print("Loaded project:", self.project_name)
        print("Max students for operation:", self.max_students_for_operation)
    def __str__(self):
        return f"{self.project_name} ({self.department}) - {self.project_description}"
    
    def check_if_major_reqs(self):
        if self.me_students == '':
            self.max_me_students = self.max_students_for_operation
        if self.che_students == '':
            self.max_che_students = self.max_students_for_operation
        if self.ece_students == '':
            self.max_ece_students = self.max_students_for_operation
        if self.cee_students == '':
            self.max_cee_students = self.max_students_for_operation
        if self.exe_students == '':
            self.max_exe_students = self.max_students_for_operation
        if self.bme_students == '':
            self.max_bme_students = self.max_students_for_operation
    def check_max_students(self):
        if self.max_students_for_operation == '':
            self.max_students_for_operation = int(self.max_me_students) + int(self.max_che_students) + int(self.max_ece_students) + int(self.max_cee_students) + int(self.max_exe_students) + int(self.max_bme_students)
        return int(self.max_students_for_operation)
    def fixLinks(self):
        count = 1
        for link in self.project_url_links:
            newlink = f'=HYPERLINK("{link.strip()}", "[{count}]")'
            count += 1
            self.project_url_links[self.project_url_links.index(link)] = newlink
        self.project_image = f'=HYPERLINK("{self.project_image}", IMAGE("https://drive.google.com/thumbnail?id={self.project_image.split("id=")[-1]}&sz=h800w800"))'


Projects = []
completed_projects = []
AddedProjects = []
def get_project_data():
    with open(csvPath, encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)  # Skip header row
        #print("Length of CSV: ", len(list(reader)))
        for row in reader:
            if len(row) > 1:  # Ensure the row is not empty
                project = Project(row)
                if project is None:
                    break
                project.check_if_major_reqs()
                project.check_max_students() # Check if max was provided
                if any(existing.project_name == project.project_name for existing in Projects):
                    print("Duplicate project found,  28394 skipping:", project.project_name)
                    continue
                project.project_ID = (len(Projects) + 1) #Track each projects ID by counting the length of the project and adding one. The one is needed because Project 0 cannot exist, so the counter will always be ahead of the length by one.
                project.fixLinks()
                Projects.append(project)
                
        #print(len(Projects), " projects loaded.")
        csvfile.close()
        return Projects
    #Clinic displays are in blocks of 5x6 cells

#get_project_data()

def rgb_dict_to_hex(rgb):
    r = int(rgb['red'] * 255)
    g = int(rgb['green'] * 255)
    b = int(rgb['blue'] * 255)
    return '#{:02X}{:02X}{:02X}'.format(r, g, b)


def assemble_data_chunk(project):
    #Arrange the hyperlinks properly
    count = 1
    
    data_chunk = [
        ['', project.project_name + ' | ' + project.department, '', '', '', '', '', project.project_image],
        ['Manager(s)'] + project.manager_last_names + ([''] * (5 - len(project.manager_last_names)) + ['PI: 0']),
        ['Description', project.project_description, '', '', '', '', ''],
        ['Seeking', 'ME: ' + project.max_me_students, 'ChE: ' + project.max_che_students, 'ECE: ' + project.max_ece_students, 'CEE: ' + project.max_cee_students, 'EXE: ' + project.max_exe_students, 'BME: ' + project.max_bme_students],
        ['Links:'] + project.project_url_links + [''] * (6 - len(project.project_url_links)),
    ]
    return data_chunk

def clear_sheet():
    # Clear the sheet before writing new data
    sheet.clear(start='A1', end='Z1000')  # Adjust the range as needed


def updateSheet():
    get_project_data()  # Load the project data from the CSV
    #clear_sheet()  # Clear the sheet before updating
    with open('AddedProjects.csv', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            AddedProjects.append(row)
    
    print("Updating the sheet with project data...")
    for project in Projects:
        if project in completed_projects:
            continue
        #print(project.project_type)
        project_counter = Projects.index(project) + 1
        if any(project.project_name.strip() == added[0].strip() for added in AddedProjects):
            continue
        
        print(project.project_name.strip(), " is project number ", project_counter)
        
        data_chunk = assemble_data_chunk(project)
        data_chunk[0][0] = 'Project ' + str(project_counter)  # Set the project number in the first cell of the first row
        sheet.update_values('A' + str((project_counter - 1) * 5 + 1), data_chunk) 
        

        color = {
            "red": 171 / 255,
            "green": 203 / 255,
            "blue": 255 / 255
        }
        
        factor = 0
        if project.department == "ME":
            color = {
                "red": ME_color[0] + (1 - ME_color[0]) * factor,  # Slightly lighter
                "green": ME_color[1] + (1 - ME_color[1]) * factor,
                "blue": ME_color[2] + (1 - ME_color[2]) * factor,
    
            }
            textColor = {
                "red": ME_text_color[0],
                "green": ME_text_color[1],
                "blue": ME_text_color[2],
            }
        elif project.department == "ChE":
            color = {
                "red": ChE_color[0] + (1 - ChE_color[0]) * factor,
                "green": ChE_color[1] + (1 - ChE_color[1]) * factor,
                "blue": ChE_color[2] + (1 - ChE_color[2]) * factor,
            }
            textColor = {
                "red": ChE_text_color[0],
                "green": ChE_text_color[1],
                "blue": ChE_text_color[2],
            }
        elif project.department == "ECE":
            color = {
                "red": ECE_color[0] + (1 - ECE_color[0]) * factor,
                "green": ECE_color[1] + (1 - ECE_color[1]) * factor,
                "blue": ECE_color[2] + (1 - ECE_color[2]) * factor,
            }
            textColor = {
                "red": ECE_text_color[0],
                "green": ECE_text_color[1],
                "blue": ECE_text_color[2],
            }
        elif project.department == "CEE":
            color = {
                "red": CEE_color[0] + (1 - CEE_color[0]) * factor,
                "green": CEE_color[1] + (1 - CEE_color[1]) * factor,
                "blue": CEE_color[2] + (1 - CEE_color[2]) * factor,
            }
            textColor = {
                "red": CEE_text_color[0],
                "green": CEE_text_color[1],
                "blue": CEE_text_color[2],
            }
        elif project.department == "EXE":
            color = {
                "red": EXE_color[0] + (1 - EXE_color[0]) * factor,
                "green": EXE_color[1] + (1 - EXE_color[1]) * factor,
                "blue": EXE_color[2] + (1 - EXE_color[2]) * factor,
            }
            textColor = {
                "red": EXE_text_color[0],
                "green": EXE_text_color[1],
                "blue": EXE_text_color[2],
            }
        elif project.department == "BME":
            color = {
                "red": BME_color[0] + (1 - BME_color[0]) * factor,
                "green": BME_color[1] + (1 - BME_color[1]) * factor,
                "blue": BME_color[2] + (1 - BME_color[2]) * factor,
            }
            textColor = {
                "red": BME_text_color[0],
                "green": BME_text_color[1],
                "blue": BME_text_color[2],
            }
        elif project.department == "EET":
            color = {
                "red": 0.95,
                "green": 0.95,
                "blue": 0.44
            }
            textColor = {
                "red": 0.65,
                "green": 0.65,
                "blue": 0
            }
        elif project.department == "MET":
            color = {
                "red": 0.95,
                "green": 0.44,
                "blue": 0.44
            }
            textColor = {
                "red": 0.65,
                "green": 0,
                "blue": 0
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
            "wrapStrategy": "WRAP",
            "textFormat": {
            },
            "textRotation": {
            }
        }
        titleFormat = {
            "textFormat": {
                "fontSize": 10,
                "bold": True,
                "fontFamily": "Verdana"
            },
            "horizontalAlignment": "CENTER",
            "verticalAlignment": "MIDDLE",
            "wrapStrategy": "WRAP",
            "backgroundColor": color,
            "borders": {
                "top": {"style": "SOLID", "width": 1, "colorStyle": {"rgbColor": black_rgb}},
                }
        }
        seekingFormat = {
            "textFormat": {
                "fontSize": 10,
                "bold": False,
                "fontFamily": "Verdana"
            },
            "horizontalAlignment": "CENTER",
            "verticalAlignment": "MIDDLE",
            "wrapStrategy": "WRAP",
            "backgroundColor": color,
        }
        white_background = {
            "backgroundColor": {"red": 1, "green": 1, "blue": 1},
            "horizontalAlignment": "LEFT",
            "verticalAlignment": "MIDDLE",
            "wrapStrategy": "WRAP",
            "textFormat": {
                "fontSize": 10,
                "bold": False,
                "fontFamily": "Verdana"}

        }
        rightJustified = {
            "horizontalAlignment": "RIGHT",
            "verticalAlignment": "MIDDLE",
            "wrapStrategy": "WRAP",
            "backgroundColor": color,
            "textFormat": {
                "fontSize": 10,
                "bold": False,
                "fontFamily": "Verdana",
                "foregroundColor": textColor}
        }
        
        #Merging the rows 1 and 3 of the set, columns 2-7
        row_start = (project_counter - 1) * 5 + 1
        sheet.merge_cells((row_start, 2),(row_start,6 ))
        cell = sheet.cell((row_start, 2))
        cell.wrap_strategy = 'WRAP' 
        sheet.merge_cells((row_start + 2, 2), (row_start + 2, 7))
        cell = sheet.cell((row_start + 2, 2))
        cell.wrap_strategy = 'WRAP'
        sheet.merge_cells((row_start, 8), (row_start + 4, 9)) #Merging the image cells
        sheet.apply_format('H' + str(row_start) + ':I' + str(row_start + 4), white_background)
        #Formatting the data chunk
        sheet.apply_format('A' + str((project_counter - 1) * 5 + 1) + ':G' + str((project_counter - 1) * 5 + 1),titleFormat)
        sheet.apply_format('A' + str((project_counter - 1) * 5 + 2) + ':G' + str((project_counter - 1) * 5 + 5), format )
        sheet.apply_format('B' + str((project_counter - 1) * 5 + 2) + ':F' + str((project_counter - 1) * 5 + 3), white_background)
        sheet.apply_format('A' + str((project_counter - 1) * 5 + 2) + ':A' + str((project_counter - 1) * 5 + 5), rightJustified)
        sheet.apply_format('G' + str((project_counter - 1) * 5 + 2) +':G' + str((project_counter - 1) * 5 + 2)  , rightJustified)
        

    
        #Merge the cells to just display total students, rather than specifics
        if project.request_classification =='General: I would like to specify a general number of students required.':
            sheet.merge_cells((row_start + 3, 2), (row_start + 3, 7))
            sheet.cell((row_start + 3, 2)).value = 'Total Students: ' + str(project.max_students_for_operation)
            cell = sheet.cell((row_start + 3, 2))
            seekingFormat["backgroundColor"] = {"red":1, "green": 1, "blue": 1}
            sheet.apply_format('B' + str((project_counter - 1) * 5 + 4) + ':G' + str((project_counter - 1) * 5 + 4), seekingFormat)
            pass
        else:
            #Go through each cell and check if it contains ME, etc, to change the color of the cell
            sheet.apply_format('B' + str((project_counter - 1) * 5 + 4) + ':G' + str((project_counter - 1) * 5 + 4), seekingFormat)
            for val in data_chunk:
                for i in range(1, 7):
                    #print(val[i])  # Debugging line to see the values being processed
                    if val[i] == 'ME: ' + project.max_me_students:
                        sheet.cell((row_start + 3, i + 1)).color = ME_color
                    elif val[i] == 'ChE: ' + project.max_che_students:
                        sheet.cell((row_start + 3, i + 1)).color = ChE_color
                    elif val[i] == 'ECE: ' + project.max_ece_students:
                        sheet.cell((row_start + 3, i + 1)).color = ECE_color
                    elif val[i] == 'CEE: ' + project.max_cee_students:
                        sheet.cell((row_start + 3, i + 1)).color = CEE_color
                    elif val[i] == 'EXE: ' + project.max_exe_students:
                        sheet.cell((row_start + 3, i + 1)).color = EXE_color
                    elif val[i] == 'BME: ' + project.max_bme_students:
                        sheet.cell((row_start + 3, i + 1)).color = BME_color
        
        completed_projects.append(project)
        #Add the projec tto the end of AddedProjects.csv
        with open('AddedProjects.csv', 'a', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([project.project_name])
            csvfile.close()
csvDL_link = 'https://docs.google.com/spreadsheets/d/1_pwkw2Ld3o3EZt6FIeJlFeFmleYWzjWoKTNpDPmDbOo/gviz/tq?tqx=out:csv&sheet=Form Responses 30'

StudentResponses = []

def getStudentResponses():
    StudentResponses = []
    response = requests.get(csvDL_link)
    with open('Student Clinic Requests (Responses) - Form.csv', 'wb') as file:
        file.write(response.content)

    with open('Student Clinic Requests (Responses) - Form.csv', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)
        for line in reader:
            StudentResponses.append(line)
    print(len(StudentResponses), " student responses loaded.")
    return StudentResponses



def ProjectPI():
    PIDict = {}
    Projects = get_project_data()  # Load the project data from the CSV
    for project in Projects:
        PIDict[project.project_ID] = 0 #Create a dictionary entry for each project, associated by its ID.
    StudentResponses = getStudentResponses()  # Load the student responses from the CSV
    for response in StudentResponses:
        firstChoice = response[6].strip()
        '''filteredChoice = ' '.join(firstChoice.split(' ')[2:]).strip()
        filteredChoice = filteredChoice.split()
        for word in filteredChoice:
            word.capitalize()
        filteredChoice = ' '.join(filteredChoice).strip()'''
        filteredchoice = firstChoice.split(' ')[0].strip()
        filteredchoice = filteredchoice.replace('-', '')
        ProjectID = int(filteredchoice) #Grab the number which is at the start of the string
        PIDict[ProjectID] += 1 #Add one to the PI counter
    
        
    counter = 0
    for project, pi in PIDict.items():
        
        RowCalc = (project + 1) +  (counter * 4)
        cell = (RowCalc, 7)
        print(RowCalc)
        sheet.update_value(cell, 'PI: ' + str(pi))
        counter += 1
        

    


    



#updateSheet()  # Call the function to update the sheet with project data