# backend/tech_answer.py
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from backend.ollama_client import evaluate_technical_answer

router = APIRouter()

@router.post("/submit-answer")
def submit_answer(request: Request, payload: dict):

    answer = payload.get("answer")
    question = request.session.get("current_question")
    level = request.session.get("current_level")
    branch = request.session.get("branch")

    # 🚨 HARD VALIDATION
    if not question:
        return JSONResponse(
            {"error": "Interview state corrupted (missing question)"},
            status_code=400
        )

    if not answer:
        return JSONResponse(
            {"error": "Empty answer"},
            status_code=400
        )

    feedback = evaluate_technical_answer(
        question=question,
        answer=answer,
        branch=branch,
        level=level
    )

    # advance index
    request.session["tech_q_index"] += 1

    return {"feedback": feedback}
