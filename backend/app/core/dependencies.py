
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.core.database import (
    get_db,
    set_platform_admin_context,
    set_tenant_context,
)
from app.core.security import verify_access_token
from app.models.identity import Role, User
from app.models.platform_admin import PlatformAdmin

bearer_scheme = HTTPBearer(auto_error=False)


def unauthorized(detail: str = "Invalid or missing authentication credentials"):
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=detail,
        headers={"WWW-Authenticate": "Bearer"},
    )


def get_token_claims(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> dict:
    if credentials is None:
        raise unauthorized()

    try:
        return verify_access_token(credentials.credentials)
    except (JWTError, ValueError):
        raise unauthorized("Invalid or expired access token")


def get_current_user(
    claims: dict = Depends(get_token_claims),
    db: Session = Depends(get_db),
) -> User:
    tenant_claim = claims.get("tenant_id")
    subject = claims.get("sub")

    if not tenant_claim or not subject:
        raise unauthorized("Token is missing tenant_id or sub claim")

    try:
        tenant_id = UUID(str(tenant_claim))
    except (ValueError, TypeError):
        raise unauthorized("Invalid tenant_id claim")

    # RLS context must be established BEFORE querying the tenant-scoped user.
    set_tenant_context(db, str(tenant_id))

    statement = (
        select(User)
        .options(
            selectinload(User.roles).selectinload(Role.permissions)
        )
        .where(
            User.keycloak_subject == subject,
            User.tenant_id == tenant_id,
            User.is_active.is_(True),
        )
    )

    user = db.scalar(statement)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not registered or active in this municipality",
        )

    return user


def require_permission(permission_code: str):
    def permission_checker(
        current_user: User = Depends(get_current_user),
    ) -> User:
        user_permissions = {
            permission.code
            for role in current_user.roles
            for permission in role.permissions
        }

        if permission_code not in user_permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Missing required permission: {permission_code}",
            )

        return current_user

    return permission_checker


def get_platform_admin(
    claims: dict = Depends(get_token_claims),
    db: Session = Depends(get_db),
) -> PlatformAdmin:
    realm_access = claims.get("realm_access") or {}
    realm_roles = realm_access.get("roles") or []

    if "SUPER_ADMIN" not in realm_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Platform Super Admin role required",
        )

    subject = claims.get("sub")

    if not subject:
        raise unauthorized("Token is missing sub claim")

    # Set platform context before platform-level tenant operations.
    set_platform_admin_context(db)

    admin = db.scalar(
        select(PlatformAdmin).where(
            PlatformAdmin.keycloak_subject == subject,
            PlatformAdmin.is_active.is_(True),
        )
    )

    if admin is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Platform administrator is not registered or active",
        )

    return admin
