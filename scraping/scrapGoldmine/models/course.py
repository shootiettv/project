"""
Modelo de datos para Course.
"""

from dataclasses import dataclass
from typing import Optional, List, Dict, Any


@dataclass
class Course:
    """Modelo de datos para un curso básico."""
    crn: str
    course_title: Optional[str]
    subject: Optional[str]
    course_number: Optional[str]
    section: Optional[str]
    term: Optional[str]
    detail_url: Optional[str]
    registration_start: Optional[str]
    registration_end: Optional[str]
    level: Optional[str]
    credits: float
    campus: Dict[str, Optional[str]]
    schedule_type: Dict[str, Optional[str]]
    instructional_method: Optional[str]
    course_fees_amount: float
    course_fees_currency: str
    books_url: Optional[str]
    catalog_entry_url: Optional[str]
    attributes: List[Dict[str, Optional[str]]]
    instructor_id: Optional[str]
    instructor: Dict[str, Any]
    meeting_times: List[Dict[str, Any]]

