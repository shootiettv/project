import sys
import os
from pathlib import Path

# Agregar el directorio actual al path para importar módulos relativos
current_dir = Path(__file__).parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

from scrapers.hb2504_scraper import HB2504Scraper
from scrapers.evaluations import EvaluationScraper
from processors.professor_profile import ProfessorProfile
from processors.professor_json_manager import add_professor_to_merged
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock
from typing import Dict, List, Optional

# Lock para sincronizar prints en paralelo
print_lock = Lock()


def safe_print(*args, **kwargs):
    """Función helper para prints thread-safe."""
    with print_lock:
        print(*args, **kwargs)


def process_evaluation(eval_item, index, total, professor_name: str = ""):
    """Procesa una evaluación individual y retorna el resultado con su índice."""
    safe_print(f"    [{professor_name}] Evaluación {index + 1}/{total}...", end=" ")
    start_eval = time.time()
    
    if eval_item.evaluation_link:
        try:
            eval_scraper = EvaluationScraper(eval_item.evaluation_link)
            eval_details = eval_scraper.get_evaluation_details()
            
            if eval_details:
                elapsed = time.time() - start_eval
                safe_print(f"✓ ({elapsed:.2f}s)")
                return (index, eval_details)
            else:
                safe_print(f"✗ (No se pudieron extraer los detalles)")
                return (index, None)
        except Exception as e:
            safe_print(f"✗ (Error: {str(e)})")
            return (index, None)
    else:
        safe_print(f"✗ (Sin link de evaluación)")
        return (index, None)


def fetch_professor_evaluations_from_profile(profile) -> Dict:
    """
    Procesa las evaluaciones de un profesor usando un objeto FacultyProfile.
    
    Args:
        profile: Objeto FacultyProfile con la información del profesor
    
    Returns:
        Dict con los resultados del procesamiento
    """
    start_total = time.time()
    result = {
        'success': False,
        'query': profile.name,
        'username': profile.username,
        'evaluations_count': 0,
        'time_profile': 0.0,
        'time_evaluations': 0.0,
        'time_total': 0.0,
        'error': None
    }
    
    try:
        safe_print(f"\n{'='*60}")
        safe_print(f"Procesando profesor: '{profile.name}' ({profile.username})")
        safe_print(f"{'='*60}")
        
        # Extraer Course Evaluations
        safe_print(f"  Extrayendo las primeras 10 evaluaciones del profesor...")
        start_profile = time.time()
        professor_profile = ProfessorProfile(profile.profile_url, course_name=None)
        evaluations = professor_profile.get_course_evaluations()
        result['time_profile'] = time.time() - start_profile
        safe_print(f"  Tiempo extracción links: {result['time_profile']:.2f}s")
        
        evaluations_details = []
        
        if evaluations:
            start_evaluations = time.time()
            safe_print(f"  Procesando {len(evaluations)} evaluaciones en paralelo...")
            
            # Procesar evaluaciones en paralelo
            with ThreadPoolExecutor(max_workers=5) as executor:
                future_to_eval = {
                    executor.submit(process_evaluation, eval_item, i, len(evaluations), profile.username): i
                    for i, eval_item in enumerate(evaluations)
                }
                
                results = [None] * len(evaluations)
                for future in as_completed(future_to_eval):
                    index, eval_details = future.result()
                    results[index] = eval_details
            
            evaluations_details = [r for r in results if r is not None]
            result['time_evaluations'] = time.time() - start_evaluations
            result['evaluations_count'] = len(evaluations_details)
            safe_print(f"  Tiempo total evaluaciones: {result['time_evaluations']:.2f}s")
        else:
            safe_print(f"  No se encontraron evaluaciones.")
        
        # Extraer información completa del perfil
        safe_print(f"\n  Extrayendo información completa del perfil...")
        start_profile_extraction = time.time()
        
        basic_info = professor_profile.get_basic_info()
        contact_info = professor_profile.get_contact_info()
        bio_data = professor_profile.get_bio_and_awards()
        education = professor_profile.get_education()
        courses = professor_profile.get_courses()
        scholarly_activity = professor_profile.get_scholarly_activity()
        grants = professor_profile.get_grants()
        
        profile_extraction_time = time.time() - start_profile_extraction
        safe_print(f"  Tiempo extracción perfil: {profile_extraction_time:.2f}s")
        
        # Agregar profesor directamente al merged JSON
        if basic_info or evaluations_details:
            safe_print(f"\n  Agregando profesor al merged JSON...")
            add_professor_to_merged(
                basic_info=basic_info,
                contact_info=contact_info,
                bio_data=bio_data,
                education=education,
                courses=courses,
                scholarly_activity=scholarly_activity,
                grants=grants,
                evaluations_details=evaluations_details,
                professor_id=profile.username
            )
            result['success'] = True
            result['time_total'] = time.time() - start_total
            safe_print(f"\n{'='*60}")
            safe_print(f"✓ COMPLETADO: {profile.username}")
            safe_print(f"  Evaluaciones encontradas: {result['evaluations_count']}")
            safe_print(f"  Tiempo total: {result['time_total']:.2f}s")
            safe_print(f"  Profesor agregado a: dataset/json/professorsProfile/merged_professors.json")
            safe_print(f"{'='*60}\n")
        else:
            result['error'] = "No hay datos para guardar"
            result['time_total'] = time.time() - start_total
            safe_print(f"  ✗ {result['error']}")
            safe_print(f"\n{'='*60}")
            safe_print(f"✗ COMPLETADO (sin datos): {profile.username}")
            safe_print(f"  Tiempo total: {result['time_total']:.2f}s")
            safe_print(f"{'='*60}\n")
        
    except Exception as e:
        result['error'] = str(e)
        result['time_total'] = time.time() - start_total
        safe_print(f"✗ Error procesando '{profile.name}': {str(e)}")
        safe_print(f"\n{'='*60}")
        safe_print(f"✗ ERROR: {profile.name}")
        safe_print(f"  Tiempo total: {result['time_total']:.2f}s")
        safe_print(f"  Error: {result['error']}")
        safe_print(f"{'='*60}\n")
    
    return result


