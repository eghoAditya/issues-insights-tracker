from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Request
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
import shutil
import uuid
import os
import requests

from app import models, schemas, auth
from app.database import get_db

router = APIRouter()

# --- Include auth router ---
router.include_router(auth.router)  # ✅ this includes Google OAuth endpoints

# --- Traditional Login ---
@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = auth.create_access_token({"sub": str(user.id)})
    return {"access_token": token, "token_type": "bearer"}


# --- Google OAuth Login (receives Google ID token from frontend) ---
@router.post("/login/google")
async def login_with_google(request: Request, db: Session = Depends(get_db)):
    data = await request.json()
    token = data.get("token")
    if not token:
        raise HTTPException(status_code=400, detail="Google ID token missing")

    resp = requests.get(f"https://oauth2.googleapis.com/tokeninfo?id_token={token}")
    if resp.status_code != 200:
        raise HTTPException(status_code=401, detail="Invalid Google token")

    info = resp.json()
    email = info.get("email")
    if not email:
        raise HTTPException(status_code=400, detail="Email not found in Google token")

    user = db.query(models.User).filter(models.User.email == email).first()
    if not user:
        user = models.User(email=email, hashed_password="", role="REPORTER")
        db.add(user)
        db.commit()
        db.refresh(user)

    access_token = auth.create_access_token(data={"sub": str(user.id)})
    return {"access_token": access_token, "token_type": "bearer"}


# --- Uploads Directory ---
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# --- Create Issue (REPORTER or ADMIN) ---
@router.post("/issues/", response_model=schemas.IssueOut)
def create_issue(
    title: str = Form(...),
    description: str = Form(...),
    severity: schemas.Severity = Form(...),
    file: UploadFile = File(None),
    db: Session = Depends(get_db),
    user: models.User = Depends(auth.require_reporter),
):
    filename = None
    if file:
        file_ext = os.path.splitext(file.filename)[1]
        filename = f"{uuid.uuid4()}{file_ext}"
        file_path = os.path.join(UPLOAD_DIR, filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

    new_issue = models.Issue(
        title=title,
        description=description,
        severity=severity,
        reporter_id=user.id,
        file_path=filename
    )
    db.add(new_issue)
    db.commit()
    db.refresh(new_issue)
    return new_issue


# --- Get Own Issues (REPORTER only) ---
@router.get("/issues/my", response_model=list[schemas.IssueOut])
def get_own_issues(db: Session = Depends(get_db),
                   user: models.User = Depends(auth.require_reporter)):
    return db.query(models.Issue).filter(models.Issue.reporter_id == user.id).all()


# --- Get All Issues (TEMP: public for now) ---
@router.get("/issues/", response_model=list[schemas.IssueOut])
def list_issues(db: Session = Depends(get_db)):
    return db.query(models.Issue).all()


# --- Update Issue Status (MAINTAINER or ADMIN) ---
@router.patch("/issues/{issue_id}", response_model=schemas.IssueOut)
def update_issue(issue_id: int,
                 status: schemas.Status,
                 db: Session = Depends(get_db),
                 user: models.User = Depends(auth.require_maintainer)):

    issue = db.query(models.Issue).filter(models.Issue.id == issue_id).first()
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")

    issue.status = status
    db.commit()
    db.refresh(issue)
    return issue


# --- Delete Issue (ADMIN only) ---
@router.delete("/issues/{issue_id}")
def delete_issue(issue_id: int,
                 db: Session = Depends(get_db),
                 user: models.User = Depends(auth.require_admin)):

    issue = db.query(models.Issue).filter(models.Issue.id == issue_id).first()
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")

    db.delete(issue)
    db.commit()
    return {"msg": "Issue deleted"}
