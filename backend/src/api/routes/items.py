from __future__ import annotations

from datetime import datetime, timezone
from typing import List

from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, Path, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from src.api.db import get_db
from src.api.models import ItemCreate, ItemOut, ItemUpdate, object_id_from_str

router = APIRouter(prefix="/items", tags=["items"])


def _item_doc_to_out(doc: dict) -> ItemOut:
    """Convert a MongoDB document to the ItemOut model."""
    return ItemOut(
        id=str(doc["_id"]),
        name=doc["name"],
        description=doc.get("description"),
        created_at=doc["created_at"],
    )


@router.post(
    "",
    response_model=ItemOut,
    status_code=status.HTTP_201_CREATED,
    summary="Create item",
    description="Create a new item in the MongoDB `items` collection.",
    operation_id="create_item",
)
async def create_item(payload: ItemCreate, db: AsyncIOMotorDatabase = Depends(get_db)) -> ItemOut:
    created_at = datetime.now(timezone.utc)
    doc = {"name": payload.name, "description": payload.description, "created_at": created_at}
    result = await db["items"].insert_one(doc)
    doc["_id"] = result.inserted_id
    return _item_doc_to_out(doc)


@router.get(
    "",
    response_model=List[ItemOut],
    summary="List items",
    description="List items from the MongoDB `items` collection.",
    operation_id="list_items",
)
async def list_items(db: AsyncIOMotorDatabase = Depends(get_db)) -> List[ItemOut]:
    cursor = db["items"].find({}).sort("created_at", -1)
    docs = await cursor.to_list(length=1000)
    return [_item_doc_to_out(d) for d in docs]


@router.get(
    "/{id}",
    response_model=ItemOut,
    summary="Get item",
    description="Fetch a single item by its MongoDB ObjectId.",
    operation_id="get_item",
)
async def get_item(
    id: str = Path(..., description="MongoDB ObjectId string"),
    db: AsyncIOMotorDatabase = Depends(get_db),
) -> ItemOut:
    try:
        oid: ObjectId = object_id_from_str(id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid ObjectId")

    doc = await db["items"].find_one({"_id": oid})
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    return _item_doc_to_out(doc)


@router.put(
    "/{id}",
    response_model=ItemOut,
    summary="Update item",
    description="Update an existing item by its MongoDB ObjectId.",
    operation_id="update_item",
)
async def update_item(
    payload: ItemUpdate,
    id: str = Path(..., description="MongoDB ObjectId string"),
    db: AsyncIOMotorDatabase = Depends(get_db),
) -> ItemOut:
    try:
        oid: ObjectId = object_id_from_str(id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid ObjectId")

    update_doc: dict = {}
    if payload.name is not None:
        update_doc["name"] = payload.name
    if payload.description is not None:
        update_doc["description"] = payload.description

    if not update_doc:
        # No-op update; still return current record if it exists
        doc = await db["items"].find_one({"_id": oid})
        if not doc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
        return _item_doc_to_out(doc)

    result = await db["items"].find_one_and_update(
        {"_id": oid},
        {"$set": update_doc},
        return_document=True,
    )
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    return _item_doc_to_out(result)


@router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete item",
    description="Delete an existing item by its MongoDB ObjectId.",
    operation_id="delete_item",
)
async def delete_item(
    id: str = Path(..., description="MongoDB ObjectId string"),
    db: AsyncIOMotorDatabase = Depends(get_db),
) -> None:
    try:
        oid: ObjectId = object_id_from_str(id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid ObjectId")

    result = await db["items"].delete_one({"_id": oid})
    if result.deleted_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    return None
