from fastapi import APIRouter, Form, Depends, Request, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from passlib.context import CryptContext

from backend.db import SessionLocal
from backend.models import User

router = APIRouter()

pwd_context = CryptContext(
    schemes=["argon2"],
    deprecated="auto"
)


# DB dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Password helpers
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


# REGISTER
@router.post("/register")
def register(
    name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
      print("RAW PASSWORD:", password)
      print("PASSWORD LENGTH:", len(password.encode("utf-8")))


      if len(password) < 6:
        raise HTTPException(
        status_code=400,
        detail="Password must be at least 6 characters"
    )

      if len(password.encode("utf-8")) > 72:
        raise HTTPException(
            status_code=400,
            detail="Password too long (max 72 characters)"
        )
      hashed = hash_password(password)
      print("HASH OK")

      existing_user = db.query(User).filter(User.email == email).first()
      if existing_user:
        return RedirectResponse("/login", status_code=303)

      new_user = User(
        name=name,
        email=email,
        password=hash_password(password)  # must match model field
    )

      db.add(new_user)
      db.commit()
      db.refresh(new_user)

      return RedirectResponse("/login", status_code=303)


# LOGIN
@router.post("/login")
def login(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.email == email).first()

    if not user or not verify_password(password, user.password):
        return RedirectResponse("/login", status_code=303)

    request.session["user"] = user.email
    return RedirectResponse("/upload", status_code=303)
