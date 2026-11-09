
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user, get_platform_admin
from app.models.audit import AuditLog
from app.models.identity import User
from app.models.platform_admin import PlatformAdmin
from app.models.tenant import Tenant
from app.schemas.tenant import TenantCreate, TenantResponse

router = APIRouter(prefix="/tenants", tags=["Tenants"])


@router.post(
    "",
    response_model=TenantResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_tenant(
    payload: TenantCreate,
    db: Session = Depends(get_db),
    platform_admin: PlatformAdmin = Depends(get_platform_admin),
):
    existing = db.scalar(
        select(Tenant).where(Tenant.code == payload.code)
    )

    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Municipality code already exists",
        )

    tenant = Tenant(
        code=payload.code,
        name=payload.name,
        municipality_type=payload.municipality_type,
        region=payload.region,
        address=payload.address,
        is_active=True,
    )

    try:
        db.add(tenant)
        db.flush()

        audit = AuditLog(
            tenant_id=tenant.id,
            actor_id=None,
            action="TENANT_CREATED",
            resource_type="tenant",
            resource_id=str(tenant.id),
            details={
                "tenant_code": tenant.code,
                "created_by_platform_admin": str(platform_admin.id),
            },
        )

        db.add(audit)

        # Refresh before commit, while the platform RLS context is active.
        db.refresh(tenant)

        db.commit()
        return tenant

    except Exception:
        db.rollback()
        raise


@router.get("/current")
def get_current_tenant(
    current_user: User = Depends(get_current_user),
):
    return {
        "tenant_id": str(current_user.tenant_id),
        "user_id": str(current_user.id),
    }


@router.get("", response_model=list[TenantResponse])
def list_tenants(
    db: Session = Depends(get_db),
    platform_admin: PlatformAdmin = Depends(get_platform_admin),
):
    return db.scalars(
        select(Tenant).order_by(Tenant.created_at.desc())
    ).all()
