from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import require_permission
from app.models.department import Department
from app.models.identity import User
from app.models.staff import Staff
from app.schemas.staff import StaffCreate, StaffResponse, StaffUpdate

router = APIRouter(prefix="/staff", tags=["Staff"])


def validate_department(
    db: Session,
    tenant_id: UUID,
    department_id: UUID,
) -> Department:
    department = db.scalar(
        select(Department).where(
            Department.id == department_id,
            Department.tenant_id == tenant_id,
            Department.is_active.is_(True),
        )
    )

    if department is None:
        raise HTTPException(
            status_code=422,
            detail="Department does not exist or is inactive",
        )

    return department


def validate_user(
    db: Session,
    tenant_id: UUID,
    user_id: UUID | None,
) -> None:
    if user_id is None:
        return

    user = db.scalar(
        select(User).where(
            User.id == user_id,
            User.tenant_id == tenant_id,
            User.is_active.is_(True),
        )
    )

    if user is None:
        raise HTTPException(
            status_code=422,
            detail="Login account does not exist in this municipality",
        )


@router.post(
    "",
    response_model=StaffResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_staff(
    payload: StaffCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("staff.create")),
):
    validate_department(db, current_user.tenant_id, payload.department_id)
    validate_user(db, current_user.tenant_id, payload.user_id)

    existing = db.scalar(
        select(Staff).where(
            Staff.tenant_id == current_user.tenant_id,
            Staff.employee_number == payload.employee_number,
        )
    )

    if existing:
        raise HTTPException(
            status_code=409,
            detail="Employee number already exists",
        )

    if payload.user_id is not None:
        linked_staff = db.scalar(
            select(Staff).where(Staff.user_id == payload.user_id)
        )
        if linked_staff:
            raise HTTPException(
                status_code=409,
                detail="This login account is already linked to another staff record",
            )

    staff = Staff(
        tenant_id=current_user.tenant_id,
        **payload.model_dump(),
    )

    db.add(staff)
    db.flush()
    db.commit()

    return staff


@router.get("", response_model=list[StaffResponse])
def list_staff(
    department_id: UUID | None = None,
    active_only: bool = True,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("staff.read")),
):
    statement = select(Staff).where(
        Staff.tenant_id == current_user.tenant_id
    )

    if department_id is not None:
        statement = statement.where(Staff.department_id == department_id)

    if active_only:
        statement = statement.where(Staff.is_active.is_(True))

    return db.scalars(
        statement.order_by(Staff.employee_number.asc())
    ).all()


@router.get("/{staff_id}", response_model=StaffResponse)
def get_staff(
    staff_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("staff.read")),
):
    staff = db.scalar(
        select(Staff).where(
            Staff.id == staff_id,
            Staff.tenant_id == current_user.tenant_id,
        )
    )

    if staff is None:
        raise HTTPException(status_code=404, detail="Staff record not found")

    return staff


@router.patch("/{staff_id}", response_model=StaffResponse)
def update_staff(
    staff_id: UUID,
    payload: StaffUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("staff.update")),
):
    staff = db.scalar(
        select(Staff).where(
            Staff.id == staff_id,
            Staff.tenant_id == current_user.tenant_id,
        )
    )

    if staff is None:
        raise HTTPException(status_code=404, detail="Staff record not found")

    changes = payload.model_dump(exclude_unset=True)

    if "department_id" in changes:
        if changes["department_id"] is None:
            raise HTTPException(status_code=422, detail="Department is required")
        validate_department(
            db,
            current_user.tenant_id,
            changes["department_id"],
        )

    if "user_id" in changes:
        validate_user(
            db,
            current_user.tenant_id,
            changes["user_id"],
        )

        if changes["user_id"] is not None:
            linked_staff = db.scalar(
                select(Staff).where(
                    Staff.user_id == changes["user_id"],
                    Staff.id != staff.id,
                )
            )
            if linked_staff:
                raise HTTPException(
                    status_code=409,
                    detail="This login account is already linked to another staff record",
                )

    for field, value in changes.items():
        setattr(staff, field, value)

    db.flush()
    db.commit()

    return staff


@router.delete("/{staff_id}", status_code=status.HTTP_204_NO_CONTENT)
def deactivate_staff(
    staff_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("staff.deactivate")),
):
    staff = db.scalar(
        select(Staff).where(
            Staff.id == staff_id,
            Staff.tenant_id == current_user.tenant_id,
        )
    )

    if staff is None:
        raise HTTPException(status_code=404, detail="Staff record not found")

    staff.is_active = False
    db.commit()