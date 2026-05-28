from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, UTC
from typing import Any

from pymongo import DESCENDING, MongoClient
from pymongo.collection import Collection
from pymongo.errors import PyMongoError

from app.config import MONGO_COLLECTION, MONGO_DATABASE, MONGO_URI
from app.logger import logger


@dataclass
class PopularQuery:
    query: dict[str, Any]
    count: int
    last_searched_at: datetime


class MongoHistoryConnection:
    def __init__(self):
        self._client: MongoClient | None = None
        self._collection: Collection | None = None

    def __enter__(self) -> MongoHistoryConnection:
        return self.connect()

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()

    def connect(self) -> MongoHistoryConnection:
        if self._client is not None:
            return self

        self._client = MongoClient(MONGO_URI)
        self._collection = self._client[MONGO_DATABASE][MONGO_COLLECTION]
        try:
            self._collection.create_index([("query", DESCENDING), ("searched_at", DESCENDING)])
        except PyMongoError:
            pass
        return self

    def close(self) -> None:
        if self._client is None:
            return
        self._client.close()
        self._client = None
        self._collection = None

    @property
    def collection(self) -> Collection:
        if self._collection is None:
            self.connect()
        return self._collection

    def save_query(self, query: dict[str, Any]) -> None:
        if not query:
            return

        try:
            self.collection.insert_one({"query": query, "searched_at": datetime.now(UTC)})
            logger.debug("Search query saved: %s", query)
        except PyMongoError as e:
            logger.debug("Search query was not saved: %s", e)
            return

    def get_popular_queries(self, limit: int = 5) -> list[PopularQuery]:
        try:
            items = self.collection.aggregate(
                [
                    {"$match": {"query": {"$exists": True, "$type": "object"}}},
                    {
                        "$group": {
                            "_id": "$query",
                            "count": {"$sum": 1},
                            "last_searched_at": {"$max": "$searched_at"},
                        }
                    },
                    {"$sort": {"count": -1, "last_searched_at": -1}},
                    {"$limit": limit},
                ]
            )
        except PyMongoError:
            return []

        popular_queries: list[PopularQuery] = []
        for item in items:
            query = item.get("_id")
            if not query:
                continue
            popular_queries.append(
                PopularQuery(
                    query=query,
                    count=int(item.get("count", 0)),
                    last_searched_at=item.get("last_searched_at") or datetime.now(UTC),
                )
            )
        return popular_queries

    def clear_queries(self) -> None:
        try:
            self.collection.delete_many({})
        except PyMongoError:
            return
