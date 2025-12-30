import os
import uuid
from fastapi import APIRouter, UploadFile, File, Request, HTTPException
from fastapi.responses import RedirectResponse
from PyPDF2 import PdfReader

from backend.llm import extract_skills_and_branch

router = APIRouter()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


def extract_text_from_pdf(path: str) -> str:
    reader = PdfReader(path)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text.strip()
@router.post("/upload-resume")
async def upload_resume(
    request: Request,
    resume: UploadFile = File(...)
):
    # 🔒 AUTH CHECK (YOU MISSED THIS)
    if "user" not in request.session:
        return RedirectResponse("/login", status_code=303)

    # Generate safe filename to prevent path traversal
    safe_filename = f"{uuid.uuid4()}.pdf"
    file_path = os.path.join(UPLOAD_DIR, safe_filename)

    with open(file_path, "wb") as f:
        f.write(await resume.read())

    resume_text = extract_text_from_pdf(file_path)
    extracted_data = extract_skills_and_branch(resume_text)

    # Resume data
    request.session["resume_uploaded"] = True
    request.session["resume_text"] = resume_text
    request.session["resume_data"] = extracted_data
    request.session["branch"] = extracted_data["branch"]
    request.session["skills"] = extracted_data["skills"]

    # Interview state
    request.session["intro_done"] = False
    request.session["tech_done"] = False
    request.session["tech_q_index"] = 0
    request.session["tech_levels"] = [
        "easy", "easy",
        "medium", "medium",
        "hard"
    ]

    return RedirectResponse("/chat", status_code=303)
