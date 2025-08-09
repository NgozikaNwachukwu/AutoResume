import re

# ---------- Helper Functions ----------
def not_empty(prompt):
    while True:
        value = input(prompt).strip()
        if value:
            return value
        print("This field cannot be empty.")

def valid_email():
    while True:
        email = input("Email address(e.g allydee2@gmail.com): ").strip()
        if re.match(r"[^@\s]+@[^@\s]+\.[a-zA-Z0-9]+$", email):
            return email
        print("Invalid email format. Try again.")

def valid_phone():
    while True:
        phone = input("Phone number(e.g +16473807394): ").strip()
        if re.match(r"^\+?\d+$", phone):
            return phone
        print("Invalid phone number. Only digits allowed (optionally starting with '+').")

def valid_url(prompt):
    while True:
        url = input(prompt).strip()
        if url == "" or re.match(r"^https?://[^\s]+$", url):
            return url
        print("Invalid URL. Try again.")

def yes_no(prompt):
    while True:
        response = input(prompt).strip().lower()
        if response in ["yes", "no"]:
            return response
        print("Please answer with 'yes' or 'no'.")

# ---------- Section Functions ----------
def contact_info():
    print("Let's start with your contact information")
    contact = {}
    contact["full_name"] = not_empty("Full name: ")
    contact["email"] = valid_email()
    contact["phone"] = valid_phone()
    contact["location"] = not_empty("Location (e.g Toronto, ON): ")

    if yes_no("Do you have a Linkedin page? (yes/no): ") == "yes":
        contact["linkedin"] = valid_url("LinkedIn URL: ")

    if yes_no("Do you have a github page? (yes/no): ") == "yes":
        contact["github"] = valid_url("Github profile URL: ")

    if yes_no("Do you have a portfolio? (yes/no): ") == "yes":
        contact["portfolio"] = valid_url("Portfolio URL: ")

    return contact

def education_info():
    print("\nLet's enter your education history:")
    education = []
    while True:
        school = not_empty("School name: ")
        degree = not_empty("Degree or major(e.g Software Engineering): ")
        start_date = not_empty("Start Date (e.g. Jan 2024): ")
        end_date = not_empty("End Date (or 'Present'): ")
        location = not_empty("School location(e.g Oshawa, ON): ")
        date_range = f"{start_date} - {end_date}"
        entry = {"school": school, "degree": degree, "date": date_range, "location": location}

        if yes_no("Would you like to include your GPA? (yes/no): ") == "yes":
            entry["GPA"] = not_empty("Enter your GPA (e.g 3.7): ")

        education.append(entry)
        if yes_no("Would you like to add another education entry? (yes/no): ") == "no":
            break
    return education

def experience_info():
    print("\nLet's enter your past experiences.")
    experiences = []
    while True:
        title = not_empty("Job Title: ")
        company = not_empty("Company Name: ")
        location = not_empty("Location(e.g Toronto, ON): ")
        start = not_empty("Start Date (e.g. Jan 2024): ")
        end = not_empty("End Date (or 'Present'): ")
        summary = not_empty("Briefly describe your responsibilities/duties: ")

        experiences.append({
            "title": title,
            "company": company,
            "location": location,
            "dates": f"{start} - {end}",
            "summary": summary
        })
        if yes_no("Would you like to add another experience? (yes/no): ") == "no":
            break
    return experiences

def project_info():
    projects = []
    if yes_no("Would you like to add any projects? (yes/no): ") == "yes":
        while True:
            title = not_empty("Project Title: ")
            tools = not_empty("Tools & Technologies used(e.g Python, Java, etc): ")
            start = not_empty("Start Date (e.g. Feb 2025): ")
            end = not_empty("End Date (or 'Present'): ")
            summary = not_empty("What did you do in the project?(describe what was done): ")

            projects.append({
                "title": title,
                "tools": tools,
                "dates": f"{start} - {end}",
                "summary": summary
            })
            if yes_no("Would you like to add another project? (yes/no): ") == "no":
                break
    return projects

def skill_info():
    print("\nLet's add your skills!\n")
    skills = {}
    while True:
        category = not_empty("Enter skill category (e.g., Languages, Frameworks): ")
        skills[category] = []
        print(f"Enter skills for {category} tip, separate them by commas! eg: Python, Java, etc.(type 'done' when finished):")
        while True:
            skill = input(f"- {category}: ").strip()
            if skill.lower() == "done":
                if not skills[category]:
                    print("You must enter at least one skill before typing 'done'.")
                    continue
                break
            elif skill:
                skills[category].append(skill)
            else:
                print("Skill cannot be empty.")
        if yes_no("Would you like to add another skill category? (yes/no): ") == "no":
            break
    return skills

def extra_curriculars():
    extracurriculars = []
    if yes_no("\nWould you like to add an extracurricular activity? (yes/no): ") == "yes":
        while True:
            title = not_empty("Enter the title of the activity: ")
            start = not_empty("Start Date (e.g. Jan 2023): ")
            end = not_empty("End Date (or 'Present'): ")
            description = not_empty("Briefly describe the activity: ")

            extracurriculars.append({
                "title": title,
                "dates": f"{start} - {end}",
                "summary": description
            })

            if yes_no("Would you like to add another extracurricular activity? (yes/no): ") == "no":
                break
    return extracurriculars

# ---------- New Bundler Function ----------
def collect_all_input():
    return {
        "contact": contact_info(),
        "education": education_info(),
        "experience": experience_info(),
        "projects": project_info(),
        "skills": skill_info(),
        "extracurriculars": extra_curriculars()
    }

# ---------- Main Runner ----------
if __name__ == "__main__":
    data = collect_all_input()

    from src.builder import build_resume
    structured = build_resume(data)
    print("\nStructured resume data:\n", structured)

    from src.pdf_generator import build_pdf
    pdf_path = build_pdf(structured, filename="AutoResume.pdf")
    print(f"\nPDF created: {pdf_path}")
