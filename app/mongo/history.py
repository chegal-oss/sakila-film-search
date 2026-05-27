from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, UTC

from pymongo import DESCENDING, MongoClient
from pymongo.collection import Collection
from pymongo.errors import PyMongoError

from app.config import MONGO_COLLECTION, MONGO_DATABASE, MONGO_URI


@dataclass
class PopularQuery:
    query: str
    count: int
    last_searched_at: datetime


class SearchHistoryRepository:
    def __init__(self):
        self._client = MongoClient(MONGO_URI)
        self._collection: Collection = self._client[MONGO_DATABASE][MONGO_COLLECTION]
        try:
            self._collection.create_index([("query", DESCENDING), ("searched_at", DESCENDING)])
        except PyMongoError:
            pass

    def save_query(self, query: str) -> None:
        normalized_query = query.strip()
        if not normalized_query:
            return

        try:
            self._collection.insert_one({"query": normalized_query, "searched_at": datetime.now(UTC)})
        except PyMongoError:
            return

    def get_popular_queries(self, limit: int = 5) -> list[PopularQuery]:
        try:
            items = self._collection.aggregate(
                [
                    {"$match": {"query": {"$exists": True, "$ne": ""}}},
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
            self._collection.delete_many({})
        except PyMongoError:
            return
