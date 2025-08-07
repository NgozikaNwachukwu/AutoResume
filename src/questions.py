def contact_info():
    print(" Let's start with your contact information")

    contact = {} # We are creating the contact dictionary
    contact["full_name"] = input("Full name: ")
    contact["email"] = input("Email address: ")
    contact["phone"] = input("Phone number: ")
    contact["Location"] = input("Location: ")
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
        print("✅ Inside education_info()")  # Confirm function runs

    education_list = []

    while True:
        school = input("Enter school name (or type 'done' to finish): ").strip()
        if school.lower() == "done":
            break
        degree = input("Enter degree: ").strip()
        start = input("Start date: ").strip()
        end = input("End date: ").strip()

        education_list.append({
            "school": school,
            "degree": degree,
            "start_date": start,
            "end_date": end
        })

    return education_list

#     print("Let's continue with your education details")
#     educations = []
    

#     education = {} #Education dictionary 
#     education["School"] = input("What school did you attend?: ")
#     education["Degree"] = input("What was your major?: ")
#     start = input("start date: ")
#     end = input("end date: ")
#      #creating concatenated date string 
#     education["date"] = start + "-" + end
#     education["Location"] = input("location of school: ")
   
# #gpa info
#     has_gpa = input("Would you like to input your GPA? (yes/no): ").lower()
#     if has_gpa == "yes":
#         education["gpa"] = input("GPA: ")
#     return education


    #Skills section
def skill_info():
        print("Enter your skills one by one")
        skill_catergories= {}#skill dictionary
        categories = [
            "languages",
            "Developer tools",
            "Frameworks",
            "Libraries",
            "Other"
        ]
        for category in categories:
            print(f"\nEnter skills for {categories}(Type done when you're finished:")
            skills = []
        while True:
            skill = input(f"-{category}skill: ").capitalize()
            if skill.lower() =="done":
                break
            if skill:
                skills.append(skill)
            skill_categories[category] = skills
        return skill_categories
#Exta curricular
def extra_curriculars():
    choice = input("\n would you like to add an extra curricular activity?(yes/no)")
    if choice.lower() != "yes":
            return []
    extras = []
    while True:
            print("\nEnter extracurricular activity (or type done as title to finish)" )
            title = input("Activity Title: ").strip()
            if title.lower() == "done":
                break
            if not title:
                print("Title caanot be empty")
                continue
            start_date = input("start Date ")
            end_date = input("End Date ")
            description = input("Describe the activity ").strip()
            extras.append({
                "title":title,
                "start_date": start_date,
                "end_date": end_date,
                "description": description
 })
            
    return extras


    if __name__ == "__main__":
        # print(contact_info())
        print(education_info())
        # print(skill_info())
        # print(extra_curriculars())
 