def fetch_professor_evaluations(query: str) -> Dict:
    """
    Busca y procesa las evaluaciones de un profesor.
    
    Args:
        query: String para buscar el profesor (ej: "Gurijala")
    
    Returns:
        Dict con:
            - success: bool
            - query: str
            - username: str | None
            - evaluations_count: int
            - time_profile: float
            - time_evaluations: float
            - time_total: float
            - error: str | None
    """
    start_total = time.time()
    result = {
        'success': False,
        'query': query,
        'username': None,
        'evaluations_count': 0,
        'time_profile': 0.0,
        'time_evaluations': 0.0,
        'time_total': 0.0,
        'error': None
    }
    
    try:
        safe_print(f"\n{'='*60}")
        safe_print(f"Buscando profesor: '{query}'")
        safe_print(f"{'='*60}")
        
        scraper = HB2504Scraper()
        perfiles = scraper.search(name=query)
        
        if not perfiles:
            result['error'] = "No se encontraron profesores con ese nombre"
            result['time_total'] = time.time() - start_total
            safe_print(f"✗ {result['error']}")
            safe_print(f"\n{'='*60}")
            safe_print(f"✗ NO ENCONTRADO: {query}")
            safe_print(f"  Tiempo total: {result['time_total']:.2f}s")
            safe_print(f"{'='*60}\n")
            return result
        
        # Procesar el primer perfil encontrado
        profile = perfiles[0]
        result['username'] = profile.username
        safe_print(f"✓ Profesor encontrado: {profile.username}")
        
        # Extraer Course Evaluations
        safe_print(f"  Extrayendo las primeras 10 evaluaciones del profesor...")
        start_profile = time.time()
        professor_profile = ProfessorProfile(profile.profile_url, course_name=None)
        evaluations = professor_profile.get_course_evaluations()
        result['time_profile'] = time.time() - start_profile
        safe_print(f"  Tiempo extracción links: {result['time_profile']:.2f}s")
        
        evaluations_details = []
        
        if evaluations:
            start_evaluations = time.time()
            safe_print(f"  Procesando {len(evaluations)} evaluaciones en paralelo...")
            
            # Procesar evaluaciones en paralelo
            with ThreadPoolExecutor(max_workers=5) as executor:
                future_to_eval = {
                    executor.submit(process_evaluation, eval_item, i, len(evaluations), profile.username): i
                    for i, eval_item in enumerate(evaluations)
                }
                
                results = [None] * len(evaluations)
                for future in as_completed(future_to_eval):
                    index, eval_details = future.result()
                    results[index] = eval_details
            
            evaluations_details = [r for r in results if r is not None]
            result['time_evaluations'] = time.time() - start_evaluations
            result['evaluations_count'] = len(evaluations_details)
            safe_print(f"  Tiempo total evaluaciones: {result['time_evaluations']:.2f}s")
        else:
            safe_print(f"  No se encontraron evaluaciones.")
        
        # Extraer información completa del perfil
        safe_print(f"\n  Extrayendo información completa del perfil...")
        start_profile_extraction = time.time()
        
        basic_info = professor_profile.get_basic_info()
        contact_info = professor_profile.get_contact_info()
        bio_data = professor_profile.get_bio_and_awards()
        education = professor_profile.get_education()
        courses = professor_profile.get_courses()
        scholarly_activity = professor_profile.get_scholarly_activity()
        grants = professor_profile.get_grants()
        
        profile_extraction_time = time.time() - start_profile_extraction
        safe_print(f"  Tiempo extracción perfil: {profile_extraction_time:.2f}s")
        
        # Agregar profesor directamente al merged JSON
        if basic_info or evaluations_details:
            safe_print(f"\n  Agregando profesor al merged JSON...")
            add_professor_to_merged(
                basic_info=basic_info,
                contact_info=contact_info,
                bio_data=bio_data,
                education=education,
                courses=courses,
                scholarly_activity=scholarly_activity,
                grants=grants,
                evaluations_details=evaluations_details,
                professor_id=profile.username
            )
            result['success'] = True
            result['time_total'] = time.time() - start_total
            safe_print(f"\n{'='*60}")
            safe_print(f"✓ COMPLETADO: {profile.username}")
            safe_print(f"  Evaluaciones encontradas: {result['evaluations_count']}")
            safe_print(f"  Tiempo total: {result['time_total']:.2f}s")
            safe_print(f"  Profesor agregado a: dataset/json/professorsProfile/merged_professors.json")
            safe_print(f"{'='*60}\n")
        else:
            result['error'] = "No hay datos para guardar"
            result['time_total'] = time.time() - start_total
            safe_print(f"  ✗ {result['error']}")
            safe_print(f"\n{'='*60}")
            safe_print(f"✗ COMPLETADO (sin datos): {profile.username}")
            safe_print(f"  Tiempo total: {result['time_total']:.2f}s")
            safe_print(f"{'='*60}\n")
        
    except Exception as e:
        result['error'] = str(e)
        result['time_total'] = time.time() - start_total
        safe_print(f"✗ Error procesando '{query}': {str(e)}")
        safe_print(f"\n{'='*60}")
        safe_print(f"✗ ERROR: {query}")
        safe_print(f"  Tiempo total: {result['time_total']:.2f}s")
        safe_print(f"  Error: {result['error']}")
        safe_print(f"{'='*60}\n")
    
    return result


