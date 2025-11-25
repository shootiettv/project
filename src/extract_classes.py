import io
import re
from typing import List, Optional, Tuple, Dict
import uuid

import pdfplumber
from pdfminer.high_level import extract_text as pdfminer_extract_text



def extract_classes_from_pdf(pdf_bytes: bytes) -> List[Dict]:

    parsed = parse_degree_evaluation(pdf_bytes)

    # dict containing:
    # {
    #   header fields ...,
    #   "courses": [
    #       { "course_title": "...", "subject": "CS", "course_number": "2302", ... }
    #   ]
    # }

    course_list = parsed.get("courses", [])

    formatted = []
    for course in course_list:
        subject = course.get("subject")
        num = course.get("course_number") or course.get("number")
        title = course.get("course_title") or course.get("title", "")

        if not subject or not num:
            continue

        # your backend requires _id = f"{subject}{num}"
        formatted.append({
            "_id": f"{subject}{num}",
            "course_title": title,
            "subject": subject,
            "course_number": num
        })

    print("📘 extract_classes_from_pdf returns:", formatted)
    return formatted



COURSE_CODE_RE = re.compile(r"\b([A-Z]{2,4})\s+(\d{4})\b")

def _extract_text_from_pdf_bytes(pdf_bytes: bytes) -> str:
    """Extract text from PDF bytes using pdfplumber first, and by pdfminer as a failure alternative."""
    text = ""
    try:
        with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
            pages = []
            for p in pdf.pages:
                t = p.extract_text(x_tolerance=2, y_tolerance=2) or ""
                pages.append(t)
            text = "\n".join(pages)
    except Exception:
        text = ""

    if len(text.strip()) < 20:
        try:
            text = pdfminer_extract_text(io.BytesIO(pdf_bytes)) or text
        except Exception:
            pass

    return text


def _extract_header(lines: List[str]) -> Dict[str, Optional[str]]:
    """Extract student ID, student name, semester term, degree program from UTEP degree evaluation PDF"""

    student_id = None
    student_name = None
    semester_term = None
    degree_program = None

    # First non-empty line of the document
    for line in lines:
        s = line.strip()
        if not s:
            continue
        m = re.match(r"^(\d{8})\s+(.+)$", s)

        if m:
            student_id = m.group(1).strip()
            student_name = m.group(2).strip()
            break

    for line in lines:
        if "Program" in line:
            m = re.search(r"Program\s*:\s*(.+)$", line)

            if m:
                degree_program = m.group(1).strip()

        if "Catalog Term" in line:
           m = re.search(r"Catalog\s*Term\s*:\s*(.+)$", line)
           if m:
               semester_term = m.group(1).strip()

    return{
        "student_id": student_id,
        "student_name": student_name,
        "semester_term": semester_term,
        "degree_program": degree_program
    }

def _parse_no_to_requirements(line: str) -> List[dict]:
    """Read a line starting with 'No' into reqirement dictionaries"""

    requirements: List[Dict] = []

    # "No to the Technical Electives"
    if re.match(r"^No\s+Technical\s+Electives\b", line, re.IGNORECASE):
        requirements.append({
            "subject": None,
            "number": None,
            "title": None,
            "group" : "Technical Electives",
            "notes": "Requirement not fully met; choose remaining credit hours per catalog."
        })
        return requirements


    for match in COURSE_CODE_RE.finditer(line.upper()):
        subject, number = match.group(1), match.group(2)
        requirements.append({
            "subject": subject,
            "number": number,
            "title": None,
            "group": None,
            "notes": "Unmet Requirement"
        })
    return requirements


def _extract_remaining_requirements(lines: List[str]) -> List[dict]:
    remaining: List[dict] = []

    for rawLine in lines:
        line = rawLine.strip()

        if not line:
            continue
        if not line.startswith("No "):
            continue

        requirements = _parse_no_to_requirements(line)
        remaining.extend(requirements)


    duplicateRemoved: List[Dict] = []
    encountered = set()

    for rem in remaining:
        key = (rem.get("subject"), rem.get("number"), rem.get("group"))

        if key in encountered:
            continue

        encountered.add(key)
        duplicateRemoved.append(rem)
    return duplicateRemoved

def _convert_to_course_interface(remaining: List[dict]) -> List[dict]:
    """ Convert extracted requirement dicitonaries into the Course interface format"""

    courses = []

    for req in remaining:
        subject = req.get("subject")
        number = req.get("number")

        # Skip the requirement groups
        if subject is None or number is None:
            continue

        courses.append({
            "_id": str(uuid.uuid4()),
            "course_title": req.get("title") or "",
            "subject": subject,
            "course_number": number,
        })
    return courses

def parse_degree_evaluation(pdf_bytes: bytes) -> Dict:
    """Transform PDF bytes into structured JSON-like data"""

    text = _extract_text_from_pdf_bytes(pdf_bytes)
    lines = text.splitlines()
    header = _extract_header(lines)
    remaining_requirements = _extract_remaining_requirements(lines)
    course_list = _convert_to_course_interface(remaining_requirements)

    return {
        **header,
        "courses": course_list,
        "parser_version": "utep-1.0",
        "raw_preview": "\n".join(lines[:40]),
    }

