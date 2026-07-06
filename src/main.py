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

SYSTEM_PROMPT = """
Ban la mot Job Application Agent.
Nhiem vu: giup ung vien phan tich job description va resume.
Khong duoc bia dat thong tin.
"""


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


def generate_demo_package(job_description: str, resume_text: str) -> str:
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

ATS MATCH SCORE
----------------
{score}/100

MATCHED SKILLS
--------------
{matched_text}

MISSING SKILLS
--------------
{missing_text}

RESUME SKILLS FOUND
-------------------
{", ".join(ats_result["resume_skills"]) if ats_result["resume_skills"] else "Không tìm thấy"}

JOB DESCRIPTION SKILLS FOUND
----------------------------
{", ".join(ats_result["jd_skills"]) if ats_result["jd_skills"] else "Không tìm thấy"}

=========================================
COVER LETTER
=========================================

Dear Hiring Manager,

I am excited to apply for this position.

Based on the job description, I already possess several required skills, including:

{matched_text}

I am also actively learning and improving in these areas:

{missing_text}

Thank you for your consideration.

Best regards,
Candidate

=========================================
RECRUITER EMAIL
=========================================

Subject: Application for Your Position

Hello,

I hope you are doing well.

I am interested in this opportunity and believe my current skills match many of your requirements.

Thank you for your time.

Best regards,
Candidate

=========================================
PROJECT STATUS
=========================================

Running in DEMO MODE
(No OpenAI API Key)

This report is generated using:
- Resume Parser
- Resume Info Extractor
- ATS Scanner
"""


def generate_job_package(job_description: str, resume_text: str) -> str:
    if USE_DEMO_MODE:
        return generate_demo_package(job_description, resume_text)

    user_prompt = f"""
JOB DESCRIPTION:
{job_description}

RESUME:
{resume_text}

Hay tao ket qua gom:
1. Match Report
2. Cover Letter
3. Recruiter Email
"""

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
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

    result = generate_job_package(job_description, resume_text)

    print("\n=== KET QUA ===\n")
    print(result)

    save_output(result)
    print("\nDa luu ket qua vao file output.md")


if __name__ == "__main__":
    main()