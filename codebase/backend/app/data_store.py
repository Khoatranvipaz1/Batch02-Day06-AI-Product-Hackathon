from __future__ import annotations

import csv
from dataclasses import asdict, dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any


DATA_FILE = (
    Path(__file__).resolve().parents[2]
    / "mock_data"
    / "shopee_food_db_hcm_q1"
    / "v_recommendation_items.csv"
)


@dataclass(frozen=True)
class FoodItem:
    item_id: str
    item_name: str
    shop_id: str
    shop_name: str
    category_name: str
    effective_price: int
    base_price: int
    delivery_fee: int
    item_rating: float
    shop_rating: float
    sold_count: int
    spicy_level: int
    delivery_time_min: int
    is_available: bool
    is_signature: bool
    shop_status: str
    recommendation_score: float

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class FoodDataStore:
    def __init__(self, items: list[FoodItem]):
        self.items = items
        self.by_item_id = {item.item_id: item for item in items}
        self.by_shop_id = self._group_by("shop_id")
        self.by_category = self._group_by("category_name")

    def _group_by(self, field_name: str) -> dict[str, list[FoodItem]]:
        grouped: dict[str, list[FoodItem]] = {}
        for item in self.items:
            key = str(getattr(item, field_name))
            grouped.setdefault(key, []).append(item)
        return grouped

    def get_item(self, item_id: str) -> FoodItem | None:
        return self.by_item_id.get(item_id)

    def get_shop_items(self, shop_id: str) -> list[FoodItem]:
        return self.by_shop_id.get(shop_id, [])

    def get_category_items(self, category_name: str) -> list[FoodItem]:
        return self.by_category.get(category_name, [])

    def summary(self) -> dict[str, int]:
        return {
            "items": len(self.items),
            "shops": len(self.by_shop_id),
            "categories": len(self.by_category),
        }


def _to_int(value: str) -> int:
    return int(float(value or 0))


def _to_float(value: str) -> float:
    return float(value or 0)


@lru_cache(maxsize=1)
def get_data_store() -> FoodDataStore:
    with DATA_FILE.open("r", encoding="utf-8-sig", newline="") as file:
        rows = list(csv.DictReader(file))

    items = [
        FoodItem(
            item_id=row["item_id"],
            item_name=row["item_name"],
            shop_id=row["shop_id"],
            shop_name=row["shop_name"],
            category_name=row["category_name"],
            effective_price=_to_int(row["effective_price"]),
            base_price=_to_int(row["base_price"]),
            delivery_fee=_to_int(row["estimated_delivery_fee"]),
            item_rating=_to_float(row["item_rating"]),
            shop_rating=_to_float(row["shop_rating"]),
            sold_count=_to_int(row["item_sold_count"]),
            spicy_level=_to_int(row["spicy_level"]),
            delivery_time_min=_to_int(row["avg_delivery_time_min"]),
            is_available=row["is_available"] == "1",
            is_signature=row["is_signature"] == "1",
            shop_status=row["shop_status"],
            recommendation_score=_to_float(row["recommendation_score"]),
        )
        for row in rows
    ]
    return FoodDataStore(items)
