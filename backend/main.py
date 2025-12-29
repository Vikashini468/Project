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
from backend.intro_question import router as intro_q_router
from backend.tech_answer import router as tech_answer_router





app = FastAPI()

app.add_middleware(SessionMiddleware, secret_key="super-secret-key")

Base.metadata.create_all(bind=engine)

templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(auth_router)
app.include_router(resume_router)
app.include_router(interview_router)
app.include_router(intro_router)
app.include_router(intro_q_router)
app.include_router(tech_answer_router)
@app.get("/upload", response_class=HTMLResponse)
def upload_page(request: Request):
    return templates.TemplateResponse(
        "resume_upload.html",
        {"request": request}
    )

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.get("/register", response_class=HTMLResponse)
def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


@app.get("/chat", response_class=HTMLResponse)
def chat_page(request: Request):
    if "user" not in request.session:
        return RedirectResponse("/login")

    if "resume_text" not in request.session:
        return RedirectResponse("/upload")  # ⬅️ force resume upload

    return templates.TemplateResponse("chat.html", {
        "request": request
    })
