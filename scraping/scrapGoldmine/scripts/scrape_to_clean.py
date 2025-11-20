#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script principal para extraer y normalizar cursos desde HTML.
Genera courses_clean.json en dataset/json/listClasses/
"""

import sys
from pathlib import Path

# Agregar el directorio padre al path para imports
current_dir = Path(__file__).parent.parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

from scrapers.courses_scraper import scrape_html_file
from processors.course_normalizer import index_courses_by_crn, transform_course
from utils.file_manager import save_json


def main():
    """Función principal que ejecuta todo el pipeline."""
    # Rutas de archivos - usando resources para HTML y dataset para JSON
    base_dir = Path(__file__).parent.parent
    html_path = base_dir / "resources" / "goldmineBasic.html"
    output_file = base_dir / "dataset" / "json" / "listClasses" / "courses_clean.json"
    
    print("=" * 70)
    print("SCRAPING Y TRANSFORMACIÓN DIRECTA A COURSES_CLEAN.JSON")
    print("=" * 70)
    print()
    
    try:
        # 1. Extraer cursos del HTML
        print("1. Extrayendo cursos del HTML...")
        courses_array = scrape_html_file(str(html_path))
        print(f"   ✓ {len(courses_array)} cursos extraídos")
        print()
        
        # 2. Indexar por CRN
        print("2. Indexando cursos por CRN...")
        courses_indexed = index_courses_by_crn(courses_array)
        print(f"   ✓ {len(courses_indexed)} cursos únicos indexados")
        print()
        
        # 3. Transformar y limpiar
        print("3. Transformando y limpiando cursos...")
        courses_clean = {}
        errors = []
        
        for crn, course_raw in courses_indexed.items():
            try:
                course_clean = transform_course(course_raw)
                courses_clean[crn] = course_clean
            except Exception as e:
                errors.append(f"CRN {crn}: {str(e)}")
                print(f"   ⚠ Error procesando CRN {crn}: {str(e)}")
        
        print(f"   ✓ {len(courses_clean)} cursos transformados exitosamente")
        if errors:
            print(f"   ⚠ {len(errors)} cursos con errores")
        print()
        
        # 4. Guardar resultado final
        print("4. Guardando courses_clean.json...")
        output_data = {"courses": courses_clean}
        save_json(output_data, str(output_file))
        
        print(f"   ✓ Archivo guardado: {output_file}")
        print()
        
        # 5. Resumen
        print("=" * 70)
        print("RESUMEN")
        print("=" * 70)
        print(f"✓ Cursos extraídos: {len(courses_array)}")
        print(f"✓ Cursos únicos: {len(courses_indexed)}")
        print(f"✓ Cursos transformados: {len(courses_clean)}")
        print(f"✓ Archivo final: {output_file}")
        if errors:
            print(f"⚠ Errores: {len(errors)}")
        print()
        
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
