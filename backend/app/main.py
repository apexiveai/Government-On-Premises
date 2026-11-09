from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import settings

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=(
        "ApexiveAI Municipal OS - "
        "Multi-Municipality Government Management Platform"
    ),
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    allow_headers=["Authorization", "Content-Type", "X-Request-ID"],
)

app.include_router(
    api_router,
    prefix=settings.API_V1_PREFIX,
)


@app.get("/")
def root():
    return {
        "product": "ApexiveAI Municipal OS",
        "version": settings.APP_VERSION,
        "status": "operational",
    }