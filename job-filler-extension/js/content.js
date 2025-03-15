// Global variables
let personalInfo = {};
let apiKey = '';
let formElements = [];
let isProcessing = false;

// Listen for messages from popup
chrome.runtime.onMessage.addListener(function(request, sender, sendResponse) {
  // Add a ping handler to check if content script is loaded
  if (request.action === "ping") {
    sendResponse({status: 'success'});
    return;
  }
  
  if (request.action === "fillForm") {
    if (isProcessing) {
      sendResponse({status: 'error', message: 'Already processing a form'});
      return;
    }
    
    isProcessing = true;
    
    // Get personal info from storage with debug logging
    chrome.storage.sync.get(null, function(data) {
      console.log("Retrieved storage data:", data);
      personalInfo = data;
      apiKey = data.apiKey;
      
      if (!apiKey) {
        console.error("API key not found in storage");
        sendResponse({status: 'error', message: 'API key not set'});
        isProcessing = false;
        return;
      }
      
      console.log("API key retrieved successfully");
      
      // Start the form filling process
      analyzeAndFillForm()
        .then(result => {
          sendResponse({status: 'success'});
        })
        .catch(error => {
          console.error('Error filling form:', error);
          sendResponse({status: 'error', message: error.toString()});
        })
        .finally(() => {
          isProcessing = false;
        });
    });
    
    return true; // Required for async sendResponse
  }
});

// Main function to analyze and fill the form
async function analyzeAndFillForm() {
  try {
    // Show a visual indicator that the extension is working
    showOverlay('Analyzing form...');
    
    // Collect form elements
    formElements = collectFormElements();
    
    // If no form elements found, try to find them in iframes
    if (formElements.length === 0) {
      updateOverlay('No form elements found on main page. Checking iframes...');
      // Note: Accessing iframe content is subject to same-origin policy
      // This would require additional permissions and handling
    }
    
    // Analyze the form using Gemini API
    updateOverlay('Analyzing form with Gemini API...');
    const formAnalysis = await analyzeFormWithGemini();
    
    // Fill the form based on the analysis
    updateOverlay('Filling form...');
    await fillFormBasedOnAnalysis(formAnalysis);
    
    // Complete
    updateOverlay('Form filled successfully!', true);
    
    return true;
  } catch (error) {
    console.error('Error in analyzeAndFillForm:', error);
    updateOverlay('Error: ' + error.message, true, true);
    throw error;
  }
}

// Collect all form elements on the page
function collectFormElements() {
  const elements = [];
  
  // Text inputs
  document.querySelectorAll('input[type="text"], input[type="email"], input[type="tel"], input[type="url"], textarea').forEach(el => {
    elements.push({
      type: 'text',
      element: el,
      id: el.id,
      name: el.name,
      placeholder: el.placeholder,
      label: findLabelForElement(el)
    });
  });
  
  // Select dropdowns
  document.querySelectorAll('select').forEach(el => {
    elements.push({
      type: 'select',
      element: el,
      id: el.id,
      name: el.name,
      options: Array.from(el.options).map(opt => opt.text),
      label: findLabelForElement(el)
    });
  });
  
  // File inputs
  document.querySelectorAll('input[type="file"]').forEach(el => {
    elements.push({
      type: 'file',
      element: el,
      id: el.id,
      name: el.name,
      label: findLabelForElement(el)
    });
  });
  
  // Checkboxes
  document.querySelectorAll('input[type="checkbox"]').forEach(el => {
    elements.push({
      type: 'checkbox',
      element: el,
      id: el.id,
      name: el.name,
      label: findLabelForElement(el)
    });
  });
  
  // Radio buttons
  document.querySelectorAll('input[type="radio"]').forEach(el => {
    elements.push({
      type: 'radio',
      element: el,
      id: el.id,
      name: el.name,
      value: el.value,
      label: findLabelForElement(el)
    });
  });
  
  // Modern UI frameworks often use custom dropdowns (div-based)
  document.querySelectorAll('div[role="combobox"], div[class*="select"], div[class*="dropdown"]').forEach(el => {
    elements.push({
      type: 'custom-select',
      element: el,
      id: el.id,
      className: el.className,
      text: el.textContent.trim(),
      label: findLabelForElement(el)
    });
  });
  
  return elements;
}

