from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from app.db.model import Category, Year


@dataclass
class SearchFilter:
    category: Category
    years: Year
    title: str = ""

    @property
    def title_label(self) -> str:
        return self.title if self.title else "All"

    @property
    def years_param(self) -> str | None:
        return self.years.period if self.years.id else None

    def to_history_dict(self) -> dict[str, str]:
        return {
            "category": self.category.name,
            "years": self.years.period,
            "title": self.title_label,
        }

    def to_history_key(self) -> str:
        return ", ".join(f"{key} - {value}" for key, value in self.to_history_dict().items())

    def to_history_document(self) -> dict[str, Any]:
        return {
            "category": {
                "id": self.category.category_id,
                "name": self.category.name,
            },
            "years": {
                "id": self.years.id,
                "period": self.years.period,
            },
            "title": self.title,
        }

    @classmethod
    def from_history_document(cls, query: dict[str, Any]) -> SearchFilter | None:
        try:
            category = Category(query["category"]["id"], query["category"]["name"])
            years = Year(query["years"]["id"], query["years"]["period"])
            title = query.get("title", "")
        except (KeyError, TypeError):
            return None

        return cls(category=category, years=years, title=title)
