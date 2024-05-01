import pdfkit
import getpass
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select #for dropdowns
import time                                      #for pauses
import bs4
import re

# Use class name, id, name, or xpath to get the elements and click on them using the driver, use sleep to give the driver
# some time before moving on

import sys

printing = False

if len(sys.argv) == 2:
    user_ID = sys.argv[1]
elif len(sys.argv) == 3 and "--save-pdf" in sys.argv:
    printing = True
    user_ID = sys.argv[2] 
elif len(sys.argv) == 1:
    user_ID = sys.argv[0]
else:
    print('''python3 webadv_audit.py --help

This Python script retrieves your academic audit and prints a summary. 
It can optionally save a PDF copy of your entire audit.

Usage: python3 webadv_audit.py [--option] [student id, e.g., s1100841]    
   where [--option] can be:
      --help:         Display this help information and exit
      --save-pdf: Save PDF copy of entire audit to the current folder
                  as audit.pdf
''')
    
password = getpass.getpass(prompt='Enter your password: ')
    
driver = webdriver.Chrome()

driver.get('https://webadvisor.monmouth.edu')

time.sleep(2)

driver.find_element(By.CLASS_NAME, "WBST_Bars").click()

time.sleep(2)

driver.find_element(By.ID, "acctLogin").click()

time.sleep(2)

driver.find_element(By.NAME, "UserName").send_keys(user_ID)

time.sleep(2)

driver.find_element(By.ID, "nextButton").click()

time.sleep(2)

driver.find_element(By.ID, "passwordInput").send_keys(password)

time.sleep(1)

driver.find_element(By.ID, "submitButton").click()

time.sleep(2)

try:
    # Click on the element with XPath "//span[.='Academic Audit/Pgm Eval']"
    driver.find_element(By.XPATH, "//span[.='Academic Audit/Pgm Eval']").click()
except NoSuchElementException:
    # If the element is not found, it indicates failure to proceed with the audit
    print("Error: Failed to proceed with the audit. Incorrect user ID or password.")
    driver.quit()
    sys.exit(1)  # Exit with error code 1

time.sleep(2)

driver.find_element(By.ID, "LIST_VAR1_1").click()

time.sleep(1)

driver.find_element(By.NAME, "SUBMIT2").click()

time.sleep(5)

# Get the parsed html data
html_source = driver.page_source
advise_soup = bs4.BeautifulSoup(html_source, 'html.parser')

# get the name and ID using class name
td_element = advise_soup.find('td', class_='PersonName')

if td_element:
    strong_element = td_element.find('strong')
    #If the name and ID are here
    if strong_element:
        #split it apart to find both
        text = strong_element.text.strip()
        parts = text.split('(')
        name = parts[0].split(':')[1].strip()
        student_id = parts[1].replace(')', '').strip()
        print("Name:", name)
        print("Student ID:", student_id)
    else:
        print("Strong tag not found within td_element")
else:
    print("td_element not found")

# Initialize variables to store extracted information
program = None
catalog = None
anticipated_completion_date = None

# Find all <td> elements with class 'Bold'
td_elements = advise_soup.find_all('td', class_='Bold')

# Extract information from each <td> element
for td in td_elements:
    # Extract program information
    if "Program" in td.text:
        program_element = td.find_next_sibling('td')
        if program_element:
            program = program_element.text.strip()
    # Extract catalog information
    elif "Catalog" in td.text:
        catalog_element = td.find_next_sibling('td')
        if catalog_element:
            catalog = catalog_element.text.strip()
    # Extract anticipated completion date information
    elif "Anticipated Completion Date" in td.text:
        anticipated_completion_element = td.find_next_sibling('td')
        if anticipated_completion_element:
            anticipated_completion_date = anticipated_completion_element.text.strip()

# Print the extracted information
print("Program:", program)
print("Catalog:", catalog)
print("Anticipated Completion Date:", anticipated_completion_date)

# Find all <td> elements
td_elements = advise_soup.find_all('td')

# Initialize variables to store extracted information
advisor = None
class_level = None

class_level_pattern = re.compile(r'Class\s*Level:\s*(\w+)', re.IGNORECASE)

# Extract information from each <td> element
for td in td_elements:
    text = td.get_text().strip()
    # Match advisor information
    if "Advisor:" in text:
        advisor = text.split(":")[1].strip()
        if "Class Level" in advisor:
            index = advisor.index("Class Level")
            advisor = advisor[:index].strip()
    # Match class level information
    class_level_match = class_level_pattern.search(text)
    if class_level_match and not class_level:
        class_level = class_level_match.group(1).strip()

# Print the extracted information
print("Advisor:", advisor)
print("Class Level:", class_level)

#get grad elements using the class name
in_progress_elements = advise_soup.find_all(class_='ReqName')

print("Graduation Requirements in Progress:")
for element in in_progress_elements:
    print(element.get_text(strip=True))

#get courses that have this class
courses = advise_soup.find_all('td', class_='SubReqName')

#check if not started class and print
print("Graduation Requirements Not Started")
for course in courses:
    if course.find('b', class_='StatusNotStarted'):
        course_name = course.text.strip().split('<')[0].strip()  # Extract course name
        print(course_name)


# Define the regular expression pattern to capture all instances of the number
pattern = r'(\d+)\s+credits\s+needed'

# Find all instances of the pattern in the HTML content
matches = re.findall(pattern, html_source)

# Extract the 4th and 5th matches and print
fourth_match = matches[4]
fifth_match = matches[5]
print("200+ Level Credits Earned (out of 54 required): ", fourth_match)
print("Total Credits Earned (out of 120 required): ", fifth_match)

# Get the HTML content of the current page
html_content = driver.page_source

# Save HTML content to a local file
with open('webadvisor_audit.html', 'w', encoding='utf-8') as f:
    f.write(html_content)

#If error pops up with rendering the html elements ignore and continue printing
try:
    pdfkit.from_file('webadvisor_audit.html', 'audit.pdf')
except OSError as e:
    pass


