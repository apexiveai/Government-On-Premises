from fastapi import APIRouter

from app.api.v1.endpoints import departments, health, staff, tenants

api_router = APIRouter()

api_router.include_router(health.router)
api_router.include_router(tenants.router)
api_router.include_router(departments.router)
api_router.include_router(staff.router)