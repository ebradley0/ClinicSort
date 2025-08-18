import csv
import os
import pygsheets




home_directory = os.getcwd()
csvPath = home_directory + '/Professor Clinic Request (Responses) - Form.csv'

client = pygsheets.authorize(client_secret='client_secret.json')

black_rgb = {
    "red": 0,
    "green": 0,
    "blue": 0
}

ME_color = (
     0.44,
     0.67,
    0.95
)

ChE_color = (
     0.48,
     0.95,
    0.44
)
ECE_color = (
    0.95,
     0.92,
     0.44
)
CEE_color = (
  0.95,
    0.63,
  0.44
)
EXE_color = (
    1.0,
    0.28,
   0.28
)
BME_color = (
    0.43,
    0.95,
    0.75
)

sheet = client.open('Clinic Project View Fall FY26').sheet1 #Select the first page of the sheet

def initialize_sheet():
    client = pygsheets.authorize(client_secret='client_secret.json')
    sheet = client.open('Clinic Project View Fall FY26').sheet1  # Select the first page of the sheet

#Project class for filtering through the CSV.

class Project:
    def __init__(self, row):
        self.timestamp = row[0]
        self.email = row[1]
        self.manager_last_names = row[2]
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

    def __str__(self):
        return f"{self.project_name} ({self.department}) - {self.project_description}"
    
    def check_if_major_reqs(self):
        if self.me_students == '' and self.che_students == '' and self.ece_students == '' and self.cee_students == '' and self.exe_students == '' and self.bme_students == '':
            #Max them out so theres always room no matter the range, and fall back to max students for operation
            self.me_students = self.max_students_for_operation
            self.che_students = self.max_students_for_operation
            self.ece_students = self.max_students_for_operation
            self.cee_students = self.max_students_for_operation
            self.exe_students = self.max_students_for_operation
            self.bme_students = self.max_students_for_operation
            return False
    def check_max_students(self):
        if self.max_students_for_operation == '':
            self.max_students_for_operation = int(self.me_students) + int(self.che_students) + int(self.ece_students) + int(self.cee_students) + int(self.exe_students) + int(self.bme_students)
        return int(self.max_students_for_operation)


Projects = []


def get_project_data():

    with open(csvPath, encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)  # Skip header row
        #print("Length of CSV: ", len(list(reader)))
        for row in reader:
            if len(row) > 1:  # Ensure the row is not empty
                project = Project(row)
                project.check_if_major_reqs()
                project.check_max_students() # Check if max was provided
                Projects.append(project)
        print(len(Projects), " projects loaded.")
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
    for link in project.project_url_links:
        newlink = f'=HYPERLINK("{link.strip()}", "[{count}]")'
        count += 1
        project.project_url_links[project.project_url_links.index(link)] = newlink
    project.project_image = f'=HYPERLINK("{project.project_image}", IMAGE("https://drive.google.com/thumbnail?id={project.project_image.split("id=")[-1]}&sz=h800w800"))'
    data_chunk = [
        ['', project.project_name + ' | ' + project.department, '', '', '', '', 'PI: ', project.project_image],
        ['Manager(s)', project.manager_last_names, '', '', '', '', ''],
        ['Description', project.project_description, '', '', '', '', ''],
        ['Seeking', 'ME: ' + project.me_students, 'ChE: ' + project.che_students, 'ECE: ' + project.ece_students, 'CEE: ' + project.cee_students, 'EXE: ' + project.exe_students, 'BME: ' + project.bme_students],
        ['Links:'] + project.project_url_links + [''] * (6 - len(project.project_url_links)),
    ]
    return data_chunk

def clear_sheet():
    # Clear the sheet before writing new data
    sheet.clear(start='A1', end='Z1000')  # Adjust the range as needed