// Find the label for a form element
function findLabelForElement(element) {
  // Check for label with 'for' attribute
  if (element.id) {
    const label = document.querySelector(`label[for="${element.id}"]`);
    if (label) return label.textContent.trim();
  }
  
  // Check for parent label
  let parent = element.parentElement;
  while (parent) {
    if (parent.tagName === 'LABEL') {
      return parent.textContent.trim().replace(element.textContent.trim(), '').trim();
    }
    
    // Check for label-like elements nearby
    const labelLike = parent.querySelector('label, div[class*="label"], span[class*="label"]');
    if (labelLike && !labelLike.contains(element)) {
      return labelLike.textContent.trim();
    }
    
    parent = parent.parentElement;
    if (parent && parent.tagName === 'BODY') break;
  }
  
  // Check for aria-label
  if (element.getAttribute('aria-label')) {
    return element.getAttribute('aria-label');
  }
  
  // Check for placeholder as last resort
  if (element.placeholder) {
    return element.placeholder;
  }
  
  return '';
}

// Analyze the form using Gemini API
// Enhance the analyzeFormWithGemini function to generate responses for unfilled fields
async function analyzeFormWithGemini() {
  try {
    // Prepare form data for analysis with more detailed element information
    const formData = {
      url: window.location.href,
      title: document.title,
      elements: formElements.map(el => {
        // Create a more detailed representation of each form element
        const elementData = {
          type: el.type,
          id: el.id,
          name: el.name,
          label: el.label,
          placeholder: el.placeholder,
          options: el.options,
          className: el.element ? el.element.className : '',
          tagName: el.element ? el.element.tagName : '',
          ariaLabel: el.element ? el.element.getAttribute('aria-label') : '',
          // Include HTML structure for complex elements like dropdowns
          parentHTML: el.element && el.element.parentElement ? 
                     el.element.parentElement.outerHTML.substring(0, 500) : ''
        };
        
        // For select/dropdown elements, include more details about their structure
        if (el.type === 'select' || el.type === 'custom-select') {
          elementData.dropdownStructure = getDropdownStructure(el.element);
        }
        
        return elementData;
      })
    };
    
    // Enhanced prompt for Gemini with specific instructions for generating responses
    const prompt = `
      I need help filling out a job application form. Here's the detailed form structure:
      ${JSON.stringify(formData, null, 2)}
      
      I have the following personal information:
      ${JSON.stringify(personalInfo, null, 2)}
      
      Please analyze the form and tell me which personal information should go into which form field.
      
      IMPORTANT INSTRUCTIONS:
      1. For standard <select> elements, identify them by ID or name
      2. For custom dropdowns (div-based), look for elements with class names containing "select", "dropdown", or role="combobox"
      3. For each dropdown, specify both the dropdown element to click and the option to select
      4. For fields like "About yourself", "Tell us about yourself", "Why do you want to work here", or similar open-ended questions, please generate appropriate responses based on my skills and experience
      5. For salary expectation questions, generate a response based on market rates for my skills
      6. For LinkedIn profile, use: "${personalInfo.linkedin || ''}"
      7. For GitHub profile, use: "${personalInfo.github || ''}"
      8. For Portfolio website, use: "${personalInfo.portfolio || ''}"
      9. For any field not explicitly provided in my personal information, generate an appropriate response
      
      Return your response as a JSON object with the following structure:
      {
        "fields": [
          {
            "elementId": "the-id-or-name",
            "value": "the value to fill",
            "action": "fill|select|check|upload",
            "elementType": "input|select|custom-select|checkbox|radio|file",
            "dropdownDetails": {  // Only for dropdowns
              "containerSelector": "CSS selector for the dropdown container",
              "optionSelector": "CSS selector for the specific option to select"
            },
            "generated": true  // Add this flag for AI-generated responses
          }
        ],
        "generatedResponses": {
          "aboutYourself": "Generated response about myself based on my skills and experience",
          "whyThisCompany": "Generated response about why I want to work at this company",
          "salaryExpectations": "Generated salary expectation based on market rates"
        }
      }
    `;
    
    // Call Gemini API with updated model
    const response = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=${apiKey}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        contents: [{
          parts: [{
            text: prompt
          }]
        }],
        generationConfig: {
          temperature: 0.7,
          maxOutputTokens: 8192
        }
      })
    });
    
    if (!response.ok) {
      throw new Error(`Gemini API error: ${response.status} ${response.statusText}`);
    }
    
    const data = await response.json();
    
    // Extract and parse the JSON response from Gemini
    const textResponse = data.candidates[0].content.parts[0].text;
    const jsonMatch = textResponse.match(/```json\n([\s\S]*?)\n```/) || 
                      textResponse.match(/```\n([\s\S]*?)\n```/) || 
                      textResponse.match(/{[\s\S]*?}/);
                      
    if (!jsonMatch) {
      throw new Error('Could not parse Gemini response as JSON');
    }
    
    const jsonStr = jsonMatch[0].startsWith('{') ? jsonMatch[0] : jsonMatch[1];
    return JSON.parse(jsonStr);
    
  } catch (error) {
    console.error('Error analyzing form with Gemini:', error);
    throw new Error('Failed to analyze form: ' + error.message);
  }
}

