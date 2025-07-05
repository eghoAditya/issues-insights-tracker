from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from app import models, schemas, auth
from app.database import get_db
import shutil
import uuid
import os

router = APIRouter()

# Set up uploads directory
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


# --- Get All Issues (MAINTAINER or ADMIN) ---
@router.get("/issues/", response_model=list[schemas.IssueOut])
def list_issues(
    db: Session = Depends(get_db),
    # user: models.User = Depends(auth.require_maintainer)  # 👈 TEMPORARILY COMMENTED OUT
):
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