def fetch_all_professors(max_workers: int = 3, limit: Optional[int] = None, test_mode: bool = False) -> Dict:
    """
    Procesa profesores encontrados en hb2504.utep.edu.
    
    Args:
        max_workers: Número máximo de profesores a procesar simultáneamente
        limit: Número máximo de profesores a procesar (None = todos, para testing)
        test_mode: Si es True, solo procesa 'limit' profesores. Si es False, procesa todos.
    
    Returns:
        Dict con estadísticas del procesamiento
    """
    start_batch = time.time()
    safe_print(f"\n{'#'*60}")
    if test_mode and limit:
        safe_print(f"MODO TEST: PROCESANDO {limit} PROFESOR(ES) DE hb2504.utep.edu")
    else:
        safe_print(f"OBTENIENDO TODOS LOS PROFESORES DE hb2504.utep.edu")
    safe_print(f"{'#'*60}\n")
    
    # Obtener todos los profesores
    scraper = HB2504Scraper()
    safe_print("Cargando página principal y extrayendo todos los perfiles...")
    all_profiles = scraper.extract_all_profiles()
    total_found = len(all_profiles)
    safe_print(f"✓ Se encontraron {total_found} profesores en total\n")
    
    if not all_profiles:
        safe_print("✗ No se encontraron profesores")
        return {
            'total_professors': 0,
            'successful': 0,
            'failed': 0,
            'time_total': time.time() - start_batch,
            'time_average': 0.0,
            'results': []
        }
    
    # Limitar cantidad de profesores si está en modo test
    if test_mode and limit:
        all_profiles = all_profiles[:limit]
        safe_print(f"🔬 MODO TEST: Procesando solo {len(all_profiles)} profesor(es) de {total_found} encontrados\n")
    
    # Procesar profesores
    safe_print(f"{'#'*60}")
    safe_print(f"PROCESANDO {len(all_profiles)} PROFESOR(ES)")
    safe_print(f"{'#'*60}\n")
    
    results = []
    
    # Procesar profesores en paralelo
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_profile = {
            executor.submit(fetch_professor_evaluations_from_profile, profile): profile
            for profile in all_profiles
        }
        
        for future in as_completed(future_to_profile):
            result = future.result()
            results.append(result)
    
    # Calcular estadísticas
    time_total = time.time() - start_batch
    successful = sum(1 for r in results if r['success'])
    failed = len(results) - successful
    time_average = sum(r['time_total'] for r in results) / len(results) if results else 0.0
    
    # Mostrar resumen
    safe_print(f"\n{'#'*60}")
    safe_print(f"RESUMEN DEL BATCH")
    safe_print(f"{'#'*60}")
    safe_print(f"  Total de profesores procesados: {len(all_profiles)}")
    safe_print(f"  Exitosos: {successful}")
    safe_print(f"  Fallidos: {failed}")
    safe_print(f"  Tiempo total del batch: {time_total:.2f}s")
    safe_print(f"  Tiempo promedio por profesor: {time_average:.2f}s")
    safe_print(f"{'#'*60}\n")
    
    # Mostrar resumen por profesor (ordenado alfabéticamente)
    results_sorted = sorted(results, key=lambda x: x['query'])
    safe_print(f"\nDetalle por profesor (ordenado alfabéticamente):")
    safe_print(f"{'-'*60}")
    for result in results_sorted:
        status = "✓" if result['success'] else "✗"
        safe_print(f"  {status} {result['query']:30s} | "
                  f"Username: {result['username'] or 'N/A':15s} | "
                  f"Evaluaciones: {result['evaluations_count']:2d} | "
                  f"Tiempo: {result['time_total']:.2f}s")
        if result['error']:
            safe_print(f"    ⚠ Error: {result['error']}")
    safe_print(f"{'-'*60}\n")
    
    return {
        'total_professors': len(all_profiles),
        'successful': successful,
        'failed': failed,
        'time_total': time_total,
        'time_average': time_average,
        'results': results
    }