// Helper function to get dropdown structure
function getDropdownStructure(element) {
  if (!element) return null;
  
  try {
    // For standard select elements
    if (element.tagName === 'SELECT') {
      return {
        type: 'standard',
        options: Array.from(element.options).map(opt => ({
          value: opt.value,
          text: opt.text,
          selected: opt.selected
        }))
      };
    }
    
    // For custom dropdowns, try to identify the structure
    const isReactSelect = element.className.includes('select__') || 
                          element.className.includes('react-select');
    const isMaterialUI = element.className.includes('MuiSelect') || 
                         element.className.includes('MuiInputBase');
    const isBootstrap = element.className.includes('dropdown-toggle') || 
                        element.className.includes('form-select');
    
    // Return information about the dropdown type
    return {
      type: 'custom',
      framework: isReactSelect ? 'react-select' : 
                 isMaterialUI ? 'material-ui' : 
                 isBootstrap ? 'bootstrap' : 'unknown',
      className: element.className,
      id: element.id,
      role: element.getAttribute('role') || 'none'
    };
  } catch (e) {
    console.warn('Error getting dropdown structure:', e);
    return null;
  }
}

// Enhanced function to select a dropdown option based on test.py approach
async function selectDropdownOption(element, value, dropdownDetails) {
  try {
    // Handle standard select elements
    if (element.tagName === 'SELECT') {
      element.scrollIntoView({ behavior: 'smooth', block: 'center' });
      await sleep(300);
      
      // Find the option with matching text
      const options = Array.from(element.options);
      const option = options.find(opt => 
        opt.text.toLowerCase().includes(value.toLowerCase()) || 
        opt.value.toLowerCase().includes(value.toLowerCase())
      );
      
      if (option) {
        element.value = option.value;
        element.dispatchEvent(new Event('change', { bubbles: true }));
      } else {
        console.warn(`Option "${value}" not found in select`);
      }
      return;
    }
    
    // For custom dropdowns, use a more robust approach similar to test.py
    console.log("Handling custom dropdown for:", element, "with value:", value);
    
    // Scroll element into view
    element.scrollIntoView({ behavior: 'smooth', block: 'center' });
    await sleep(500);
    
    // Find the dropdown control - similar to test.py's approach
    let dropdownControl = element;
    
    // If we have a div-based dropdown, look for the control element
    if (element.tagName === 'DIV') {
      // Try to find the control element within the dropdown container
      const controlElement = element.querySelector('div[class*="control"], div[role="button"], div[aria-haspopup="listbox"]');
      if (controlElement) {
        dropdownControl = controlElement;
      }
    }
    
    // Click to open the dropdown using ActionChains-like approach
    console.log("Clicking dropdown control:", dropdownControl);
    simulateMouseClick(dropdownControl);
    await sleep(1000); // Give time for dropdown to open
    
    // Try different approaches to find and click the option (similar to test.py)
    let optionFound = false;
    
    // First attempt: Look for elements with the exact text
    const exactOptions = document.querySelectorAll('div[class*="option"], li[role="option"], div[role="option"]');
    for (const opt of exactOptions) {
      if (opt.textContent.trim() === value) {
        console.log("Found exact match option:", opt);
        simulateMouseClick(opt);
        optionFound = true;
        break;
      }
    }
    
    // Second attempt: Look for elements containing the text
    if (!optionFound) {
      const containingOptions = document.querySelectorAll('div[class*="option"], li[role="option"], div[role="option"]');
      for (const opt of containingOptions) {
        if (opt.textContent.toLowerCase().includes(value.toLowerCase())) {
          console.log("Found containing match option:", opt);
          simulateMouseClick(opt);
          optionFound = true;
          break;
        }
      }
    }
    
    // Third attempt: Try to find by partial class and text content
    if (!optionFound) {
      const allPossibleOptions = document.querySelectorAll('div, li, span, a');
      for (const opt of allPossibleOptions) {
        // Check if this element is likely an option (visible, has text matching value)
        const style = window.getComputedStyle(opt);
        const isVisible = style.display !== 'none' && style.visibility !== 'hidden' && opt.offsetParent !== null;
        
        if (isVisible && opt.textContent.toLowerCase().includes(value.toLowerCase())) {
          console.log("Found fallback option:", opt);
          simulateMouseClick(opt);
          optionFound = true;
          break;
        }
      }
    }
    
    if (!optionFound) {
      console.warn(`Could not find option with text "${value}" in dropdown`);
    }
    
    await sleep(500); // Wait for selection to register
    
  } catch (error) {
    console.error("Error in selectDropdownOption:", error);
  }
}

