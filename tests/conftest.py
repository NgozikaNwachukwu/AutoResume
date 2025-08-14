import pytest

@pytest.fixture
def sample_raw():
    return {
        "contact": {},
        "education": [
            {
                "school": "Nile University of Nigeria",
                "degree": "Information Technology",
                "dates": "Oct 2024 - Present",
                "location": "Abuja, Nigeria",
                "GPA": "4.5",
            }
        ],
        "skills": {},
        "experience": [
            {
                "title": "Web developer",
                "company": "Gabson Official",
                "location": "Abuja, Nigeria",
                "dates": "May 2025 - Present",
                "summary": "I was tasked with creating and managing the company website using Python and GitHub Actions. Delivered measurable outcomes by speeding up feedback cycles.",
            }
        ],
        "projects": [
            {
                "title": "AutoResume CLI",
                "tools": "Python",
                "dates": "Aug 2025 - Present",
                "summary": "Tested the program at every step using the command line; implemented core features and tests using Python, increasing test coverage.",
            }
        ],
        "extracurriculars": [
            {
                "title": "HiTech Club",
                "dates": "Nov 2021 – Aug 2022",
                "summary": "Co-founded the club; taught female students HTML and CSS; implemented core features and tests; increased test coverage.",
            }
        ],
    }
