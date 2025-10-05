import csv
import os




home_directory = os.getcwd()
csvPath = home_directory + '/Professor Clinic Request (Responses) - Form.csv'
AddedProjectsPath = home_directory + '/AddedProjects.csv'



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

