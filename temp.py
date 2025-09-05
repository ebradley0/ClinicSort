import SortProjects
import SortStudents
import requests



csvDL_link = 'https://docs.google.com/spreadsheets/d/1_pwkw2Ld3o3EZt6FIeJlFeFmleYWzjWoKTNpDPmDbOo/gviz/tq?tqx=out:csv&sheet=Form Responses 30'

def main():
    #initialize_sheet()  # Initialize the Google Sheets client and select the sheet
    print("This is the main function of ProjectViewLoop.py")
    
    print("Running updateSheet function...")
    response = requests.get(csvDL_link)
    with open('Student Clinic Requests (Responses) - Form.csv', 'wb') as file:
        file.write(response.content)
    #SortProjects.updateSheet()
    SortStudents.resultOutput()

    

if __name__ == "__main__":
    main()
    