def fetch_multiple_professors(queries: List[str], max_workers: int = 3) -> Dict:
    """
    Procesa múltiples profesores en paralelo.
    
    Args:
        queries: Lista de strings para buscar profesores
        max_workers: Número máximo de profesores a procesar simultáneamente
    
    Returns:
        Dict con:
            - total_professors: int
            - successful: int
            - failed: int
            - time_total: float
            - time_average: float
            - results: List[Dict] (resultados individuales)
    """
    start_batch = time.time()
    safe_print(f"\n{'#'*60}")
    safe_print(f"PROCESANDO {len(queries)} PROFESOR(ES)")
    safe_print(f"{'#'*60}\n")
    
    results = []
    
    # Procesar profesores en paralelo
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_query = {
            executor.submit(fetch_professor_evaluations, query): query
            for query in queries
        }
        
        for future in as_completed(future_to_query):
            result = future.result()
            results.append(result)
    
    # Calcular estadísticas
    time_total = time.time() - start_batch
    successful = sum(1 for r in results if r['success'])
    failed = len(results) - successful
    time_average = sum(r['time_total'] for r in results) / len(results) if results else 0.0
    
    # Mostrar resumen
    safe_print(f"\n{'#'*60}")
    safe_print(f"RESUMEN DEL BATCH")
    safe_print(f"{'#'*60}")
    safe_print(f"  Total de profesores procesados: {len(queries)}")
    safe_print(f"  Exitosos: {successful}")
    safe_print(f"  Fallidos: {failed}")
    safe_print(f"  Tiempo total del batch: {time_total:.2f}s")
    safe_print(f"  Tiempo promedio por profesor: {time_average:.2f}s")
    safe_print(f"{'#'*60}\n")
    
    # Mostrar resumen por profesor (ordenado alfabéticamente)
    results_sorted = sorted(results, key=lambda x: x['query'])
    safe_print(f"\nDetalle por profesor (ordenado alfabéticamente):")
    safe_print(f"{'-'*60}")
    for result in results_sorted:
        status = "✓" if result['success'] else "✗"
        safe_print(f"  {status} {result['query']:20s} | "
                  f"Username: {result['username'] or 'N/A':15s} | "
                  f"Evaluaciones: {result['evaluations_count']:2d} | "
                  f"Tiempo: {result['time_total']:.2f}s")
        if result['error']:
            safe_print(f"    ⚠ Error: {result['error']}")
    safe_print(f"{'-'*60}\n")
    
    return {
        'total_professors': len(queries),
        'successful': successful,
        'failed': failed,
        'time_total': time_total,
        'time_average': time_average,
        'results': results
    }


