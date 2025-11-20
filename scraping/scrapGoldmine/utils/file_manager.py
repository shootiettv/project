"""
Utilidades para gestión de archivos.
"""

import json
from pathlib import Path
from typing import Any, Dict


def ensure_directory(file_path: str) -> None:
    """Asegura que el directorio del archivo existe."""
    Path(file_path).parent.mkdir(parents=True, exist_ok=True)


def save_json(data: Any, file_path: str, indent: int = 2) -> None:
    """
    Guarda datos en un archivo JSON.
    
    Args:
        data: Datos a guardar
        file_path: Ruta del archivo
        indent: Indentación del JSON
    """
    ensure_directory(file_path)
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=indent, ensure_ascii=False)


def load_json(file_path: str) -> Dict:
    """
    Carga datos desde un archivo JSON.
    
    Args:
        file_path: Ruta del archivo
    
    Returns:
        Datos cargados del JSON
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

