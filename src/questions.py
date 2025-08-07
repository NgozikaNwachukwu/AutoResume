import re

def contact_info():
    print(" Let's start with your contact information")
    contact = {} # We are creating the contact dictionary

    def not_empty(prompt):
        while True:
            value = input(prompt).strip()
            if value:
                return value
            print("This field cannot be empty.")

    def valid_email():
        while True:
            email = input("Email address: ").strip()
            if re.match(r"[^@\s]+@[^@\s]+\.[a-zA-Z0-9]+$", email):
                return email
            print("Invalid email format. Try again.")

    def valid_url(prompt):
        while True:
            url = input(prompt).strip()
            if url == "" or re.match(r"^(https?://)?[\w.-]+(\.[a-z]{2,})+/?$", url):
                return url
            print("Invalid URL. Try again.")

    
    contact["full_name"] = input("Full name: ")
    contact["email"] = input("Email address: ")
    contact["phone"] = input("Phone number: ")
    contact["Location"] = input("Location (e.g Toronto, ON): ")
    # we have now created the key -> value pairs for out contact dictionary

    # asking the user if they have linkedin
    has_linkedin = input("Do you have a Linkedin page? (yes/no): ").lower()
    if has_linkedin == "yes":
        contact["linkedin"] = input("LinkedIn URL: ")
    
    # Asking the user if they have a github url
    has_github = input("Do you have a github page? (yes/no): ").lower()
    if has_github == "yes":
        contact["github"] = input("Github profile URL: ")

    #now we are going to ask the user if they have a portfolio
    has_portfolio = input("Do you have a portfolio? (yes/no): ").lower()
    if has_portfolio == "yes": 
        contact["portfolio"] = input("Portfolio URL: ")
   
    return contact

    
    #educational background
def education_info():
    print("\n Let's enter your education history:")
    education_list = []

    def not_empty(prompt):
        while True:
            value = input(prompt).strip()
            if value:
                return value
            print("This field cannot be empty.")

    while True:
        school = not_empty("School name: ")
        degree = not_empty("Degree or major: ")
        start = not_empty("Start Date (e.g. Jan 2024): ")
        end = not_empty("End Date (or 'Present'): ")
        location = not_empty("School location: ")

        edu_entry = {
            "school": school,
            "degree": degree,
            "date": f"{start} - {end}",
            "location": location
        }

        # Optional GPA
        has_gpa = input("Would you like to include your GPA? (yes/no): ").strip().lower()
        if has_gpa == "yes":
            edu_entry["gpa"] = input("GPA: ").strip()

        education_list.append(edu_entry)

        # Ask if they want to add another
        add_another = input("\nWould you like to add another education entry? (yes/no): ").strip().lower()
        if add_another != "yes":
            break

    return education_list

def experience_info():
    print("\nLet's enter your past experiences.")
    experiences = []

    def not_empty(prompt):
        while True:
            value = input(prompt).strip()
            if value:
                return value
            print("This field cannot be empty.")


    while True:
        title = input("Job Title: ").strip()
        company = input("Company Name: ").strip()
        location = input("Location(e.g Toronto, ON): ").strip()

        # Start and end date with option for "Present"
        start_date = input("Start Date (e.g. Jan 2024): ").strip()
        end_date = input("End Date (or 'Present'): ").strip()

        summary = input("Briefly describe your responsibilities/duties: ").strip()

        experiences.append({
            "title": title,
            "company": company,
            "location": location,
            "date": f"{start_date} - {end_date}",
            "summary": summary
        })

        another = input("Would you like to add another experience? (yes/no): ").lower()
        if another != "yes":
            break

    return experiences


def project_info():
    print("\nLet's enter your projects.")
    projects = []

    def not_empty(prompt):
        while True:
            value = input(prompt).strip()
            if value:
                return value
            print("This field cannot be empty.")


    while True:
        title = input("Project Title: ").strip()
        tools = input("Tools & Technologies used: ").strip()
        start_date = input("Start Date (e.g. Feb 2025): ").strip()
        end_date = input("End Date (or 'Present'): ").strip()
        summary = input("What did you do in the project?: ").strip()

        projects.append({
            "title": title,
            "tools": tools,
            "date": f"{start_date} - {end_date}",
            "summary": summary
        })

        another = input("Would you like to add another project? (yes/no): ").lower()
        if another != "yes":
            break

    return projects




def skill_info():
    print("\n Let's add your skills!")
    skill_categories = {}  # Dictionary to hold categories and skills

    def not_empty(prompt):
        while True:
            value = input(prompt).strip()
            if value:
                return value
            print("This field cannot be empty.")

    while True:
        category = input("\nEnter skill category (e.g., Languages, Frameworks): ").strip()
        if not category:
            print("Category name cannot be empty.")
            continue

        skills = []
        print(f"Enter skills for {category} tip, separate them by commas! eg: Python, Java, etc.(type 'done' when finished):")
        while True:
            skill = input(f"- {category}: ").strip()
            if skill.lower() == "done":
                break
            if skill:
                skills.append(skill.capitalize())

        skill_categories[category] = skills

        add_more = input("\nWould you like to add another skill category? (yes/no): ").strip().lower()
        if add_more != "yes":
            break

    return skill_categories

#Exta curricular
def extra_curriculars():
    extras = []

    def not_empty(prompt):
        while True:
            value = input(prompt).strip()
            if value:
                return value
            print("This field cannot be empty.")

    choice = input("\n Would you like to add an extracurricular activity? (yes/no): ").strip().lower()
    if choice != "yes":
        return []

    
    while True:
        print("\nEnter extracurricular activity details (or type 'done' as title to finish)")
        title = input("Activity Title: ").strip()
        if title.lower() == "done":
            break
        if not title:
            print("Title cannot be empty.")
            continue

        start_date = input("Start Date (e.g. Jan 2024): ").strip()
        end_date = input("End Date (or 'Present'): ").strip() # i added or present
        description = input("Short description of the activity: ").strip()

        extras.append({
            "title": title,
            "date": f"{start_date} - {end_date}",
            "description": description
        })

        another = input("\nWould you like to add another extracurricular activity? (yes/no): ").strip().lower()
        if another != "yes":
            break

    return extras



if __name__ == "__main__":
    contact = contact_info()
    education = education_info()
    experience = experience_info()
    projects = project_info()
    skills = skill_info()
    extracurriculars = extra_curriculars()

#there is no point of these print statements lol, its just for testing. we will remove it dw.
    print("\n collected info:")
    print("\nContact Info:", contact)
    print("\nEducation:", education)
    print("\nExperience:", experience)
    print("\nProjects:", projects)
    print("\nSkills:", skills)
    print("\nExtracurriculars:", extracurriculars)
 
