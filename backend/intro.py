from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel
from backend.ollama_client import evaluate_intro_with_llm

router = APIRouter()


class IntroRequest(BaseModel):
    intro: str


@router.post("/evaluate-intro")
def evaluate_intro(payload: IntroRequest, request: Request):
    # ---------- STATE VALIDATION ----------
    if not request.session.get("resume_uploaded"):
        raise HTTPException(status_code=403, detail="Resume not uploaded")

    if request.session.get("intro_done"):
        raise HTTPException(status_code=400, detail="Intro already completed")

    if not payload.intro.strip():
        raise HTTPException(status_code=400, detail="Empty intro")

    resume_data = request.session.get("resume_data")
    if not resume_data:
        raise HTTPException(status_code=500, detail="Resume data missing")

    # ---------- LLM EVALUATION ----------
    feedback = evaluate_intro_with_llm(
        intro_text=payload.intro,
        resume_text=request.session["resume_text"],
        branch=resume_data["branch"],
        skills=resume_data["skills"]
    )

    # ---------- UPDATE STATE ----------
    request.session["intro_done"] = True

    return {
        "feedback": feedback
    }
