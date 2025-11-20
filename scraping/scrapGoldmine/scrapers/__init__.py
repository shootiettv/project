"""
Módulos de scraping para Goldmine.
"""

from .courses_scraper import scrape_html_file, extract_course_info, parse_course_title, parse_meeting_times_table
from .class_details_scraper import scrape_class_detail, extract_seating_info, extract_restrictions, extract_prerequisites

__all__ = [
    'scrape_html_file',
    'extract_course_info',
    'parse_course_title',
    'parse_meeting_times_table',
    'scrape_class_detail',
    'extract_seating_info',
    'extract_restrictions',
    'extract_prerequisites'
]

