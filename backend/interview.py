from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from backend.ollama_client import generate_branch_question

router = APIRouter()

@router.get("/chat-state")
def chat_state(request: Request):
    return {
        "intro_done": request.session.get("intro_done", False)
    }


@router.get("/generate-question")
def generate_question(request: Request):

    # 🔒 BLOCK if intro not completed
    if not request.session.get("intro_done"):
        return JSONResponse(
            {"error": "Intro not completed"},
            status_code=400
        )

    # ✅ Interview already finished
    if request.session.get("tech_done"):
        return {"done": True}

    idx = request.session.get("tech_q_index", 0)
    levels = request.session.get("tech_levels")

    # 🔒 Safety check
    if not levels:
        return JSONResponse(
            {"error": "Interview state corrupted"},
            status_code=500
        )

    # ✅ All questions asked
    if idx >= len(levels):
        request.session["tech_done"] = True
        return {"done": True}

    level = levels[idx]

    # 🔒 Required session data
    branch = request.session.get("branch")
    skills = request.session.get("skills")

    if not branch or not skills:
        return JSONResponse(
            {"error": "Resume data missing"},
            status_code=500
        )

    # 🧠 Ollama generates question (NOT predefined)
    question = generate_branch_question(
        branch=branch,
        skills=skills,
        level=level
    )

    # 🔒 Persist current question state
    request.session["current_question"] = question
    request.session["current_level"] = level

    return {
        "question_no": idx + 1,
        "difficulty": level,
        "question": question
    }
