import re
from datetime import datetime

from app.schemas.resume import (
    ResumeProfile,
    Education,
    Experience,
    Project,
)

from src.extraction.skill_extractor import extract_skills


# ============================================================
# SECTION DEFINITIONS
# ============================================================

SECTION_HEADERS = {
    "experience": {
        "experience",
        "work experience",
        "professional experience",
        "employment",
    },
    "skills": {
        "skills",
        "technical skills",
    },
    "projects": {
        "projects",
        "personal projects",
        "academic projects",
    },
    "education": {
        "education",
        "academic background",
        "educational background",
    },
    "certifications": {
        "certifications",
        "certificates",
    },
}


# ============================================================
# TEXT CLEANING
# ============================================================

def clean_line(line: str) -> str:
    """
    Clean OCR artifacts and normalize whitespace.
    """

    if not line:
        return ""

    line = line.strip()

    # Remove OCR bullet characters.
    line = re.sub(r"^[«»•+*]\s*", "", line)

    # Fix common OCR artifact.
    line = line.replace("R?", "R²")

    # Normalize whitespace.
    line = re.sub(r"\s+", " ", line)

    return line.strip()


# ============================================================
# SECTION DETECTION
# ============================================================

def detect_section(line: str) -> str | None:
    """
    Detect whether a line is a resume section header.
    """

    normalized = clean_line(line).lower()

    normalized = re.sub(r"[:\-]+$", "", normalized)

    for section, headers in SECTION_HEADERS.items():
        if normalized in headers:
            return section

    return None


# ============================================================
# SECTION SPLITTING
# ============================================================

def split_sections(text: str) -> dict[str, list[str]]:
    """
    Split resume text into logical sections.

    Supported sections:
        header
        summary
        experience
        skills
        projects
        education
        certifications
    """

    sections = {
        "header": [],
        "summary": [],
        "experience": [],
        "skills": [],
        "projects": [],
        "education": [],
        "certifications": [],
    }

    if not text:
        return sections

    lines = []

    for raw_line in text.splitlines():

        line = clean_line(raw_line)

        if line:
            lines.append(line)

    if not lines:
        return sections

    # --------------------------------------------------------
    # Find section positions
    # --------------------------------------------------------

    section_positions = {}

    for index, line in enumerate(lines):

        detected = detect_section(line)

        if detected:
            section_positions[detected] = index

    # --------------------------------------------------------
    # HEADER
    # --------------------------------------------------------

    experience_index = section_positions.get(
        "experience",
        len(lines),
    )

    header_lines = lines[:experience_index]

    if header_lines:

        # First 4 lines are normally:
        #
        # Name
        # Title
        # Contact
        # LinkedIn / GitHub
        #
        sections["header"] = header_lines[:4]

        # Everything after the header is the summary.
        if len(header_lines) > 4:
            sections["summary"] = header_lines[4:]

    # --------------------------------------------------------
    # NORMAL SECTIONS
    # --------------------------------------------------------

    section_order = [
        "experience",
        "skills",
        "projects",
        "education",
        "certifications",
    ]

    for i, section in enumerate(section_order):

        if section not in section_positions:
            continue

        start = section_positions[section] + 1

        # Find next section.
        end = len(lines)

        for next_section in section_order[i + 1:]:

            if next_section in section_positions:

                end = section_positions[next_section]
                break

        sections[section] = lines[start:end]

    return sections


# ============================================================
# NAME EXTRACTION
# ============================================================

def extract_name(text: str) -> str | None:
    """
    Extract candidate name.

    For this resume format, the first meaningful line
    is the candidate name.
    """

    if not text:
        return None

    for line in text.splitlines():

        line = clean_line(line)

        if line:
            return line

    return None


# ============================================================
# SUMMARY EXTRACTION
# ============================================================

def extract_summary(
    sections: dict[str, list[str]],
) -> str | None:
    """
    Extract professional summary.
    """

    summary_lines = sections.get("summary", [])

    if not summary_lines:
        return None

    return " ".join(summary_lines)


# ============================================================
# DATE UTILITIES
# ============================================================