def updateSheet():
    get_project_data()  # Load the project data from the CSV
    clear_sheet()  # Clear the sheet before updating
    project_counter = 0
    for project in Projects:
        print(project.project_type)
        project_counter += 1
        data_chunk = assemble_data_chunk(project)
        data_chunk[0][0] = 'Project ' + str(project_counter)  # Set the project number in the first cell of the first row
        sheet.update_values('A' + str((project_counter - 1) * 5 + 1), data_chunk) 
        

        color = {
            "red": 171 / 255,
            "green": 203 / 255,
            "blue": 255 / 255
        }
        
        factor = 0.5
        if project.department == "ME":
            color = {
                "red": ME_color[0] + (1 - ME_color[0]) * factor,  # Slightly lighter
                "green": ME_color[1] + (1 - ME_color[1]) * factor,
                "blue": ME_color[2] + (1 - ME_color[2]) * factor,
    
            }
        elif project.department == "ChE":
            color = {
                "red": ChE_color[0] + (1 - ChE_color[0]) * factor,
                "green": ChE_color[1] + (1 - ChE_color[1]) * factor,
                "blue": ChE_color[2] + (1 - ChE_color[2]) * factor,
            }
        elif project.department == "ECE":
            color = {
                "red": ECE_color[0] + (1 - ECE_color[0]) * factor,
                "green": ECE_color[1] + (1 - ECE_color[1]) * factor,
                "blue": ECE_color[2] + (1 - ECE_color[2]) * factor,
            }
        elif project.department == "CEE":
            color = {
                "red": CEE_color[0] + (1 - CEE_color[0]) * factor,
                "green": CEE_color[1] + (1 - CEE_color[1]) * factor,
                "blue": CEE_color[2] + (1 - CEE_color[2]) * factor,
            }
        elif project.department == "EXE":
            color = {
                "red": EXE_color[0] + (1 - EXE_color[0]) * factor,
                "green": EXE_color[1] + (1 - EXE_color[1]) * factor,
                "blue": EXE_color[2] + (1 - EXE_color[2]) * factor,
            }
        elif project.department == "BME":
            color = {
                "red": BME_color[0] + (1 - BME_color[0]) * factor,
                "green": BME_color[1] + (1 - BME_color[1]) * factor,
                "blue": BME_color[2] + (1 - BME_color[2]) * factor,
            }
        elif project.department == "EET":
            color = {
                "red": 0.95,
                "green": 0.95,
                "blue": 0.44
            }
        elif project.department == "MET":
            color = {
                "red": 0.95,
                "green": 0.44,
                "blue": 0.44
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
                "fontSize": 16,
                "bold": True
            },
            "horizontalAlignment": "CENTER",
            "verticalAlignment": "MIDDLE",
            "wrapStrategy": "WRAP",
            "backgroundColor": color,
            "borders": {
                "top": {"style": "SOLID", "width": 2, "colorStyle": {"rgbColor": black_rgb}},
                "bottom": {"style": "SOLID", "width": 2, "colorStyle": {"rgbColor": black_rgb}},
                "left": {"style": "SOLID", "width": 2, "colorStyle": {"rgbColor": black_rgb}},
                "right": {"style": "SOLID", "width": 2, "colorStyle": {"rgbColor": black_rgb}}
                }
        }
        seekingFormat = {
            "textFormat": {
                "fontSize": 14,
                "bold": True
            },
            "horizontalAlignment": "CENTER",
            "verticalAlignment": "MIDDLE",
            "wrapStrategy": "WRAP",
            "backgroundColor": color,
        }
        white_background = {
            "backgroundColor": {"red": 1, "green": 1, "blue": 1},
            "horizontalAlignment": "CENTER",
            "verticalAlignment": "MIDDLE",
            "wrapStrategy": "WRAP",

        }
        
        #Merging the rows 1 and 3 of the set, columns 2-7
        row_start = (project_counter - 1) * 5 + 1
        sheet.merge_cells((row_start, 2),(row_start,6 ))
        cell = sheet.cell((row_start, 2))
        cell.wrap_strategy = 'WRAP' 
        sheet.merge_cells((row_start + 2, 2), (row_start + 2, 7))
        cell = sheet.cell((row_start + 2, 2))
        cell.wrap_strategy = 'WRAP'
        sheet.merge_cells((row_start, 8), (row_start + 4, 11))
        #Formatting the data chunk
        sheet.apply_format('A' + str((project_counter - 1) * 5 + 1) + ':G' + str((project_counter - 1) * 5 + 1),titleFormat)
        sheet.apply_format('A' + str((project_counter - 1) * 5 + 2) + ':G' + str((project_counter - 1) * 5 + 5), format )
        sheet.apply_format('B' + str((project_counter - 1) * 5 + 2) + ':F' + str((project_counter - 1) * 5 + 3), white_background)

    
        #Merge the cells to just display total students, rather than specifics
        if project.request_classification =='General: I would like to specify a general number of students required.':
            sheet.merge_cells((row_start + 3, 2), (row_start + 3, 7))
            sheet.cell((row_start + 3, 2)).value = 'Total Students: ' + str(project.min_students_required)
            cell = sheet.cell((row_start + 3, 2))
            seekingFormat["backgroundColor"] = {"red":1, "green": 1, "blue": 1}
            sheet.apply_format('B' + str((project_counter - 1) * 5 + 4) + ':G' + str((project_counter - 1) * 5 + 4), seekingFormat)
            pass
        else:
            #Go through each cell and check if it contains ME, etc, to change the color of the cell
            sheet.apply_format('A' + str((project_counter - 1) * 5 + 4) + ':G' + str((project_counter - 1) * 5 + 4), seekingFormat)
            for val in data_chunk:
                for i in range(1, 7):
                    print(val[i])  # Debugging line to see the values being processed
                    if val[i] == 'ME: ' + project.me_students:
                        sheet.cell((row_start + 3, i + 1)).color = ME_color
                    elif val[i] == 'ChE: ' + project.che_students:
                        sheet.cell((row_start + 3, i + 1)).color = ChE_color
                    elif val[i] == 'ECE: ' + project.ece_students:
                        sheet.cell((row_start + 3, i + 1)).color = ECE_color
                    elif val[i] == 'CEE: ' + project.cee_students:
                        sheet.cell((row_start + 3, i + 1)).color = CEE_color
                    elif val[i] == 'EXE: ' + project.exe_students:
                        sheet.cell((row_start + 3, i + 1)).color = EXE_color
                    elif val[i] == 'BME: ' + project.bme_students:
                        sheet.cell((row_start + 3, i + 1)).color = BME_color
        





#updateSheet()  # Call the function to update the sheet with project data