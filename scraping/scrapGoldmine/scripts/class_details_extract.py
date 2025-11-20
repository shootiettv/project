#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script principal para extraer detalles de clases desde páginas individuales.
Genera class_details_clean.json en dataset/json/listClasses/
"""

import os
import sys
import requests
from pathlib import Path
from typing import Dict, Optional
from dataclasses import asdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock

# Agregar el directorio padre al path para imports
current_dir = Path(__file__).parent.parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

from scrapers.class_details_scraper import scrape_class_detail
from processors.class_details_normalizer import transform_course
from utils.file_manager import save_json, load_json

# Lock para el contador de progreso thread-safe
progress_lock = Lock()


def process_single_course(crn: str, course_info: Dict, base_url: str, 
                          processed_crns: set, session: requests.Session) -> tuple:
    """
    Procesa un solo curso y retorna los datos normalizados.
    
    Args:
        crn: Course Reference Number
        course_info: Información del curso
        base_url: URL base
        processed_crns: Set de CRNs ya procesados (para evitar duplicados)
        session: Session de requests para reutilizar conexiones
    
    Returns:
        Tupla (crn, success: bool, skipped: bool, course_clean: Dict, error: str)
    """
    # Verificar si ya fue procesado
    if crn in processed_crns:
        return (crn, False, True, None, None)
    
    # Obtener detail_url
    detail_url = course_info.get('detail_url', '')
    if not detail_url:
        return (crn, False, False, None, "No tiene detail_url")
    
    # Construir URL completa
    if detail_url.startswith('http'):
        full_url = detail_url
    elif detail_url.startswith('/'):
        full_url = base_url + detail_url
    else:
        full_url = base_url + '/' + detail_url
    
    # Hacer scraping (sin guardar archivo individual)
    try:
        class_detail = scrape_class_detail(full_url, session=session, verbose=False)
        
        if class_detail:
            # Convertir ClassDetailInfo a dict
            course_raw = asdict(class_detail)
            
            # Aplicar transformación/normalización directamente
            course_clean = transform_course(crn, course_raw)
            
            return (crn, True, False, course_clean, None)
        else:
            return (crn, False, False, None, "No se pudo extraer información")
    except Exception as e:
        return (crn, False, False, None, str(e))


def main(limit: Optional[int] = None, test_mode: bool = False):
    """
    Función principal optimizada con procesamiento paralelo y normalización directa.
    
    Args:
        limit: Número máximo de cursos a procesar (None = todos)
        test_mode: Si es True, solo procesa 'limit' cursos. Si es False, procesa todos.
    """
    base_dir = Path(__file__).parent.parent
    base_url = "https://www.goldmine.utep.edu"
    list_classes_file = base_dir / "dataset" / "json" / "listClasses" / "courses_clean.json"
    output_file = base_dir / "dataset" / "json" / "listClasses" / "class_details_clean.json"
    max_workers = 10  # Número de hilos paralelos
    
    print("=" * 70)
    print("SCRAPING Y NORMALIZACIÓN DE DETALLES DE CLASE - GOLDMINE")
    print("=" * 70)
    print()
    
    # Cargar courses_clean.json
    try:
        list_classes_data = load_json(str(list_classes_file))
    except Exception as e:
        print(f"❌ Error al cargar {list_classes_file}: {e}")
        return
    
    if 'courses' not in list_classes_data:
        print(f"❌ El archivo {list_classes_file} no contiene la clave 'courses'")
        return
    
    courses = list_classes_data['courses']
    
    # Verificar si ya existe el archivo final para cargar CRNs procesados
    processed_crns = set()
    existing_data = {}
    
    try:
        existing_data = load_json(str(output_file))
        if 'courses' in existing_data:
            processed_crns = set(existing_data['courses'].keys())
            print(f"📂 Archivo existente encontrado: {len(processed_crns):,} cursos ya procesados")
    except FileNotFoundError:
        print("📂 Creando nuevo archivo...")
    except Exception as e:
        print(f"⚠️  Error al leer archivo existente: {e}, continuando desde cero...")
    
    # Filtrar cursos que tienen detail_url y no están procesados
    courses_to_process = []
    skipped_no_url = 0
    for crn, course_info in courses.items():
        if crn not in processed_crns:
            if course_info.get('detail_url'):
                courses_to_process.append((crn, course_info))
            else:
                skipped_no_url += 1
    
    # Aplicar límite si está en modo test
    total_available = len(courses_to_process)
    if test_mode and limit:
        courses_to_process = courses_to_process[:limit]
        print(f"🔬 MODO TEST: Procesando solo {len(courses_to_process)} curso(s) de {total_available:,} disponibles")
    elif limit and not test_mode:
        courses_to_process = courses_to_process[:limit]
        print(f"⚠️  Límite aplicado: Procesando {len(courses_to_process)} curso(s) de {total_available:,} disponibles")
    
    total_courses = len(courses_to_process)
    
    print(f"📚 Total de cursos a procesar: {total_courses:,}")
    if skipped_no_url > 0:
        print(f"⚠️  Cursos sin detail_url omitidos: {skipped_no_url:,}")
    print(f"💾 Archivo de salida: {output_file}")
    print(f"⚡ Usando {max_workers} trabajadores paralelos")
    print()
    
    if total_courses == 0:
        print("✅ Todos los cursos ya están procesados!")
        return
    
    # Inicializar estructura de datos (usar datos existentes si hay)
    merged_data = existing_data if existing_data else {"courses": {}}
    
    # Contadores thread-safe
    processed = 0
    errors = 0
    
    print("🔄 Iniciando scraping y normalización...")
    print()
    
    # Crear session de requests para reutilizar conexiones
    session = requests.Session()
    
    try:
        # Procesar en paralelo
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Enviar todas las tareas
            future_to_crn = {
                executor.submit(
                    process_single_course, 
                    crn, 
                    course_info, 
                    base_url, 
                    processed_crns,
                    session
                ): crn
                for crn, course_info in courses_to_process
            }
            
            # Procesar resultados conforme se completan
            for future in as_completed(future_to_crn):
                crn = future_to_crn[future]
                try:
                    crn_result, success, was_skipped, course_clean, error = future.result()
                    
                    with progress_lock:
                        if was_skipped:
                            pass
                        elif success and course_clean:
                            merged_data["courses"][crn] = course_clean
                            processed += 1
                            
                            # Guardar periódicamente (cada 50 cursos)
                            if processed % 50 == 0:
                                temp_file = str(output_file) + ".tmp"
                                save_json(merged_data, temp_file)
                                print(f"   💾 Guardado temporal ({processed:,} nuevos cursos)...")
                        else:
                            errors += 1
                            if errors <= 20:
                                print(f"   ❌ CRN {crn}: {error}")
                            elif errors == 21:
                                print(f"   ❌ (ocultando errores adicionales...)")
                
                except Exception as e:
                    with progress_lock:
                        errors += 1
                        if errors <= 20:
                            print(f"   ❌ CRN {crn}: Excepción - {str(e)}")
                        elif errors == 21:
                            print(f"   ❌ (ocultando errores adicionales...)")
    
    finally:
        session.close()
    
    # Guardar archivo final
    print()
    print("💾 Guardando archivo final...")
    
    # Guardar en archivo temporal primero, luego renombrar (operación atómica)
    temp_file = str(output_file) + ".tmp"
    save_json(merged_data, temp_file)
    
    # Renombrar (operación atómica en la mayoría de sistemas)
    if os.path.exists(str(output_file)):
        os.replace(temp_file, str(output_file))
    else:
        os.rename(temp_file, str(output_file))
    
    print()
    print("=" * 70)
    print("RESUMEN")
    print("=" * 70)
    print(f"✅ Cursos procesados en esta ejecución: {processed:,}")
    print(f"📊 Total de cursos en archivo final: {len(merged_data['courses']):,}")
    print(f"❌ Errores: {errors:,}")
    if skipped_no_url > 0:
        print(f"⚠️  Sin detail_url: {skipped_no_url:,}")
    print(f"💾 Archivo guardado en: {output_file}")
    print("=" * 70)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Scraping de detalles de clases")
    parser.add_argument("--limit", type=int, help="Número máximo de cursos a procesar")
    parser.add_argument("--test", action="store_true", help="Modo test")
    args = parser.parse_args()
    
    limit = args.limit if args.limit else None
    test_mode = args.test
    main(limit=limit, test_mode=test_mode)
