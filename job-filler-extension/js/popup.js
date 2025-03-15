document.addEventListener('DOMContentLoaded', function() {
  const fillFormButton = document.getElementById('fillForm');
  const statusDiv = document.getElementById('status');
  
  // First check if content script is loaded
  chrome.runtime.sendMessage({action: "checkContentScript"}, function(response) {
    if (chrome.runtime.lastError || !response || response.status === 'error') {
      statusDiv.textContent = 'Error: Content script not loaded. Please refresh the page.';
      statusDiv.style.display = 'block';
      fillFormButton.disabled = true;
      return;
    }
    
    // Enable the button if content script is loaded
    fillFormButton.disabled = false;
  });
  
  fillFormButton.addEventListener('click', function() {
    statusDiv.textContent = 'Filling form...';
    statusDiv.style.display = 'block';
    
    chrome.runtime.sendMessage({action: "fillForm"}, function(response) {
      if (chrome.runtime.lastError) {
        statusDiv.textContent = 'Error: ' + chrome.runtime.lastError.message;
        return;
      }
      
      if (response && response.status === 'success') {
        statusDiv.textContent = 'Form filling started!';
      } else if (response && response.status === 'error') {
        statusDiv.textContent = 'Error: ' + response.message;
      } else {
        statusDiv.textContent = 'Unknown error occurred.';
      }
    });
  });
  
  // Add options page link
  const optionsLink = document.getElementById('optionsLink');
  if (optionsLink) {
    optionsLink.addEventListener('click', function() {
      chrome.runtime.openOptionsPage();
    });
  }
});