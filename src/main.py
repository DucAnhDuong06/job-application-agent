import os
from dotenv import load_dotenv
from openai import OpenAI
from ats_scanner import scan_ats
from resume_parser import read_resume, extract_resume_info

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
USE_DEMO_MODE = api_key is None or api_key.strip() == ""

if not USE_DEMO_MODE:
    client = OpenAI(api_key=api_key)


def read_multiline_input(title: str) -> str:
    print(f"\n{title}")
    print("Dan noi dung vao day. Bam Enter 2 lan de ket thuc:\n")

    lines = []
    empty_count = 0

    while True:
        line = input()

        if line.strip() == "":
            empty_count += 1
            if empty_count >= 2:
                break
        else:
            empty_count = 0
            lines.append(line)

    return "\n".join(lines).strip()


def format_list(items: list[str]) -> str:
    if not items:
        return "- Không tìm thấy"

    return "\n".join([f"- {item}" for item in items])


def generate_demo_package(job_description: str, resume_text: str, resume_info: dict) -> str:
    ats_result = scan_ats(job_description, resume_text)

    matched = ats_result["matched_skills"]
    missing = ats_result["missing_skills"]
    score = ats_result["score"]

    matched_text = "\n".join([f"✓ {skill.title()}" for skill in matched]) if matched else "Không tìm thấy kỹ năng phù hợp."
    missing_text = "\n".join([f"✗ {skill.title()}" for skill in missing]) if missing else "Không có kỹ năng nào bị thiếu."

    return f"""
=========================================
        JOB APPLICATION REPORT
=========================================

CANDIDATE
---------
{resume_info["name"]}

ATS MATCH SCORE
---------------
{score}/100

MATCHED SKILLS
--------------
{matched_text}

MISSING SKILLS
--------------
{missing_text}

=========================================
STRUCTURED RESUME DATA
=========================================

SUMMARY
-------
{resume_info["summary"]}

EDUCATION
---------
{format_list(resume_info["education"])}

EXPERIENCE
----------
{format_list(resume_info["experience"])}

SKILLS
------
{format_list(resume_info["skills"])}

LANGUAGES
---------
{format_list(resume_info["languages"])}

=========================================
COVER LETTER
=========================================

Dear Hiring Manager,

I am excited to apply for this position.

Based on the job description, my background matches several important requirements, including:

{matched_text}

I am also continuing to improve in the following areas:

{missing_text}

Thank you for your time and consideration.

Best regards,
{resume_info["name"]}

=========================================
RECRUITER EMAIL
=========================================

Subject: Application for Your Position

Hello,

I hope you are doing well.

My name is {resume_info["name"]}, and I am interested in this opportunity. Based on my resume, I match several of the required skills and would appreciate the opportunity to discuss my background further.

Thank you for your time.

Best regards,
{resume_info["name"]}

=========================================
PROJECT STATUS
=========================================

Version: v0.4 Resume Structure Parser
Mode: DEMO MODE
"""


def generate_job_package(job_description: str, resume_text: str, resume_info: dict) -> str:
    if USE_DEMO_MODE:
        return generate_demo_package(job_description, resume_text, resume_info)

    user_prompt = f"""
JOB DESCRIPTION:
{job_description}

RESUME STRUCTURE:
{resume_info}

FULL RESUME TEXT:
{resume_text}

Create:
1. Match Report
2. Cover Letter
3. Recruiter Email

Do not invent information.
"""

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": "You are a professional job application assistant. Do not fabricate resume details."},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.3,
    )

    return response.choices[0].message.content


def save_output(content: str, filename: str = "output.md") -> None:
    with open(filename, "w", encoding="utf-8") as file:
        file.write(content)


def main() -> None:
    print("=== JOB APPLICATION AGENT MVP ===")

    if USE_DEMO_MODE:
        print("Dang chay DEMO MODE vi chua co OpenAI API Key.")
    else:
        print("Dang chay AI MODE voi OpenAI API Key.")

    job_description = read_multiline_input("BUOC 1: Paste Job Description")

    resume_text = read_resume("data/resume.pdf")
    resume_info = extract_resume_info(resume_text)

    print("\n===== RESUME INFO =====\n")
    print(resume_info)

    if not job_description or not resume_text:
        print("Ban can nhap Job Description va dam bao file data/resume.pdf ton tai.")
        return

    print("\nAgent dang phan tich...\n")

    result = generate_job_package(job_description, resume_text, resume_info)

    print("\n=== KET QUA ===\n")
    print(result)

    save_output(result)
    print("\nDa luu ket qua vao file output.md")


if __name__ == "__main__":
    main()