from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import time

# Configuration
job_url = "https://job-boards.greenhouse.io/affirm/jobs/6236919003"
test_mode = True
pause_for_review = True

# Personal Information
personal_information = {
    "name": "Devdatta",
    "surname": "Talele",
    "email": "devtalele0@gmail.com",
    "phone": "9370091908",
    "city": "mumbai",
    "state": "maharashtra",
    "country": "india",
    "preferred_name": "Dev",
    "pronouns": "He/Him",
    "current_company": "hdge3",
    "social_profiles": {
        "linkedin": "https://linkedin.com/in/devdattatalele",
        "github": "https://github.com/devdattatalele",
        "twitter": "https://twitter.com/yourhandle",
        "portfolio": "https://devdattatalele.com",
        "stackoverflow": "https://stackoverflow.com/users/yourid",
        "other": "https://other-profile.com"
    },
    "address": "32,threetwo,road",
    "zip_code": "429112",
    "phone_prefix": "+91"
}

# Dropdown configurations
dropdowns = {
    "question_18459316003": "He/Him",
    "question_18459317003": "No",  # Do you now, or will you in the future, require immigration sponsorship to work for Affirm in Canada?
    "question_18459318003": "New York",  #  Which U.S. State or Canadian Province do you reside in?
    "question_18459319003": "Company Website", # How did you first learn about Affirm as an employer?
    "question_18687150003": "No" # Have you previously been employed at Affirm for any length of time?
}

# Specific Answers
specific_answers = {
    "how did you hear about us": "Company Website",
    "where are you based": "New York, NY",
}

resume_path = "/Users/dev16/Documents/Krya.ai/resume.pdf"

# Initialize WebDriver with options
options = webdriver.ChromeOptions()
options.add_argument('--start-maximized')
driver = webdriver.Chrome(options=options)
wait = WebDriverWait(driver, 10)

def scroll_to_element(element):
    driver.execute_script("arguments[0].scrollIntoView({behavior: 'auto', block: 'center'});", element)
    time.sleep(0.5)  # Allow time for scrolling to complete

def fill_select(element_id, value):
    try:
        # Wait for the select element to be present
        select_element = wait.until(EC.presence_of_element_located((By.ID, element_id)))
        scroll_to_element(select_element)
        
        # Find and click the dropdown control
        select_container = select_element.find_element(By.XPATH, "./ancestor::div[contains(@class, 'select')]")
        dropdown_control = select_container.find_element(By.CSS_SELECTOR, "div[class*='control']")
        ActionChains(driver).move_to_element(dropdown_control).click().perform()
        time.sleep(1)  # Give more time for options to appear
        
        # Try different approaches to find and click the option
        try:
            # First attempt: Look for elements with the exact text
            option_xpath = f"//div[contains(@class, 'option') and normalize-space(text())='{value}']"
            option = wait.until(EC.element_to_be_clickable((By.XPATH, option_xpath)))
        except:
            try:
                # Second attempt: Look for elements containing the text
                option_xpath = f"//div[contains(@class, 'option') and contains(normalize-space(text()), '{value}')]"
                option = wait.until(EC.element_to_be_clickable((By.XPATH, option_xpath)))
            except:
                # Third attempt: Try to find by partial class and index if text matching fails
                options = driver.find_elements(By.CSS_SELECTOR, "div[class*='option']")
                found = False
                for opt in options:
                    if value.lower() in opt.text.lower():
                        option = opt
                        found = True
                        break
                
                if not found:
                    raise Exception(f"Could not find option with text '{value}'")
        
        # Click the option with more robust action chain
        ActionChains(driver).move_to_element(option).click().perform()
        time.sleep(1)  # Give time for selection to register
        
        # Verify selection was successful (optional)
        selected_text = dropdown_control.text
        if value not in selected_text:
            print(f"Warning: Selection verification failed for {element_id}. Expected: {value}, Got: {selected_text}")
            
    except Exception as e:
        print(f"Error filling select {element_id} with value {value}: {str(e)}")
        # Add debugging info
        print(f"Current URL: {driver.current_url}")
        print(f"Element visibility status: {wait.until(EC.visibility_of_element_located((By.ID, element_id))).is_displayed()}")
try:
    driver.get(job_url)
    time.sleep(2)

    # --- Personal Information ---
    driver.find_element(By.ID, "first_name").send_keys(personal_information["name"])
    driver.find_element(By.ID, "last_name").send_keys(personal_information["surname"])
    driver.find_element(By.ID, "email").send_keys(personal_information["email"])
    driver.find_element(By.ID, "phone").send_keys(personal_information["phone"])
    driver.find_element(By.ID, "question_18459314003").send_keys(personal_information["preferred_name"])


    # --- Resume Upload ---
    resume_input = driver.find_element(By.ID, "resume")
    resume_input.send_keys(resume_path)
    time.sleep(5)  # Give it time to upload

    # --- Application Questions ---
    driver.find_element(By.ID, "question_18459312003").send_keys(personal_information["social_profiles"]["linkedin"])
    driver.find_element(By.ID, "question_18459313003").send_keys(personal_information["current_company"])
    driver.find_element(By.ID, "question_18459320003").send_keys(personal_information["social_profiles"]["github"])
    driver.find_element(By.ID, "question_18459321003").send_keys(personal_information["social_profiles"]["twitter"])
    driver.find_element(By.ID, "question_18459322003").send_keys(personal_information["social_profiles"]["portfolio"])
    driver.find_element(By.ID, "question_18459323003").send_keys(personal_information["social_profiles"]["other"])
    driver.find_element(By.ID, "question_18459315003").send_keys(personal_information["preferred_name"])

    # --- Handle all dropdowns ---
    for dropdown_id, dropdown_value in dropdowns.items():
        fill_select(dropdown_id, dropdown_value)
        time.sleep(1)  # Brief pause between dropdowns

    # --- Submit Application ---
    if test_mode:
        print("Test mode enabled. Application will not be submitted.")
    else:
        if pause_for_review:
            input("Please review the application and press Enter to submit...")
        submit_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        scroll_to_element(submit_button)
        submit_button.click()

    time.sleep(5)  # Give time for submission

except Exception as e:
    print(f"An error occurred: {e}")

finally:
    if test_mode:
        print("Test mode enabled. Keeping browser open for review.")
        input("Press Enter to close the browser...")
    driver.quit()