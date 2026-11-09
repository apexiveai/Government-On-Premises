from sqlalchemy import Boolean, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, uuid_column


class Department(Base, TimestampMixin):
    __tablename__ = "departments"

    __table_args__ = (
        UniqueConstraint(
            "tenant_id",
            "code",
            name="uq_department_tenant_code",
        ),
    )

    id: Mapped[str] = uuid_column()

    tenant_id: Mapped[str] = mapped_column(
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    code: Mapped[str] = mapped_column(String(50), nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    staff_members = relationship(
        "Staff",
        back_populates="department",
        cascade="all, delete-orphan",
    )