MONTHS = {
    "january": 1,
    "february": 2,
    "march": 3,
    "april": 4,
    "may": 5,
    "june": 6,
    "july": 7,
    "august": 8,
    "september": 9,
    "october": 10,
    "november": 11,
    "december": 12,
}


def parse_month_year(value: str):
    """
    Parse:
        June 2026
        August 2026
    """

    match = re.search(
        r"([A-Za-z]+)\s+(\d{4})",
        value,
    )

    if not match:
        return None

    month_name = match.group(1).lower()
    year = int(match.group(2))

    month = MONTHS.get(month_name)

    if not month:
        return None

    return year, month


def calculate_experience_years(
    start_date: str,
    end_date: str,
) -> float:
    """
    Calculate approximate experience duration.
    """

    start = parse_month_year(start_date)

    if not start:
        return 0.0

    start_year, start_month = start

    if end_date.lower() in {
        "present",
        "current",
    }:

        now = datetime.now()

        end_year = now.year
        end_month = now.month

    else:

        end = parse_month_year(end_date)

        if not end:
            return 0.0

        end_year, end_month = end

    months = (
        (end_year - start_year) * 12
        + (end_month - start_month)
    )

    return round(
        max(months, 0) / 12,
        1,
    )


# ============================================================
# EXPERIENCE EXTRACTION
# ============================================================

def extract_experience(
    sections: dict[str, list[str]],
) -> list[Experience]:
    """
    Extract work experience.

    Expected format:

        Role | Company Date — Present

        • responsibility
        • responsibility

    Example:

        MLOps Intern | Gofreelab Technologies June 2026 — Present
    """

    lines = sections.get(
        "experience",
        [],
    )

    if not lines:
        return []

    experiences = []

    # --------------------------------------------------------
    # Role/company/date pattern
    # --------------------------------------------------------

    month_pattern = (
        r"(?:January|February|March|April|May|June|July|"
        r"August|September|October|November|December)"
    )

    experience_pattern = re.compile(
        rf"^(.*?)\s*\|\s*(.*?)\s+"
        rf"({month_pattern}\s+\d{{4}})"
        rf"\s*[—–-]\s*"
        rf"(Present|Current|{month_pattern}\s+\d{{4}})$",
        re.IGNORECASE,
    )

    for line in lines:

        match = experience_pattern.match(line)

        if not match:
            continue

        role = match.group(1).strip()

        company = match.group(2).strip()

        start_date = match.group(3).strip()

        end_date = match.group(4).strip()

        years = calculate_experience_years(
            start_date,
            end_date,
        )

        experiences.append(
            Experience(
                company=company,
                role=role,
                years=years,
            )
        )

    return experiences


# ============================================================
# PROJECT EXTRACTION
# ============================================================

def extract_projects(
    sections: dict[str, list[str]],
) -> list[Project]:
    """
    Extract projects.

    Expected format:

        Project Name | Category Date — Date
        • Description
        • Description
        • Description
    """

    lines = sections.get(
        "projects",
        [],
    )

    if not lines:
        return []

    projects = []

    current_project_name = None
    current_description = []

    month_pattern = (
        r"(?:January|February|March|April|May|June|July|"
        r"August|September|October|November|December)"
    )

    project_pattern = re.compile(
        rf"^(.+?)\s*\|\s*(.+?)\s+"
        rf"{month_pattern}\s+\d{{4}}"
        rf"\s*[—–-]\s*"
        rf"{month_pattern}\s+\d{{4}}$",
        re.IGNORECASE,
    )

    def save_current_project():

        nonlocal current_project_name
        nonlocal current_description

        if not current_project_name:
            return

        description = " ".join(
            current_description
        ).strip()

        technologies = extract_project_technologies(
            description
        )

        projects.append(
            Project(
                name=current_project_name,
                description=description or None,
                technologies=technologies,
            )
        )

    for line in lines:

        # ----------------------------------------------------
        # Project heading
        # ----------------------------------------------------

        match = project_pattern.match(line)

        if match:

            save_current_project()

            current_project_name = (
                match.group(1).strip()
            )

            current_description = []

            continue

        # ----------------------------------------------------
        # Ignore live demo lines
        # ----------------------------------------------------

        if line.lower().startswith(
            "live demo"
        ):
            continue

        # ----------------------------------------------------
        # Project description
        # ----------------------------------------------------

        if current_project_name:

            current_description.append(line)

    # Save last project.
    save_current_project()

    return projects


