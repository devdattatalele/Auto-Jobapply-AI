// Make sure the listener is properly registered
// Background script to handle communication between popup and content scripts
chrome.runtime.onMessage.addListener(function(request, sender, sendResponse) {
  console.log("Background received message:", request);
  
  if (request.action === "fillForm") {
    // Forward the message to the active tab
    chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
      if (!tabs || !tabs[0] || !tabs[0].id) {
        sendResponse({status: 'error', message: 'Cannot access current tab'});
        return;
      }
      
      chrome.tabs.sendMessage(tabs[0].id, request, function(response) {
        // Forward the response back to the popup
        sendResponse(response);
      });
    });
    
    // Return true to indicate we'll respond asynchronously
    return true;
  }
  
  if (request.action === "checkContentScript") {
    // Check if content script is loaded in the active tab
    chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
      if (!tabs || !tabs[0] || !tabs[0].id) {
        sendResponse({status: 'error', message: 'Cannot access current tab'});
        return;
      }
      
      chrome.tabs.sendMessage(tabs[0].id, {action: "ping"}, function(response) {
        if (chrome.runtime.lastError) {
          sendResponse({status: 'error', message: 'Content script not loaded'});
        } else {
          sendResponse({status: 'success', message: 'Content script loaded'});
        }
      });
    });
    
    // Return true to indicate we'll respond asynchronously
    return true;
  }
});

// Log when the background script loads
console.log("Background script loaded");

// Handle installation/update
chrome.runtime.onInstalled.addListener(function(details) {
  console.log('Extension installed/updated:', details.reason);
});