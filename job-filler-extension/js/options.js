// Save options to chrome.storage
function saveOptions() {
  const apiKey = document.getElementById('apiKey').value;
  const firstName = document.getElementById('firstName').value;
  const lastName = document.getElementById('lastName').value;
  const email = document.getElementById('email').value;
  const phone = document.getElementById('phone').value;
  const address = document.getElementById('address').value;
  const city = document.getElementById('city').value;
  const state = document.getElementById('state').value;
  const zipCode = document.getElementById('zipCode').value;
  const education = document.getElementById('education').value;
  const experience = document.getElementById('experience').value;
  const skills = document.getElementById('skills').value;
  const preferredName = document.getElementById('preferredName').value;
  const pronouns = document.getElementById('pronouns').value;
  const currentCompany = document.getElementById('currentCompany').value;
  const gender = document.getElementById('gender').value;
  const hispanicEthnicity = document.getElementById('hispanicEthnicity').value;
  const veteranStatus = document.getElementById('veteranStatus').value;
  const disabilityStatus = document.getElementById('disabilityStatus').value;
  const workAuthorization = document.getElementById('workAuthorization').value;
  const visaSponsorship = document.getElementById('visaSponsorship').value;
  const relocate = document.getElementById('relocate').value;
  
  // Make sure we're properly getting the social media links
  const linkedin = document.getElementById('linkedin').value;
  const github = document.getElementById('github').value;
  const portfolio = document.getElementById('portfolio').value;
  const salaryExpectations = document.getElementById('salaryExpectations').value;
  const availability = document.getElementById('availability').value;
  const references = document.getElementById('references').value;
  const coverLetter = document.getElementById('coverLetter').value;
  
  // Add debugging logs for social links
  console.log("Saving LinkedIn:", linkedin);
  console.log("Saving GitHub:", github);
  console.log("Saving Portfolio:", portfolio);
  console.log("Saving Salary Expectations:", salaryExpectations);
  console.log("Saving Availability:", availability);
  console.log("Saving References:", references);
  console.log("Saving Cover Letter:", coverLetter);
  
  chrome.storage.sync.set({
    apiKey: apiKey,
    firstName: firstName,
    lastName: lastName,
    email: email,
    phone: phone,
    address: address,
    city: city,
    state: state,
    zipCode: zipCode,
    education: education,
    experience: experience,
    skills: skills,
    preferredName: preferredName,
    pronouns: pronouns,
    currentCompany: currentCompany,
    gender: gender,
    hispanicEthnicity: hispanicEthnicity,
    veteranStatus: veteranStatus,
    disabilityStatus: disabilityStatus,
    workAuthorization: workAuthorization,
    visaSponsorship: visaSponsorship,
    relocate: relocate,
    // Add the missing professional information fields
    linkedin: linkedin,
    github: github,
    portfolio: portfolio,
    salaryExpectations: salaryExpectations,
    availability: availability,
    references: references,
    coverLetter: coverLetter,
    // Add these to ensure compatibility with existing code
    dropdowns: {
      pronouns: pronouns,
      gender: gender,
      hispanicEthnicity: hispanicEthnicity,
      veteranStatus: veteranStatus,
      disabilityStatus: disabilityStatus,
      visaSponsorship: visaSponsorship,
      workAuthorization: workAuthorization
    },
    specificAnswers: {
      workAuthorization: workAuthorization,
      visaSponsorship: visaSponsorship,
      relocate: relocate
    },
    // Add social_profiles object for easier access in content.js
    social_profiles: {
      linkedin: linkedin,
      github: github,
      portfolio: portfolio
    }
  }, function() {
    // Update status to let user know options were saved
    const status = document.getElementById('status');
    status.style.display = 'block';
    status.textContent = 'Options saved successfully!';
    
    // Log to verify save was attempted
    console.log("Save callback executed");
    
    setTimeout(function() {
      status.style.display = 'none';
    }, 3000);
  });
}

// Restore options from chrome.storage
function restoreOptions() {
  // Log to verify function is called
  console.log("Restoring options...");
  
  // In the restoreOptions function, add default values for LinkedIn and GitHub
  chrome.storage.sync.get({
    apiKey: '',
    firstName: '',
    lastName: '',
    email: '',
    phone: '',
    address: '',
    city: '',
    state: '',
    zipCode: '',
    education: '',
    experience: '',
    skills: '',
    linkedin: '',  // Make sure this is included
    github: '',    // Make sure this is included
    portfolio: '', // Make sure this is included
    preferredName: '',
    pronouns: 'He/Him',
    currentCompany: '',
    gender: 'Male',
    hispanicEthnicity: 'No',
    veteranStatus: 'I am not a protected veteran',
    disabilityStatus: 'No, I don\'t have a disability',
    visaSponsorship: 'No',
    workAuthorization: 'Yes',
    relocate: 'No',
    salaryExpectations: '',
    availability: 'Immediately',
    references: '',
    coverLetter: '',
    // Add social_profiles with defaults
    social_profiles: {
      linkedin: '',
      github: '',
      portfolio: ''
    }
  }, function(items) {
    // Log retrieved API key
    console.log("Retrieved API Key:", items.apiKey);
    console.log("Retrieved LinkedIn:", items.linkedin);
    console.log("Retrieved GitHub:", items.github);
    console.log("Retrieved Portfolio:", items.portfolio);
    
    document.getElementById('apiKey').value = items.apiKey;
    document.getElementById('firstName').value = items.firstName;
    document.getElementById('lastName').value = items.lastName;
    document.getElementById('email').value = items.email;
    document.getElementById('phone').value = items.phone;
    document.getElementById('address').value = items.address;
    document.getElementById('city').value = items.city;
    document.getElementById('state').value = items.state;
    document.getElementById('zipCode').value = items.zipCode;
    document.getElementById('education').value = items.education;
    document.getElementById('experience').value = items.experience;
    document.getElementById('skills').value = items.skills;
    document.getElementById('preferredName').value = items.preferredName;
    document.getElementById('pronouns').value = items.pronouns;
    document.getElementById('currentCompany').value = items.currentCompany;
    document.getElementById('gender').value = items.gender;
    document.getElementById('hispanicEthnicity').value = items.hispanicEthnicity;
    document.getElementById('veteranStatus').value = items.veteranStatus;
    document.getElementById('disabilityStatus').value = items.disabilityStatus;
    document.getElementById('workAuthorization').value = items.workAuthorization;
    document.getElementById('visaSponsorship').value = items.visaSponsorship;
    document.getElementById('relocate').value = items.relocate;
    
    // Make sure these are properly set with fallbacks
    document.getElementById('linkedin').value = items.linkedin || items.social_profiles?.linkedin || '';
    document.getElementById('github').value = items.github || items.social_profiles?.github || '';
    document.getElementById('portfolio').value = items.portfolio || items.social_profiles?.portfolio || '';
    document.getElementById('salaryExpectations').value = items.salaryExpectations || '';
    document.getElementById('availability').value = items.availability || 'Immediately';
    document.getElementById('references').value = items.references || '';
    document.getElementById('coverLetter').value = items.coverLetter || '';
  });
}

// Initialize the page
document.addEventListener('DOMContentLoaded', function() {
  // Log when page loads
  console.log("Options page loaded");
  restoreOptions();
  
  // Add event listener to save button
  document.getElementById('save').addEventListener('click', saveOptions);
});