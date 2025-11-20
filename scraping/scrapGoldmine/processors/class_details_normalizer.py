#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Normalizador para detalles de clases extraídos desde páginas individuales.
"""

import re
from typing import Dict, Any, Optional, List
from urllib.parse import urlparse, parse_qs
import sys
from pathlib import Path

# Agregar el directorio padre al path para imports
current_dir = Path(__file__).parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

from utils.url_utils import extract_term_code


# Mapeos de configuración
LEVEL_MAPPING = {
    "Undergraduate": {"code": "UG", "label": "Undergraduate"},
    "Graduate": {"code": "GR", "label": "Graduate"},
    "Doctoral": {"code": "DOC", "label": "Doctoral"},
    "Post Baccalaureate": {"code": "PB", "label": "Post Baccalaureate"},
    "Special Professional": {"code": "SP", "label": "Special Professional"},
}

CAMPUS_MAPPING = {
    "Main Campus": {"code": "MAIN", "name": "Main Campus"},
}

SCHEDULE_TYPE_MAPPING = {
    "LECT": {"code": "LECT", "label": "Lecture"},
    "LAB": {"code": "LAB", "label": "Laboratory"},
    "SEM": {"code": "SEM", "label": "Seminar"},
    "WKS": {"code": "WKS", "label": "Workshop"},
    "IND": {"code": "IND", "label": "Independent Study"},
    "FLD": {"code": "FLD", "label": "Field Experience"},
    "PRC": {"code": "PRC", "label": "Practicum"},
    "THS": {"code": "THS", "label": "Thesis"},
    "DIS": {"code": "DIS", "label": "Dissertation"},
}


def parse_credits(credits_raw: Any) -> Optional[float]:
    """
    Convierte credits de string "3.000" a float 3.0.
    
    Args:
        credits_raw: Valor crudo de credits (puede ser string o float)
    
    Returns:
        Float con los créditos o None si no se puede parsear
    """
    if credits_raw is None:
        return None
    
    if isinstance(credits_raw, (int, float)):
        return float(credits_raw)
    
    if isinstance(credits_raw, str):
        credits_str = credits_raw.strip()
        if not credits_str or credits_str == "":
            return None
        
        try:
            return float(credits_str)
        except ValueError:
            return None
    
    return None


def normalize_term(associated_term: str, catalog_entry_url: str) -> Dict[str, Optional[str]]:
    """
    Normaliza el término en un objeto con code y label.
    
    Args:
        associated_term: Label del término (ej: "Spring 2026")
        catalog_entry_url: URL para extraer el código de término
    
    Returns:
        Dict con "code" y "label"
    """
    term_code = extract_term_code(catalog_entry_url)
    term_label = associated_term.strip() if associated_term else None
    
    return {
        "code": term_code,
        "label": term_label if term_label else None
    }


def normalize_levels(levels_raw: List[str]) -> List[Dict[str, str]]:
    """
    Normaliza levels de strings a objetos con code y label.
    
    Args:
        levels_raw: Lista de strings con los niveles (ej: ["Undergraduate"])
    
    Returns:
        Lista de dicts con "code" y "label"
    """
    if not levels_raw or not isinstance(levels_raw, list):
        return []
    
    normalized = []
    for level_str in levels_raw:
        if not isinstance(level_str, str):
            continue
        
        level_str = level_str.strip()
        if not level_str:
            continue
        
        # Buscar en el mapeo
        if level_str in LEVEL_MAPPING:
            normalized.append(LEVEL_MAPPING[level_str].copy())
        else:
            code = level_str[:3].upper() if len(level_str) >= 3 else level_str.upper()
            normalized.append({"code": code, "label": level_str})
    
    return normalized


def normalize_campus(campus_raw: str) -> Dict[str, Optional[str]]:
    """
    Normaliza campus de string a objeto con code y name.
    
    Args:
        campus_raw: String con el campus (ej: "Main Campus")
    
    Returns:
        Dict con "code" y "name"
    """
    if not campus_raw or campus_raw.strip() == "":
        return {"code": None, "name": None}
    
    campus_str = campus_raw.strip()
    
    # Buscar en el mapeo
    if campus_str in CAMPUS_MAPPING:
        return CAMPUS_MAPPING[campus_str].copy()
    
    # Si no está en el mapeo, generar uno básico
    code = campus_str.upper().replace(" ", "_")
    return {"code": code, "name": campus_str}


def normalize_schedule_type(schedule_type_raw: str) -> Optional[Dict[str, str]]:
    """
    Normaliza schedule_type de string a objeto con code y label.
    
    Args:
        schedule_type_raw: String con el schedule type (ej: "LECT" o "")
    
    Returns:
        Dict con "code" y "label" o None si está vacío
    """
    if not schedule_type_raw or schedule_type_raw.strip() == "":
        return None
    
    schedule_type_str = schedule_type_raw.strip().upper()
    
    # Buscar en el mapeo
    if schedule_type_str in SCHEDULE_TYPE_MAPPING:
        return SCHEDULE_TYPE_MAPPING[schedule_type_str].copy()
    
    # Si no está en el mapeo, usar el código como label también
    return {"code": schedule_type_str, "label": schedule_type_str}


def parse_instructional_method(instructional_method_raw: str) -> Dict[str, Any]:
    """
    Parsea instructional_method y determina mode y online_percentage.
    
    Ejemplo: "49%" -> {"mode": "Hybrid", "online_percentage": 49}
    Ejemplo: "" -> {"mode": None, "online_percentage": None}
    
    Args:
        instructional_method_raw: String con el método instructivo
    
    Returns:
        Dict con "mode" y "online_percentage"
    """
    if not instructional_method_raw or instructional_method_raw.strip() == "":
        return {"mode": None, "online_percentage": None}
    
    method_str = instructional_method_raw.strip()
    
    # Buscar porcentaje (ej: "49%" o "49 %")
    percentage_match = re.search(r'(\d+)\s*%', method_str)
    
    if percentage_match:
        percentage = int(percentage_match.group(1))
        
        # Determinar mode basado en el porcentaje
        if percentage == 0:
            mode = "Face to Face"
        elif percentage == 100:
            mode = "Online"
        elif 1 <= percentage <= 99:
            mode = "Hybrid"
        else:
            mode = None
        
        return {"mode": mode, "online_percentage": percentage}
    
    # Si no hay porcentaje, intentar detectar por texto
    method_lower = method_str.lower()
    if "online" in method_lower:
        return {"mode": "Online", "online_percentage": 100}
    elif "hybrid" in method_lower:
        return {"mode": "Hybrid", "online_percentage": None}
    elif "face to face" in method_lower or "face-to-face" in method_lower:
        return {"mode": "Face to Face", "online_percentage": 0}
    
    # Si no se puede determinar, devolver null
    return {"mode": None, "online_percentage": None}


def deduplicate_programs(programs_raw: List[str]) -> List[str]:
    """
    Deduplica una lista de programas.
    
    Args:
        programs_raw: Lista de strings con programas (puede tener duplicados)
    
    Returns:
        Lista de strings sin duplicados, manteniendo el orden
    """
    if not programs_raw or not isinstance(programs_raw, list):
        return []
    
    seen = set()
    deduplicated = []
    
    for program in programs_raw:
        if not isinstance(program, str):
            continue
        
        program_str = program.strip()
        if not program_str:
            continue
        
        # Normalizar para comparación (case-insensitive)
        normalized = program_str.lower()
        if normalized not in seen:
            seen.add(normalized)
            deduplicated.append(program_str)
    
    return deduplicated


def normalize_program(program_name: str) -> Dict[str, Optional[str]]:
    """
    Normaliza un programa en un objeto con code y name.
    
    Args:
        program_name: String con el nombre del programa
    
    Returns:
        Dict con "code" y "name"
    """
    if not program_name or program_name.strip() == "":
        return {"code": None, "name": None}
    
    program_str = program_name.strip()
    
    # Si es un código corto (menos de 10 caracteres y todo mayúsculas), usarlo como código
    if len(program_str) <= 10 and program_str.isupper() and program_str.isalnum():
        return {"code": program_str, "name": program_str}
    
    # Por ahora, devolver null para código si no se puede inferir
    return {"code": None, "name": program_str}


def normalize_prohibited_programs(programs_raw: List[str]) -> List[Dict[str, Optional[str]]]:
    """
    Normaliza y deduplica prohibited_programs.
    
    Args:
        programs_raw: Lista de strings con programas prohibidos (puede tener duplicados)
    
    Returns:
        Lista de dicts con "code" y "name", sin duplicados
    """
    # Primero deduplicar
    deduplicated = deduplicate_programs(programs_raw)
    
    # Normalizar cada programa
    normalized = []
    for program in deduplicated:
        normalized_program = normalize_program(program)
        normalized.append(normalized_program)
    
    return normalized


def normalize_required_levels(levels_raw: List[str]) -> List[Dict[str, str]]:
    """
    Normaliza restrictions_required_levels usando el mismo mapeo que levels.
    
    Args:
        levels_raw: Lista de strings con los niveles requeridos
    
    Returns:
        Lista de dicts con "code" y "label"
    """
    return normalize_levels(levels_raw)


def normalize_required_campuses(campuses_raw: List[str]) -> List[Dict[str, str]]:
    """
    Normaliza restrictions_required_campuses.
    
    Args:
        campuses_raw: Lista de strings con los campus requeridos
    
    Returns:
        Lista de dicts con "code" y "name"
    """
    if not campuses_raw or not isinstance(campuses_raw, list):
        return []
    
    normalized = []
    for campus_str in campuses_raw:
        if not isinstance(campus_str, str):
            continue
        
        campus_normalized = normalize_campus(campus_str)
        normalized.append(campus_normalized)
    
    return normalized


def normalize_prohibited_classifications(classifications_raw: List[str]) -> List[Dict[str, Optional[str]]]:
    """
    Normaliza prohibited_classifications (similar a programs).
    
    Args:
        classifications_raw: Lista de strings con clasificaciones prohibidas
    
    Returns:
        Lista de dicts con "code" y "name"
    """
    if not classifications_raw or not isinstance(classifications_raw, list):
        return []
    
    deduplicated = deduplicate_programs(classifications_raw)
    normalized = []
    
    for classification in deduplicated:
        normalized_class = normalize_program(classification)
        normalized.append(normalized_class)
    
    return normalized


def normalize_restrictions(raw_course: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normaliza todas las restricciones en un objeto restrictions.
    
    Args:
        raw_course: Dict con los datos crudos del curso
    
    Returns:
        Dict con todas las restricciones normalizadas
    """
    prohibited_programs_raw = raw_course.get("restrictions_prohibited_programs", [])
    prohibited_classifications_raw = raw_course.get("restrictions_prohibited_classifications", [])
    required_levels_raw = raw_course.get("restrictions_required_levels", [])
    required_campuses_raw = raw_course.get("restrictions_required_campuses", [])
    
    return {
        "prohibited_programs": normalize_prohibited_programs(prohibited_programs_raw),
        "prohibited_classifications": normalize_prohibited_classifications(prohibited_classifications_raw),
        "required_levels": normalize_required_levels(required_levels_raw),
        "required_campuses": normalize_required_campuses(required_campuses_raw)
    }


