
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings

engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def set_tenant_context(db: Session, tenant_id: str) -> None:
    """Set transaction-local tenant context for PostgreSQL RLS."""
    db.execute(
        text("SELECT set_config('app.current_tenant', :tenant_id, true)"),
        {"tenant_id": tenant_id},
    )
    db.execute(
        text("SELECT set_config('app.is_platform_admin', 'false', true)")
    )


def set_platform_admin_context(db: Session) -> None:
    """Grant platform-admin RLS context for the current transaction."""
    db.execute(
        text("SELECT set_config('app.is_platform_admin', 'true', true)")
    )
