import uuid

def extract_classes_from_pdf(file):
    """
    Dummy extractor that returns Course objects in the correct format.
    Replace this later with your real PDF parsing logic.
    """

    classes = [
        ("Introduction to Computer Science", "CS", "1301"),
        ("Data Structures", "CS", "2302"),
        ("Advanced Object-Oriented Programming", "CS", "3331"),
        ("Software Engineering", "CS", "4350"),
        ("Physics I", "PHYS", "2320"),
        ("Physics I Lab", "PHYS", "2120")
    ]

    formatted = []
    for title, subject, number in classes:
        formatted.append({
            "_id": f"{subject}{number}",          # unique ID as string
            "course_title": title,
            "subject": subject,
            "course_number": number
        })

    print("📘 extract_classes returns:", formatted)
    return formatted

