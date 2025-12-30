from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from backend.db import engine, Base
from backend.auth import router as auth_router
from backend.resume import router as resume_router
from backend.interview import router as interview_router
from backend.intro import router as intro_router
from backend.tech_answer import router as tech_answer_router
from backend.debug import router as debug_router

# ---------------- APP ----------------
app = FastAPI()

app.add_middleware(
    SessionMiddleware,
    secret_key="super-secret-key",
    same_site="lax",
    https_only=False 
)

Base.metadata.create_all(bind=engine)

templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# ---------------- ROUTERS ----------------
app.include_router(auth_router)
app.include_router(resume_router)
app.include_router(interview_router)
app.include_router(intro_router)
app.include_router(tech_answer_router)
app.include_router(debug_router)
# ---------------- PAGES ----------------
@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/register", response_class=HTMLResponse)
def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@app.get("/upload", response_class=HTMLResponse)
def upload_page(request: Request):
    if "user" not in request.session:
        return RedirectResponse("/login", status_code=303)
    return templates.TemplateResponse("resume_upload.html", {"request": request})

@app.get("/chat", response_class=HTMLResponse)
def chat_page(request: Request):
    if "user" not in request.session:
        return RedirectResponse("/login", status_code=303)

    if not request.session.get("resume_uploaded"):
        return RedirectResponse("/upload", status_code=303)

    return templates.TemplateResponse("chat.html", {"request": request})

# ---------------- CHAT STATE (CRITICAL) ----------------
@app.get("/chat-state")
def chat_state(request: Request):
    return {
        "resume_uploaded": request.session.get("resume_uploaded", False),
        "intro_done": request.session.get("intro_done", False),
        "tech_done": request.session.get("tech_done", False),
    }

@app.post("/chat")
def chat_endpoint(request: Request):
    """Unified chat endpoint for frontend compatibility"""
    return {
        "bot_message": "Please use the specific endpoints for interview flow.",
        "resume_uploaded": request.session.get("resume_uploaded", False),
        "intro_done": request.session.get("intro_done", False),
        "tech_done": request.session.get("tech_done", False),
    }

# ---------------- DEBUG ----------------
@app.get("/debug-session")
def debug_session(request: Request):
    return dict(request.session)