// Helper function to simulate a mouse click (similar to ActionChains in Selenium)
function simulateMouseClick(element) {
  // First try the click() method
  try {
    element.click();
    return;
  } catch (e) {
    console.log("Standard click failed, trying MouseEvents");
  }
  
  // If that fails, try MouseEvents
  try {
    const evt = new MouseEvent('click', {
      bubbles: true,
      cancelable: true,
      view: window
    });
    element.dispatchEvent(evt);
  } catch (e) {
    console.error("MouseEvent click failed:", e);
  }
}

// Improved function to find elements by various identifiers, especially for social links
function findElementByIdentifiers(identifier) {
  console.log("Looking for element with identifier:", identifier);
  
  // Try by ID
  let element = document.getElementById(identifier);
  if (element) return element;
  
  // Try by name
  element = document.querySelector(`[name="${identifier}"]`);
  if (element) return element;
  
  // Try by placeholder
  element = document.querySelector(`[placeholder="${identifier}"]`);
  if (element) return element;
  
  // Try by aria-label
  element = document.querySelector(`[aria-label="${identifier}"]`);
  if (element) return element;
  
  // Enhanced social profile detection (LinkedIn, GitHub, Portfolio, etc.)
  if (identifier.toLowerCase().includes('linkedin') || 
      identifier.toLowerCase().includes('github') || 
      identifier.toLowerCase().includes('portfolio') || 
      identifier.toLowerCase().includes('website')) {
    
    // Get all input elements that might be profile fields
    const inputElements = document.querySelectorAll('input[type="text"], input[type="url"], input:not([type])');
    
    for (const input of inputElements) {
      // Check various attributes that might indicate this is the right field
      const inputId = (input.id || '').toLowerCase();
      const inputName = (input.name || '').toLowerCase();
      const inputPlaceholder = (input.placeholder || '').toLowerCase();
      const inputLabel = findLabelForElement(input).toLowerCase();
      const inputAriaLabel = (input.getAttribute('aria-label') || '').toLowerCase();
      
      // For LinkedIn
      if (identifier.toLowerCase().includes('linkedin') && 
          (inputId.includes('linkedin') || 
           inputName.includes('linkedin') || 
           inputPlaceholder.includes('linkedin') || 
           inputLabel.includes('linkedin') || 
           inputAriaLabel.includes('linkedin'))) {
        console.log("Found LinkedIn field:", input);
        return input;
      }
      
      // For GitHub
      if (identifier.toLowerCase().includes('github') && 
          (inputId.includes('github') || 
           inputName.includes('github') || 
           inputPlaceholder.includes('github') || 
           inputLabel.includes('github') || 
           inputAriaLabel.includes('github'))) {
        console.log("Found GitHub field:", input);
        return input;
      }
      
      // For Portfolio/Website
      if ((identifier.toLowerCase().includes('portfolio') || identifier.toLowerCase().includes('website')) && 
          (inputId.includes('portfolio') || inputId.includes('website') || 
           inputName.includes('portfolio') || inputName.includes('website') || 
           inputPlaceholder.includes('portfolio') || inputPlaceholder.includes('website') || 
           inputLabel.includes('portfolio') || inputLabel.includes('website') || 
           inputAriaLabel.includes('portfolio') || inputAriaLabel.includes('website'))) {
        console.log("Found Portfolio/Website field:", input);
        return input;
      }
    }
    
    // If we still haven't found it, try a more general approach for URL fields
    const allInputs = document.querySelectorAll('input');
    for (const input of allInputs) {
      const label = findLabelForElement(input).toLowerCase();
      if (label.includes('url') || label.includes('link') || label.includes('profile') || 
          input.type === 'url' || input.placeholder?.toLowerCase().includes('http')) {
        console.log("Found potential URL field:", input, "with label:", label);
        return input;
      }
    }
  }
  
  // Try to find by label text for common fields
  const allLabels = document.querySelectorAll('label');
  for (const label of allLabels) {
    const labelText = label.textContent.toLowerCase();
    if (identifier.toLowerCase().includes(labelText) || labelText.includes(identifier.toLowerCase())) {
      const forId = label.getAttribute('for');
      if (forId) {
        const linkedElement = document.getElementById(forId);
        if (linkedElement) {
          console.log("Found element by label text:", linkedElement);
          return linkedElement;
        }
      }
    }
  }
  
  return null;
}

