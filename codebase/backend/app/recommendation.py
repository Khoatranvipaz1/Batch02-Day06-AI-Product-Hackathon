from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from typing import Any

from app.data_store import FoodItem, get_data_store

MEAL_KEYWORDS = {
    "lunch": ["an trua", "trua", "com", "bun", "pho", "chao", "banh mi", "mi", "hu tieu"],
    "light": ["an nhe", "nhe", "snack", "cuon", "salad", "sup", "banh mi"],
    "healthy": ["healthy", "lanh manh", "salad", "gao lut", "chay", "uc ga", "quinoa"],
    "cheap": ["re nhat", "re", "tiet kiem"],
}


@dataclass(frozen=True)
class Intent:
    raw: str
    budget: int | None
    max_delivery_min: int | None
    no_spicy: bool
    lunch: bool
    healthy: bool
    light: bool
    cheap: bool
    unclear: bool


def _strip_accents(value: str) -> str:
    normalized = unicodedata.normalize("NFD", value)
    without_marks = "".join(ch for ch in normalized if unicodedata.category(ch) != "Mn")
    return without_marks.replace("đ", "d").replace("Đ", "D").lower()


def parse_intent(message: str) -> Intent:
    text = _strip_accents(message)
    budget_match = re.search(r"(?:duoi|toi da|<=|<)\s*(\d+)\s*k", text)
    budget = int(budget_match.group(1)) * 1000 if budget_match else None

    explicit_fast = any(word in text for word in ["giao nhanh", "nhanh", "gap"])
    time_match = re.search(r"(\d+)\s*(?:phut|p)", text)
    max_delivery = int(time_match.group(1)) if time_match else (30 if explicit_fast else None)

    unclear = (
        len(text.strip()) < 12
        or "gi cung duoc" in text
        or text.strip() in {"an gi", "goi y", "tim mon", "an gi day"}
    )

    return Intent(
        raw=message,
        budget=budget,
        max_delivery_min=max_delivery,
        no_spicy=any(word in text for word in ["khong cay", "ko cay", "khong an cay", "it cay"]),
        lunch=any(word in text for word in ["an trua", "bua trua", "trua", "an no"]),
        healthy=any(word in text for word in MEAL_KEYWORDS["healthy"]),
        light=any(word in text for word in MEAL_KEYWORDS["light"]),
        cheap=any(word in text for word in MEAL_KEYWORDS["cheap"]),
        unclear=unclear,
    )


def _contains_any(value: str, keywords: list[str]) -> bool:
    normalized = _strip_accents(value)
    return any(keyword in normalized for keyword in keywords)


def _score(item: FoodItem, intent: Intent) -> float:
    total_price = item.effective_price + item.delivery_fee
    item_text = item.item_name + " " + item.category_name
    score = item.recommendation_score * 100
    score += item.item_rating * 4 + item.shop_rating * 3

    if intent.budget:
        score += max(0, (intent.budget - item.effective_price) / 1000) * 0.7
    if intent.max_delivery_min:
        score += max(0, intent.max_delivery_min - item.delivery_time_min) * 1.4
    if intent.no_spicy and item.spicy_level == 0:
        score += 18
    if intent.lunch and _contains_any(item_text, MEAL_KEYWORDS["lunch"]):
        score += 22
    if intent.healthy and _contains_any(item_text, MEAL_KEYWORDS["healthy"]):
        score += 22
    if intent.light and _contains_any(item_text, MEAL_KEYWORDS["light"]):
        score += 12
    if intent.cheap:
        score += max(0, 70000 - total_price) / 1000
    if intent.lunch and _is_side_or_drink(item):
        score -= 35
    if item.is_signature:
        score += 4

    return round(score, 2)


def _is_side_or_drink(item: FoodItem) -> bool:
    item_text = _strip_accents(item.item_name + " " + item.category_name)
    side_words = [
        "do uong",
        "ca phe",
        "tra",
        "topping",
        "mon them",
        "trang mieng",
        "banh ngot",
        "cookie",
        "sua",
        "nuoc",
        "quay",
    ]
    return any(word in item_text for word in side_words)


