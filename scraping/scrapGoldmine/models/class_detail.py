"""
Modelo de datos para ClassDetailInfo.
"""

from dataclasses import dataclass
from typing import Optional, List, Dict


@dataclass
class ClassDetailInfo:
    """Información detallada de una clase."""
    course_title: str
    crn: str
    subject: str
    course_number: str
    section: str
    associated_term: str
    levels: List[str]
    campus: str
    schedule_type: str
    instructional_method: str
    credits: str
    capacity: int
    actual_seats: int
    remaining_seats: int
    waitlist_seats: int
    waitlist_remaining: int
    restrictions_prohibited_programs: List[str]
    restrictions_prohibited_classifications: List[str]
    restrictions_required_levels: List[str]
    restrictions_required_campuses: List[str]
    prerequisites: List[Dict[str, str]]
    meeting_times: List[Dict[str, str]]
    instructor: Optional[Dict[str, str]] = None
    catalog_entry_url: Optional[str] = None

