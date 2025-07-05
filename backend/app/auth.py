from datetime import datetime, timedelta
from typing import Optional

from fastapi import HTTPException, Depends, Request, APIRouter
from fastapi.responses import RedirectResponse
from jose import jwt, JWTError
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer
from urllib.parse import urlencode
from app import models, schemas
from app.database import get_db
import httpx
import os

router = APIRouter()

# --- Config ---
SECRET_KEY = "super-secret-key"  # Use env in prod
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/token")

# --- Auth Helpers ---
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

# --- User Retrieval ---
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> models.User:
    payload = decode_token(token)
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = db.query(models.User).filter(models.User.id == int(user_id)).first()
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")

    return user

# --- Role Checks ---
def require_admin(user: models.User = Depends(get_current_user)):
    if user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="Admin access required")
    return user

def require_maintainer(user: models.User = Depends(get_current_user)):
    if user.role not in ("ADMIN", "MAINTAINER"):
        raise HTTPException(status_code=403, detail="Maintainer access required")
    return user

def require_reporter(user: models.User = Depends(get_current_user)):
    if user.role not in ("ADMIN", "REPORTER"):
        raise HTTPException(status_code=403, detail="Reporter access required")
    return user

# --- Google OAuth Flow ---
@router.get("/auth/google")
def google_login():
    params = urlencode({
        "client_id": GOOGLE_CLIENT_ID,
        "response_type": "code",
        "redirect_uri": GOOGLE_REDIRECT_URI,
        "scope": "openid email profile",
        "access_type": "offline",
        "prompt": "consent"
    })
    return RedirectResponse(f"https://accounts.google.com/o/oauth2/v2/auth?{params}")

@router.get("/auth/google/callback")
async def google_callback(request: Request, db: Session = Depends(get_db)):
    code = request.query_params.get("code")
    if not code:
        raise HTTPException(status_code=400, detail="Missing code in callback")

    async with httpx.AsyncClient() as client:
        # Step 1: Exchange code for token
        token_res = await client.post("https://oauth2.googleapis.com/token", data={
            "code": code,
            "client_id": GOOGLE_CLIENT_ID,
            "client_secret": GOOGLE_CLIENT_SECRET,
            "redirect_uri": GOOGLE_REDIRECT_URI,
            "grant_type": "authorization_code"
        })

        if token_res.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to fetch token from Google")

        token_data = token_res.json()
        access_token = token_data["access_token"]

        # Step 2: Get user info
        user_res = await client.get("https://www.googleapis.com/oauth2/v2/userinfo", headers={
            "Authorization": f"Bearer {access_token}"
        })

        if user_res.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to fetch user info from Google")

        user_data = user_res.json()
        email = user_data["email"]

        # Step 3: Check if user exists in DB, else create
        user = db.query(models.User).filter(models.User.email == email).first()
        if not user:
            user = models.User(email=email, hashed_password="GOOGLE_OAUTH", role="REPORTER")
            db.add(user)
            db.commit()
            db.refresh(user)

        # ✅ Token now includes email
        token = create_access_token({"sub": str(user.id), "email": user.email})
        return {"access_token": token, "token_type": "bearer"}
