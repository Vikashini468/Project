from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel
from backend.ollama_client import evaluate_intro_with_llm

router = APIRouter()

class IntroRequest(BaseModel):
    intro: str

@router.post("/evaluate-intro")
def evaluate_intro(req: IntroRequest, request: Request):

    if not request.session.get("resume_uploaded"):
        raise HTTPException(403, "Resume not uploaded")

    if request.session.get("intro_done"):
        raise HTTPException(400, "Intro already completed")

    resume_data = request.session["resume_data"]

    feedback = evaluate_intro_with_llm(
        intro_text=req.intro,
        resume_text=request.session["resume_text"],
        branch=resume_data["branch"],
        skills=resume_data["skills"]
    )

    # ✅ SET ONLY HERE
    request.session["intro_done"] = True

    return {
        "feedback": feedback,
        "next": "tech"
    }

