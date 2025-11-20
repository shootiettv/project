"""
Módulos de scraping para hb2504.utep.edu
"""
from .hb2504_scraper import HB2504Scraper
from .evaluations import EvaluationScraper, EvaluationDetails, RatingBreakdown

__all__ = ['HB2504Scraper', 'EvaluationScraper', 'EvaluationDetails', 'RatingBreakdown']

