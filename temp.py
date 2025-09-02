import SortProjects
import requests



csvDL_link = 'https://docs.google.com/spreadsheets/d/1ut_h6P_T9qt08hg-CDwVrZMgPHknqSq17LsuJ4cbmcA/gviz/tq?tqx=out:csv&sheet=Form'

def main():
    #initialize_sheet()  # Initialize the Google Sheets client and select the sheet
    print("This is the main function of ProjectViewLoop.py")
    
    print("Running updateSheet function...")
    response = requests.get(csvDL_link)
    with open('Professor Clinic Request (Responses) - Form.csv', 'wb') as file:
        file.write(response.content)
    
    print('Sleeping for 30 seconds...')
    Projects = SortProjects.get_project_data()
    SortProjects.updateSheet()
    print(len(Projects), " projects loaded.")

    

if __name__ == "__main__":
    main()
    
