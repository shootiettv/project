"""
Procesadores y lógica de negocio del pipeline
"""
from .professor_profile import ProfessorProfile, CourseEvaluation
from .professor_json_manager import (
    add_professor_to_merged,
    load_merged_json,
    get_merged_json_path
)

__all__ = [
    'ProfessorProfile', 'CourseEvaluation',
    'add_professor_to_merged',
    'load_merged_json', 'get_merged_json_path'
]

