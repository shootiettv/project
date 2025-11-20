"""
Procesadores y normalizadores de datos.
"""

from .course_normalizer import index_courses_by_crn, transform_course
from .class_details_normalizer import transform_course as transform_class_detail

__all__ = [
    'index_courses_by_crn',
    'transform_course',
    'transform_class_detail'
]

