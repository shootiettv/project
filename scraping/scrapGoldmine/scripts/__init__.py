"""
Scripts ejecutables del pipeline de scraping de Goldmine.
"""

from .scrape_to_clean import main as scrape_to_clean_main
from .class_details_extract import main as class_details_main

__all__ = ['scrape_to_clean_main', 'class_details_main']

