#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Normalizador para cursos extraídos desde HTML.
"""

import re
from typing import Dict, Any, Optional, List
from html import unescape
from bs4 import BeautifulSoup
import sys
from pathlib import Path

# Agregar el directorio padre al path para imports
current_dir = Path(__file__).parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

from utils.url_utils import extract_crn_from_detail_url, extract_instructor_id


def is_numeric_crn(crn: str) -> bool:
    """Verifica si el CRN es numérico."""
    if not crn:
        return False
    return crn.strip().isdigit()


def index_courses_by_crn(courses_array: list) -> Dict[str, Dict]:
    """
    Indexa cursos por CRN, corrigiendo CRNs no numéricos automáticamente.
    
    Returns:
        Dict con cursos indexados por CRN
    """
    courses_indexed = {}
    corrected_count = 0
    duplicate_count = 0
    
    for course in courses_array:
        crn = course.get('crn')
        
        if not crn:
            continue
        
        crn_str = str(crn)
        
        # Verificar si el CRN es numérico
        if not is_numeric_crn(crn_str):
            detail_url = course.get('detail_url', '')
            real_crn = extract_crn_from_detail_url(detail_url)
            
            if real_crn:
                course['crn'] = real_crn
                crn_str = real_crn
                corrected_count += 1
        
        # Verificar duplicados
        if crn_str in courses_indexed:
            duplicate_count += 1
        
        courses_indexed[crn_str] = course
    
    return courses_indexed


def parse_registration_dates(dates_raw: str) -> Dict[str, Optional[str]]:
    """Parsea registration_dates_raw en registration_start y registration_end en formato ISO."""
    if not dates_raw or dates_raw.strip() == "":
        return {"start": None, "end": None}
    
    try:
        pattern = r'([A-Za-z]+)\s+(\d+),\s+(\d{4})\s+to\s+([A-Za-z]+)\s+(\d+),\s+(\d{4})'
        match = re.match(pattern, dates_raw.strip())
        
        if match:
            start_month, start_day, start_year = match.groups()[:3]
            end_month, end_day, end_year = match.groups()[3:]
            
            month_map = {
                "Jan": "01", "Feb": "02", "Mar": "03", "Apr": "04",
                "May": "05", "Jun": "06", "Jul": "07", "Aug": "08",
                "Sep": "09", "Oct": "10", "Nov": "11", "Dec": "12"
            }
            
            start_month_num = month_map.get(start_month[:3], None)
            end_month_num = month_map.get(end_month[:3], None)
            
            if start_month_num and end_month_num:
                start_date = f"{start_year}-{start_month_num}-{start_day.zfill(2)}"
                end_date = f"{end_year}-{end_month_num}-{end_day.zfill(2)}"
                return {"start": start_date, "end": end_date}
    except Exception:
        pass
    
    return {"start": None, "end": None}


def clean_campus(campus_raw: str) -> Dict[str, Optional[str]]:
    """Limpia el campo campus."""
    if not campus_raw or campus_raw.strip() == "":
        return {"code": None, "name": None}
    
    cleaned = campus_raw.replace("Campus Campus", "Campus").strip()
    words = cleaned.split()
    if len(words) > 0:
        first_word = words[0].upper()
        code_map = {
            "MAIN": "MAIN",
            "ONLINE": "ONLINE",
            "HYBRID": "HYBRID"
        }
        code = code_map.get(first_word, first_word)
        return {"code": code, "name": cleaned}
    
    return {"code": None, "name": cleaned}


def clean_schedule_type(schedule_type_raw: str) -> Dict[str, Optional[str]]:
    """Limpia schedule_type."""
    if not schedule_type_raw or schedule_type_raw.strip() == "":
        return {"code": None, "label": None}
    
    pattern = r'([A-Za-z][A-Za-z\s]*?)\s*\(([A-Z]+)\)'
    matches = list(re.finditer(pattern, schedule_type_raw))
    
    if matches:
        match = matches[-1]
        label = match.group(1).strip()
        code = match.group(2).strip()
        label = re.sub(r'\s+', ' ', label)
        label = re.sub(r'View my Books', '', label, flags=re.IGNORECASE)
        label = re.sub(r'Main Campus Campus', '', label, flags=re.IGNORECASE)
        label = re.sub(r'\s+', ' ', label).strip()
        return {"code": code, "label": label}
    
    cleaned = schedule_type_raw.replace("View my Books", "").strip()
    cleaned = re.sub(r'Main Campus Campus', '', cleaned)
    cleaned = re.sub(r'\n+', ' ', cleaned)
    cleaned = re.sub(r'\s+', ' ', cleaned)
    cleaned = cleaned.strip()
    
    schedule_types = ["Lecture", "Laboratory", "Seminar", "Workshop", "Independent Study", 
                      "Field Experience", "Practicum", "Thesis", "Dissertation", "Lab"]
    
    for st in schedule_types:
        if re.search(r'^' + re.escape(st) + r'\b', cleaned, re.IGNORECASE):
            return {"code": None, "label": st}
        if len(cleaned) < 100 and st.lower() in cleaned.lower():
            return {"code": None, "label": st}
    
    if cleaned:
        return {"code": None, "label": cleaned}
    
    return {"code": None, "label": None}


def infer_instructional_method(raw_data: Dict[str, Any]) -> Optional[str]:
    """Intenta inferir el instructional_method."""
    campus = raw_data.get("campus", "").lower()
    if "online" in campus:
        return "Online"
    
    schedule_type = raw_data.get("schedule_type", "").lower()
    if "online" in schedule_type or "web" in schedule_type:
        return "Online"
    
    meeting_times = raw_data.get("meeting_times", [])
    if not meeting_times or len(meeting_times) == 0:
        return None
    
    has_physical_location = False
    for mt in meeting_times:
        location = mt.get("location_building", "")
        if location and "online" not in location.lower() and "web" not in location.lower():
            has_physical_location = True
            break
    
    if not has_physical_location and meeting_times:
        return "Online"
    
    if has_physical_location:
        return "Face to Face"
    
    return None


def normalize_course_fees(fees_raw: Any) -> Dict[str, Any]:
    """Normaliza course_fees."""
    if fees_raw is None:
        return {"amount": 0.0, "currency": "USD"}
    
    if isinstance(fees_raw, (int, float)):
        return {"amount": float(fees_raw), "currency": "USD"}
    
    if isinstance(fees_raw, str):
        fees_str = fees_raw.strip()
        if fees_str.lower() in ["none.", "none", "", "n/a", "na"]:
            return {"amount": 0.0, "currency": "USD"}
        
        amount_match = re.search(r'\$?(\d+\.?\d*)', fees_str)
        if amount_match:
            try:
                amount = float(amount_match.group(1))
                return {"amount": amount, "currency": "USD"}
            except ValueError:
                pass
    
    return {"amount": 0.0, "currency": "USD"}


def normalize_attributes(attributes_raw: List[str]) -> List[Dict[str, Optional[str]]]:
    """Normaliza attributes."""
    if not attributes_raw or not isinstance(attributes_raw, list):
        return []
    
    normalized = []
    for attr in attributes_raw:
        if not isinstance(attr, str):
            continue
        
        attr = attr.strip()
        if not attr:
            continue
        
        pattern = r'^\[([A-Z]+)\]\s*(.+)$'
        match = re.match(pattern, attr)
        
        if match:
            code = match.group(1)
            label = match.group(2).strip()
            normalized.append({"code": code, "label": label})
        else:
            normalized.append({"code": None, "label": attr})
    
    return normalized


def parse_instructor_name(name_raw: str) -> Dict[str, Optional[str]]:
    """Parsea el nombre del instructor."""
    if not name_raw or name_raw.strip() == "":
        return {"first_name": None, "middle_name": None, "last_name": None}
    
    cleaned = re.sub(r'\s+', ' ', name_raw.strip())
    parts = cleaned.split()
    
    if len(parts) == 0:
        return {"first_name": None, "middle_name": None, "last_name": None}
    elif len(parts) == 1:
        return {"first_name": None, "middle_name": None, "last_name": parts[0]}
    elif len(parts) == 2:
        return {"first_name": parts[0], "middle_name": None, "last_name": parts[1]}
    else:
        return {
            "first_name": parts[0],
            "middle_name": " ".join(parts[1:-1]) if len(parts) > 2 else None,
            "last_name": parts[-1]
        }


def clean_location_building(location_raw: str) -> Dict[str, Optional[str]]:
    """Limpia location_building."""
    if not location_raw or location_raw.strip() == "":
        return {"building": None, "room": None}
    
    try:
        soup = BeautifulSoup(location_raw, 'html.parser')
        text = soup.get_text(strip=True)
    except Exception:
        text = re.sub(r'<[^>]+>', '', location_raw)
        text = unescape(text).strip()
    
    if not text:
        return {"building": None, "room": None}
    
    room_match = re.search(r'\s+(\d+[A-Za-z]*)\s*$', text)
    
    if room_match:
        room = room_match.group(1).strip()
        building = text[:room_match.start()].strip()
        return {"building": building, "room": room}
    
    return {"building": text, "room": None}


def parse_date_range(date_range_raw: str) -> Dict[str, Optional[str]]:
    """Parsea date_range_raw en start_date y end_date."""
    if not date_range_raw or date_range_raw.strip() == "":
        return {"start": None, "end": None}
    
    try:
        pattern = r'([A-Za-z]+)\s+(\d+),\s+(\d{4})\s+-\s+([A-Za-z]+)\s+(\d+),\s+(\d{4})'
        match = re.match(pattern, date_range_raw.strip())
        
        if match:
            start_month, start_day, start_year = match.groups()[:3]
            end_month, end_day, end_year = match.groups()[3:]
            
            month_map = {
                "Jan": "01", "Feb": "02", "Mar": "03", "Apr": "04",
                "May": "05", "Jun": "06", "Jul": "07", "Aug": "08",
                "Sep": "09", "Oct": "10", "Nov": "11", "Dec": "12"
            }
            
            start_month_num = month_map.get(start_month[:3], None)
            end_month_num = month_map.get(end_month[:3], None)
            
            if start_month_num and end_month_num:
                start_date = f"{start_year}-{start_month_num}-{start_day.zfill(2)}"
                end_date = f"{end_year}-{end_month_num}-{end_day.zfill(2)}"
                return {"start": start_date, "end": end_date}
    except Exception:
        pass
    
    return {"start": None, "end": None}


def normalize_time(time_raw: str) -> str:
    """Normaliza el formato de tiempo."""
    if not time_raw or time_raw.strip() == "":
        return time_raw
    return time_raw.strip()


def clean_meeting_time(meeting_time_raw: Dict[str, Any], instructor_id: Optional[str]) -> Dict[str, Any]:
    """Limpia y normaliza un meeting_time individual."""
    cleaned = {
        "type": meeting_time_raw.get("type") or None,
        "days": meeting_time_raw.get("days") or [],
        "location_ada_accessible": meeting_time_raw.get("location_ada_accessible", False)
    }
    
    time_raw = meeting_time_raw.get("time", "")
    cleaned["time"] = normalize_time(time_raw) if time_raw else None
    
    location_raw = meeting_time_raw.get("location_building", "")
    location_clean = clean_location_building(location_raw)
    cleaned["location_building"] = location_clean["building"]
    cleaned["location_room"] = location_clean["room"]
    
    date_range_raw = meeting_time_raw.get("date_range_raw", "")
    dates = parse_date_range(date_range_raw)
    cleaned["start_date"] = dates["start"]
    cleaned["end_date"] = dates["end"]
    
    schedule_type_raw = meeting_time_raw.get("schedule_type", "")
    schedule_clean = clean_schedule_type(schedule_type_raw)
    cleaned["schedule_type"] = schedule_clean
    
    cleaned["instructor_id"] = instructor_id
    
    return cleaned


def transform_course(course_raw: Dict[str, Any]) -> Dict[str, Any]:
    """Transforma un curso de la estructura cruda a la estructura limpia normalizada."""
    instructor_profile_url = course_raw.get("instructor_profile_url", "")
    instructor_id = extract_instructor_id(instructor_profile_url)
    
    instructor_name_raw = course_raw.get("instructor_name", "")
    instructor_name_parts = parse_instructor_name(instructor_name_raw)
    
    registration_dates_raw = course_raw.get("registration_dates_raw", "")
    registration_dates = parse_registration_dates(registration_dates_raw)
    
    campus_raw = course_raw.get("campus", "")
    campus_clean = clean_campus(campus_raw)
    
    schedule_type_raw = course_raw.get("schedule_type", "")
    schedule_type_clean = clean_schedule_type(schedule_type_raw)
    
    instructional_method = infer_instructional_method(course_raw)
    
    fees_raw = course_raw.get("course_fees")
    fees_clean = normalize_course_fees(fees_raw)
    
    attributes_raw = course_raw.get("attributes", [])
    attributes_clean = normalize_attributes(attributes_raw)
    
    instructor_email = course_raw.get("instructor_email", "")
    instructor_email = instructor_email.strip() if instructor_email else None
    if instructor_email == "":
        instructor_email = None
    
    meeting_times_raw = course_raw.get("meeting_times", [])
    meeting_times_clean = [
        clean_meeting_time(mt, instructor_id) 
        for mt in meeting_times_raw
    ]
    
    course_clean = {
        "crn": course_raw.get("crn"),
        "course_title": course_raw.get("course_title") or None,
        "subject": course_raw.get("subject") or None,
        "course_number": course_raw.get("course_number") or None,
        "section": course_raw.get("section") or None,
        "term": course_raw.get("associated_term") or None,
        "detail_url": course_raw.get("detail_url") or None,
        "registration_start": registration_dates["start"],
        "registration_end": registration_dates["end"],
        "level": course_raw.get("level") or None,
        "credits": course_raw.get("credits"),
        "campus": campus_clean,
        "schedule_type": schedule_type_clean,
        "instructional_method": instructional_method,
        "course_fees_amount": fees_clean["amount"],
        "course_fees_currency": fees_clean["currency"],
        "books_url": course_raw.get("books_url") or None,
        "catalog_entry_url": course_raw.get("catalog_entry_url") or None,
        "attributes": attributes_clean,
        "instructor_id": instructor_id,
        "instructor": {
            "first_name": instructor_name_parts["first_name"],
            "middle_name": instructor_name_parts["middle_name"],
            "last_name": instructor_name_parts["last_name"],
            "role": course_raw.get("instructor_role") or None,
            "profile_url": course_raw.get("instructor_profile_url") or None,
            "email": instructor_email
        },
        "meeting_times": meeting_times_clean
    }
    
    return course_clean

