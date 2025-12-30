# backend/interview.py
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from backend.ollama_client import generate_branch_question

router = APIRouter()

@router.get("/generate-question")
def generate_question(request: Request):

    if not request.session.get("intro_done"):
        return JSONResponse(
            {"error": "Intro not completed"},
            status_code=400
        )

    if request.session.get("tech_done"):
        return {"done": True}

    idx = request.session.get("tech_q_index", 0)
    levels = request.session.get("tech_levels", [])

    if idx >= len(levels):
        request.session["tech_done"] = True
        return {"done": True}

    level = levels[idx]
    branch = request.session.get("branch")
    skills = request.session.get("skills")

    question = generate_branch_question(
        branch=branch,
        skills=skills,
        level=level
    )

    # ✅ THIS IS WHAT YOU WERE MISSING
    request.session["current_question"] = question
    request.session["current_level"] = level

    return {
        "question_no": idx + 1,
        "difficulty": level,
        "question": question
    }
