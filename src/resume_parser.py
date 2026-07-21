from pypdf import PdfReader


def read_resume(pdf_path: str) -> str:
    reader = PdfReader(pdf_path)

    text = ""

    for page in reader.pages:
        page_text = page.extract_text()

        if page_text:
            text += page_text + "\n"

    return text


def clean_bullet(line: str) -> str:
    return (
        line.replace("", "")
        .replace("•", "")
        .replace("·", "")
        .strip()
    )


def extract_section(lines: list[str], start_title: str, end_titles: list[str]) -> list[str]:
    collecting = False
    result = []

    for line in lines:
        upper = line.upper()

        if upper == start_title:
            collecting = True
            continue

        if collecting and upper in end_titles:
            break

        if collecting:
            cleaned = clean_bullet(line)
            if cleaned:
                result.append(cleaned)

    return result


def split_skills(skill_lines: list[str]) -> list[str]:
    skills = []

    for line in skill_lines:
        if ":" in line:
            line = line.split(":", 1)[1]

        parts = line.split(",")

        for part in parts:
            skill = part.strip()
            if skill:
                skills.append(skill)

    return skills


def split_languages(language_lines: list[str]) -> list[str]:
    languages = []

    for line in language_lines:
        cleaned = clean_bullet(line)
        if cleaned:
            languages.append(cleaned)

    return languages


def extract_resume_info(text: str) -> dict:
    lines = [clean_bullet(line) for line in text.split("\n") if line.strip()]

    section_titles = [
        "SUMMARY",
        "EDUCATION",
        "EXPERIENCE",
        "LEADERSHIP & ACTIVITIES",
        "HONORS & AWARDS",
        "SKILLS",
        "LANGUAGES",
    ]

    resume = {
        "name": lines[0] if lines else "",
        "summary": "",
        "education": [],
        "experience": [],
        "leadership": [],
        "honors_awards": [],
        "skills": [],
        "languages": [],
    }

    summary_lines = extract_section(lines, "SUMMARY", section_titles)
    education_lines = extract_section(lines, "EDUCATION", section_titles)
    experience_lines = extract_section(lines, "EXPERIENCE", section_titles)
    leadership_lines = extract_section(lines, "LEADERSHIP & ACTIVITIES", section_titles)
    honors_lines = extract_section(lines, "HONORS & AWARDS", section_titles)
    skill_lines = extract_section(lines, "SKILLS", section_titles)
    language_lines = extract_section(lines, "LANGUAGES", section_titles)

    resume["summary"] = " ".join(summary_lines)
    resume["education"] = education_lines
    resume["experience"] = experience_lines
    resume["leadership"] = leadership_lines
    resume["honors_awards"] = honors_lines
    resume["skills"] = split_skills(skill_lines)
    resume["languages"] = split_languages(language_lines)

    return resume