from langchain_openai import ChatOpenAI
from browser_use import Agent
from dotenv import load_dotenv
load_dotenv()

import asyncio

llm = gemini_pro = ChatOpenAI(temperature=0, model_name="gemini-pro")
async def main():
    agent = Agent(
        task="""
        # Task configuration for job application automation
        # Target job board URL and settings
        fill out the job application on this website : https://job-boards.greenhouse.io/affirm/jobs/6354992003
        test_mode: true
        pause_for_review: true

        # Job positions to search for
        positions:
          - "Software Engineer"
          - "Python Developer" 
          - "Full Stack Developer"

        # Target location
        locations:
          - "Mumbai, India"

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
          address: "32,threetwo,road"
          zip_code: "429112"
          phone_prefix: "+91"

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

        # Experience level indicators
        experience_level:
          entry: false
          mid: true
          senior: false

        # Path to resume file
        resume_path: "resume.pdf"
        """,
        llm=llm,
    )
    result = await agent.run()
    print(result)

asyncio.run(main())