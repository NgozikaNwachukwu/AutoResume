def contact_info():
    print(" Let's start with your contact information")

    contact = {} # We are creating the contact dictionary
    contact["full_name"] = input("Full name: ")
    contact["email"] = input("Email address: ")
    contact["phone"] = input("Phone number: ")
    contact["linkedin"] = input("LinkedIn URL: ")
    # we have now created the key -> value pairs for out contact dictionary
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

contact_info()