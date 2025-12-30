from fastapi import APIRouter, Request

router = APIRouter()

@router.get("/debug-session")
def debug_session(request: Request):
    return dict(request.session)
