from fastapi import APIRouter

router = APIRouter()

@router.get("/intro-question")
def intro_question():
    return {"question": "Tell me about yourself."}