def normalize_prerequisites(prerequisites_raw: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Normaliza prerequisites, convirtiendo minimum_grade vacío a null.
    
    Args:
        prerequisites_raw: Lista de dicts con los prerequisitos
    
    Returns:
        Lista de dicts con prerequisitos normalizados
    """
    if not prerequisites_raw or not isinstance(prerequisites_raw, list):
        return []
    
    normalized = []
    
    for prereq in prerequisites_raw:
        if not isinstance(prereq, dict):
            continue
        
        normalized_prereq = {
            "subject": prereq.get("subject") or None,
            "course_number": prereq.get("course_number") or None,
            "minimum_grade": None if (not prereq.get("minimum_grade") or prereq.get("minimum_grade") == "") else prereq.get("minimum_grade"),
            "concurrent_allowed": prereq.get("concurrent_allowed", False)
        }
        
        normalized.append(normalized_prereq)
    
    return normalized


def normalize_enrollment(raw_course: Dict[str, Any]) -> Dict[str, int]:
    """
    Normaliza datos de enrollment en un objeto enrollment.
    
    Args:
        raw_course: Dict con los datos crudos del curso
    
    Returns:
        Dict con enrollment normalizado
    """
    return {
        "capacity": raw_course.get("capacity", 0),
        "actual": raw_course.get("actual_seats", 0),
        "remaining": raw_course.get("remaining_seats", 0),
        "waitlist_capacity": raw_course.get("waitlist_seats", 0),
        "waitlist_remaining": raw_course.get("waitlist_remaining", 0)
    }


def transform_course(crn: str, course_raw: Dict[str, Any]) -> Dict[str, Any]:
    """
    Transforma un curso de la estructura cruda a la estructura limpia normalizada.
    
    Args:
        crn: CRN del curso (usado como key)
        course_raw: Dict con los datos crudos del curso
    
    Returns:
        Dict con el curso en estructura limpia normalizada
    """
    # Credits: convertir de string "3.000" a float 3.0
    credits = parse_credits(course_raw.get("credits"))
    
    # Term: extraer código de catalog_entry_url y usar associated_term como label
    term = normalize_term(
        course_raw.get("associated_term", ""),
        course_raw.get("catalog_entry_url", "")
    )
    
    # Levels: convertir de strings a objetos con code y label
    levels = normalize_levels(course_raw.get("levels", []))
    
    # Campus: convertir de string a objeto con code y name
    campus = normalize_campus(course_raw.get("campus", ""))
    
    # Schedule type: convertir de string a objeto con code y label (o null si está vacío)
    schedule_type = normalize_schedule_type(course_raw.get("schedule_type", ""))
    
    # Instructional method: parsear porcentaje y determinar mode
    instructional_method_raw = course_raw.get("instructional_method", "")
    instructional_method = parse_instructional_method(instructional_method_raw)
    
    # Enrollment: agrupar todos los campos de enrollment
    enrollment = normalize_enrollment(course_raw)
    
    # Restrictions: normalizar todas las restricciones
    restrictions = normalize_restrictions(course_raw)
    
    # Prerequisites: normalizar y convertir minimum_grade vacío a null
    prerequisites = normalize_prerequisites(course_raw.get("prerequisites", []))
    
    # Meeting times: mantener como está (generalmente vacío)
    meeting_times = course_raw.get("meeting_times", [])
    if not isinstance(meeting_times, list):
        meeting_times = []
    
    # Instructor: extraer instructor_id si está disponible, sino null
    instructor_raw = course_raw.get("instructor")
    instructor_id = None
    if instructor_raw and isinstance(instructor_raw, dict):
        profile_url = instructor_raw.get("profile_url", "")
        if profile_url:
            try:
                parsed = urlparse(profile_url)
                params = parse_qs(parsed.query)
                if 'ID' in params:
                    instructor_id = params['ID'][0]
            except Exception:
                pass
    
    # Construir curso limpio
    course_clean = {
        "crn": crn,
        "course_title": course_raw.get("course_title") or None,
        "subject": course_raw.get("subject") or None,
        "course_number": course_raw.get("course_number") or None,
        "section": course_raw.get("section") or None,
        "term": term,
        "levels": levels,
        "campus": campus,
        "schedule_type": schedule_type,
        "instructional_method": instructional_method,
        "credits": credits,
        "enrollment": enrollment,
        "restrictions": restrictions,
        "prerequisites": prerequisites,
        "meeting_times": meeting_times,
        "instructor_id": instructor_id,
        "catalog_entry_url": course_raw.get("catalog_entry_url") or None
    }
    
    return course_clean

