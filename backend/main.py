from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import router
from app import auth  # ✅ import auth to include login route

app = FastAPI(title="Issues & Insights Tracker API")

# ✅ CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Frontend origin (adjust if needed)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ API routes
app.include_router(router)
# app.include_router(auth.router)  # ✅ Login route: /api/token
