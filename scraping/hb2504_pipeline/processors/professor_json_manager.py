"""
Gestión de conversión y almacenamiento de datos de profesores a JSON.

Este módulo se encarga de:
- Convertir datos estructurados de profesores a formato JSON
- Agregar profesores directamente al archivo merged_professors.json
"""
from typing import Dict, List, Any, Optional
import json
from pathlib import Path
from threading import Lock
import sys

# Agregar el directorio raíz del pipeline al path
pipeline_root = Path(__file__).parent.parent
if str(pipeline_root) not in sys.path:
    sys.path.insert(0, str(pipeline_root))

from models.professor_profile_extractor import (
    ProfessorBasicInfo, ContactInfo, AwardHonor, Education, 
    Course, Publication, Presentation
)
from scrapers.evaluations import EvaluationDetails

# Lock para sincronizar escrituras al archivo merged cuando se procesa en paralelo
_merged_file_lock = Lock()


# ============================================================================
# FUNCIONES DE CONVERSIÓN DE DATOS A JSON
# ============================================================================

def convert_basic_info_to_dict(basic_info: Optional[ProfessorBasicInfo]) -> Dict[str, Any]:
    """Convierte ProfessorBasicInfo a diccionario."""
    if not basic_info:
        return {}
    return {
        'name': basic_info.name,
        'photo_url': basic_info.photo_url,
        'position': basic_info.position,
        'department': basic_info.department,
        'cv_url': basic_info.cv_url
    }


def convert_contact_info_to_dict(contact_info: ContactInfo) -> Dict[str, Any]:
    """Convierte ContactInfo a diccionario."""
    result = {}
    if contact_info.office_building:
        result['office_building'] = contact_info.office_building
    if contact_info.office_room:
        result['office_room'] = contact_info.office_room
    if contact_info.phone:
        result['phone'] = contact_info.phone
    if contact_info.email:
        result['email'] = contact_info.email
    return result


def convert_awards_to_list(awards: List[AwardHonor]) -> List[Dict[str, Any]]:
    """Convierte lista de AwardHonor a lista de diccionarios."""
    result = []
    for award in awards:
        award_dict = {'title': award.title}
        if award.date:
            award_dict['date'] = award.date
        if award.organization:
            award_dict['organization'] = award.organization
        result.append(award_dict)
    return result


def convert_education_to_list(education: List[Education]) -> List[Dict[str, Any]]:
    """Convierte lista de Education a lista de diccionarios."""
    result = []
    for edu in education:
        edu_dict = {
            'degree': edu.degree,
            'field': edu.field,
            'institution': edu.institution
        }
        if edu.year:
            edu_dict['year'] = edu.year
        result.append(edu_dict)
    return result


def convert_courses_to_dict(courses: Dict) -> Dict[str, Any]:
    """Convierte cursos a diccionario."""
    current_future = []
    for course in courses.get('current_future', []):
        course_dict = {
            'term': course.term,
            'course': course.course,
            'section': course.section
        }
        if course.syllabus_url:
            course_dict['syllabus_url'] = course.syllabus_url
        current_future.append(course_dict)
    
    past = []
    for course in courses.get('past', []):
        course_dict = {
            'term': course.term,
            'course': course.course,
            'section': course.section
        }
        if course.syllabus_url:
            course_dict['syllabus_url'] = course.syllabus_url
        past.append(course_dict)
    
    return {
        'current_future': current_future,
        'past': past
    }


def convert_scholarly_activity_to_dict(activity: Dict) -> Dict[str, Any]:
    """Convierte actividad académica a diccionario."""
    publications = [{'title': pub.title} for pub in activity.get('publications', [])]
    presentations = [{'title': pres.title} for pres in activity.get('presentations', [])]
    return {
        'publications': publications,
        'presentations': presentations
    }


