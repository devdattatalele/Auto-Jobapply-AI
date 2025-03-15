import os
import time
import asyncio
import pandas as pd
import google.generativeai as genai
import logging
from bs4 import BeautifulSoup
import requests
from dotenv import load_dotenv
from pathlib import Path
from pydantic import SecretStr
from langchain_google_genai import ChatGoogleGenerativeAI

from browser_use import Agent, Controller, ActionResult
from browser_use.browser.browser import Browser, BrowserConfig
from browser_use.browser.context import BrowserContext, BrowserContextConfig

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler('job_application_browser_use.log', mode='w'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Configure API keys
GEMINI_API_KEY = "AIzaSyBQbqjN9Tp-egQokdfTY7TKHM0mlnh_z4s"
CSV_PATH = "Early Bird February Internship Database 1938686a9cc2802dad6bf8933f46e300.csv"
RESUME_PATH = "/Users/dev16/Documents/Krya.ai/resume.pdf"

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
    "gender": "Male",
    "hispanic_ethnicity": "No",
    "veteran_status": "I am not a protected veteran",
    "disability_status": "No, I don't have a disability",
    "question_11886622004": "Yes",  # Are you currently eligible to work in your country of residence?
    "question_11886623004": "No",  # Do you now or in the future require visa sponsorship?
    "4000681004": "Male", #What gender identity do you most closely identify with?
    "4000691004": "No" #Are you a person of transgender experience?
}

# Specific Answers
specific_answers = {
    "what country and time zone are you based in?": "New York, NY",
    "Are you legally authorized to work in the United States?": "Yes",
    "Do you now or in the future require sponsorship for employment visa status?": "No",
    "how did you hear about us": "Company Website",
    "where are you based": "New York, NY"
}

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
    system_instruction="You are an assistant helping to fill out job applications. Analyze the HTML structure and provide guidance on how to interact with form elements."
)

# Initialize controller for custom actions
controller = Controller()

@controller.action('Fill text field')
async def fill_text_field(browser: BrowserContext, selector: str, value: str):
    """Fill a text field with the given value"""
    try:
        element = await browser.page.wait_for_selector(selector, timeout=5000)
        await element.fill(value)
        return ActionResult(extracted_content=f"Filled {selector} with {value}")
    except Exception as e:
        return ActionResult(error=f"Failed to fill {selector}: {str(e)}")

@controller.action('Click element')
async def click_element(browser: BrowserContext, selector: str):
    """Click on an element"""
    try:
        element = await browser.page.wait_for_selector(selector, timeout=5000)
        await element.click()
        return ActionResult(extracted_content=f"Clicked {selector}")
    except Exception as e:
        return ActionResult(error=f"Failed to click {selector}: {str(e)}")

@controller.action('Select dropdown option')
async def select_dropdown_option(browser: BrowserContext, selector: str, option_text: str):
    """Select an option from a dropdown"""
    try:
        # First click to open the dropdown
        dropdown = await browser.page.wait_for_selector(selector, timeout=5000)
        await dropdown.click()
        await asyncio.sleep(0.5)
        
        # Then find and click the option
        option_selector = f"//div[contains(@class, 'select__option') and contains(text(), '{option_text}')]"
        option = await browser.page.wait_for_selector(option_selector, timeout=5000)
        await option.click()
        
        return ActionResult(extracted_content=f"Selected {option_text} from dropdown {selector}")
    except Exception as e:
        return ActionResult(error=f"Failed to select from dropdown {selector}: {str(e)}")

@controller.action('Upload resume')
async def upload_resume(browser: BrowserContext, selector: str):
    """Upload resume to a file input field"""
    try:
        file_input = await browser.page.wait_for_selector(selector, timeout=5000)
        await file_input.set_input_files(RESUME_PATH)
        return ActionResult(extracted_content=f"Uploaded resume to {selector}")
    except Exception as e:
        return ActionResult(error=f"Failed to upload resume to {selector}: {str(e)}")

