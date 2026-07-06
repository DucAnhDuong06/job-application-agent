from pypdf import PdfReader


def read_resume(pdf_path: str) -> str:

    reader = PdfReader(pdf_path)

    text = ""

    for page in reader.pages:
        page_text = page.extract_text()

        if page_text:
            text += page_text + "\n"

    return text

def extract_resume_info(text: str) -> dict:
    """
    Phân tích nội dung CV thành dữ liệu có cấu trúc.
    """

    resume = {
        "name": "",
        "skills": [],
        "languages": []
    }

    lines = [line.strip() for line in text.split("\n") if line.strip()]

    if lines:
        resume["name"] = lines[0]

    collecting_skills = False
    collecting_languages = False

    for line in lines:

        upper = line.upper()

        if upper == "SKILLS":
            collecting_skills = True
            collecting_languages = False
            continue

        if upper == "LANGUAGES":
            collecting_languages = True
            collecting_skills = False
            continue

        if upper in [
            "SUMMARY",
            "EDUCATION",
            "EXPERIENCE",
            "HONORS & AWARDS",
            "LEADERSHIP & ACTIVITIES",
        ]:
            collecting_skills = False
            collecting_languages = False

        if collecting_skills:
            resume["skills"].append(line)

        if collecting_languages:
            resume["languages"].append(line)

    return resume