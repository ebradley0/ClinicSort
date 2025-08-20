from SortProjects import updateSheet, initialize_sheet
import time
import requests

csvDL_link = 'https://docs.google.com/spreadsheets/d/1ut_h6P_T9qt08hg-CDwVrZMgPHknqSq17LsuJ4cbmcA/gviz/tq?tqx=out:csv&sheet=Form'

def main():
    initialize_sheet()  # Initialize the Google Sheets client and select the sheet
    print("This is the main function of ProjectViewLoop.py")
    while True:
        print("Running updateSheet function...")
        response = requests.get(csvDL_link)
        with open('Professor Clinic Request (Responses) - Form.csv', 'wb') as file:
            file.write(response.content)
        updateSheet()
        print('Sleeping for 30 seconds...')
        time.sleep(30)

if __name__ == "__main__":
    main()
from SortProjects import updateSheet, initialize_sheet
import time
import requests

csvDL_link = 'https://docs.google.com/spreadsheets/d/1ut_h6P_T9qt08hg-CDwVrZMgPHknqSq17LsuJ4cbmcA/gviz/tq?tqx=out:csv&sheet=Form'

def main():
    initialize_sheet()  # Initialize the Google Sheets client and select the sheet
    print("This is the main function of ProjectViewLoop.py")
    while True:
        print("Running updateSheet function...")
        response = requests.get(csvDL_link)
        with open('Professor Clinic Request (Responses) - Form.csv', 'wb') as file:
            file.write(response.content)
        updateSheet()
        print('Sleeping for 30 minutes...')
        time.sleep(60*30)

if __name__ == "__main__":
    main()