// Update the fillFormBasedOnAnalysis function to handle social links better
async function fillFormBasedOnAnalysis(analysis) {
  if (!analysis || !analysis.fields || !Array.isArray(analysis.fields)) {
    throw new Error('Invalid analysis format');
  }
  
  // Store generated responses for potential reuse
  const generatedResponses = analysis.generatedResponses || {};
  console.log("Generated responses:", generatedResponses);
  
  // First pass: Handle all fields except dropdowns
  for (const field of analysis.fields) {
    try {
      // Skip dropdowns in first pass
      if (field.action === 'select' || field.elementType === 'select' || field.elementType === 'custom-select') {
        continue;
      }
      
      updateOverlay(`Filling field: ${field.elementId || 'unnamed field'}`);
      
      // Find the element by ID, name, or other attributes
      let element = findElementByIdentifiers(field.elementId);
      
      if (!element) {
        console.warn(`Element not found: ${field.elementId}`);
        continue;
      }
      
      // Get the value to fill, using generated responses if needed
      let valueToFill = field.value;
      
      // Special handling for social profile links
      if (field.elementId.toLowerCase().includes('linkedin')) {
        valueToFill = personalInfo.linkedin || personalInfo.social_profiles?.linkedin || valueToFill;
      } else if (field.elementId.toLowerCase().includes('github')) {
        valueToFill = personalInfo.github || personalInfo.social_profiles?.github || valueToFill;
      } else if (field.elementId.toLowerCase().includes('portfolio') || field.elementId.toLowerCase().includes('website')) {
        valueToFill = personalInfo.portfolio || personalInfo.social_profiles?.portfolio || valueToFill;
      }
      
      // If this is a textarea and might need a generated response
      if (element.tagName === 'TEXTAREA' && (!valueToFill || valueToFill.trim() === '')) {
        // Try to determine if this is an "about yourself" field
        const labelText = findLabelForElement(element).toLowerCase();
        if (labelText.includes('about') || labelText.includes('introduce') || labelText.includes('tell us')) {
          valueToFill = generatedResponses.aboutYourself || "I am a dedicated professional with experience in...";
        } else if (labelText.includes('why') && (labelText.includes('company') || labelText.includes('position'))) {
          valueToFill = generatedResponses.whyThisCompany || "I'm interested in this position because...";
        } else if (labelText.includes('salary') || labelText.includes('compensation')) {
          valueToFill = generatedResponses.salaryExpectations || "My salary expectations are competitive and negotiable based on the total compensation package.";
        }
      }
      
      // Handle different element types
      switch (field.action) {
        case 'fill':
          await fillTextField(element, valueToFill);
          break;
          
        case 'check':
          if (element.checked !== true) {
            element.click();
          }
          break;
          
        case 'upload':
          // File upload would require additional handling
          console.log('File upload not implemented yet');
          break;
          
        default:
          console.warn(`Unknown action: ${field.action}`);
      }
      
      await sleep(500); // Add a small delay between fields
      
    } catch (error) {
      console.error(`Error filling field ${field.elementId}:`, error);
    }
  }
  
  // Second pass: Handle all dropdowns
  for (const field of analysis.fields) {
    try {
      if (field.action !== 'select' && field.elementType !== 'select' && field.elementType !== 'custom-select') {
        continue;
      }
      
      updateOverlay(`Filling dropdown: ${field.elementId || 'unnamed dropdown'}`);
      
      // Find the element by ID, name, or other attributes
      let element = findElementByIdentifiers(field.elementId);
      
      if (!element) {
        console.warn(`Dropdown element not found: ${field.elementId}`);
        continue;
      }
      
      // Get the value to select
      let valueToSelect = field.value;
      
      // Handle dropdown selection with the enhanced function
      await selectDropdownOption(element, valueToSelect, field.dropdownDetails);
      
      await sleep(1000); // Add a longer delay after dropdown selection
      
    } catch (error) {
      console.error(`Error filling dropdown ${field.elementId}:`, error);
    }
  }
}