def parse_percentage(percentage_str: str) -> Optional[float]:
    """Convierte un string de porcentaje a float.
    
    Ejemplo: "30.0%" -> 30.0
    """
    if not percentage_str:
        return None
    
    # Remover el símbolo % y espacios
    cleaned = percentage_str.replace('%', '').strip()
    try:
        return float(cleaned)
    except (ValueError, AttributeError):
        return None


def parse_average(avg_str: str) -> Optional[float]:
    """Convierte un string de promedio a float.
    
    Ejemplo: "3.78" -> 3.78
    """
    if not avg_str:
        return None
    
    try:
        return float(avg_str.strip())
    except (ValueError, AttributeError):
        return None


def parse_response_count(response_count_str: str) -> int:
    """Convierte un string de response count a int.
    
    Ejemplo: "10" -> 10
    """
    if not response_count_str:
        return 0
    
    try:
        return int(response_count_str.strip())
    except (ValueError, AttributeError):
        return 0


def convert_rating_to_json(rating) -> Dict[str, Any]:
    """Convierte un RatingBreakdown a el formato JSON requerido."""
    rating_dict = {}
    
    # Convertir porcentajes (solo si tienen valor)
    excellent_pct = parse_percentage(rating.excellent)
    if excellent_pct is not None:
        rating_dict['excellent_pct'] = excellent_pct
    
    good_pct = parse_percentage(rating.good)
    if good_pct is not None:
        rating_dict['good_pct'] = good_pct
    
    satisfactory_pct = parse_percentage(rating.satisfactory)
    if satisfactory_pct is not None:
        rating_dict['satisfactory_pct'] = satisfactory_pct
    
    poor_pct = parse_percentage(rating.poor)
    if poor_pct is not None:
        rating_dict['poor_pct'] = poor_pct
    
    # Convertir average (siempre incluirlo si está disponible)
    average = parse_average(rating.avg)
    if average is not None:
        rating_dict['average'] = average
    
    return rating_dict


def convert_evaluation_to_json(eval_details: EvaluationDetails) -> Dict[str, Any]:
    """Convierte EvaluationDetails a formato JSON."""
    evaluation = {
        'term': eval_details.term.strip(),
        'response_count': parse_response_count(eval_details.response_count),
        'instructor_rating': convert_rating_to_json(eval_details.instructor_rating)
    }
    
    # Agregar course_rating si está disponible
    if eval_details.course_rating:
        evaluation['course_rating'] = convert_rating_to_json(eval_details.course_rating)
    
    return evaluation


def create_complete_profile_json(
    basic_info: Optional[ProfessorBasicInfo],
    contact_info: ContactInfo,
    bio_data: Dict,
    education: List[Education],
    courses: Dict,
    scholarly_activity: Dict,
    grants: List[Dict],
    evaluations_details: List[EvaluationDetails],
    professor_id: Optional[str] = None
) -> Dict[str, Any]:
    """Crea el objeto JSON completo con toda la información del profesor."""
    
    json_data = {}
    
    # ID del profesor
    if professor_id:
        json_data['professor_id'] = professor_id
    
    # Información básica
    json_data['professor_info'] = convert_basic_info_to_dict(basic_info)
    
    # Información de contacto
    json_data['contact_info'] = convert_contact_info_to_dict(contact_info)
    
    # Biografía y premios
    json_data['bio'] = {
        'description': bio_data.get('description', ''),
        'awards_honors': convert_awards_to_list(bio_data.get('awards_honors', []))
    }
    
    # Educación
    json_data['education'] = convert_education_to_list(education)
    
    # Actividad académica
    json_data['scholarly_activity'] = convert_scholarly_activity_to_dict(scholarly_activity)
    
    # Grants
    json_data['grants'] = grants
    
    # Cursos
    json_data['courses'] = convert_courses_to_dict(courses)
    
    # Evaluaciones
    evaluations_history = []
    for eval_detail in evaluations_details:
        if eval_detail:
            evaluations_history.append(convert_evaluation_to_json(eval_detail))
    json_data['evaluations_history'] = evaluations_history
    
    return json_data


