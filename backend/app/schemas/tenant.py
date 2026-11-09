
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class TenantCreate(BaseModel):
    code: str = Field(
        min_length=2,
        max_length=50,
        pattern=r"^[A-Z0-9_-]+$",
    )
    name: str = Field(min_length=2, max_length=255)
    municipality_type: str = "MUNICIPALITY"
    region: str | None = None
    address: str | None = None


class TenantResponse(BaseModel):
    id: UUID
    code: str
    name: str
    municipality_type: str
    region: str | None
    address: str | None
    is_active: bool

    model_config = ConfigDict(from_attributes=True)