// Helper function to fill a text field with improved handling
async function fillTextField(element, value) {
  if (!value) {
    console.warn("Empty value provided for field:", element);
    return;
  }
  
  console.log("Filling text field:", element, "with value:", value);
  
  // Scroll element into view
  element.scrollIntoView({ behavior: 'smooth', block: 'center' });
  await sleep(300);
  
  // Focus the element
  element.focus();
  await sleep(100);
  
  // Clear existing value - try multiple approaches
  element.value = '';
  element.dispatchEvent(new Event('input', { bubbles: true }));
  
  // For stubborn fields, try select-all + delete
  try {
    element.select();
    document.execCommand('delete');
  } catch (e) {
    console.log("Select-all + delete failed, continuing with direct value setting");
  }
  
  await sleep(100);
  
  // Set the value directly first (faster)
  element.value = value;
  element.dispatchEvent(new Event('input', { bubbles: true }));
  
  // Trigger change event
  element.dispatchEvent(new Event('change', { bubbles: true }));
  
  // Blur the element
  element.blur();
  await sleep(200);
}

// Helper function to check/uncheck a checkbox
async function checkCheckbox(element, check = true) {
  element.scrollIntoView({ behavior: 'smooth', block: 'center' });
  await sleep(300);
  
  if ((element.checked && !check) || (!element.checked && check)) {
    element.click();
    await sleep(200);
  }
}

