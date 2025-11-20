#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Scraper para extraer detalles de clases desde páginas individuales de Goldmine.
"""

import re
import requests
from bs4 import BeautifulSoup
from typing import Dict, Optional, List
from dataclasses import asdict
from urllib.parse import urljoin
import sys
from pathlib import Path

# Agregar el directorio padre al path para imports
current_dir = Path(__file__).parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

from models.class_detail import ClassDetailInfo
from utils.url_utils import extract_crn_from_url
from utils.html_parser import extract_text_after_label


def parse_course_title(title_text: str) -> Dict[str, str]:
    """Parsea el título del curso en sus componentes."""
    # Formato: "Principles of Accounting I - 21059 - ACCT 2301 - 001"
    parts = [p.strip() for p in title_text.split(' - ')]
    
    result = {
        'course_title': title_text,
        'crn': '',
        'subject': '',
        'course_number': '',
        'section': ''
    }
    
    if len(parts) >= 4:
        result['course_title'] = parts[0]
        result['crn'] = parts[1]
        # "ACCT 2301" -> subject="ACCT", course_number="2301"
        course_parts = parts[2].split()
        if len(course_parts) >= 2:
            result['subject'] = course_parts[0]
            result['course_number'] = course_parts[1]
        result['section'] = parts[3]
    
    return result


def extract_seating_info(soup: BeautifulSoup) -> Dict[str, int]:
    """Extrae información de capacidad y asientos."""
    result = {
        'capacity': 0,
        'actual_seats': 0,
        'remaining_seats': 0,
        'waitlist_seats': 0,
        'waitlist_remaining': 0
    }
    
    # Buscar tabla de capacidad
    capacity_text = soup.get_text()
    
    # Buscar patrón: "Capacity Actual Remaining Seats 80 27 53"
    capacity_match = re.search(r'Capacity\s+Actual\s+Remaining\s+Seats\s+(\d+)\s+(\d+)\s+(\d+)', capacity_text)
    if capacity_match:
        result['capacity'] = int(capacity_match.group(1))
        result['actual_seats'] = int(capacity_match.group(2))
        result['remaining_seats'] = int(capacity_match.group(3))
    
    # Buscar patrón de waitlist
    waitlist_match = re.search(r'Waitlist\s+Seats\s+(\d+)\s+(\d+)', capacity_text)
    if waitlist_match:
        result['waitlist_seats'] = int(waitlist_match.group(1))
        result['waitlist_remaining'] = int(waitlist_match.group(2))
    
    return result


def extract_restrictions(soup: BeautifulSoup) -> Dict[str, List[str]]:
    """Extrae restricciones de la clase."""
    result = {
        'prohibited_programs': [],
        'prohibited_classifications': [],
        'required_levels': [],
        'required_campuses': []
    }
    
    full_text = soup.get_text(separator='\n', strip=True)
    
    # 1. Buscar restricciones prohibidas: Programas
    prohibited_programs_match = re.search(
        r'May not be enrolled in one of the following Programs:?\s*\n(.+?)(?:\nMust be enrolled|May not be enrolled|Prerequisites|$)',
        full_text,
        re.DOTALL | re.I
    )
    if prohibited_programs_match:
        prohibited_text = prohibited_programs_match.group(1)
        programs = re.findall(r'(BA in [^\n]+(?:Online|Onl)?|BS in [^\n]+(?:Online|Onl)?|MA in [^\n]+(?:Online|Onl)?|MS in [^\n]+(?:Online|Onl)?|MFA in [^\n]+(?:Online|Onl)?|MBA[^\n]*(?:Online|Onl)?|MSN[^\n]*(?:Online|Onl)?|MEd[^\n]*(?:Online|Onl)?|Grad Cer[^\n]*(?:Online|Onl)?|GRCER[^\n]*(?:Online|Onl)?|General Studies[^\n]*(?:Online|Onl)?|Pre-Nursing[^\n]*(?:Online|Onl)?|RN-BSN[^\n]*(?:Online|Onl)?)', prohibited_text, re.I)
        result['prohibited_programs'] = [p.strip() for p in programs if p.strip() and len(p.strip()) > 3]
    
    # 2. Buscar restricciones prohibidas: Clasificaciones
    prohibited_classifications_match = re.search(
        r'May not be enrolled as the following Classifications:?\s*\n(.+?)(?:\nMust be enrolled|May not be enrolled|Prerequisites|Return to|Skip to|Release:|$)',
        full_text,
        re.DOTALL | re.I
    )
    if prohibited_classifications_match:
        classifications_text = prohibited_classifications_match.group(1)
        classifications = []
        exclude_words = ['Return to Previous', 'Skip to top', 'Release:', '©', 'Ellucian', 'Company', 'EXIT', 'HELP', 'SITE MAP']
        
        for line in classifications_text.split('\n'):
            line = line.strip()
            if any(exclude in line for exclude in exclude_words):
                continue
            
            valid_classifications = ['Doctoral', 'Graduate', 'Undergraduate', 'Post', 'Special', 'Professional', 
                                   'Freshman', 'Sophomore', 'Junior', 'Senior', 'Baccalaureate']
            
            if line and len(line) > 2:
                line_lower = line.lower()
                if (line[0].isupper() and 
                    any(line_lower.startswith(cls.lower()) or cls.lower() in line_lower for cls in valid_classifications)):
                    line_clean = ' '.join(line.split())
                    if not re.match(r'^\d+\.\d+', line_clean) and len(line_clean) < 50:
                        classifications.append(line_clean)
        
        result['prohibited_classifications'] = classifications
    
    # 3. Buscar restricciones requeridas: Niveles
    required_levels_match = re.search(
        r'Must be enrolled in one of the following Levels:?\s*\n(.+?)(?:\nMust be enrolled|May not be enrolled|Prerequisites|Return to|Skip to|Release:|$)',
        full_text,
        re.DOTALL | re.I
    )
    if required_levels_match:
        levels_text = required_levels_match.group(1)
        levels = []
        exclude_words = ['Return to Previous', 'Skip to top', 'Release:', '©', 'Ellucian', 'Company', 'EXIT', 'HELP', 'SITE MAP']
        valid_levels = ['Doctoral', 'Graduate', 'Undergraduate', 'Post', 'Baccalaureate', 'Special', 'Professional']
        
        for line in levels_text.split('\n'):
            line = line.strip()
            if any(exclude in line for exclude in exclude_words):
                continue
            
            if line and len(line) > 2:
                line_lower = line.lower()
                if (line[0].isupper() and 
                    any(line_lower.startswith(lvl.lower()) or lvl.lower() in line_lower for lvl in valid_levels)):
                    line_clean = ' '.join(line.split())
                    if not re.match(r'^\d+\.\d+', line_clean) and len(line_clean) < 50:
                        levels.append(line_clean)
        
        result['required_levels'] = levels
    
    # 4. Buscar restricciones requeridas: Campus
    required_campuses_match = re.search(
        r'Must be enrolled in one of the following Campuses:?\s*\n(.+?)(?:\nMust be enrolled|May not be enrolled|Prerequisites|Return to|Skip to|Release:|$)',
        full_text,
        re.DOTALL | re.I
    )
    if required_campuses_match:
        campuses_text = required_campuses_match.group(1)
        campuses = []
        exclude_words = ['Return to Previous', 'Skip to top', 'Release:', '©', 'Ellucian', 'Company', 'EXIT', 'HELP', 'SITE MAP']
        
        for line in campuses_text.split('\n'):
            line = line.strip()
            if any(exclude in line for exclude in exclude_words):
                continue
            
            if line and (line[0].isupper() or 'Main Campus' in line or 'Online Campus' in line):
                line_clean = ' '.join(line.split())
                if line_clean and len(line_clean) > 2 and ('Campus' in line_clean or len(line_clean) < 30):
                    campuses.append(line_clean)
        
        if not campuses:
            if 'Main Campus' in campuses_text:
                campuses = ['Main Campus']
            elif 'Online Campus' in campuses_text:
                campuses = ['Online Campus']
            else:
                campus_pattern = re.findall(r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s*Campus)', campuses_text)
                campuses = [c.strip() for c in campus_pattern if c.strip() and len(c.strip()) > 3]
        
        result['required_campuses'] = campuses
    
    return result


def extract_prerequisites(soup: BeautifulSoup) -> List[Dict[str, str]]:
    """Extrae prerequisitos de la clase."""
    prerequisites = []
    
    # Buscar la sección de prerequisitos
    prereq_label = soup.find('span', class_='fieldlabeltext', string=re.compile(r'Prerequisites:', re.I))
    
    if not prereq_label:
        prereq_label = soup.find(string=re.compile(r'Prerequisites:', re.I))
        if not prereq_label:
            return prerequisites
    
    if prereq_label:
        if hasattr(prereq_label, 'parent'):
            container = prereq_label.find_parent('td', class_='dddefault')
        else:
            container = prereq_label.find_parent('td', class_='dddefault')
    else:
        return prerequisites
    
    if not container:
        return prerequisites
    
    # Buscar todos los bloques "Course or Test:"
    course_or_test_spans = container.find_all(string=re.compile(r'Course or Test:', re.I))
    
    for span_text in course_or_test_spans:
        parent = span_text.find_parent()
        if not parent:
            continue
        
        link = parent.find('a', href=re.compile(r'bwckctlg'))
        subject = ''
        course_number = ''
        minimum_grade = ''
        
        if link:
            link_text = link.get_text(strip=True)
            if link_text == 'View Catalog Entry':
                continue
            
            subject = link_text
            next_text = link.next_sibling
            if next_text:
                course_number = str(next_text).strip()
                course_number = re.sub(r'\D', '', course_number)[:5]
                
                if not course_number:
                    href = link.get('href', '')
                    course_match = re.search(r'sel_crse_strt=(\d+)', href, re.I)
                    if course_match:
                        course_number = course_match.group(1)
        else:
            test_match = re.search(r'(SX[A-Z]{2,4})\s+(\d+)', str(parent.get_text()))
            if test_match:
                subject = test_match.group(1)
                course_number = test_match.group(2)
        
        grade_match = re.search(r'Minimum Grade of\s+([A-Z]+)', parent.get_text(), re.I)
        if grade_match:
            minimum_grade = grade_match.group(1)
        
        if subject and course_number:
            is_duplicate = any(
                p.get('subject') == subject and p.get('course_number') == course_number 
                for p in prerequisites
            )
            if not is_duplicate:
                prerequisites.append({
                    'subject': subject,
                    'course_number': course_number,
                    'minimum_grade': minimum_grade if minimum_grade else '',
                    'concurrent_allowed': 'May not be taken concurrently' in parent.get_text()
                })
    
    return prerequisites


def extract_meeting_times(soup: BeautifulSoup) -> List[Dict[str, str]]:
    """Extrae horarios de reunión de la clase."""
    meeting_times = []
    # Por ahora retornar lista vacía, se puede implementar más adelante
    return meeting_times


def scrape_class_detail(url: str, session: Optional[requests.Session] = None, timeout: int = 30, verbose: bool = True) -> Optional[ClassDetailInfo]:
    """
    Hace scraping de la página de detalles de una clase en Goldmine.
    
    Args:
        url: URL de la página de detalles de la clase
        session: Session de requests opcional para reutilizar conexiones
        timeout: Timeout para la petición HTTP
        verbose: Si True, imprime mensajes de progreso
        
    Returns:
        ClassDetailInfo con la información extraída
    """
    headers = {
        'User-Agent': (
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
            'AppleWebKit/537.36 (KHTML, like Gecko) '
            'Chrome/91.0.4472.124 Safari/537.36'
        )
    }
    
    if verbose:
        print(f"📥 Descargando: {url}")
    try:
        if session:
            response = session.get(url, headers=headers, timeout=timeout)
        else:
            response = requests.get(url, headers=headers, timeout=timeout)
        
        response.raise_for_status()
        response.encoding = response.apparent_encoding or 'utf-8'
    except requests.RequestException as e:
        if verbose:
            print(f"❌ Error al descargar la URL: {e}")
        return None
    
    if verbose:
        print("🔍 Parseando HTML...")
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Extraer título del curso
    title_elem = soup.find('th', class_='ddtitle')
    
    if not title_elem:
        all_th = soup.find_all('th')
        for th in all_th:
            text = th.get_text(strip=True)
            if ' - ' in text and len(text.split(' - ')) >= 4:
                title_elem = th
                break
    
    if not title_elem:
        if verbose:
            print("❌ No se encontró el título del curso")
        return None
    
    title_text = title_elem.get_text(strip=True)
    if verbose:
        print(f"📚 Título encontrado: {title_text}")
    
    course_info = parse_course_title(title_text)
    
    # Extraer CRN de la URL (más confiable)
    crn_from_url = extract_crn_from_url(url)
    if crn_from_url:
        if course_info['crn'] != crn_from_url:
            if verbose:
                print(f"⚠️  CRN del título ({course_info['crn']}) no coincide con URL ({crn_from_url}), usando CRN de URL")
            course_info['crn'] = crn_from_url
    
    # Buscar la tabla principal de detalles
    detail_table = soup.find('table', class_='detailclass')
    if not detail_table:
        detail_table = soup.find('td', class_='dddefault')
    
    if not detail_table:
        print("❌ No se encontró la tabla de detalles")
        return None
    
    # Extraer información básica
    full_text = soup.get_text(separator=' ', strip=True)
    
    # Término asociado
    term_match = re.search(r'Associated Term:\s*(Spring|Fall|Summer|Winter)\s+(\d{4})', full_text, re.I)
    if term_match:
        associated_term = f"{term_match.group(1)} {term_match.group(2)}"
    else:
        term_match = re.search(r'Spring\s+2026|Fall\s+2026|Summer\s+2026|Winter\s+2026', full_text, re.I)
        associated_term = term_match.group(0) if term_match else ''
    
    # Niveles
    levels_match = re.search(r'Levels:\s*([A-Za-z\s,]+?)(?:\s+Main Campus|Campus|Schedule Type|$)', full_text, re.I)
    levels_text = levels_match.group(1).strip() if levels_match else ''
    levels = [l.strip() for l in levels_text.split(',') if l.strip()] if levels_text else []
    
    # Campus
    campus_match = re.search(r'Main Campus\s+Campus|Campus:\s*([A-Za-z\s]+?)(?:\s+Lecture|Schedule Type|$)', full_text, re.I)
    if 'Main Campus' in full_text:
        campus = 'Main Campus'
    elif campus_match:
        campus = campus_match.group(1).strip() if campus_match.lastindex else ''
    else:
        campus = ''
    
    # Tipo de horario
    schedule_match = re.search(r'Lecture\s*\(([A-Z]+)\)|Schedule Type:\s*([A-Za-z\s()]+?)(?:\s+Min Tech|Instructional Method|$)', full_text, re.I)
    if schedule_match:
        schedule_type = schedule_match.group(1) or schedule_match.group(2)
        schedule_type = schedule_type.strip() if schedule_type else ''
    else:
        schedule_type = ''
    
    # Método de instrucción
    method_match = re.search(r'Min Tech:\s*(\d+%)\s+or\s+Less\s+Online|Instructional Method\s+([\d%]+|[A-Za-z\s]+?)(?:\s+Credits|$)', full_text, re.I)
    if method_match:
        instructional_method = method_match.group(1) or method_match.group(2)
        instructional_method = instructional_method.strip() if instructional_method else ''
    else:
        instructional_method = ''
    
    # Créditos
    credits_match = re.search(r'([\d.]+)\s+Credits|Credits\s+\[View Catalog Entry\]\s*([\d.]+)', full_text, re.I)
    if credits_match:
        credits = credits_match.group(1) or credits_match.group(2)
        credits = credits.strip() if credits else ''
    else:
        credits = ''
    
    # Extraer información de asientos
    seating_info = extract_seating_info(soup)
    
    # Extraer restricciones
    restrictions = extract_restrictions(soup)
    
    # Extraer prerequisitos
    prerequisites = extract_prerequisites(soup)
    
    # Extraer horarios de reunión
    meeting_times = extract_meeting_times(soup)
    
    # Extraer URL del catálogo
    catalog_link = None
    all_links = soup.find_all('a', href=re.compile(r'bwckctlg'))
    for link in all_links:
        if link.get_text(strip=True) == 'View Catalog Entry':
            catalog_link = link
            break
    
    catalog_entry_url = ''
    if catalog_link:
        catalog_entry_url = urljoin(url, catalog_link.get('href', ''))
    
    # Crear objeto de información de clase
    class_detail = ClassDetailInfo(
        course_title=course_info['course_title'],
        crn=course_info['crn'],
        subject=course_info['subject'],
        course_number=course_info['course_number'],
        section=course_info['section'],
        associated_term=associated_term,
        levels=levels,
        campus=campus,
        schedule_type=schedule_type,
        instructional_method=instructional_method,
        credits=credits,
        capacity=seating_info['capacity'],
        actual_seats=seating_info['actual_seats'],
        remaining_seats=seating_info['remaining_seats'],
        waitlist_seats=seating_info['waitlist_seats'],
        waitlist_remaining=seating_info['waitlist_remaining'],
        restrictions_prohibited_programs=restrictions['prohibited_programs'],
        restrictions_prohibited_classifications=restrictions['prohibited_classifications'],
        restrictions_required_levels=restrictions['required_levels'],
        restrictions_required_campuses=restrictions['required_campuses'],
        prerequisites=prerequisites,
        meeting_times=meeting_times,
        catalog_entry_url=catalog_entry_url
    )
    
    if verbose:
        print("✅ Información extraída exitosamente")
    return class_detail

