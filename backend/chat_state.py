from fastapi import APIRouter, Request

router = APIRouter()


@router.get("/chat-state")
def chat_state(request: Request):
    return {
        "resume_uploaded": request.session.get("resume_uploaded", False),
        "intro_done": request.session.get("intro_done", False),
        "tech_done": request.session.get("tech_done", False),
        "tech_q_index": request.session.get("tech_q_index", 0)
    }
