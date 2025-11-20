from typing import Optional, Dict
import requests
from bs4 import BeautifulSoup
from dataclasses import dataclass


@dataclass
class RatingBreakdown:
    """Estructura para almacenar el desglose de calificaciones."""
    no_response: str
    excellent: str
    good: str
    satisfactory: str
    poor: str
    very_poor: str
    avg: str

    def to_dict(self) -> Dict[str, str]:
        return {
            'no_response': self.no_response,
            'excellent': self.excellent,
            'good': self.good,
            'satisfactory': self.satisfactory,
            'poor': self.poor,
            'very_poor': self.very_poor,
            'avg': self.avg
        }


@dataclass
class EvaluationDetails:
    """Estructura para almacenar los detalles completos de una evaluación."""
    instructor_name: str
    course: str
    section: str
    term: str
    response_count: str
    instructor_rating: RatingBreakdown
    course_rating: Optional[RatingBreakdown] = None

    def to_dict(self) -> Dict:
        result = {
            'instructor_name': self.instructor_name,
            'course': self.course,
            'section': self.section,
            'term': self.term,
            'response_count': self.response_count,
            'instructor_rating': self.instructor_rating.to_dict()
        }
        if self.course_rating:
            result['course_rating'] = self.course_rating.to_dict()
        return result


