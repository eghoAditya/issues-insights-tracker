from fastapi import FastAPI
from app.routes import router

app = FastAPI(title="Issues & Insights Tracker API")

# Include all our API routes
app.include_router(router)
