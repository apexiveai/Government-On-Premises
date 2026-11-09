from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import require_permission
from app.models.department import Department
from app.models.identity import User
from app.schemas.department import (
    DepartmentCreate,
    DepartmentResponse,
    DepartmentUpdate,
)

router = APIRouter(prefix="/departments", tags=["Departments"])


@router.post(
    "",
    response_model=DepartmentResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_department(
    payload: DepartmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("department.create")),
):
    existing = db.scalar(
        select(Department).where(
            Department.tenant_id == current_user.tenant_id,
            Department.code == payload.code,
        )
    )

    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Department code already exists",
        )

    department = Department(
        tenant_id=current_user.tenant_id,
        code=payload.code,
        name=payload.name,
        description=payload.description,
        is_active=True,
    )

    db.add(department)
    db.flush()
    db.commit()

    return department


@router.get("", response_model=list[DepartmentResponse])
def list_departments(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("department.read")),
):
    return db.scalars(
        select(Department)
        .where(Department.tenant_id == current_user.tenant_id)
        .order_by(Department.name.asc())
    ).all()


@router.get("/{department_id}", response_model=DepartmentResponse)
def get_department(
    department_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("department.read")),
):
    department = db.scalar(
        select(Department).where(
            Department.id == department_id,
            Department.tenant_id == current_user.tenant_id,
        )
    )

    if department is None:
        raise HTTPException(status_code=404, detail="Department not found")

    return department


@router.patch("/{department_id}", response_model=DepartmentResponse)
def update_department(
    department_id: UUID,
    payload: DepartmentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("department.update")),
):
    department = db.scalar(
        select(Department).where(
            Department.id == department_id,
            Department.tenant_id == current_user.tenant_id,
        )
    )

    if department is None:
        raise HTTPException(status_code=404, detail="Department not found")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(department, field, value)

    db.flush()
    db.commit()
    
    return department


@router.delete("/{department_id}", status_code=status.HTTP_204_NO_CONTENT)
def deactivate_department(
    department_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("department.deactivate")),
):
    department = db.scalar(
        select(Department).where(
            Department.id == department_id,
            Department.tenant_id == current_user.tenant_id,
        )
    )

    if department is None:
        raise HTTPException(status_code=404, detail="Department not found")

    # Soft delete: retain historical staff and department records.
    department.is_active = False
    db.commit()