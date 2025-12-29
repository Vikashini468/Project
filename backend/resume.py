import os
import json
import uuid
from fastapi import APIRouter, UploadFile, File, Request
from fastapi.responses import RedirectResponse
from PyPDF2 import PdfReader
from backend.ollama_client import evaluate_technical_answer

from backend.llm import extract_skills_and_branch

router = APIRouter()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


def extract_text_from_pdf(file_path: str) -> str:
    reader = PdfReader(file_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text


@router.post("/upload-resume")
async def upload_resume(
    request: Request,
    resume: UploadFile = File(...)
):
    file_path = os.path.join(UPLOAD_DIR, resume.filename)

    with open(file_path, "wb") as f:
        f.write(await resume.read())

    resume_text = extract_text_from_pdf(file_path)
    extracted_data = extract_skills_and_branch(resume_text)

    request.session["resume_uploaded"] = True
    request.session["resume_text"] = resume_text
    request.session["resume_data"] = extracted_data
    request.session["branch"] = extracted_data["branch"]
    request.session["skills"] = extracted_data["skills"]

    return RedirectResponse("/chat", status_code=303)

