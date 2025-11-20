from typing import Dict


class FacultyProfile:
    def __init__(self, name: str, username: str, college: str,
                 department: str, position: str, profile_url: str = ""):
        self.name = name.strip()
        self.username = username.strip()
        self.college = college.strip()
        self.department = department.strip()
        self.position = position.strip()
        self.profile_url = profile_url.strip()

    def __repr__(self):
        return (
            f"FacultyProfile(name='{self.name}', "
            f"college='{self.college}', department='{self.department}')"
        )

    def to_dict(self) -> Dict[str, str]:
        return {
            'name': self.name,
            'username': self.username,
            'college': self.college,
            'department': self.department,
            'position': self.position,
            'profile_url': self.profile_url
        }
