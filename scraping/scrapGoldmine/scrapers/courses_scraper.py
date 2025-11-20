#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Scraper para extraer cursos desde HTML de Goldmine.
"""

import re
from typing import Dict, List, Optional
from bs4 import BeautifulSoup
import sys
from pathlib import Path

# Agregar el directorio padre al path para imports
current_dir = Path(__file__).parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

from utils.html_parser import extract_text_after_label, parse_days, parse_location
from utils.url_utils import extract_crn_from_detail_url


def parse_course_title(title_text: str) -> Dict[str, str]:
    """Parsea el título del curso en sus componentes."""
    parts = [p.strip() for p in title_text.split(' - ')]
    
    result = {
        'course_title': '',
        'crn': '',
        'subject': '',
        'course_number': '',
        'section': ''
    }
    
    if len(parts) >= 4:
        result['course_title'] = parts[0]
        result['crn'] = parts[1]
        course_parts = parts[2].split()
        if len(course_parts) >= 2:
            result['subject'] = course_parts[0]
            result['course_number'] = course_parts[1]
        result['section'] = parts[3]
    
    return result


def parse_meeting_times_table(table) -> List[Dict]:
    """Extrae información de la tabla de Scheduled Meeting Times."""
    meetings = []
    
    if not table:
        return meetings
    
    rows = table.find_all('tr')
    if len(rows) <= 1:
        return meetings
    
    for row in rows[1:]:
        cells = row.find_all('td', class_='dddefault')
        if len(cells) < 8:
            continue
        
        meeting = {}
        meeting['type'] = cells[0].get_text(strip=True)
        meeting['time'] = cells[1].get_text(strip=True)
        
        days_text = cells[2].get_text(strip=True)
        meeting['days'] = parse_days(days_text)
        
        where_html = str(cells[3])
        location_info = parse_location(where_html)
        meeting['location_building'] = location_info['location_building']
        meeting['location_room'] = location_info['location_room']
        meeting['location_ada_accessible'] = location_info['location_ada_accessible']
        
        meeting['date_range_raw'] = cells[4].get_text(strip=True)
        
        schedule_type = cells[5].get_text(strip=True)
        schedule_type = re.sub(r'\s*Schedule\s*Type$', '', schedule_type, flags=re.I).strip()
        meeting['schedule_type'] = schedule_type
        
        instructor_cell = cells[6]
        instructor_link = instructor_cell.find('a', href=re.compile(r'facultyprofile'))
        if instructor_link:
            meeting['instructor_name'] = instructor_link.get_text(strip=True)
        else:
            instructor_name = instructor_cell.get_text(strip=True)
            instructor_name = re.sub(r'\([PS]\)', '', instructor_name).strip()
            instructor_name = re.sub(r'E-mail', '', instructor_name, flags=re.I).strip()
            instructor_name = re.sub(r'\[.*?\]', '', instructor_name).strip()
            instructor_name = ' '.join(instructor_name.split())
            meeting['instructor_name'] = instructor_name
        
        abbr = instructor_cell.find(['abbr', 'ABBR'], title=re.compile(r'Primary|Secondary', re.I))
        if abbr:
            title_attr = abbr.get('title', '').strip()
            if 'Primary' in title_attr:
                meeting['instructor_role'] = 'Primary'
            elif 'Secondary' in title_attr:
                meeting['instructor_role'] = 'Secondary'
            else:
                meeting['instructor_role'] = ''
        else:
            meeting['instructor_role'] = ''
        
        meeting['description_text'] = cells[7].get_text(strip=True)
        meetings.append(meeting)
    
    return meetings


def extract_course_info(title_elem, detail_cell) -> Optional[Dict]:
    """Extrae toda la información de un curso."""
    course = {}
    
    title_link = title_elem.find('a')
    if not title_link:
        return None
    
    title_text = title_link.get_text(strip=True)
    detail_url = title_link.get('href', '')
    
    title_parts = parse_course_title(title_text)
    course.update(title_parts)
    course['detail_url'] = detail_url
    
    course['associated_term'] = extract_text_after_label(detail_cell, 'Associated Term')
    course['registration_dates_raw'] = extract_text_after_label(detail_cell, 'Registration Dates')
    course['level'] = extract_text_after_label(detail_cell, 'Levels')
    
    attributes_text = extract_text_after_label(detail_cell, 'Attributes')
    if attributes_text:
        attributes = [attr.strip() for attr in attributes_text.split(',') if attr.strip()]
        course['attributes'] = attributes
    else:
        course['attributes'] = []
    
    instructor_info = {'instructor_name': '', 'instructor_role': '', 'instructor_profile_url': '', 'instructor_email': ''}
    
    instructor_spans = detail_cell.find_all(['span', 'SPAN'], class_=re.compile(r'fieldlabeltext', re.I))
    for span in instructor_spans:
        span_text = span.get_text(strip=True)
        if 'Public Access' in span_text:
            parent = span.parent
            if parent:
                instructor_link = parent.find('a', href=re.compile(r'facultyprofile', re.I))
                if instructor_link:
                    instructor_info['instructor_name'] = instructor_link.get_text(strip=True)
                    instructor_info['instructor_profile_url'] = instructor_link.get('href', '')
                    
                    abbr = parent.find(['abbr', 'ABBR'], title=re.compile(r'Primary|Secondary', re.I))
                    if abbr:
                        title_attr = abbr.get('title', '').strip()
                        if 'Primary' in title_attr:
                            instructor_info['instructor_role'] = 'Primary'
                        elif 'Secondary' in title_attr:
                            instructor_info['instructor_role'] = 'Secondary'
            
            current = span.next_sibling
            while current and not instructor_info['instructor_name']:
                if hasattr(current, 'name'):
                    if current.name == 'a' and 'facultyprofile' in current.get('href', ''):
                        instructor_info['instructor_name'] = current.get_text(strip=True)
                        instructor_info['instructor_profile_url'] = current.get('href', '')
                        
                        abbr = current.find_next(['abbr', 'ABBR'], title=re.compile(r'Primary|Secondary', re.I))
                        if abbr:
                            title_attr = abbr.get('title', '').strip()
                            if 'Primary' in title_attr:
                                instructor_info['instructor_role'] = 'Primary'
                            elif 'Secondary' in title_attr:
                                instructor_info['instructor_role'] = 'Secondary'
                        break
                    if current.name in ['br', 'BR']:
                        break
                current = current.next_sibling
            break
    
    course.update(instructor_info)
    course['course_fees'] = extract_text_after_label(detail_cell, 'Course Fee(s)')
    
    books_link = detail_cell.find('a', href=re.compile(r'bookstore|books', re.I))
    if books_link:
        course['books_url'] = books_link.get('href', '')
    else:
        course['books_url'] = ''
    
    campus_text = detail_cell.get_text()
    campus_match = re.search(r'(Main Campus|Online Campus)[\s]*Campus', campus_text, re.I)
    if campus_match:
        course['campus'] = campus_match.group(0).strip()
    else:
        course['campus'] = ''
    
    schedule_match = re.search(r'([A-Za-z\s]+\([A-Z]+\))\s*Schedule Type', detail_cell.get_text(), re.I)
    if schedule_match:
        schedule_type = schedule_match.group(1).strip()
        course['schedule_type'] = schedule_type
    else:
        course['schedule_type'] = ''
    
    method_match = re.search(r'Instructional Method[:\s]*(.+?)(?:\n|Credits|$)', detail_cell.get_text(), re.I | re.DOTALL)
    if method_match:
        course['instructional_method'] = method_match.group(1).strip()
    else:
        course['instructional_method'] = ''
    
    credits_match = re.search(r'(\d+\.\d+)\s*Credits?', detail_cell.get_text(), re.I)
    if credits_match:
        try:
            course['credits'] = float(credits_match.group(1))
        except ValueError:
            course['credits'] = 0.0
    else:
        course['credits'] = 0.0
    
    catalog_link = detail_cell.find('a', href=re.compile(r'bwckctlg'))
    if catalog_link:
        course['catalog_entry_url'] = catalog_link.get('href', '')
    else:
        course['catalog_entry_url'] = ''
    
    meeting_times_table = None
    captions = detail_cell.find_all(['caption', 'CAPTION'], class_=re.compile(r'captiontext', re.I))
    for caption in captions:
        if 'Scheduled Meeting Times' in caption.get_text():
            meeting_times_table = caption.find_parent('table')
            break
    
    if not meeting_times_table:
        tables = detail_cell.find_all('table', class_=re.compile(r'datadisplaytable', re.I))
        for table in tables:
            summary = table.get('summary', '')
            if summary and 'Scheduled Meeting Times' in summary:
                meeting_times_table = table
                break
    
    if meeting_times_table:
        course['meeting_times'] = parse_meeting_times_table(meeting_times_table)
    else:
        course['meeting_times'] = []
    
    return course


def scrape_html_file(html_path: str) -> List[Dict]:
    """Lee el archivo HTML y extrae todos los cursos."""
    print(f"Leyendo archivo HTML: {html_path}")
    
    with open(html_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    print("Parseando HTML con BeautifulSoup...")
    soup = BeautifulSoup(html_content, 'html.parser')
    
    course_titles = soup.find_all('th', class_='ddtitle', scope='colgroup')
    print(f"Encontrados {len(course_titles)} cursos")
    
    courses = []
    
    for title_elem in course_titles:
        detail_cell = title_elem.find_next('td', class_='dddefault')
        
        if not detail_cell:
            continue
        
        course_info = extract_course_info(title_elem, detail_cell)
        if course_info:
            courses.append(course_info)
    
    print(f"Extraídos {len(courses)} cursos exitosamente")
    
    return courses