# ============================================================
# PROJECT TECHNOLOGY EXTRACTION
# ============================================================

def extract_project_technologies(
    text: str,
) -> list[str]:
    """
    Extract technologies mentioned in project description.
    """

    if not text:
        return []

    technology_dictionary = [
        "python",
        "sql",
        "mysql",
        "pandas",
        "numpy",
        "scikit-learn",
        "xgboost",
        "tensorflow",
        "pytorch",
        "cnn",
        "computer vision",
        "flask",
        "fastapi",
        "streamlit",
        "docker",
        "aws",
        "dvc",
        "feast",
        "javascript",
        "html",
        "css",
        "git",
        "github",
    ]

    found = []

    normalized = text.lower()

    for technology in technology_dictionary:

        pattern = rf"\b{re.escape(technology)}\b"

        if re.search(
            pattern,
            normalized,
        ):
            found.append(technology)

    return found


# ============================================================
# EDUCATION EXTRACTION
# ============================================================

def extract_education(
    sections: dict[str, list[str]],
) -> list[Education]:
    """
    Extract education.

    Expected format:

        UNIVERSITY OF KERALA September 2022 — May 2025

        Bachelor of Science in Computer Science
        (University Institute of Technology, Yeroor)
    """

    lines = sections.get(
        "education",
        [],
    )

    if not lines:
        return []

    education = []

    institution = None
    education_year = None

    month_pattern = (
        r"(?:January|February|March|April|May|June|July|"
        r"August|September|October|November|December)"
    )

    institution_pattern = re.compile(
        rf"^(.+?)\s+"
        rf"{month_pattern}\s+\d{{4}}"
        rf"\s*[—–-]\s*"
        rf"{month_pattern}\s+\d{{4}}$",
        re.IGNORECASE,
    )

    for line in lines:

        # ----------------------------------------------------
        # Institution + dates
        # ----------------------------------------------------

        match = institution_pattern.match(line)

        if match:

            institution = match.group(1).strip()

            start_year_match = re.search(
                r"\d{4}",
                line,
            )

            if start_year_match:
                education_year = int(
                    start_year_match.group()
                )

            continue

        # ----------------------------------------------------
        # Degree
        # ----------------------------------------------------

        if line:

            education.append(
                Education(
                    degree=line,
                    institution=institution,
                    year=education_year,
                )
            )

            # Reset after one education entry.
            institution = None
            education_year = None

    return education


# ============================================================
# CERTIFICATION EXTRACTION
# ============================================================

def extract_certifications(
    sections: dict[str, list[str]],
) -> list[str]:
    """
    Extract certifications.
    """

    certifications = sections.get(
        "certifications",
        [],
    )

    return [
        clean_line(certification)
        for certification in certifications
        if clean_line(certification)
    ]


# ============================================================
# MAIN RESUME EXTRACTION
# ============================================================

def extract_resume(
    text: str,
    candidate_id: str,
) -> ResumeProfile:
    """
    Convert raw resume text into ResumeProfile.
    """

    if not text or not text.strip():

        return ResumeProfile(
            candidate_id=candidate_id
        )

    # --------------------------------------------------------
    # Split document
    # --------------------------------------------------------

    sections = split_sections(text)

    # --------------------------------------------------------
    # Extract fields
    # --------------------------------------------------------

    name = extract_name(text)

    summary = extract_summary(
        sections
    )

    skills = extract_skills(text)

    experience = extract_experience(
        sections
    )

    projects = extract_projects(
        sections
    )

    education = extract_education(
        sections
    )

    certifications = extract_certifications(
        sections
    )

    # --------------------------------------------------------
    # Create structured profile
    # --------------------------------------------------------

    return ResumeProfile(
        candidate_id=candidate_id,
        name=name,
        summary=summary,
        skills=skills,
        education=education,
        experience=experience,
        projects=projects,
        certifications=certifications,
    )