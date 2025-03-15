import os
import time
import subprocess
import google.generativeai as genai
import pandas as pd
from bs4 import BeautifulSoup
import requests

# Configure API keys
GEMINI_API_KEY = "AIzaSyBQbqjN9Tp-egQokdfTY7TKHM0mlnh_z4s"
CSV_PATH = "Early Bird February Internship Database 1938686a9cc2802dad6bf8933f46e300.csv"

# Configure Gemini
genai.configure(api_key=GEMINI_API_KEY)
generation_config = {
    "temperature": 1.55,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

model = genai.GenerativeModel(
  model_name="gemini-2.0-flash",
  generation_config=generation_config,
  system_instruction="you are a bot specially made to generate CODE ONLY which would be on selenium code in python which would go to provided url and auto all the questions of JOB APPLICATION (including dropdown boxes) and even uplaod the resume at last. \n\nYOU WILL BE provided with url and all elements of that URL which would contain the main application from which you would extract questions and element ID for properly generating code which will navigate to that element and fill the answer by refering the content below. I have resume.pdf in same directory to code would be stored \n\nFor dropdown handeling it should have a click event on select element = \"select__\"\n\ntest_mode: true\npause_for_review: true\n\npersonal_information:\n  name: \"Devdatta\"\n  surname: \"Talele\"\n  email: \"devtalele0@gmail.com\"\n  phone: \"9370091908\"\n  city: \"mumbai\"\n  state: \"maharashtra\"\n  country: \"india\"\n  preferred_name: \"Dev\"\n  pronouns: \"He/Him\"  \n  current_company: \"hdge3\"\n  social_profiles:\n    linkedin: \"https://linkedin.com/in/devdattatalele\"\n    github: \"https://github.com/devdattatalele\"\n    twitter: \"https://twitter.com/yourhandle\"\n    portfolio: \"https://devdattatalele.com\" \n    stackoverflow: \"https://stackoverflow.com/users/yourid\" ]\n    other: \"https://other-profile.com\"\n  address: \"32,threetwo,road\"\n  zip_code: \"429112\"\n  phone_prefix: \"+91\"\n\nprofessional_profile:\n  years_of_experience: 5\n  technical:\n    - \"Python\"\n    - \"JavaScript\"\n    - \"React\"\n    # Add more skills\n  achievements:\n    - \"thingbot project\"\n    - \"Achievement 2\"\n    # Add more achievements\n  work_history: \"Brief work history\"\n  education:\n    - degree: \"Bachelor's Degree\"\n      field: \"Computer Science\"\n      school: \"University Name\"\n      year: 2020\n  previous_employee: \"No\" \n\nexperience_level:\n  entry: false\n  mid: true\n  senior: false\n\n# VERY IMPORTANT: Dropdown configurations (add entries for ALL dropdowns you encounter)\ndropdowns:\n  pronouns: \"He/Him\"  # Example\n  eeo_gender: \"Male\" #  Based on Affirm form\n  eeo_hispanic_latino: \"No\" # Based on Affirm form\n  veteran_status: \"I am not a protected veteran\"  # Based on Affirm form\n  disability_status: \"No, I don't have a disability\"  # Based on Affirm form\n  # Add more dropdown configurations here, based on Inspect Element\n  #  Use the ID or name of the dropdown as the key\n  # Examples:\n  # source: \"Referral\" #  If 'source' is a dropdown\n  visa_sponsorship_required: \"No\"\n  us_authorization: \"Yes\" # name taken from dropdown\n  ca_authorization: \"Yes\" # name taken from dropdown\n\n# Specific answers (for questions the AI might not handle well)\nspecific_answers:\n  \"Are you legally authorized to work in the United States?\": \"Yes\"\n  \"Do you now or in the future require sponsorship for employment visa status (e.g., H-1B, TN, E-3, F-1 visa status)?\": \"No\"\n  # Add more specific answers as needed\n\nwork_authorization:\n  us_work_permit: false\n  eu_work_permit: false\n  uk_work_permit: false\n  requires_sponsorship: false\n  visa_status: \"\"\n  legally_allowed_to_work_in_us: false\n  legally_allowed_to_work_in_eu: false\n  legally_allowed_to_work_in_uk: false\n  requires_us_visa: true\n  requires_eu_visa: true\n  requires_uk_visa: true\n  willing_to_undergo_background_checks: true\n  willing_to_undergo_drug_tests: false\n\nlocation_preferences:\n  remote: true\n  hybrid: true\n  onsite: false\n  willing_to_relocate: false\n  preferred_locations:\n    - \"Sanjose\"\n    - \"calfornia\"\n\nresume_path: \"/Users/dev16/Documents/Krya.ai/resume.pdf\"  #  CORRECT THIS PATH\n\nresponse_templates:\n  why_interested: \"Template for why interested\"\n  greatest_strength: \"Template for greatest strength\"\n  work_style: \"Template for work style\"\n  salary_expectation: \"Template for salary expectations\"\n\napplication_preferences:\n  preferred_job_type:\n    - \"full-time\"\n    - \"contract\"\n  industry_preferences:\n    - \"Technology\"\n    - \"Software\"\n  company_blacklist: []\n  salary_range:\n    minimum: \"\"\n    preferred: \"\"\n    currency: \"USD\"\n\napplication_info:\n  source: \"LinkedIn\"  # or any other source\ndropdowns:\n  pronouns:\n    value: \"He/Him\"\n  work_authorization:\n    value: \"Yes\"\n  visa_sponsorship:\n    value: \"No\"\n  location:\n    value: \"New York\"\n  source:\n    value: \"LinkedIn\"\n\nspecific_answers:\n  \"how did you hear about us\": \"Company Website\"\n  \"where are you based\": \"New York, NY\"\n\n\nFollowing is example code output from selenium import webdriver\nfrom selenium.webdriver.common.by import By\nfrom selenium.webdriver.support.ui import WebDriverWait\nfrom selenium.webdriver.support import expected_conditions as EC\nfrom selenium.webdriver.common.action_chains import ActionChains\nimport time\n\n# Configuration\njob_url = \"https://job-boards.greenhouse.io/grafanalabs/jobs/5336218004\"\ntest_mode = True\npause_for_review = True\n\n# Personal Information\npersonal_information = {\n    \"name\": \"Devdatta\",\n    \"surname\": \"Talele\",\n    \"email\": \"devtalele0@gmail.com\",\n    \"phone\": \"9370091908\",\n    \"city\": \"mumbai\",\n    \"state\": \"maharashtra\",\n    \"country\": \"india\",\n    \"preferred_name\": \"Dev\",\n    \"pronouns\": \"He/Him\",\n    \"current_company\": \"hdge3\",\n    \"social_profiles\": {\n        \"linkedin\": \"https://linkedin.com/in/devdattatalele\",\n        \"github\": \"https://github.com/devdattatalele\",\n        \"twitter\": \"https://twitter.com/yourhandle\",\n        \"portfolio\": \"https://devdattatalele.com\",\n        \"stackoverflow\": \"https://stackoverflow.com/users/yourid\",\n        \"other\": \"https://other-profile.com\"\n    },\n    \"address\": \"32,threetwo,road\",\n    \"zip_code\": \"429112\",\n    \"phone_prefix\": \"+91\"\n}\n\n# Dropdown configurations\ndropdowns = {\n    \"gender\": \"Male\",\n    \"hispanic_ethnicity\": \"No\",\n    \"veteran_status\": \"I am not a protected veteran\",\n    \"disability_status\": \"No, I don't have a disability\",\n    \"question_11886622004\": \"Yes\",  # Are you currently eligible to work in your country of residence?\n    \"question_11886623004\": \"No\",  # Do you now or in the future require visa sponsorship?\n    \"4000681004\": \"Male\", #What gender identity do you most closely identify with?\n    \"4000691004\": \"No\" #Are you a person of transgender experience?\n}\n\n# Specific Answers\nspecific_answers = {\n    \"what country and time zone are you based in?\": \"New York, NY\",\n}\n\nresume_path = \"/Users/dev16/Documents/Krya.ai/resume.pdf\"\n\n# Initialize WebDriver with options\noptions = webdriver.ChromeOptions()\noptions.add_argument('--start-maximized')\ndriver = webdriver.Chrome(options=options)\nwait = WebDriverWait(driver, 10)\n\ndef scroll_to_element(element):\n    driver.execute_script(\"arguments[0].scrollIntoView({behavior: 'auto', block: 'center'});\", element)\n    time.sleep(0.5)  # Allow time for scrolling to complete\n\ndef fill_select(element_id, value):\n    try:\n        # Wait for the select element to be present\n        select_element = wait.until(EC.presence_of_element_located((By.ID, element_id)))\n        scroll_to_element(select_element)\n        \n        # Find the parent element with class 'select-shell'\n        select_shell = select_element.find_element(By.XPATH, \"./ancestor::div[contains(@class, 'select-shell')]\")\n        \n        # Click the control to open dropdown\n        control = select_shell.find_element(By.CLASS_NAME, \"select__control\")\n        scroll_to_element(control)\n        ActionChains(driver).move_to_element(control).click().perform()\n        time.sleep(0.5)\n        \n        # Wait for and click the option\n        option_xpath = f\"//div[contains(@class, 'select__option') and contains(text(), '{value}')]\"\n        option = wait.until(EC.element_to_be_clickable((By.XPATH, option_xpath)))\n        ActionChains(driver).move_to_element(option).click().perform()\n        time.sleep(0.5)\n        \n    except Exception as e:\n        print(f\"Error filling select {element_id}: {str(e)}\")\n\ntry:\n    driver.get(job_url)\n    time.sleep(2)\n\n    # --- Personal Information ---\n    driver.find_element(By.ID, \"first_name\").send_keys(personal_information[\"name\"])\n    driver.find_element(By.ID, \"last_name\").send_keys(personal_information[\"surname\"])\n    driver.find_element(By.ID, \"preferred_name\").send_keys(personal_information[\"preferred_name\"])\n    driver.find_element(By.ID, \"email\").send_keys(personal_information[\"email\"])\n    driver.find_element(By.ID, \"phone\").send_keys(personal_information[\"phone\"])\n\n    # --- Resume Upload ---\n    resume_input = driver.find_element(By.ID, \"resume\")\n    resume_input.send_keys(resume_path)\n    time.sleep(5)  # Give it time to upload\n\n    # --- Application Questions ---\n    driver.find_element(By.ID, \"question_11886619004\").send_keys(personal_information[\"social_profiles\"][\"linkedin\"])\n    driver.find_element(By.ID, \"question_11886620004\").send_keys(personal_information[\"current_company\"])\n    driver.find_element(By.ID, \"question_11886621004\").send_keys(specific_answers[\"what country and time zone are you based in?\"])\n\n    # --- Handle all dropdowns ---\n    for dropdown_id, dropdown_value in dropdowns.items():\n        fill_select(dropdown_id, dropdown_value)\n        time.sleep(1)  # Brief pause between dropdowns\n\n    # --- Consent Checkbox ---\n    try:\n        consent_checkbox = driver.find_element(By.ID, \"gdpr_demographic_data_consent_given_1\")\n        scroll_to_element(consent_checkbox)\n        consent_checkbox.click()\n    except Exception as e:\n        print(f\"Error with consent checkbox: {str(e)}\")\n\n    # --- Submit Application ---\n    if test_mode:\n        print(\"Test mode enabled. Application will not be submitted.\")\n    else:\n        if pause_for_review:\n            input(\"Please review the application and press Enter to submit...\")\n        submit_button = driver.find_element(By.CSS_SELECTOR, \"button[type='submit']\")\n        scroll_to_element(submit_button)\n        submit_button.click()\n\n    time.sleep(5)  # Give time for submission\n\nexcept Exception as e:\n    print(f\"An error occurred: {e}\")\n\nfinally:\n    if test_mode:\n        print(\"Test mode enabled. Keeping browser open for review.\")\n        input(\"Press Enter to close the browser...\")\n    driver.quit()",
)


def get_urls_from_csv():
    """Retrieve URLs from the CSV file"""
    try:
        df = pd.read_csv(CSV_PATH)
        return df['URL'].dropna().tolist()
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        return []

def extract_job_details(url):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # List of potential selectors for application containers
        selectors = [
            {'class': 'application--container'},
            {'id': 'main_fields'},
            {'class': 'application-form'},
            {'class': 'job-application'},
            {'id': 'application-form'},
            {'class': 'greenhouse-job-application'}
        ]
        
        # Try each selector until we find content
        for selector in selectors:
            container = soup.find('div', selector)
            if container:
                return {
                    'application_html': str(container),
                    'url': url,
                    'selector_used': selector
                }
        
        print(f"No application container found for {url}")
        return None
            
    except requests.RequestException as e:
        print(f"Network error for {url}: {e}")
        return None
    except Exception as e:
        print(f"Error extracting application container from {url}: {e}")
        return None

def generate_and_save_output(url, application_data):
    """Generate Selenium automation code using Gemini and save it"""
    # Add template code that will be included in every generated file
    template_code = """
# Configuration and personal information code as before...
"""
    
    prompt = f"""
    Job URL: {url}
    
    
    {application_data['application_html']}
    
    """
    
    try:
        chat_session = model.start_chat(
            history=[
               
            ]
        )
        response = chat_session.send_message(prompt)
        generated_code = response.text

        # Clean up and save code as before...
        
        if generated_code.startswith("```python"):
            generated_code = generated_code[len("```python"):].strip()
        if generated_code.endswith("```"):
            generated_code = generated_code[:-len("```")].strip()

        # Save the output
        script_path = os.path.join(os.getcwd(), f"automation_run.py")
        with open(script_path, "w") as f:
            f.write(generated_code)
        
        return script_path
    except Exception as e:
        print(f"Error generating automation code: {e}")
        return None

def run_generated_script(script_path):
    """Run the generated Python script and wait for completion"""
    try:
        result = subprocess.run(
            ['python', script_path],
            capture_output=True,
            text=True,
            check=True
        )
        print("Analysis output:", result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error running analysis: {e}")
        print("Error output:", e.stderr)
        return False

def main():
    # Get URLs from CSV
    urls = get_urls_from_csv()
    
    for url in urls:
        print(f"\nProcessing job listing: {url}")
        
        # Extract job details
        job_details = extract_job_details(url)
        if not job_details:
            continue
            
        # Generate and save analysis code
        script_path = generate_and_save_output(url, job_details)
        if not script_path:
            continue
            
        # Run the analysis
        print(f"Running analysis for {url}")
        success = run_generated_script(script_path)
        
        if success:
            print(f"Successfully analyzed {url}")
        else:
            print(f"Failed to analyze {url}")
        
        # Add a small delay between processing URLs
        time.sleep(2)

if __name__ == "__main__":
    main()