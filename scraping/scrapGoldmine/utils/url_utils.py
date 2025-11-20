"""
Utilidades para trabajar con URLs.
"""

import re
from typing import Optional
from urllib.parse import urlparse, parse_qs


def extract_crn_from_url(url: str) -> Optional[str]:
    """
    Extrae el CRN de la URL del detalle.
    
    Args:
        url: URL de la página de detalles (ej: ...?term_in=202620&crn_in=24184)
    
    Returns:
        CRN extraído o None si no se encuentra
    """
    try:
        parsed = urlparse(url)
        params = parse_qs(parsed.query)
        
        if 'crn_in' in params:
            crn_value = params['crn_in'][0]
            return crn_value
        
        # Fallback: buscar con regex
        match = re.search(r'crn_in[=&](\d+)', url)
        if match:
            return match.group(1)
        
        return None
    except Exception:
        return None


def extract_crn_from_detail_url(detail_url: str) -> Optional[str]:
    """Extrae el CRN real del campo detail_url."""
    if not detail_url:
        return None
    
    try:
        parsed = urlparse(detail_url)
        params = parse_qs(parsed.query)
        
        if 'crn_in' in params:
            crn_value = params['crn_in'][0]
            if crn_value.isdigit():
                return crn_value
        
        match = re.search(r'crn_in[=&](\d+)', detail_url)
        if match:
            return match.group(1)
        
        return None
    except Exception:
        return None


def extract_term_code(catalog_entry_url: str) -> Optional[str]:
    """
    Extrae el código de término (term_in) de catalog_entry_url.
    
    Ejemplo: URL con term_in=202620 -> "202620"
    
    Args:
        catalog_entry_url: URL del catálogo
    
    Returns:
        String con el código de término o None
    """
    if not catalog_entry_url or catalog_entry_url.strip() == "":
        return None
    
    try:
        parsed = urlparse(catalog_entry_url)
        params = parse_qs(parsed.query)
        
        if 'term_in' in params:
            term_code = params['term_in'][0]
            return term_code.strip() if term_code else None
        
        # Fallback: buscar con regex
        match = re.search(r'term_in[=&](\d+)', catalog_entry_url)
        if match:
            return match.group(1)
        
        return None
    except Exception:
        return None


def extract_instructor_id(profile_url: str) -> Optional[str]:
    """Extrae instructor_id de la URL del perfil."""
    if not profile_url or profile_url.strip() == "":
        return None
    
    try:
        parsed = urlparse(profile_url)
        params = parse_qs(parsed.query)
        
        if 'ID' in params:
            return params['ID'][0]
        
        match = re.search(r'[?&]ID=([^&]+)', profile_url)
        if match:
            return match.group(1)
    except Exception:
        pass
    
    return None