class EvaluationScraper:
    def __init__(self, evaluation_url: str):
        self.evaluation_url = evaluation_url
        self._soup: Optional[BeautifulSoup] = None
        self._details: Optional[EvaluationDetails] = None

    def _load_html(self, timeout: int = 10) -> BeautifulSoup:
        """Carga el HTML de la URL de evaluación."""
        if self._soup is not None:
            return self._soup
        
        import time
        start = time.time()
            
        headers = {
            'User-Agent': (
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                'AppleWebKit/537.36 (KHTML, like Gecko) '
                'Chrome/91.0.4472.124 Safari/537.36'
            )
        }

        response = requests.get(self.evaluation_url, headers=headers, timeout=timeout)
        response.raise_for_status()
        response.encoding = response.apparent_encoding or 'utf-8'
        
        request_time = time.time() - start
        print(f" (HTTP: {request_time:.2f}s", end="")

        start_parse = time.time()
        self._soup = BeautifulSoup(response.text, 'html.parser')
        parse_time = time.time() - start_parse
        print(f", Parse: {parse_time:.2f}s)", end="")
        
        return self._soup

    def _extract_text_after_label(self, label: str) -> str:
        """Extrae el texto que sigue después de una etiqueta."""
        soup = self._load_html()
        text = soup.get_text()
        
        # Buscar el label en el texto
        if label in text:
            # Encontrar la posición del label
            idx = text.find(label)
            if idx != -1:
                # Obtener el texto después del label
                after_label = text[idx + len(label):].strip()
                # Tomar hasta el primer salto de línea o dos puntos
                lines = after_label.split('\n')
                if lines:
                    result = lines[0].strip()
                    # Limpiar caracteres especiales
                    result = result.replace(':', '').strip()
                    return result
        
        return ""

    def _extract_rating_breakdown(self, rating_text: str) -> RatingBreakdown:
        """Extrae el desglose de calificaciones de un texto de tabla."""
        no_response = "0.0%"
        excellent = "0.0%"
        good = "0.0%"
        satisfactory = "0.0%"
        poor = "0.0%"
        very_poor = "0.0%"
        avg = "0.0"

        import re
        
        # Buscar cada categoría y su porcentaje
        # El formato puede ser: "No Response\n10.0%" o "No Response 10.0%"
        patterns = {
            'no_response': r'No Response\s*[\n\s]*([\d.]+%)',
            'excellent': r'Excellent\s*[\n\s]*([\d.]+%)',
            'good': r'Good\s*[\n\s]*([\d.]+%)',
            'satisfactory': r'Satisfactory\s*[\n\s]*([\d.]+%)',
            'poor': r'Poor\s*[\n\s]*([\d.]+%)',
            'very_poor': r'Very Poor\s*[\n\s]*([\d.]+%)',
            'avg': r'Avg\s*[\n\s]*([\d.]+)'
        }

        for key, pattern in patterns.items():
            match = re.search(pattern, rating_text, re.IGNORECASE | re.MULTILINE)
            if match:
                value = match.group(1)
                if key == 'no_response':
                    no_response = value
                elif key == 'excellent':
                    excellent = value
                elif key == 'good':
                    good = value
                elif key == 'satisfactory':
                    satisfactory = value
                elif key == 'poor':
                    poor = value
                elif key == 'very_poor':
                    very_poor = value
                elif key == 'avg':
                    avg = value

        return RatingBreakdown(
            no_response=no_response,
            excellent=excellent,
            good=good,
            satisfactory=satisfactory,
            poor=poor,
            very_poor=very_poor,
            avg=avg
        )
    
    def _extract_rating_from_table(self, table) -> RatingBreakdown:
        """Extrae el desglose de calificaciones de una tabla HTML."""
        no_response = "0.0%"
        excellent = "0.0%"
        good = "0.0%"
        satisfactory = "0.0%"
        poor = "0.0%"
        very_poor = "0.0%"
        avg = "0.0"

        if not table:
            return RatingBreakdown(no_response, excellent, good, satisfactory, poor, very_poor, avg)

        # Buscar todas las filas de la tabla
        rows = table.find_all('tr')
        for row in rows:
            cells = row.find_all(['td', 'th'])
            if len(cells) >= 2:
                # La primera celda tiene la categoría, la segunda el porcentaje
                category = cells[0].get_text(strip=True)
                value = cells[1].get_text(strip=True)
                
                category_lower = category.lower()
                if 'no response' in category_lower:
                    no_response = value
                elif 'excellent' in category_lower:
                    excellent = value
                elif 'good' in category_lower:
                    good = value
                elif 'satisfactory' in category_lower:
                    satisfactory = value
                elif 'poor' in category_lower and 'very' not in category_lower:
                    poor = value
                elif 'very poor' in category_lower:
                    very_poor = value
                elif 'avg' in category_lower:
                    avg = value

        return RatingBreakdown(
            no_response=no_response,
            excellent=excellent,
            good=good,
            satisfactory=satisfactory,
            poor=poor,
            very_poor=very_poor,
            avg=avg
        )

    def _extract_field_value(self, label: str) -> str:
        """Extrae el valor de un campo desde el div courseEvalHeader."""
        soup = self._load_html()
        
        # Buscar el div con id="courseEvalHeader"
        header_div = soup.find('div', id='courseEvalHeader')
        if header_div:
            # Buscar todos los spans con clase evalText
            label_spans = header_div.find_all('span', class_='evalText')
            for span in label_spans:
                span_text = span.get_text(strip=True)
                if label in span_text:
                    # Buscar el siguiente span con clase evalTextNormal
                    next_span = span.find_next_sibling('span', class_='evalTextNormal')
                    if next_span:
                        return next_span.get_text(strip=True)
                    # Si no hay siguiente hermano, buscar en el siguiente elemento después del <br />
                    # O buscar en el texto completo del header_div
                    parent = span.parent
                    if parent:
                        # Buscar el siguiente span con evalTextNormal en el mismo nivel
                        for sibling in parent.next_siblings:
                            if hasattr(sibling, 'find'):
                                next_span = sibling.find('span', class_='evalTextNormal')
                                if next_span:
                                    return next_span.get_text(strip=True)
        
        return ""

    def extract_evaluation_details(self) -> Optional[EvaluationDetails]:
        """Extrae todos los detalles de la evaluación."""
        if self._details is not None:
            return self._details

        try:
            soup = self._load_html()
            
            # Extraer información básica usando el método mejorado
            instructor_name = self._extract_field_value("Instructor Name:")
            course = self._extract_field_value("Course:")
            section = self._extract_field_value("Section:")
            term = self._extract_field_value("Term:")
            response_count = self._extract_field_value("Response Count:")

            # Extraer calificaciones del instructor y del curso
            instructor_rating = RatingBreakdown("0.0%", "0.0%", "0.0%", "0.0%", "0.0%", "0.0%", "0.0")
            course_rating = None
            
            # Buscar todas las tablas con clase CourseEval
            tables = soup.find_all('table', class_='CourseEval')
            for table in tables:
                # Buscar el caption de la tabla
                caption = table.find('caption')
                if caption:
                    caption_text = caption.get_text().lower()
                    if 'instructor' in caption_text:
                        instructor_rating = self._extract_rating_from_table(table)
                    elif 'course' in caption_text:
                        course_rating = self._extract_rating_from_table(table)

            self._details = EvaluationDetails(
                instructor_name=instructor_name,
                course=course,
                section=section,
                term=term,
                response_count=response_count,
                instructor_rating=instructor_rating,
                course_rating=course_rating
            )

            return self._details

        except Exception as e:
            print(f"Error al extraer detalles de evaluación: {e}")
            return None

    def get_evaluation_details(self) -> Optional[EvaluationDetails]:
        """Obtiene los detalles de la evaluación, extrayéndolos si no están disponibles."""
        if self._details is None:
            self.extract_evaluation_details()
        return self._details

