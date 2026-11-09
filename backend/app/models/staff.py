from sqlalchemy import (
    Boolean,
    Date,
    ForeignKey,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, uuid_column


class Staff(Base, TimestampMixin):
    __tablename__ = "staff"

    __table_args__ = (
        UniqueConstraint(
            "tenant_id",
            "employee_number",
            name="uq_staff_tenant_employee_number",
        ),
    )

    id: Mapped[str] = uuid_column()

    tenant_id: Mapped[str] = mapped_column(
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    department_id: Mapped[str] = mapped_column(
        ForeignKey("departments.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    # Optional login account. A staff member may exist without system access.
    user_id: Mapped[str | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        unique=True,
    )

    employee_number: Mapped[str] = mapped_column(String(50), nullable=False)
    full_name: Mapped[str] = mapped_column(String(200), nullable=False)
    job_title: Mapped[str] = mapped_column(String(150), nullable=False)

    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(50), nullable=True)

    employment_type: Mapped[str] = mapped_column(
        String(30),
        default="PERMANENT",
        nullable=False,
    )

    hire_date: Mapped[Date] = mapped_column(Date, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    department = relationship("Department", back_populates="staff_members")
    user = relationship("User")