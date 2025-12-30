from fastapi import APIRouter, Request, HTTPException
from backend.ollama_client import generate_branch_question

router = APIRouter()
@router.get("/reset-session")
def reset_session(request: Request):
    request.session.clear()
    return {"status": "reset"}


@router.get("/generate-question")
def generate_question(request: Request):

    if not request.session.get("intro_done"):
        raise HTTPException(status_code=400, detail="Intro not completed")

    # If a question already exists → return it
    if request.session.get("current_question"):
        return {
            "question_no": request.session["tech_q_index"] + 1,
            "difficulty": request.session["current_level"],
            "question": request.session["current_question"]
        }

    tech_levels = request.session.get("tech_levels")
    if not tech_levels:
        raise HTTPException(status_code=400, detail="Tech levels missing")

    idx = request.session.get("tech_q_index", 0)

    if idx >= len(tech_levels):
        request.session["tech_done"] = True
        return {"done": True}

    level = tech_levels[idx]
    branch = request.session["branch"]

    question = generate_branch_question(
        branch=branch,
        level=level
    )

    # ✅ SAVE ONCE
    request.session["current_question"] = question
    request.session["current_level"] = level

    return {
        "question_no": idx + 1,
        "difficulty": level,
        "question": question
    }
