import uuid

from sqlalchemy import JSON, ForeignKey, Index, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    tenant_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tenants.id"),
        nullable=True,
        index=True,
    )

    actor_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=True,
    )

    action: Mapped[str] = mapped_column(String(100), nullable=False)

    resource_type: Mapped[str] = mapped_column(
        String(100), nullable=False
    )

    resource_id: Mapped[str | None] = mapped_column(String(100))

    details: Mapped[dict] = mapped_column(JSON, default=dict)

    ip_address: Mapped[str | None] = mapped_column(String(50))

    user_agent: Mapped[str | None] = mapped_column(Text)

    __table_args__ = (
        Index("ix_audit_tenant_action", "tenant_id", "action"),
    )