// Helper function to highlight an element for user attention
function highlightElement(element, message) {
  element.scrollIntoView({ behavior: 'smooth', block: 'center' });
  
  // Create highlight overlay
  const overlay = document.createElement('div');
  overlay.style.position = 'absolute';
  overlay.style.zIndex = '10000';
  overlay.style.backgroundColor = 'rgba(255, 215, 0, 0.3)';
  overlay.style.border = '2px solid gold';
  overlay.style.borderRadius = '4px';
  overlay.style.padding = '10px';
  overlay.style.pointerEvents = 'none';
  
  // Add message
  const messageEl = document.createElement('div');
  messageEl.textContent = message;
  messageEl.style.backgroundColor = 'rgba(0, 0, 0, 0.7)';
  messageEl.style.color = 'white';
  messageEl.style.padding = '5px 10px';
  messageEl.style.borderRadius = '4px';
  messageEl.style.fontSize = '14px';
  messageEl.style.fontWeight = 'bold';
  messageEl.style.marginBottom = '5px';
  overlay.appendChild(messageEl);
  
  // Position the overlay
  const rect = element.getBoundingClientRect();
  overlay.style.top = `${window.scrollY + rect.top - 10}px`;
  overlay.style.left = `${window.scrollX + rect.left - 10}px`;
  overlay.style.width = `${rect.width + 20}px`;
  overlay.style.height = `${rect.height + 20}px`;
  
  // Add to document
  document.body.appendChild(overlay);
  
  // Remove after 5 seconds
  setTimeout(() => {
    if (document.body.contains(overlay)) {
      document.body.removeChild(overlay);
    }
  }, 5000);
}

// Helper function to show overlay during processing
function showOverlay(message) {
  // Remove any existing overlay
  const existingOverlay = document.getElementById('job-filler-overlay');
  if (existingOverlay) {
    document.body.removeChild(existingOverlay);
  }
  
  // Create new overlay
  const overlay = document.createElement('div');
  overlay.id = 'job-filler-overlay';
  overlay.style.position = 'fixed';
  overlay.style.top = '20px';
  overlay.style.right = '20px';
  overlay.style.backgroundColor = 'rgba(0, 0, 0, 0.8)';
  overlay.style.color = 'white';
  overlay.style.padding = '15px 20px';
  overlay.style.borderRadius = '8px';
  overlay.style.zIndex = '10000';
  overlay.style.boxShadow = '0 4px 8px rgba(0, 0, 0, 0.2)';
  overlay.style.fontSize = '14px';
  overlay.style.fontFamily = 'Arial, sans-serif';
  overlay.style.transition = 'opacity 0.3s';
  
  // Add message
  const messageEl = document.createElement('div');
  messageEl.id = 'job-filler-message';
  messageEl.textContent = message;
  overlay.appendChild(messageEl);
  
  // Add progress indicator
  const progress = document.createElement('div');
  progress.id = 'job-filler-progress';
  progress.style.width = '100%';
  progress.style.height = '4px';
  progress.style.backgroundColor = '#333';
  progress.style.marginTop = '10px';
  progress.style.borderRadius = '2px';
  progress.style.overflow = 'hidden';
  overlay.appendChild(progress);
  
  const progressBar = document.createElement('div');
  progressBar.id = 'job-filler-progress-bar';
  progressBar.style.width = '0%';
  progressBar.style.height = '100%';
  progressBar.style.backgroundColor = '#4CAF50';
  progressBar.style.transition = 'width 0.3s';
  progress.appendChild(progressBar);
  
  // Add to document
  document.body.appendChild(overlay);
  
  // Animate progress bar
  let width = 0;
  const interval = setInterval(() => {
    if (width >= 90) {
      clearInterval(interval);
    } else {
      width += 1;
      progressBar.style.width = `${width}%`;
    }
  }, 100);
}