# Lista de profesores para procesar
PROFESSOR_QUERIES = [
    "Abdallah",
    "Abed",
    "Acosta",
    "Aggarwal",
    "Akbar",
    "Aldouri",
    "Aldrete",
    "Ambhore",
    "Armanuzzaman",
    "Arrieta",
    "Artus",
    "Austen",
    "Avila",
]


if __name__ == "__main__":
    import sys
    
    # Modo 1: Quick Test - Procesar solo 10 profesores (--test10)
    if len(sys.argv) > 1 and sys.argv[1] == "--test10":
        safe_print(f"🔬 QUICK TEST: Procesando 10 profesores\n")
        fetch_all_professors(max_workers=5, limit=10, test_mode=True)
    
    # Modo 2: Modo TEST - Procesar solo X profesores (--test X)
    elif len(sys.argv) > 1 and sys.argv[1] == "--test":
        try:
            limit = int(sys.argv[2]) if len(sys.argv) > 2 else 5
            safe_print(f"🔬 MODO TEST activado: Procesando solo {limit} profesor(es)\n")
            fetch_all_professors(max_workers=5, limit=limit, test_mode=True)
        except ValueError:
            safe_print("✗ Error: El límite debe ser un número entero")
            safe_print("Uso: python main.py --test <número>")
    
    # Modo 3: Por defecto - Procesar TODOS los profesores del sitio (--all o sin argumentos)
    elif len(sys.argv) > 1 and sys.argv[1] == "--all":
        fetch_all_professors(max_workers=5, limit=None, test_mode=False)
    # Modo por defecto (sin argumentos): Procesar TODOS los profesores
    elif len(sys.argv) == 1:
        fetch_all_professors(max_workers=5, limit=None, test_mode=False)
    
    # Modo 4: Procesar múltiples profesores (todos los de PROFESSOR_QUERIES) (--batch)
    elif len(sys.argv) > 1 and sys.argv[1] == "--batch":
        # Procesar TODOS los profesores de la lista
        queries_to_process = PROFESSOR_QUERIES
        fetch_multiple_professors(queries_to_process, max_workers=5)
    
    # Modo 5: Procesar un solo profesor (si se pasa un nombre)
    else:
        # Si se pasa un nombre como argumento, procesar solo ese
        query = sys.argv[1]
        fetch_professor_evaluations(query)
