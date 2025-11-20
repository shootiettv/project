#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Orquestador principal del pipeline de scraping de Goldmine.

Este script ejecuta automáticamente todo el pipeline:
1. scrape_to_clean.py → courses_clean.json
2. classDetailsExtractInfo.py → class_details_clean.json

Uso:
    python3 main.py                    # Pipeline completo
    python3 main.py --test 10          # Modo test con 10 cursos
    python3 main.py --skip-details      # Solo generar courses_clean.json
    python3 main.py --test 5 --skip-details  # Test solo courses_clean.json
"""

import sys
import argparse
from pathlib import Path
from typing import Optional
import time

# Agregar el directorio actual al path para importar módulos
current_dir = Path(__file__).parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

# Importar funciones main de los scripts
from scripts.scrape_to_clean import main as scrape_to_clean_main
from scripts.class_details_extract import main as class_details_main


def run_stage_1(test_mode: bool = False, test_limit: Optional[int] = None) -> int:
    """
    Ejecuta la etapa 1: Generar courses_clean.json desde HTML.
    
    Args:
        test_mode: Si es True, limita el número de cursos procesados
        test_limit: Número de cursos a procesar en modo test (solo para info)
    
    Returns:
        0 si exitoso, 1 si hay error
    """
    print("=" * 70)
    print("ETAPA 1: GENERANDO COURSES_CLEAN.JSON")
    print("=" * 70)
    if test_mode:
        print(f"🔬 MODO TEST: Procesando datos de prueba")
    print()
    
    start_time = time.time()
    
    try:
        result = scrape_to_clean_main()
        elapsed_time = time.time() - start_time
        
        if result == 0:
            print(f"\n✓ Etapa 1 completada exitosamente ({elapsed_time:.2f}s)")
            return 0
        else:
            print(f"\n✗ Etapa 1 falló ({elapsed_time:.2f}s)")
            return 1
    except Exception as e:
        elapsed_time = time.time() - start_time
        print(f"\n✗ Error en Etapa 1: {str(e)} ({elapsed_time:.2f}s)")
        import traceback
        traceback.print_exc()
        return 1


def run_stage_2(test_mode: bool = False, test_limit: Optional[int] = None) -> int:
    """
    Ejecuta la etapa 2: Generar class_details_clean.json desde courses_clean.json.
    
    Args:
        test_mode: Si es True, limita el número de cursos procesados
        test_limit: Número de cursos a procesar en modo test
    
    Returns:
        0 si exitoso, 1 si hay error
    """
    print("\n" + "=" * 70)
    print("ETAPA 2: GENERANDO CLASS_DETAILS_CLEAN.JSON")
    print("=" * 70)
    if test_mode:
        print(f"🔬 MODO TEST: Procesando {test_limit} curso(s)")
    else:
        print("📡 Esto puede tardar varios minutos (scraping web)...")
    print()
    
    start_time = time.time()
    
    try:
        # classDetailsExtractInfo.main() no retorna valor, así que capturamos excepciones
        class_details_main(limit=test_limit if test_mode else None, test_mode=test_mode)
        elapsed_time = time.time() - start_time
        
        print(f"\n✓ Etapa 2 completada exitosamente ({elapsed_time:.2f}s)")
        return 0
    except KeyboardInterrupt:
        elapsed_time = time.time() - start_time
        print(f"\n⚠ Etapa 2 interrumpida por el usuario ({elapsed_time:.2f}s)")
        return 1
    except Exception as e:
        elapsed_time = time.time() - start_time
        print(f"\n✗ Error en Etapa 2: {str(e)} ({elapsed_time:.2f}s)")
        import traceback
        traceback.print_exc()
        return 1


def verify_input_files() -> bool:
    """
    Verifica que los archivos de entrada necesarios existan.
    
    Returns:
        True si todos los archivos existen, False si falta alguno
    """
    base_dir = Path(__file__).parent
    html_path = base_dir / "resources" / "goldmineBasic.html"
    
    if not html_path.exists():
        print(f"✗ Error: No se encuentra el archivo HTML de entrada")
        print(f"  Ruta esperada: {html_path}")
        print(f"  Por favor, asegúrate de que el archivo existe antes de ejecutar el pipeline.")
        return False
    
    return True


def verify_stage_1_output() -> bool:
    """
    Verifica que la Etapa 1 haya generado el archivo necesario.
    
    Returns:
        True si el archivo existe, False si no
    """
    base_dir = Path(__file__).parent
    courses_clean_path = base_dir / "dataset" / "json" / "listClasses" / "courses_clean.json"
    
    if not courses_clean_path.exists():
        print(f"✗ Error: No se encuentra courses_clean.json")
        print(f"  Ruta esperada: {courses_clean_path}")
        print(f"  La Etapa 1 debe completarse exitosamente antes de ejecutar la Etapa 2.")
        return False
    
    return True


def print_summary(stage1_result: int, stage2_result: Optional[int], 
                  skip_details: bool, total_time: float):
    """
    Imprime un resumen final del pipeline.
    
    Args:
        stage1_result: Resultado de la Etapa 1 (0 = éxito, 1 = error)
        stage2_result: Resultado de la Etapa 2 (0 = éxito, 1 = error, None = no ejecutada)
        skip_details: Si se saltó la Etapa 2
        total_time: Tiempo total de ejecución
    """
    print("\n" + "=" * 70)
    print("RESUMEN FINAL DEL PIPELINE")
    print("=" * 70)
    print()
    
    # Etapa 1
    if stage1_result == 0:
        print("✓ Etapa 1: courses_clean.json generado exitosamente")
    else:
        print("✗ Etapa 1: Falló")
    
    # Etapa 2
    if skip_details:
        print("⊘ Etapa 2: Omitida (--skip-details)")
    elif stage2_result is None:
        print("⊘ Etapa 2: No ejecutada")
    elif stage2_result == 0:
        print("✓ Etapa 2: class_details_clean.json generado exitosamente")
    else:
        print("✗ Etapa 2: Falló")
    
    print()
    print(f"⏱  Tiempo total: {total_time:.2f} segundos")
    print()
    
    # Estado final
    if stage1_result == 0 and (skip_details or stage2_result == 0):
        print("=" * 70)
        print("✅ PIPELINE COMPLETADO EXITOSAMENTE")
        print("=" * 70)
    else:
        print("=" * 70)
        print("⚠️  PIPELINE COMPLETADO CON ERRORES")
        print("=" * 70)


def main():
    """Función principal del orquestador."""
    parser = argparse.ArgumentParser(
        description="Orquestador del pipeline de scraping de Goldmine",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:
  python3 main.py                    # Pipeline completo
  python3 main.py --test 10          # Modo test con 10 cursos
  python3 main.py --skip-details      # Solo generar courses_clean.json
  python3 main.py --test 5 --skip-details  # Test solo courses_clean.json
        """
    )
    
    parser.add_argument(
        "--test",
        type=int,
        metavar="N",
        help="Modo test: procesa solo N cursos (útil para pruebas rápidas)"
    )
    
    parser.add_argument(
        "--test10",
        action="store_true",
        help="Modo test rápido: procesa solo 10 cursos (alias de --test 10)"
    )
    
    parser.add_argument(
        "--skip-details",
        action="store_true",
        help="Omitir la Etapa 2 (solo generar courses_clean.json)"
    )
    
    parser.add_argument(
        "--skip-verification",
        action="store_true",
        help="Omitir verificación de archivos de entrada"
    )
    
    args = parser.parse_args()
    
    # Determinar modo test y límite
    test_mode = False
    test_limit = None
    
    if args.test10:
        test_mode = True
        test_limit = 10
    elif args.test is not None:
        test_mode = True
        test_limit = args.test
        if test_limit <= 0:
            print("✗ Error: El número de cursos para test debe ser mayor a 0")
            return 1
    
    # Banner inicial
    print("=" * 70)
    print("PIPELINE COMPLETO DE SCRAPING - GOLDMINE")
    print("=" * 70)
    print()
    
    if test_mode:
        print(f"🔬 MODO TEST ACTIVADO: Procesando {test_limit} curso(s)")
        print("   (Usa sin --test para procesar todos los cursos)")
    else:
        print("📊 MODO PRODUCCIÓN: Procesando todos los cursos")
    
    if args.skip_details:
        print("⊘ Etapa 2 omitida: Solo se generará courses_clean.json")
    
    print()
    
    # Verificar archivos de entrada
    if not args.skip_verification:
        print("Verificando archivos de entrada...")
        if not verify_input_files():
            return 1
        print("✓ Archivos de entrada verificados")
        print()
    
    # Iniciar cronómetro
    pipeline_start_time = time.time()
    
    # ETAPA 1: Generar courses_clean.json
    stage1_result = run_stage_1(test_mode=test_mode, test_limit=test_limit)
    
    if stage1_result != 0:
        total_time = time.time() - pipeline_start_time
        print_summary(stage1_result, None, False, total_time)
        return 1
    
    # Verificar que la Etapa 1 generó el archivo necesario para la Etapa 2
    if not args.skip_details and not verify_stage_1_output():
        total_time = time.time() - pipeline_start_time
        print_summary(stage1_result, None, False, total_time)
        return 1
    
    # ETAPA 2: Generar class_details_clean.json (si no se omite)
    stage2_result = None
    if not args.skip_details:
        stage2_result = run_stage_2(test_mode=test_mode, test_limit=test_limit)
    else:
        print("\n⊘ Etapa 2 omitida (--skip-details)")
    
    # Resumen final
    total_time = time.time() - pipeline_start_time
    print_summary(stage1_result, stage2_result, args.skip_details, total_time)
    
    # Código de salida
    if stage1_result == 0 and (args.skip_details or stage2_result == 0):
        return 0
    else:
        return 1


if __name__ == "__main__":
    exit(main())