// Helper function to update overlay message
function updateOverlay(message, complete = false, error = false) {
  const messageEl = document.getElementById('job-filler-message');
  const progressBar = document.getElementById('job-filler-progress-bar');
  
  if (messageEl) {
    messageEl.textContent = message;
  }
  
  if (progressBar) {
    if (complete) {
      progressBar.style.width = '100%';
      progressBar.style.backgroundColor = error ? '#F44336' : '#4CAF50';
      
      // Remove overlay after a delay if complete
      setTimeout(() => {
        const overlay = document.getElementById('job-filler-overlay');
        if (overlay) {
          overlay.style.opacity = '0';
          setTimeout(() => {
            if (document.body.contains(overlay)) {
              document.body.removeChild(overlay);
            }
          }, 300);
        }
      }, error ? 5000 : 3000);
    } else {
      // Update progress bar to show activity
      const currentWidth = parseInt(progressBar.style.width, 10);
      progressBar.style.width = `${Math.min(currentWidth + 5, 90)}%`;
    }
  }
}

// Helper function for sleep/delay
function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

// Add jQuery-like :contains selector functionality
document.querySelectorAll = (function(originalQuerySelectorAll) {
  return function(selector) {
    try {
      // Check if selector contains the :contains pseudo-selector
      if (selector.includes(':contains')) {
        // Extract the text to search for
        const match = selector.match(/:contains\("([^"]*)"\)/);
        if (match) {
          const searchText = match[1];
          // Remove the :contains part and get elements
          const newSelector = selector.replace(/:contains\("[^"]*"\)/, '');
          const elements = originalQuerySelectorAll.call(this, newSelector);
          // Filter elements that contain the text
          return Array.from(elements).filter(el => 
            el.textContent.toLowerCase().includes(searchText.toLowerCase())
          );
        }
      }
      // Default behavior
      return originalQuerySelectorAll.call(this, selector);
    } catch (e) {
      console.warn('Error with selector:', selector, e);
      return originalQuerySelectorAll.call(this, selector.replace(/:contains\("[^"]*"\)/, ''));
    }
  };
})(document.querySelectorAll);

// Initialize the extension when the page is fully loaded
window.addEventListener('load', function() {
  console.log('Job Application Filler content script loaded');
  
  // Add a floating button to trigger form filling
  addFloatingButton();
});

// Add a floating button to the page
function addFloatingButton() {
  const button = document.createElement('button');
  button.textContent = '📝 Fill Form';
  button.style.position = 'fixed';
  button.style.bottom = '20px';
  button.style.right = '20px';
  button.style.zIndex = '10000';
  button.style.backgroundColor = '#4285F4';
  button.style.color = 'white';
  button.style.border = 'none';
  button.style.borderRadius = '50px';
  button.style.padding = '10px 20px';
  button.style.fontSize = '14px';
  button.style.fontWeight = 'bold';
  button.style.boxShadow = '0 2px 10px rgba(0, 0, 0, 0.2)';
  button.style.cursor = 'pointer';
  button.style.display = 'flex';
  button.style.alignItems = 'center';
  button.style.justifyContent = 'center';
  button.style.transition = 'all 0.3s';
  
  // Hover effect
  button.addEventListener('mouseover', function() {
    button.style.backgroundColor = '#3367D6';
    button.style.transform = 'scale(1.05)';
  });
  
  button.addEventListener('mouseout', function() {
    button.style.backgroundColor = '#4285F4';
    button.style.transform = 'scale(1)';
  });
  
  // Click event
  button.addEventListener('click', function() {
    if (isProcessing) {
      alert('Already processing a form. Please wait...');
      return;
    }
    
    // Handle the form filling directly first, then we'll check local storage
    chrome.storage.sync.get(null, function(data) {
      if (chrome.runtime.lastError) {
        console.error('Storage error:', chrome.runtime.lastError);
        alert('Error accessing extension storage. Please refresh the page.');
        return;
      }
      
      personalInfo = data;
      apiKey = data.apiKey;
      
      if (!apiKey) {
        alert('Please set your API key in the extension options first.');
        return;
      }
      
      // Start form filling process directly
      analyzeAndFillForm()
        .catch(error => {
          console.error('Error filling form:', error);
          alert('Error filling form: ' + error.message);
        });
    });
  });
  
  document.body.appendChild(button);
}