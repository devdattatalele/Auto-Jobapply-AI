from langchain_google_genai import ChatGoogleGenerativeAI
import google.generativeai as genai
from pydantic import SecretStr
from browser_use import Agent, Controller, ActionResult
from browser_use.browser.browser import Browser, BrowserConfig
from browser_use.browser.context import BrowserContext
from dotenv import load_dotenv
import asyncio
import os
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler('improved_job_application.log', mode='w'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Resume path
RESUME_PATH = os.path.abspath("resume.pdf")

# Initialize controller with improved custom actions
controller = Controller()

@controller.action('Wait for page load')
async def wait_for_page_load(browser: BrowserContext):
    """Wait for the page to be fully loaded"""
    try:
        # Wait for network to be idle
        await browser.context.page.wait_for_load_state("networkidle", timeout=30000)
        # Wait for DOM content to be loaded
        await browser.context.page.wait_for_load_state("domcontentloaded", timeout=30000)
        return ActionResult(extracted_content="Page fully loaded")
    except Exception as e:
        return ActionResult(error=f"Failed to wait for page load: {str(e)}")

@controller.action('Fill text field with retry')
async def fill_text_field_with_retry(browser: BrowserContext, selector: str, value: str, max_retries: int = 3):
    """Fill a text field with retry mechanism"""
    for attempt in range(max_retries):
        try:
            # Wait for element to be visible and enabled
            element = await browser.context.page.wait_for_selector(selector, timeout=10000, state="visible")
            
            # Ensure element is ready for interaction
            await browser.context.page.evaluate("(element) => { element.scrollIntoView({behavior: 'smooth', block: 'center'}); }", element)
            await asyncio.sleep(1.0)  # Increased delay after scrolling
            
            # Clear the field first
            await element.click(click_count=3)  # Triple click to select all text
            await element.press("Backspace")  # Delete selected text
            await asyncio.sleep(0.5)  # Wait after clearing
            
            # Type the value with small delays between characters
            await element.type(value, delay=100)  # Increased delay between keystrokes
            await asyncio.sleep(0.5)  # Wait after typing
            
            # Verify the input was accepted
            try:
                input_value = await browser.context.page.evaluate(f"document.querySelector('{selector}').value")
                if input_value == value:
                    return ActionResult(extracted_content=f"Successfully filled {selector} with {value} (attempt {attempt+1})")
                else:
                    logger.warning(f"Input verification failed for {selector}. Expected: {value}, Got: {input_value}")
                    # Try again with a different approach
                    await element.fill('')  # Clear using fill method
                    await asyncio.sleep(0.5)
                    await element.fill(value)  # Fill using fill method
                    await asyncio.sleep(0.5)
                    
                    # Verify again
                    input_value = await browser.context.page.evaluate(f"document.querySelector('{selector}').value")
                    if input_value == value:
                        return ActionResult(extracted_content=f"Successfully filled {selector} with {value} using alternative method (attempt {attempt+1})")
            except Exception as verify_error:
                logger.warning(f"Verification error for {selector}: {str(verify_error)}")
                # Continue with the retry loop
                
        except Exception as e:
            logger.warning(f"Attempt {attempt+1} failed to fill {selector}: {str(e)}")
            if attempt == max_retries - 1:
                return ActionResult(error=f"Failed to fill {selector} after {max_retries} attempts: {str(e)}")
            await asyncio.sleep(2)  # Increased wait before retrying
    
    return ActionResult(error=f"Failed to fill {selector} after {max_retries} attempts")

@controller.action('Click element with retry')
async def click_element_with_retry(browser: BrowserContext, selector: str, max_retries: int = 3):
    """Click an element with retry mechanism"""
    for attempt in range(max_retries):
        try:
            # Wait for element to be visible and enabled
            element = await browser.context.page.wait_for_selector(selector, timeout=10000, state="visible")
            
            # Ensure element is ready for interaction
            await browser.context.page.evaluate("(element) => { element.scrollIntoView({behavior: 'smooth', block: 'center'}); }", element)
            await asyncio.sleep(1.0)  # Increased delay after scrolling
            
            # Check if element is clickable
            is_clickable = await browser.context.page.evaluate("""
                (element) => {
                    const style = window.getComputedStyle(element);
                    return style.display !== 'none' && 
                           style.visibility !== 'hidden' && 
                           style.opacity !== '0' &&
                           element.offsetWidth > 0 &&
                           element.offsetHeight > 0;
                }
            """, element)
            
            if not is_clickable:
                logger.warning(f"Element {selector} is not clickable")
                if attempt == max_retries - 1:
                    return ActionResult(error=f"Element {selector} is not clickable after {max_retries} attempts")
                await asyncio.sleep(2)  # Increased wait before retrying
                continue
            
            # Click the element
            await element.click()
            await asyncio.sleep(1.5)  # Increased delay after clicking
            
            return ActionResult(extracted_content=f"Successfully clicked {selector} (attempt {attempt+1})")
                
        except Exception as e:
            logger.warning(f"Attempt {attempt+1} failed to click {selector}: {str(e)}")
            if attempt == max_retries - 1:
                return ActionResult(error=f"Failed to click {selector} after {max_retries} attempts: {str(e)}")
            await asyncio.sleep(2)  # Increased wait before retrying
    
    return ActionResult(error=f"Failed to click {selector} after {max_retries} attempts")

@controller.action('Select dropdown option with retry')
async def select_dropdown_option_with_retry(browser: BrowserContext, selector: str, option_text: str, max_retries: int = 3):
    """Select an option from a dropdown with retry mechanism"""
    for attempt in range(max_retries):
        try:
            # First click to open the dropdown
            dropdown = await browser.context.page.wait_for_selector(selector, timeout=10000, state="visible")
            
            # Ensure dropdown is ready for interaction
            await browser.context.page.evaluate("(element) => { element.scrollIntoView({behavior: 'smooth', block: 'center'}); }", dropdown)
            await asyncio.sleep(0.5)  # Small delay after scrolling
            
            # Click the dropdown
            await dropdown.click()
            await asyncio.sleep(1.5)  # Increased delay after opening dropdown
            
            # Try different option selectors with more comprehensive patterns
            option_selectors = [
                # React-select specific patterns
                f"//div[contains(@class, 'select__option') and contains(., '{option_text}')]",
                f"//div[contains(@class, 'select-option') and contains(., '{option_text}')]",
                # Common dropdown patterns
                f"//li[contains(@class, 'select__option') and contains(., '{option_text}')]",
                f"//li[contains(@class, 'dropdown-item') and contains(., '{option_text}')]",
                # More generic patterns
                f"//div[contains(@role, 'option') and contains(., '{option_text}')]",
                f"//li[contains(@role, 'option') and contains(., '{option_text}')]",
                # Very generic patterns as fallback
                f"//div[contains(., '{option_text}') and not(contains(., '{option_text} '))]",
                f"//li[contains(., '{option_text}') and not(contains(., '{option_text} '))]",
                f"//span[contains(., '{option_text}')]"
            ]
            
            # Try to find the option
            option = None
            for option_selector in option_selectors:
                try:
                    # Use a longer timeout for finding options
                    options = await browser.context.page.query_selector_all(option_selector)
                    if options and len(options) > 0:
                        option = options[0]
                        break
                except Exception as selector_error:
                    logger.debug(f"Selector {option_selector} failed: {str(selector_error)}")
                    continue
            
            if not option:
                logger.warning(f"Option '{option_text}' not found in dropdown {selector}")
                # Try clicking on the dropdown again to ensure it's open
                try:
                    await dropdown.click()
                    await asyncio.sleep(1.5)
                except:
                    pass
                    
                # Try to take a screenshot for debugging if in test mode
                try:
                    await browser.context.page.screenshot(path=f"dropdown_debug_{attempt}.png")
                    logger.info(f"Saved dropdown debug screenshot to dropdown_debug_{attempt}.png")
                except:
                    pass
                    
                # Close dropdown by clicking elsewhere
                try:
                    await browser.context.page.mouse.click(0, 0)
                except:
                    pass
                    
                if attempt == max_retries - 1:
                    return ActionResult(error=f"Option '{option_text}' not found in dropdown {selector} after {max_retries} attempts")
                    
                await asyncio.sleep(2)  # Longer wait before retrying
                continue
            
            # Click the option with retry
            click_success = False
            for click_attempt in range(3):
                try:
                    await option.click()
                    click_success = True
                    break
                except Exception as click_error:
                    logger.warning(f"Click attempt {click_attempt+1} failed: {str(click_error)}")
                    await asyncio.sleep(0.5)
            
            if not click_success:
                if attempt == max_retries - 1:
                    return ActionResult(error=f"Failed to click option '{option_text}' after multiple attempts")
                continue
                
            # Wait after selection to let the UI update
            await asyncio.sleep(1.0)  # Increased delay after selection
            
            return ActionResult(extracted_content=f"Successfully selected '{option_text}' from dropdown {selector} (attempt {attempt+1})")
                
        except Exception as e:
            logger.warning(f"Attempt {attempt+1} failed to select from dropdown {selector}: {str(e)}")
            # Try to close dropdown by clicking elsewhere
            try:
                await browser.context.page.mouse.click(0, 0)
            except:
                pass
                
            if attempt == max_retries - 1:
                return ActionResult(error=f"Failed to select from dropdown {selector} after {max_retries} attempts: {str(e)}")
                
            await asyncio.sleep(2)  # Increased wait before retrying
    
    return ActionResult(error=f"Failed to select from dropdown {selector} after {max_retries} attempts")

@controller.action('Upload resume with retry')
async def upload_resume_with_retry(browser: BrowserContext, selector: str, max_retries: int = 3):
    """Upload resume with retry mechanism"""
    for attempt in range(max_retries):
        try:
            # Wait for file input to be present
            file_input = await browser.context.page.wait_for_selector(selector, timeout=10000)
            
            # Ensure element is ready for interaction
            try:
                await browser.context.page.evaluate("(element) => { element.scrollIntoView({behavior: 'smooth', block: 'center'}); }", file_input)
                await asyncio.sleep(1.0)  # Delay after scrolling
            except Exception as scroll_error:
                logger.warning(f"Scroll error: {str(scroll_error)}")
                # Continue anyway as file inputs might be hidden
            
            # Upload the file
            await file_input.set_input_files(RESUME_PATH)
            await asyncio.sleep(3)  # Wait for upload to complete
            
            # Try to verify upload success
            try:
                # Check for success indicators like file name display or upload complete message
                upload_success = await browser.context.page.query_selector('div[class*="file-name"], span[class*="file-uploaded"]')
                if upload_success:
                    logger.info("Found upload success indicator")
            except Exception as verify_error:
                logger.warning(f"Upload verification error: {str(verify_error)}")
                # Continue anyway as verification is optional
            
            return ActionResult(extracted_content=f"Successfully uploaded resume to {selector} (attempt {attempt+1})")
                
        except Exception as e:
            logger.warning(f"Attempt {attempt+1} failed to upload resume to {selector}: {str(e)}")
            if attempt == max_retries - 1:
                return ActionResult(error=f"Failed to upload resume to {selector} after {max_retries} attempts: {str(e)}")
            await asyncio.sleep(2)  # Increased wait before retrying
    
    return ActionResult(error=f"Failed to upload resume to {selector} after {max_retries} attempts")

@controller.action('Direct dropdown selection')
async def direct_dropdown_selection(browser: BrowserContext, dropdown_index: int, option_index: int):
    """Directly select a dropdown option using element indices rather than selectors"""
    try:
        # Get all dropdown elements
        dropdown_elements = await browser.context.page.query_selector_all('div[class*="select__"], div[role="combobox"]')
        
        if dropdown_index >= len(dropdown_elements):
            return ActionResult(error=f"Dropdown index {dropdown_index} out of range (only {len(dropdown_elements)} dropdowns found)")
            
        # Click the dropdown to open it
        dropdown = dropdown_elements[dropdown_index]
        await dropdown.click()
        await asyncio.sleep(2)  # Longer wait for dropdown to open fully
        
        # Get all option elements that appear after clicking
        option_elements = await browser.context.page.query_selector_all('div[class*="select__option"], div[role="option"], li[role="option"]')
        
        if not option_elements or option_index >= len(option_elements):
            # Take screenshot for debugging
            try:
                await browser.context.page.screenshot(path=f"dropdown_options_debug.png")
                logger.info(f"Saved dropdown options debug screenshot")
            except:
                pass
                
            return ActionResult(error=f"Option index {option_index} out of range (only {len(option_elements)} options found)")
        
        # Click the option
        option = option_elements[option_index]
        await option.click()
        await asyncio.sleep(1.5)  # Wait for selection to take effect
        
        # Get the text of the selected option for logging
        option_text = await browser.context.page.evaluate('(element) => element.textContent', option)
        
        return ActionResult(extracted_content=f"Successfully selected option {option_index} ('{option_text}') from dropdown {dropdown_index}")
        
    except Exception as e:
        return ActionResult(error=f"Failed to select dropdown option: {str(e)}")

async def main():
    # Configure Gemini API
    GEMINI_API_KEY = "AIzaSyBQbqjN9Tp-egQokdfTY7TKHM0mlnh_z4s"  # You should store this in environment variables for production
    genai.configure(api_key=GEMINI_API_KEY)
    
    # Initialize LLM with Gemini
    llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", api_key=SecretStr(GEMINI_API_KEY), temperature=0)
    
    # Initialize browser with improved configuration
    browser = Browser(config=BrowserConfig(
        headless=False,  # Set to True for production
        disable_security=True
    ))
    
    # Create agent with improved task description
    agent = Agent(
        task="""
        # Task configuration for job application automation
        # Target job board URL and settings
        fill out the job application on this website : https://job-boards.greenhouse.io/affirm/jobs/6354992003
        test_mode: true
        pause_for_review: true

        # Personal and contact information
        personal_information:
          name: "Devdatta"
          surname: "Talele"
          email: "devtalele0@gmail.com"
          phone: "9370091908"
          city: "mumbai"
          state: "maharashtra"
          country: "india"
          preferred_name: "Dev"
          pronouns: "He/Him"
          current_company: "hdge3"
          # Social media and professional profiles
          social_profiles:
            linkedin: "https://linkedin.com/in/yourprofile"
            github: "https://github.com/yourusername"
            twitter: "https://twitter.com/yourhandle"
            portfolio: "https://yourportfolio.com"
            stackoverflow: "https://stackoverflow.com/users/yourid"
            other: "https://other-profile.com"

        # Professional background and skills
        professional_profile:
          years_of_experience: 5
          # Technical skills
          technical:
            - "Python"
            - "JavaScript"
            - "React"
          # Professional achievements
          achievements:
            - "Achievement 1"
            - "Achievement 2"
          work_history: "Brief work history"
          # Educational background
          education:
            - degree: "Bachelor's Degree"
              field: "Computer Science"
              school: "University Name"
              year: 2020
          previous_employee: "No"

        # Path to resume file
        resume_path: "resume.pdf"
        
        # Important Instructions:
        1. First navigate to the URL and wait for the page to fully load using the 'Wait for page load' action.
        2. Fill out the basic information fields (first name, last name, email, phone) using the 'Fill text field with retry' action.
        3. Upload the resume using the 'Upload resume with retry' action with selector '#resume'.
        4. Fill out additional fields like LinkedIn profile, current company, preferred name using the 'Fill text field with retry' action.
        5. For dropdowns, try these approaches in order:
           a. First try using the 'Select dropdown option with retry' action with the appropriate selector.
           b. If that fails, use the 'Direct dropdown selection' action with the dropdown index and option index.
           c. As a last resort, use 'Click element' actions to click the dropdown and then the option directly by index.
        6. For any buttons or links, use the 'Click element with retry' action.
        7. If you encounter any errors, try alternative selectors or approaches.
        8. Take your time between actions to ensure the page has time to respond - add delays of 1-2 seconds between actions.
        9. For dropdown issues, try clicking the dropdown first, then clicking the option as separate steps.
        """,
        llm=llm,
        controller=controller,
        browser=browser
    )
    
    try:
        # Run the agent
        result = await agent.run()
        print(result)
    except Exception as e:
        logger.error(f"Error running agent: {e}")
    finally:
        # Clean up
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())