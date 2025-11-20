"""
Utilidades para parsing HTML.
"""

import re
from typing import List, Dict
from html import unescape
from bs4 import BeautifulSoup


def extract_text_after_label(element, label: str) -> str:
    """Extrae el texto que sigue después de un label."""
    label_spans = element.find_all(['span', 'SPAN'], class_=re.compile(r'fieldlabeltext', re.I))
    
    for label_span in label_spans:
        span_text = label_span.get_text(strip=True)
        if label in span_text or span_text.startswith(label):
            current = label_span.next_sibling
            value_parts = []
            while current:
                if hasattr(current, 'name'):
                    if current.name in ['span', 'SPAN'] and 'fieldlabeltext' in str(current.get('class', [])):
                        break
                    if current.name == 'br' or current.name == 'BR':
                        break
                
                if isinstance(current, str):
                    value_parts.append(current.strip())
                elif hasattr(current, 'get_text'):
                    text = current.get_text(strip=True)
                    if text:
                        value_parts.append(text)
                
                current = current.next_sibling
            
            value = ' '.join(value_parts).strip()
            value = ' '.join(value.split())
            return value
    
    full_text = element.get_text(separator=' ', strip=True)
    pattern = rf'{re.escape(label)}[:\s]+(.+?)(?:\s+[A-Z][a-z]+\s*:|$)'
    match = re.search(pattern, full_text, re.I)
    if match:
        return match.group(1).strip()
    
    return ''


def parse_days(days_text: str) -> List[str]:
    """Convierte días en lista (ej. "MWF" -> ["M", "W", "F"])."""
    if not days_text or not days_text.strip():
        return []
    
    days_text = days_text.strip().upper()
    days_list = [day for day in days_text if day.isalpha()]
    return days_list


def parse_location(location_text: str) -> Dict[str, any]:
    """Parsea la ubicación extrayendo edificio, sala y accesibilidad ADA."""
    result = {
        'location_building': '',
        'location_room': '',
        'location_ada_accessible': False
    }
    
    location_text = re.sub(r'<br\s*/?>', ' ', location_text, flags=re.I)
    location_text = ' '.join(location_text.split())
    
    if 'ADA Accessible' in location_text or 'ADA Access' in location_text:
        result['location_ada_accessible'] = True
        location_text = re.sub(r'ADA\s+Accessible?', '', location_text, flags=re.I).strip()
    
    room_match = re.search(r'(\d+[A-Z]?)$', location_text)
    if room_match:
        result['location_room'] = room_match.group(1)
        result['location_building'] = location_text[:room_match.start()].strip()
    else:
        result['location_building'] = location_text.strip()
    
    return result