# ============================================================================
# FUNCIONES PARA GESTIÓN DEL ARCHIVO MERGED JSON
# ============================================================================

def load_json_file(file_path: Path) -> Dict[str, Any]:
    """
    Carga un archivo JSON y retorna su contenido.
    
    Args:
        file_path: Ruta al archivo JSON
    
    Returns:
        Diccionario con el contenido del JSON
    
    Raises:
        Exception: Si hay error al leer o parsear el JSON
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        raise Exception(f"Error al parsear JSON en {file_path.name}: {str(e)}")
    except Exception as e:
        raise Exception(f"Error al leer {file_path.name}: {str(e)}")


def get_merged_json_path() -> Path:
    """
    Retorna la ruta del archivo merged_professors.json.
    
    Returns:
        Path al archivo merged_professors.json
    """
    project_root = Path(__file__).parent.parent
    return project_root / "dataset" / "json" / "professorsProfile" / "merged_professors.json"


def load_merged_json() -> Dict[str, Any]:
    """
    Carga el archivo merged_professors.json si existe, o retorna un diccionario vacío.
    
    Returns:
        Diccionario con el formato {"professors": {...}} o {"professors": {}} si no existe
    """
    merged_path = get_merged_json_path()
    
    if merged_path.exists():
        try:
            return load_json_file(merged_path)
        except Exception as e:
            print(f"⚠ Error al cargar merged_professors.json: {str(e)}")
            return {"professors": {}}
    else:
        return {"professors": {}}


def add_professor_to_merged(
    basic_info: Optional[ProfessorBasicInfo],
    contact_info: ContactInfo,
    bio_data: Dict,
    education: List[Education],
    courses: Dict,
    scholarly_activity: Dict,
    grants: List[Dict],
    evaluations_details: List[EvaluationDetails],
    professor_id: str
) -> None:
    """
    Agrega un profesor directamente al archivo merged_professors.json.
    Si el archivo no existe, lo crea. Si el profesor ya existe, lo actualiza.
    Esta función es thread-safe para procesamiento en paralelo.
    
    Args:
        basic_info: Información básica del profesor
        contact_info: Información de contacto
        bio_data: Biografía y premios
        education: Lista de educación
        courses: Cursos actuales y pasados
        scholarly_activity: Publicaciones y presentaciones
        grants: Lista de grants
        evaluations_details: Lista de evaluaciones
        professor_id: ID del profesor (username)
    """
    # Crear el JSON del profesor antes de adquirir el lock
    professor_json = create_complete_profile_json(
        basic_info, contact_info, bio_data, education,
        courses, scholarly_activity, grants, evaluations_details, professor_id
    )
    
    # Usar lock para sincronizar acceso al archivo cuando se procesa en paralelo
    with _merged_file_lock:
        # Obtener la ruta del archivo
        merged_path = get_merged_json_path()
        
        # Verificar si el archivo existe
        file_exists = merged_path.exists()
        
        # Cargar el archivo merged existente (o crear uno nuevo si no existe)
        merged_data = load_merged_json()
        
        # Agregar o actualizar el profesor en el diccionario
        if "professors" not in merged_data:
            merged_data["professors"] = {}
        
        # Verificar si el profesor ya existe
        professor_exists = professor_id in merged_data["professors"]
        if professor_exists:
            print(f"  ⚠ Profesor {professor_id} ya existe, actualizando...")
        
        merged_data["professors"][professor_id] = professor_json
        
        # Crear el directorio si no existe
        merged_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            # Crear o actualizar el archivo
            with open(merged_path, 'w', encoding='utf-8', newline='\n') as f:
                json.dump(merged_data, f, indent=2, ensure_ascii=False)
            
            if not file_exists:
                print(f"  ✓ Archivo merged_professors.json creado")
            
            print(f"  ✓ Profesor {professor_id} agregado al merged JSON")
            print(f"    Total de profesores en merged: {len(merged_data['professors'])}")
        except Exception as e:
            raise Exception(f"Error al guardar profesor en merged JSON: {str(e)}")

