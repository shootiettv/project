from typing import List, Optional, Dict
from urllib.parse import urlparse, parse_qs

import requests
from bs4 import BeautifulSoup

import sys
from pathlib import Path

# Agregar el directorio raíz del pipeline al path
pipeline_root = Path(__file__).parent.parent
if str(pipeline_root) not in sys.path:
    sys.path.insert(0, str(pipeline_root))

from models.faculty_profile import FacultyProfile


class HB2504Scraper:
    URL = "https://hb2504.utep.edu/"

    def __init__(self, html_file_path: Optional[str] = None, url: Optional[str] = None):
        self.html_file_path = html_file_path
        self.url = url or self.URL
        self.soup: Optional[BeautifulSoup] = None
        self._profiles: Optional[List[FacultyProfile]] = None

    def load_html_from_url(self, url: Optional[str] = None, timeout: int = 30) -> BeautifulSoup:
        target_url = url or self.url

        headers = {
            'User-Agent': (
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                'AppleWebKit/537.36 (KHTML, like Gecko) '
                'Chrome/91.0.4472.124 Safari/537.36'
            )
        }

        response = requests.get(target_url, headers=headers, timeout=timeout)
        response.raise_for_status()
        response.encoding = response.apparent_encoding or 'utf-8'

        self.soup = BeautifulSoup(response.text, 'html.parser')
        return self.soup

    def load_html_from_file(self, file_path: Optional[str] = None) -> BeautifulSoup:
        path = file_path or self.html_file_path
        if not path:
            raise ValueError("Debe proporcionar una ruta al archivo HTML")

        with open(path, 'r', encoding='utf-8') as f:
            html_content = f.read()

        self.soup = BeautifulSoup(html_content, 'html.parser')
        return self.soup

    def load_html_from_string(self, html_content: str) -> BeautifulSoup:
        self.soup = BeautifulSoup(html_content, 'html.parser')
        return self.soup

    def _parse_profile_from_row(self, row) -> Optional[FacultyProfile]:
        try:
            link = row.find('a', href=True)
            if not link:
                return None

            href = link.get('href', '')
            username = self._extract_username_from_url(href)
            name = link.get_text(strip=True)

            info_span = row.find('span', class_='fst-italic')
            if not info_span:
                return None

            info_text = info_span.get_text(strip=True)
            parts = [p.strip() for p in info_text.split(' - ') if p.strip()]

            if len(parts) < 3:
                return None

            college = parts[0]
            position = parts[-1]
            departments = parts[1:-1]
            department = ' - '.join(departments) if departments else ""

            base_url = "https://hb2504.utep.edu"
            profile_url = base_url + href if href.startswith('/') else href

            return FacultyProfile(
                name=name,
                username=username,
                college=college,
                department=department,
                position=position,
                profile_url=profile_url
            )
        except Exception:
            return None

    def extract_all_profiles(self, force_reload: bool = False) -> List[FacultyProfile]:
        if self.soup is None or force_reload:
            if self.html_file_path:
                self.load_html_from_file()
            else:
                self.load_html_from_url()

        profiles: List[FacultyProfile] = []

        faculty_rows = self.soup.find_all('p', class_='FacultyRow')

        for row in faculty_rows:
            profile = self._parse_profile_from_row(row)
            if profile:
                profiles.append(profile)

        self._profiles = profiles
        return profiles

    def _extract_username_from_url(self, url: str) -> str:
        try:
            parsed = urlparse(url)
            params = parse_qs(parsed.query)
            username = params.get('username', [''])[0]
            return username
        except Exception:
            return ""

    def search(
        self,
        name: Optional[str] = None,
        college: Optional[str] = None,
        department: Optional[str] = None,
        position: Optional[str] = None,
        case_sensitive: bool = False
    ) -> List[FacultyProfile]:
        if self.soup is None:
            if self.html_file_path:
                self.load_html_from_file()
            else:
                self.load_html_from_url()

        name_filter = name if case_sensitive else (name.lower() if name else None)
        college_filter = college if case_sensitive else (college.lower() if college else None)
        department_filter = department if case_sensitive else (department.lower() if department else None)
        position_filter = position if case_sensitive else (position.lower() if position else None)

        matching_profiles: List[FacultyProfile] = []

        faculty_rows = self.soup.find_all('p', class_='FacultyRow')

        for row in faculty_rows:
            profile = self._parse_profile_from_row(row)
            if not profile:
                continue

            matches = True

            if name_filter:
                profile_name = profile.name if case_sensitive else profile.name.lower()
                if name_filter not in profile_name:
                    matches = False

            if matches and college_filter:
                profile_college = profile.college if case_sensitive else profile.college.lower()
                if college_filter not in profile_college:
                    matches = False

            if matches and department_filter:
                profile_dept = profile.department if case_sensitive else profile.department.lower()
                if department_filter not in profile_dept:
                    matches = False

            if matches and position_filter:
                profile_pos = profile.position if case_sensitive else profile.position.lower()
                if position_filter not in profile_pos:
                    matches = False

            if matches:
                matching_profiles.append(profile)

        return matching_profiles

    def filter_profiles(
        self,
        name: Optional[str] = None,
        college: Optional[str] = None,
        department: Optional[str] = None,
        position: Optional[str] = None,
        case_sensitive: bool = False
    ) -> List[FacultyProfile]:
        return self.search(
            name=name,
            college=college,
            department=department,
            position=position,
            case_sensitive=case_sensitive
        )

    def get_all_colleges(self) -> List[str]:
        if self._profiles is None:
            self.extract_all_profiles()

        colleges = set(p.college for p in self._profiles)
        return sorted(list(colleges))

    def get_all_departments(self, college: Optional[str] = None) -> List[str]:
        if self._profiles is None:
            self.extract_all_profiles()

        profiles = self._profiles
        if college:
            college_lower = college.lower()
            profiles = [p for p in profiles if college_lower in p.college.lower()]

        departments = set(p.department for p in profiles if p.department)
        return sorted(list(departments))

    def export_to_dict_list(self, profiles: Optional[List[FacultyProfile]] = None) -> List[Dict[str, str]]:
        if profiles is None:
            if self._profiles is None:
                self.extract_all_profiles()
            profiles = self._profiles

        return [p.to_dict() for p in profiles]
