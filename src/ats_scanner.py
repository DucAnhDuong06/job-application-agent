COMMON_SKILLS = [
    "python",
    "java",
    "javascript",
    "html",
    "css",
    "sql",
    "git",
    "github",
    "docker",
    "aws",
    "azure",
    "linux",
    "excel",
    "communication",
    "teamwork",
    "problem solving",
    "data analysis",
    "machine learning",
    "ai",
    "api",
    "fastapi",
    "flask",
    "django",
]


def normalize_text(text: str) -> str:
    return text.lower()


def extract_skills(text: str) -> list[str]:
    normalized = normalize_text(text)

    found_skills = []

    for skill in COMMON_SKILLS:
        if skill in normalized:
            found_skills.append(skill)

    return found_skills


def scan_ats(job_description: str, resume_text: str) -> dict:
    jd_skills = extract_skills(job_description)
    resume_skills = extract_skills(resume_text)

    matched_skills = []
    missing_skills = []

    for skill in jd_skills:
        if skill in resume_skills:
            matched_skills.append(skill)
        else:
            missing_skills.append(skill)

    if len(jd_skills) == 0:
        score = 0
    else:
        score = int((len(matched_skills) / len(jd_skills)) * 100)

    return {
        "jd_skills": jd_skills,
        "resume_skills": resume_skills,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "score": score,
    }