@controller.action('Check checkbox')
async def check_checkbox(browser: BrowserContext, selector: str):
    """Check a checkbox"""
    try:
        checkbox = await browser.page.wait_for_selector(selector, timeout=5000)
        await checkbox.check()
        return ActionResult(extracted_content=f"Checked checkbox {selector}")
    except Exception as e:
        return ActionResult(error=f"Failed to check checkbox {selector}: {str(e)}")

def get_urls_from_csv():
    """Retrieve URLs from the CSV file"""
    try:
        df = pd.read_csv(CSV_PATH)
        return df['URL'].dropna().tolist()
    except Exception as e:
        logger.error(f"Error reading CSV file: {e}")
        return []

def extract_job_details(url):
    """Extract job application HTML from the URL"""
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
        
        logger.warning(f"No application container found for {url}")
        return None
            
    except requests.RequestException as e:
        logger.error(f"Network error for {url}: {e}")
        return None
    except Exception as e:
        logger.error(f"Error extracting application container from {url}: {e}")
        return None

async def analyze_application_form(url, application_html):
    """Use Gemini to analyze the application form and generate guidance"""
    prompt = f"""
    Job URL: {url}
    
    Analyze the following job application HTML and provide a structured JSON with:
    1. Text field selectors and their corresponding personal information fields
    2. Dropdown selectors and their options
    3. Checkbox selectors
    4. File upload selectors
    5. Submit button selector
    
    {application_html}
    """
    
    try:
        chat_session = model.start_chat(history=[])
        response = chat_session.send_message(prompt)
        return response.text
    except Exception as e:
        logger.error(f"Error analyzing application form: {e}")
        return None

async def process_job_application(url):
    """Process a single job application using browser-use"""
    logger.info(f"Processing job application: {url}")
    
    # Extract job details
    job_details = extract_job_details(url)
    if not job_details:
        logger.error(f"Failed to extract job details for {url}")
        return False
    
    # Analyze the application form
    form_analysis = await analyze_application_form(url, job_details['application_html'])
    if not form_analysis:
        logger.error(f"Failed to analyze application form for {url}")
        return False
    
    # Create a task for the agent
    task = f"""
    Fill out the job application at {url} with the following information:
    
    Personal Information:
    - First Name: {personal_information['name']}
    - Last Name: {personal_information['surname']}
    - Email: {personal_information['email']}
    - Phone: {personal_information['phone']}
    - Preferred Name: {personal_information['preferred_name']}
    - LinkedIn: {personal_information['social_profiles']['linkedin']}
    - Current Company: {personal_information['current_company']}
    
    For dropdowns, use these values:
    {dropdowns}
    
    For specific questions, use these answers:
    {specific_answers}
    
    Upload resume when prompted.
    
    Form Analysis:
    {form_analysis}
    """
    
    # Initialize LLM with Gemini API key
    llm = ChatGoogleGenerativeAI(model='gemini-2.0-flash', api_key=SecretStr(GEMINI_API_KEY))
    
    # Initialize browser and agent
    browser = Browser(config=BrowserConfig(headless=False, disable_security=True))
    agent = Agent(task=task, llm=llm, controller=controller, browser=browser)
    
    try:
        # Run the agent
        await agent.run()
        logger.info(f"Successfully processed job application for {url}")
        return True
    except Exception as e:
        logger.error(f"Error processing job application for {url}: {e}")
        return False
    finally:
        # Clean up
        await browser.close()

async def main():
    # Get URLs from CSV
    urls = get_urls_from_csv()
    
    for url in urls:
        logger.info(f"\nProcessing job listing: {url}")
        success = await process_job_application(url)
        
        if success:
            logger.info(f"Successfully processed {url}")
        else:
            logger.error(f"Failed to process {url}")
        
        # Add a small delay between processing URLs
        await asyncio.sleep(2)

if __name__ == "__main__":
    asyncio.run(main())