from __future__ import annotations

from datetime import datetime
from typing import Optional

from bson import ObjectId
from pydantic import BaseModel, Field


# PUBLIC_INTERFACE
def object_id_from_str(value: str) -> ObjectId:
    """Parse an ObjectId from a string or raise ValueError for invalid input."""
    try:
        return ObjectId(value)
    except Exception as exc:  # pragma: no cover
        raise ValueError("Invalid ObjectId") from exc


class ItemBase(BaseModel):
    """Common editable fields for an item."""

    name: str = Field(..., description="Human-readable item name", min_length=1)
    description: Optional[str] = Field(
        default=None, description="Optional item description"
    )


class ItemCreate(ItemBase):
    """Payload for creating an item."""


class ItemUpdate(BaseModel):
    """Payload for updating an item (all fields optional)."""

    name: Optional[str] = Field(default=None, description="Human-readable item name")
    description: Optional[str] = Field(
        default=None, description="Optional item description"
    )


class ItemOut(ItemBase):
    """Response model for an item."""

    id: str = Field(..., description="MongoDB ObjectId as string")
    created_at: datetime = Field(..., description="UTC creation timestamp")
