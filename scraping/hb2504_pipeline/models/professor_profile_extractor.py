from typing import Dict, List, Optional
from bs4 import BeautifulSoup
from dataclasses import dataclass
from urllib.parse import urljoin


@dataclass
class ProfessorBasicInfo:
    name: str
    photo_url: str
    position: str
    department: str
    cv_url: Optional[str] = None


@dataclass
class ContactInfo:
    office_building: Optional[str] = None
    office_room: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None


@dataclass
class AwardHonor:
    title: str
    date: Optional[str] = None
    organization: Optional[str] = None


@dataclass
class Education:
    degree: str
    field: str
    institution: str
    year: Optional[str] = None


@dataclass
class Course:
    term: str
    course: str
    section: str
    syllabus_url: Optional[str] = None


@dataclass
class Publication:
    title: str
    details: Optional[str] = None


@dataclass
class Presentation:
    title: str
    details: Optional[str] = None


class ProfessorProfileExtractor:
    def __init__(self, soup: BeautifulSoup, base_url: str = "https://hb2504.utep.edu"):
        self.soup = soup
        self.base_url = base_url

    def extract_basic_info(self) -> Optional[ProfessorBasicInfo]:
        """Extrae información básica del profesor."""
        try:
            # Nombre
            name_elem = self.soup.find('h3', class_='openSans colorBlue')
            if not name_elem:
                name_elem = self.soup.find('h3')
            name = name_elem.get_text(strip=True) if name_elem else ""

            # Foto
            photo_elem = self.soup.find('img', class_='FP_Profile')
            photo_url = ""
            if photo_elem:
                photo_url = photo_elem.get('src', '')
                if photo_url and not photo_url.startswith('http'):
                    photo_url = urljoin(self.base_url, photo_url)

            # Posición y departamento
            position = ""
            department = ""
            article_divs = self.soup.find_all('div', class_='article')
            for div in article_divs:
                text = div.get_text(strip=True)
                if 'Senior Lecturer' in text or 'Professor' in text or 'Assistant' in text or 'Associate' in text or 'Lecturer' in text:
                    lines = [line.strip() for line in text.split('\n') if line.strip()]
                    if lines:
                        position = lines[0]
                        if len(lines) > 1:
                            department = lines[1]
                        break

            # CV
            cv_url = None
            cv_link = self.soup.find('a', class_='ApplyClass underlined')
            if cv_link and 'Curriculum Vitae' in cv_link.get_text():
                cv_url = cv_link.get('href', '')
                if cv_url and not cv_url.startswith('http'):
                    cv_url = urljoin(self.base_url, cv_url)

            return ProfessorBasicInfo(
                name=name,
                photo_url=photo_url,
                position=position,
                department=department,
                cv_url=cv_url
            )
        except Exception as e:
            print(f"Error extrayendo información básica: {e}")
            return None

    def extract_contact_info(self) -> ContactInfo:
        """Extrae información de contacto."""
        try:
            contact_info = ContactInfo()
            article_divs = self.soup.find_all('div', class_='article')
            
            for div in article_divs:
                text = div.get_text()
                if 'Office Building' in text or 'Phone' in text or 'Email' in text:
                    lines = text.split('\n')
                    for line in lines:
                        line = line.strip()
                        if 'Office Building:' in line:
                            contact_info.office_building = line.split(':', 1)[1].strip() if ':' in line else None
                        elif 'Office Room:' in line:
                            contact_info.office_room = line.split(':', 1)[1].strip() if ':' in line else None
                        elif 'Phone:' in line:
                            contact_info.phone = line.split(':', 1)[1].strip() if ':' in line else None
                        elif 'Email:' in line:
                            email_link = div.find('a', href=lambda x: x and 'mailto:' in x)
                            if email_link:
                                contact_info.email = email_link.get('href', '').replace('mailto:', '').strip()
                            else:
                                contact_info.email = line.split(':', 1)[1].strip() if ':' in line else None
                    break

            return contact_info
        except Exception as e:
            print(f"Error extrayendo información de contacto: {e}")
            return ContactInfo()

    def extract_bio_and_awards(self) -> Dict:
        """Extrae biografía y premios."""
        try:
            bio_section = self.soup.find('div', id='Bio')
            if not bio_section:
                # Buscar en versión móvil
                bio_section = self.soup.find('div', id='collapseOne')
            
            bio_text = ""
            awards = []
            
            if bio_section:
                # Extraer biografía
                paragraphs = bio_section.find_all('p')
                for p in paragraphs:
                    text = p.get_text(strip=True)
                    if text and 'No info available' not in text:
                        if not any(award_word in text.lower() for award_word in ['award', 'honor', 'excellence']):
                            bio_text += text + " "
                
                # Extraer premios
                awards_header = bio_section.find('span', class_='tabHeader', string=lambda x: x and 'Awards' in x)
                if not awards_header:
                    awards_header = bio_section.find(string=lambda x: x and 'Awards and Honors' in x)
                
                if awards_header:
                    awards_list = awards_header.find_next('ul')
                    if not awards_list:
                        awards_list = awards_header.find_parent().find_next('ul')
                    
                    if awards_list:
                        for li in awards_list.find_all('li'):
                            award_text = li.get_text(strip=True)
                            if award_text:
                                # Intentar parsear fecha y organización
                                parts = award_text.split('(')
                                title = parts[0].strip()
                                date = None
                                organization = None
                                
                                if len(parts) > 1:
                                    date_org = parts[1].rstrip(')')
                                    if '-' in date_org:
                                        date_parts = date_org.split('-', 1)
                                        date = date_parts[0].strip()
                                        if len(date_parts) > 1:
                                            organization = date_parts[1].strip()
                                    else:
                                        date = date_org.strip()
                                
                                awards.append(AwardHonor(
                                    title=title,
                                    date=date,
                                    organization=organization
                                ))

            return {
                'description': bio_text.strip(),
                'awards_honors': awards
            }
        except Exception as e:
            print(f"Error extrayendo biografía y premios: {e}")
            return {'description': '', 'awards_honors': []}

    def extract_education(self) -> List[Education]:
        """Extrae información educativa."""
        try:
            education_section = self.soup.find('div', id='Education')
            if not education_section:
                education_section = self.soup.find('div', id='collapseTwo')
            
            education_list = []
            
            if education_section:
                ul = education_section.find('ul')
                if ul:
                    for li in ul.find_all('li'):
                        text = li.get_text(strip=True)
                        if text:
                            # Parsear formato: "MAcc in Accounting, University of Texas at El Paso (2007)"
                            if ',' in text:
                                parts = text.split(',')
                                degree_field = parts[0].strip()
                                
                                # Separar degree y field
                                if ' in ' in degree_field:
                                    degree, field = degree_field.split(' in ', 1)
                                    degree = degree.strip()
                                    field = field.strip()
                                else:
                                    degree = degree_field
                                    field = ""
                                
                                institution = parts[1].strip() if len(parts) > 1 else ""
                                year = None
                                
                                # Extraer año si está entre paréntesis
                                if '(' in institution:
                                    year_match = institution.split('(')
                                    institution = year_match[0].strip()
                                    if len(year_match) > 1:
                                        year = year_match[1].rstrip(')').strip()
                                
                                education_list.append(Education(
                                    degree=degree,
                                    field=field,
                                    institution=institution,
                                    year=year
                                ))

            return education_list
        except Exception as e:
            print(f"Error extrayendo educación: {e}")
            return []

    def extract_courses(self) -> Dict:
        """Extrae cursos actuales/futuros y pasados."""
        try:
            courses_section = self.soup.find('div', id='CurrentCourses')
            if not courses_section:
                courses_section = self.soup.find('div', id='collapseFive')
            
            current_future = []
            past = []
            
            if courses_section:
                # Cursos actuales/futuros
                current_table = courses_section.find('table', class_='course-table')
                if current_table:
                    rows = current_table.find_all('tr')[1:]  # Skip header
                    for row in rows:
                        cells = row.find_all('td')
                        if len(cells) >= 3:
                            term = cells[0].get_text(strip=True)
                            course = cells[1].get_text(strip=True)
                            section = cells[2].get_text(strip=True)
                            syllabus_url = None
                            
                            syllabus_link = row.find('a', href=True)
                            if syllabus_link:
                                syllabus_url = syllabus_link.get('href', '')
                                if syllabus_url and not syllabus_url.startswith('http'):
                                    syllabus_url = urljoin(self.base_url, syllabus_url)
                            
                            current_future.append(Course(
                                term=term,
                                course=course,
                                section=section,
                                syllabus_url=syllabus_url
                            ))
                
                # Cursos pasados
                past_table = courses_section.find('table', id='past-courses')
                if not past_table:
                    # Buscar en versión móvil
                    past_div = courses_section.find('div', id='mobile-pastcourses-list')
                    if past_div:
                        past_items = past_div.find_all('div', recursive=False)
                        for item in past_items:
                            rows = item.find_all('div', class_='row fixedRow')
                            term = ""
                            course = ""
                            section = ""
                            syllabus_url = None
                            
                            for row in rows:
                                cols = row.find_all('div')
                                if len(cols) >= 2:
                                    label = cols[0].get_text(strip=True)
                                    value = cols[1].get_text(strip=True)
                                    
                                    if 'Term' in label:
                                        term = value
                                    elif 'Course' in label:
                                        course = value
                                    elif 'Section' in label:
                                        section = value
                                    elif 'Syllabus' in label:
                                        link = cols[1].find('a', href=True)
                                        if link:
                                            syllabus_url = link.get('href', '')
                                            if syllabus_url and not syllabus_url.startswith('http'):
                                                syllabus_url = urljoin(self.base_url, syllabus_url)
                            
                            if term and course:
                                past.append(Course(
                                    term=term,
                                    course=course,
                                    section=section,
                                    syllabus_url=syllabus_url
                                ))
                else:
                    rows = past_table.find_all('tr')[1:]  # Skip header
                    for row in rows:
                        cells = row.find_all('td')
                        if len(cells) >= 3:
                            term = cells[0].get_text(strip=True)
                            course = cells[1].get_text(strip=True)
                            section = cells[2].get_text(strip=True)
                            syllabus_url = None
                            
                            syllabus_link = row.find('a', href=True)
                            if syllabus_link:
                                syllabus_url = syllabus_link.get('href', '')
                                if syllabus_url and not syllabus_url.startswith('http'):
                                    syllabus_url = urljoin(self.base_url, syllabus_url)
                            
                            past.append(Course(
                                term=term,
                                course=course,
                                section=section,
                                syllabus_url=syllabus_url
                            ))

            return {
                'current_future': current_future,
                'past': past
            }
        except Exception as e:
            print(f"Error extrayendo cursos: {e}")
            return {'current_future': [], 'past': []}

    def extract_scholarly_activity(self) -> Dict:
        """Extrae publicaciones y presentaciones."""
        try:
            publications_section = self.soup.find('div', id='RecentPublications')
            if not publications_section:
                publications_section = self.soup.find('div', id='collapseThree')
            
            publications = []
            presentations = []
            
            if publications_section:
                # Buscar sección de Publications
                pub_header = publications_section.find('span', class_='tabHeader', string=lambda x: x and 'Publications' in x)
                if not pub_header:
                    pub_header = publications_section.find(string=lambda x: x and 'Publications' in x)
                
                if pub_header:
                    # Buscar lista o párrafos después del header
                    next_elem = pub_header.find_next()
                    while next_elem:
                        if next_elem.name == 'ul':
                            for li in next_elem.find_all('li'):
                                text = li.get_text(strip=True)
                                if text and 'No info available' not in text:
                                    publications.append(Publication(title=text))
                            break
                        elif next_elem.name == 'p' and 'No info available' not in next_elem.get_text():
                            text = next_elem.get_text(strip=True)
                            if text:
                                publications.append(Publication(title=text))
                            break
                        next_elem = next_elem.find_next_sibling()
                
                # Buscar sección de Presentations
                pres_header = publications_section.find('span', class_='tabHeader', string=lambda x: x and 'Presentations' in x)
                if not pres_header:
                    pres_header = publications_section.find(string=lambda x: x and 'Presentations' in x)
                
                if pres_header:
                    next_elem = pres_header.find_next()
                    while next_elem:
                        if next_elem.name == 'ul':
                            for li in next_elem.find_all('li'):
                                text = li.get_text(strip=True)
                                if text and 'No info available' not in text:
                                    presentations.append(Presentation(title=text))
                            break
                        elif next_elem.name == 'p' and 'No info available' not in next_elem.get_text():
                            text = next_elem.get_text(strip=True)
                            if text:
                                presentations.append(Presentation(title=text))
                            break
                        next_elem = next_elem.find_next_sibling()

            return {
                'publications': publications,
                'presentations': presentations
            }
        except Exception as e:
            print(f"Error extrayendo actividad académica: {e}")
            return {'publications': [], 'presentations': []}

    def extract_grants(self) -> List[Dict]:
        """Extrae información de grants."""
        try:
            grants_section = self.soup.find('div', id='AwardsHonors')
            if not grants_section:
                grants_section = self.soup.find('div', id='collapseFour')
            
            grants = []
            
            if grants_section:
                no_info = grants_section.find('p', class_='noInfo')
                if not no_info:
                    # Buscar lista de grants
                    ul = grants_section.find('ul')
                    if ul:
                        for li in ul.find_all('li'):
                            text = li.get_text(strip=True)
                            if text:
                                grants.append({'title': text})

            return grants
        except Exception as e:
            print(f"Error extrayendo grants: {e}")
            return []

