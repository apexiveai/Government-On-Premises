import uuid

from sqlalchemy import Boolean, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class Tenant(Base, TimestampMixin):
    __tablename__ = "tenants"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    code: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False, index=True
    )

    name: Mapped[str] = mapped_column(
        String(255), nullable=False
    )

    municipality_type: Mapped[str] = mapped_column(
        String(50), default="MUNICIPALITY"
    )

    region: Mapped[str | None] = mapped_column(String(150))

    address: Mapped[str | None] = mapped_column(String(500))

    is_active: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False
    )