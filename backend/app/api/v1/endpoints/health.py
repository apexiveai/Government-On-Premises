from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.database import get_db

router = APIRouter()


@router.get("/health")
def health():
    return {
        "status": "healthy",
        "service": "municipal-os-api",
    }


@router.get("/health/ready")
def readiness(db: Session = Depends(get_db)):
    db.execute(text("SELECT 1"))

    return {
        "status": "ready",
        "database": "connected",
    }