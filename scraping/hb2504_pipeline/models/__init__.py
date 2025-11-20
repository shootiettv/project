"""
Modelos de datos y estructuras para el pipeline
"""
from .faculty_profile import FacultyProfile
from .professor_profile_extractor import (
    ProfessorBasicInfo, ContactInfo, AwardHonor, Education,
    Course, Publication, Presentation, ProfessorProfileExtractor
)

__all__ = [
    'FacultyProfile',
    'ProfessorBasicInfo', 'ContactInfo', 'AwardHonor', 'Education',
    'Course', 'Publication', 'Presentation', 'ProfessorProfileExtractor'
]

