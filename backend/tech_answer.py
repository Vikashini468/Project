from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel
from backend.ollama_client import evaluate_answer_with_llm

router = APIRouter()

class AnswerRequest(BaseModel):
    answer: str


@router.post("/submit-answer")
def submit_answer(payload: AnswerRequest, request: Request):

    # ---- BASIC FLOW CHECKS ----
    if not request.session.get("intro_done"):
        raise HTTPException(status_code=400, detail="Intro not completed")

    if request.session.get("tech_done"):
        raise HTTPException(status_code=400, detail="Interview already completed")

    # ---- REQUIRED STATE ----
    question = request.session.get("current_question")
    level = request.session.get("current_level")
    branch = request.session.get("branch")

    if not all([question, level, branch]):
        raise HTTPException(
            status_code=400,
            detail="No active technical question"
        )

    # ---- EVALUATE ----
    feedback = evaluate_answer_with_llm(
        question=question,
        answer=payload.answer,
        branch=branch,
        level=level
    )

    # ---- ADVANCE INDEX ----
    request.session["tech_q_index"] += 1

    # ---- CHECK COMPLETION ----
    if request.session["tech_q_index"] >= len(request.session.get("tech_levels", [])):
        request.session["tech_done"] = True

    return {
        "feedback": feedback,
        "tech_done": request.session.get("tech_done", False)
    }
