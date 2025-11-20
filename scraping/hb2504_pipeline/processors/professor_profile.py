from typing import Optional, List, Dict
import re
import requests
from bs4 import BeautifulSoup
from dataclasses import dataclass
from urllib.parse import urlparse, parse_qs
import sys
from pathlib import Path

# Agregar el directorio raíz del pipeline al path
pipeline_root = Path(__file__).parent.parent
if str(pipeline_root) not in sys.path:
    sys.path.insert(0, str(pipeline_root))

from models.professor_profile_extractor import ProfessorProfileExtractor


@dataclass
class CourseEvaluation:
    term: str
    course: str
    section: str
    evaluation_link: str

    def to_dict(self) -> Dict[str, str]:
        return {
            'term': self.term,
            'course': self.course,
            'section': self.section,
            'evaluation_link': self.evaluation_link
        }


class ProfessorProfile:
    def __init__(self, profile_url: str, course_name: Optional[str] = None):
        self.profile_url = profile_url
        self.course_name = course_name
        self._soup: Optional[BeautifulSoup] = None
        self._course_evaluations: Optional[List[CourseEvaluation]] = None
        self._username: Optional[str] = None

    def _extract_username_from_url(self, url: str) -> str:
        if self._username:
            return self._username
        try:
            parsed = urlparse(url)
            params = parse_qs(parsed.query)
            username = params.get('username', [''])[0]
            self._username = username
            return username
        except Exception:
            return ""

    def _build_evaluation_link(self, course_id: str) -> str:
        username = self._extract_username_from_url(self.profile_url)
        if not username:
            return ""
        return f"https://hb2504.utep.edu/Home/CourseEval?username={username}&courseID={course_id}"

    def _extract_course_id_from_link(self, href: str) -> Optional[str]:
        if not href:
            return None
        
        # Si el href ya contiene courseID, extraerlo
        if 'courseID=' in href or 'courseid=' in href.lower():
            try:
                parsed = urlparse(href)
                params = parse_qs(parsed.query)
                course_id = params.get('courseID', params.get('courseid', ['']))
                if course_id:
                    return course_id[0]
            except Exception:
                pass
        
        # Si el href es relativo y contiene números, podría ser el courseID
        # Por ejemplo: /Home/CourseEval?courseID=280505876480
        if href.startswith('/') or 'CourseEval' in href:
            match = re.search(r'courseID[=:](\d+)', href, re.IGNORECASE)
            if match:
                return match.group(1)
        
        # Buscar números largos que podrían ser courseID
        # Los courseID parecen ser números largos (ej: 280505876480)
        numbers = re.findall(r'\d{10,}', href)
        if numbers:
            return numbers[0]
        
        return None

    def _load_html(self, timeout: int = 10) -> BeautifulSoup:
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

        response = requests.get(self.profile_url, headers=headers, timeout=timeout)
        response.raise_for_status()
        response.encoding = response.apparent_encoding or 'utf-8'
        
        request_time = time.time() - start
        print(f"     Request HTTP perfil: {request_time:.2f}s", end=" ")

        start_parse = time.time()
        self._soup = BeautifulSoup(response.text, 'html.parser')
        parse_time = time.time() - start_parse
        print(f"| Parsing HTML: {parse_time:.2f}s")
        
        return self._soup

    def extract_course_evaluations(self) -> List[CourseEvaluation]:
        if self._course_evaluations is not None:
            return self._course_evaluations
        
        try:
            soup = self._load_html()
            evaluations: List[CourseEvaluation] = []
            
            # Buscar sección de Course Evaluations
            # Intentar diferentes patrones comunes para encontrar la sección
            course_eval_section = None
            
            # Método 1: Buscar por texto "Course Evaluation" o "Course Evaluations"
            headings = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'div', 'span'])
            for heading in headings:
                text = heading.get_text(strip=True).lower()
                if 'course evaluation' in text or 'evaluations' in text:
                    # Buscar la tabla o lista más cercana
                    course_eval_section = heading
                    break
            
            # Método 2: Buscar tablas que puedan contener información de cursos
            if course_eval_section is None:
                tables = soup.find_all('table')
                for table in tables:
                    table_text = table.get_text().lower()
                    if 'term' in table_text and ('course' in table_text or 'section' in table_text):
                        course_eval_section = table
                        break
            
            # Si encontramos una sección, buscar las filas/entradas
            if course_eval_section:
                # Buscar en tablas
                if course_eval_section.name == 'table':
                    rows = course_eval_section.find_all('tr')
                    header_found = False
                    for row in rows:
                        cells = row.find_all(['td', 'th'])
                        if len(cells) >= 3:
                            # Verificar si es la fila de encabezado
                            cell_texts = [cell.get_text(strip=True).lower() for cell in cells]
                            if 'term' in cell_texts or 'course' in cell_texts:
                                header_found = True
                                continue
                            
                            if header_found:
                                # Extraer datos de la fila
                                term = cells[0].get_text(strip=True) if len(cells) > 0 else ""
                                course = cells[1].get_text(strip=True) if len(cells) > 1 else ""
                                section = cells[2].get_text(strip=True) if len(cells) > 2 else ""
                                
                                # Buscar el link de evaluación
                                eval_link = ""
                                link = row.find('a', href=True)
                                if link:
                                    href = link.get('href', '')
                                    # Buscar courseID en atributos data-* o en el href
                                    course_id = None
                                    for attr_name, attr_value in link.attrs.items():
                                        if 'course' in attr_name.lower() and 'id' in attr_name.lower():
                                            course_id = str(attr_value)
                                            break
                                        elif attr_name.startswith('data-'):
                                            # Buscar números largos en atributos data-*
                                            numbers = re.findall(r'\d{10,}', str(attr_value))
                                            if numbers:
                                                course_id = numbers[0]
                                                break
                                    
                                    if not course_id:
                                        course_id = self._extract_course_id_from_link(href)
                                    
                                    if course_id:
                                        eval_link = self._build_evaluation_link(course_id)
                                    elif href:
                                        # Si no se puede extraer courseID, usar el href directamente
                                        if href.startswith('/'):
                                            base_url = "https://hb2504.utep.edu"
                                            eval_link = base_url + href
                                        elif href.startswith('http'):
                                            eval_link = href
                                
                                # Solo agregar si el link es de evaluación (CourseEval), no de syllabus
                                is_evaluation_link = eval_link and ('CourseEval' in eval_link or '/Home/CourseEval' in eval_link)
                                
                                if term and course and is_evaluation_link:
                                    evaluations.append(CourseEvaluation(
                                        term=term,
                                        course=course,
                                        section=section,
                                        evaluation_link=eval_link
                                    ))
                                    # Limitar a las primeras 10 evaluaciones
                                    if len(evaluations) >= 10:
                                        break
                        
                        if len(evaluations) >= 10:
                            break
                
                # Buscar en listas o divs
                else:
                    # Buscar tablas dentro de la sección
                    tables = course_eval_section.find_next_siblings('table')
                    if not tables:
                        tables = course_eval_section.find_all('table')
                    
                    for table in tables:
                        rows = table.find_all('tr')
                        header_found = False
                        for row in rows:
                            cells = row.find_all(['td', 'th'])
                            if len(cells) >= 3:
                                cell_texts = [cell.get_text(strip=True).lower() for cell in cells]
                                if 'term' in cell_texts or 'course' in cell_texts:
                                    header_found = True
                                    continue
                                
                                if header_found:
                                    term = cells[0].get_text(strip=True) if len(cells) > 0 else ""
                                    course = cells[1].get_text(strip=True) if len(cells) > 1 else ""
                                    section = cells[2].get_text(strip=True) if len(cells) > 2 else ""
                                    
                                    eval_link = ""
                                    link = row.find('a', href=True)
                                    if link:
                                        href = link.get('href', '')
                                        # Buscar courseID en atributos data-* o en el href
                                        course_id = None
                                        for attr_name, attr_value in link.attrs.items():
                                            if 'course' in attr_name.lower() and 'id' in attr_name.lower():
                                                course_id = str(attr_value)
                                                break
                                            elif attr_name.startswith('data-'):
                                                # Buscar números largos en atributos data-*
                                                numbers = re.findall(r'\d{10,}', str(attr_value))
                                                if numbers:
                                                    course_id = numbers[0]
                                                    break
                                        
                                        if not course_id:
                                            course_id = self._extract_course_id_from_link(href)
                                        
                                        if course_id:
                                            eval_link = self._build_evaluation_link(course_id)
                                        elif href:
                                            # Si no se puede extraer courseID, usar el href directamente
                                            if href.startswith('/'):
                                                base_url = "https://hb2504.utep.edu"
                                                eval_link = base_url + href
                                            elif href.startswith('http'):
                                                eval_link = href
                                    
                                    # Solo agregar si el link es de evaluación (CourseEval), no de syllabus
                                    is_evaluation_link = eval_link and ('CourseEval' in eval_link or '/Home/CourseEval' in eval_link)
                                    
                                    if term and course and is_evaluation_link:
                                        evaluations.append(CourseEvaluation(
                                            term=term,
                                            course=course,
                                            section=section,
                                            evaluation_link=eval_link
                                        ))
                                        # Limitar a las primeras 10 evaluaciones
                                        if len(evaluations) >= 10:
                                            break
                        
                        if len(evaluations) >= 10:
                            break
            
            # Método alternativo: buscar directamente en todo el HTML por patrones
            if not evaluations:
                # Buscar todas las tablas y analizar su contenido
                all_tables = soup.find_all('table')
                for table in all_tables:
                    rows = table.find_all('tr')
                    for row in rows:
                        cells = row.find_all(['td', 'th'])
                        if len(cells) >= 2:
                            term = ""
                            course = ""
                            section = ""
                            eval_link = ""
                            
                            # Intentar extraer term, course, section de las celdas
                            for i, cell in enumerate(cells):
                                cell_text = cell.get_text(strip=True)
                                cell_lower = cell_text.lower()
                                
                                # Detectar term (puede contener "Fall", "Spring", "Summer", año)
                                if any(word in cell_lower for word in ['fall', 'spring', 'summer', 'winter']) or re.search(r'20\d{2}', cell_text):
                                    if not term:
                                        term = cell_text
                                
                                # Detectar course (cualquier texto que parezca un código de curso)
                                if re.match(r'^[A-Z]+\s*\d+', cell_text):
                                    if not course:
                                        course = cell_text
                                
                                # Detectar section (puede ser número o código)
                                if re.match(r'^\d+[A-Z]?$|^[A-Z]\d+$', cell_text):
                                    if not section:
                                        section = cell_text
                            
                            # Buscar link de evaluación
                            link = row.find('a', href=True)
                            if link:
                                href = link.get('href', '')
                                # Buscar courseID en atributos data-* o en el href
                                course_id = None
                                for attr_name, attr_value in link.attrs.items():
                                    if 'course' in attr_name.lower() and 'id' in attr_name.lower():
                                        course_id = str(attr_value)
                                        break
                                    elif attr_name.startswith('data-'):
                                        # Buscar números largos en atributos data-*
                                        numbers = re.findall(r'\d{10,}', str(attr_value))
                                        if numbers:
                                            course_id = numbers[0]
                                            break
                                
                                if not course_id:
                                    course_id = self._extract_course_id_from_link(href)
                                
                                if course_id:
                                    eval_link = self._build_evaluation_link(course_id)
                                elif href:
                                    # Si no se puede extraer courseID, usar el href directamente
                                    if href.startswith('/'):
                                        base_url = "https://hb2504.utep.edu"
                                        eval_link = base_url + href
                                    elif href.startswith('http'):
                                        eval_link = href
                            
                            # Solo agregar si el link es de evaluación (CourseEval), no de syllabus
                            is_evaluation_link = eval_link and ('CourseEval' in eval_link or '/Home/CourseEval' in eval_link)
                            
                            if term and course and is_evaluation_link:
                                evaluations.append(CourseEvaluation(
                                    term=term,
                                    course=course,
                                    section=section or "N/A",
                                    evaluation_link=eval_link
                                ))
                                # Limitar a las primeras 10 evaluaciones
                                if len(evaluations) >= 10:
                                    break
                    
                    if len(evaluations) >= 10:
                        break
            
            # Limitar a las primeras 10 evaluaciones
            self._course_evaluations = evaluations[:10]
            return self._course_evaluations
            
        except Exception as e:
            print(f"Error al extraer Course Evaluations: {e}")
            return []

    def get_course_evaluations(self) -> List[CourseEvaluation]:
        if self._course_evaluations is None:
            self.extract_course_evaluations()
        return self._course_evaluations or []

    def get_basic_info(self):
        """Extrae información básica del profesor."""
        soup = self._load_html()
        extractor = ProfessorProfileExtractor(soup)
        return extractor.extract_basic_info()

    def get_contact_info(self):
        """Extrae información de contacto."""
        soup = self._load_html()
        extractor = ProfessorProfileExtractor(soup)
        return extractor.extract_contact_info()

    def get_bio_and_awards(self):
        """Extrae biografía y premios."""
        soup = self._load_html()
        extractor = ProfessorProfileExtractor(soup)
        return extractor.extract_bio_and_awards()

    def get_education(self):
        """Extrae información educativa."""
        soup = self._load_html()
        extractor = ProfessorProfileExtractor(soup)
        return extractor.extract_education()

    def get_courses(self):
        """Extrae cursos."""
        soup = self._load_html()
        extractor = ProfessorProfileExtractor(soup)
        return extractor.extract_courses()

    def get_scholarly_activity(self):
        """Extrae actividad académica."""
        soup = self._load_html()
        extractor = ProfessorProfileExtractor(soup)
        return extractor.extract_scholarly_activity()

    def get_grants(self):
        """Extrae grants."""
        soup = self._load_html()
        extractor = ProfessorProfileExtractor(soup)
        return extractor.extract_grants()

