from datetime import date
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class StaffCreate(BaseModel):
    department_id: UUID
    user_id: UUID | None = None

    employee_number: str = Field(min_length=1, max_length=50)
    full_name: str = Field(min_length=2, max_length=200)
    job_title: str = Field(min_length=2, max_length=150)

    email: EmailStr | None = None
    phone: str | None = Field(default=None, max_length=50)

    employment_type: str = Field(
        default="PERMANENT",
        pattern="^(PERMANENT|CONTRACT|TEMPORARY)$",
    )

    hire_date: date
    is_active: bool = True


class StaffUpdate(BaseModel):
    department_id: UUID | None = None
    user_id: UUID | None = None

    full_name: str | None = Field(default=None, min_length=2, max_length=200)
    job_title: str | None = Field(default=None, min_length=2, max_length=150)

    email: EmailStr | None = None
    phone: str | None = Field(default=None, max_length=50)

    employment_type: str | None = Field(
        default=None,
        pattern="^(PERMANENT|CONTRACT|TEMPORARY)$",
    )

    hire_date: date | None = None
    is_active: bool | None = None


class StaffResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    tenant_id: UUID
    department_id: UUID
    user_id: UUID | None

    employee_number: str
    full_name: str
    job_title: str

    email: EmailStr | None
    phone: str | None
    employment_type: str

    hire_date: date
    is_active: bool