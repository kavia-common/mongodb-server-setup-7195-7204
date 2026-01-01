from __future__ import annotations

import os
from typing import Optional

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase


class MongoDB:
    """Holds MongoDB client/database singletons for the app lifecycle."""

    def __init__(self) -> None:
        self._client: Optional[AsyncIOMotorClient] = None
        self._db: Optional[AsyncIOMotorDatabase] = None

    @property
    def client(self) -> AsyncIOMotorClient:
        """Return the initialized Mongo client or raise if not initialized."""
        if self._client is None:
            raise RuntimeError("MongoDB client is not initialized. Did startup run?")
        return self._client

    @property
    def db(self) -> AsyncIOMotorDatabase:
        """Return the initialized Mongo database or raise if not initialized."""
        if self._db is None:
            raise RuntimeError("MongoDB database is not initialized. Did startup run?")
        return self._db

    def init(self) -> None:
        """Initialize Mongo client + db from environment variables."""
        mongodb_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
        db_name = os.getenv("MONGODB_DB_NAME", "app")

        self._client = AsyncIOMotorClient(mongodb_uri)
        self._db = self._client[db_name]

    async def close(self) -> None:
        """Close the Mongo client."""
        if self._client is not None:
            self._client.close()
        self._client = None
        self._db = None


mongodb = MongoDB()


# PUBLIC_INTERFACE
async def get_db() -> AsyncIOMotorDatabase:
    """FastAPI dependency that returns the active AsyncIOMotorDatabase."""
    return mongodb.db