def _allows_side_or_drink(intent: Intent) -> bool:
    text = _strip_accents(intent.raw)
    allowed_words = [
        "do uong",
        "nuoc",
        "tra sua",
        "ca phe",
        "topping",
        "mon them",
        "trang mieng",
        "banh ngot",
        "snack",
    ]
    return any(word in text for word in allowed_words)


def _reason(item: FoodItem | dict[str, Any], intent: Intent) -> list[str]:
    if isinstance(item, dict):
        item = item["item"]
    total_price = item.effective_price + item.delivery_fee
    reasons = [
        f"mon {item.effective_price // 1000}k, tong tam {total_price // 1000}k gom phi ship",
        f"giao {item.delivery_time_min} phut",
        f"rating mon {item.item_rating}/5 va quan {item.shop_rating}/5",
    ]
    if intent.no_spicy and item.spicy_level == 0:
        reasons.append("khong cay")
    if item.base_price > item.effective_price:
        discount = item.base_price - item.effective_price
        reasons.append(f"giam {discount // 1000}k tren gia mon")
    return reasons


def recommend(message: str, limit: int = 3) -> dict[str, Any]:
    intent = parse_intent(message)
    candidates: list[dict[str, Any]] = []
    warnings: list[str] = []

    for item in get_data_store().items:
        if not item.is_available or item.shop_status == "closed":
            continue
        if _is_side_or_drink(item) and not _allows_side_or_drink(intent):
            continue
        if intent.budget and item.effective_price > intent.budget:
            continue
        if intent.max_delivery_min and item.delivery_time_min > intent.max_delivery_min:
            continue
        if intent.no_spicy and item.spicy_level > 0:
            continue
        candidates.append({"item": item, "score": _score(item, intent)})

    ranked = sorted(candidates, key=lambda item: item["score"], reverse=True)[:limit]
    if intent.unclear:
        warnings.append("Yeu cau con mo ho, nen hoi lai truoc khi chot goi y.")
    if intent.budget is None:
        warnings.append("Chua thay ngan sach ro rang; dang mac dinh uu tien gia hop ly.")
    if not ranked:
        warnings.append("Khong co mon nao khop tat ca rang buoc; can noi long gia, thoi gian hoac do cay.")

    recommendations = [
        {
            "item_id": item["item"].item_id,
            "item_name": item["item"].item_name,
            "shop_name": item["item"].shop_name,
            "category_name": item["item"].category_name,
            "effective_price": item["item"].effective_price,
            "delivery_fee": item["item"].delivery_fee,
            "total_price": item["item"].effective_price + item["item"].delivery_fee,
            "delivery_time_min": item["item"].delivery_time_min,
            "item_rating": item["item"].item_rating,
            "shop_rating": item["item"].shop_rating,
            "spicy_level": item["item"].spicy_level,
            "score": item["score"],
            "reasons": _reason(item, intent),
        }
        for item in ranked
    ]

    return {
        "intent": {
            "budget": intent.budget,
            "max_delivery_min": intent.max_delivery_min,
            "no_spicy": intent.no_spicy,
            "lunch": intent.lunch,
            "healthy": intent.healthy,
            "light": intent.light,
            "cheap": intent.cheap,
            "unclear": intent.unclear,
        },
        "clarifying_question": (
            "Ban muon an no, an nhe, healthy hay re nhat?"
            if intent.unclear
            else None
        ),
        "warnings": warnings,
        "recommendations": recommendations,
    }


def format_reply(result: dict[str, Any]) -> str:
    question = result.get("clarifying_question")
    if question:
        return question

    items = result["recommendations"]
    if not items:
        return "Chua co mon nao khop het dieu kien. Ban co muon noi long ngan sach hoac thoi gian giao khong?"

    lines = ["Minh chon 3 lua chon phu hop nhat:"]
    for index, item in enumerate(items, start=1):
        reasons = "; ".join(item["reasons"])
        lines.append(f"{index}. {item['item_name']} - {item['shop_name']}: {reasons}.")
    return "\n".join(lines)
