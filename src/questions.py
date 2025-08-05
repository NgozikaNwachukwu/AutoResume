def contact_info():
    print(" Let's start with your contact information")

    contact = {} # We are creating the contact dictionary
    contact["full_name"] = input("Full name: ")
    contact["email"] = input("Email address: ")
    contact["phone"] = input("Phone number: ")
    contact["Location"] = input("Location")
    # we have now created the key -> value pairs for out contact dictionary

    # asking the user if they have linkedin
    has_linkedin = input("Do you have a Linkedin page? (yes/no): ").lower()
    if has_linkedin == "yes":
        contact["linkedin"] = input("LinkedIn URL: ")
    else:
        contact["linkedin"] = None
    
    # Asking the user if they have a github url
    has_github = input("Do you have a github page? (yes/no): ").lower()
    if has_github == "yes":
        contact["github"] = input("Github profile URL: ")
    else:
        contact["github"] = None

    #now we are going to ask the user if they have a portfolio
    has_portfolio = input("Do you have a portfolio? (yes/no): ").lower()
    if has_portfolio == "yes": 
        contact["portfolio"] = input("Portfolio URL: ")
    else:
        contact["portfolio"] = None
    
    return contact

if __name__ == "__main__":
    print(contact_info())