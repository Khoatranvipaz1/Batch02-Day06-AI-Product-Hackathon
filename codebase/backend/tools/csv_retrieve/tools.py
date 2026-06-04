from __future__ import annotations

import csv
import unicodedata
from pathlib import Path
from typing import Any


BACKEND_DIR = Path(__file__).resolve().parents[2]
PROJECT_DIR = BACKEND_DIR.parent
DEFAULT_RECOMMENDATION_CSV = (
    PROJECT_DIR
    / "mock_data"
    / "shopee_food_db_hcm_q1"
    / "v_recommendation_items.csv"
)


def retrieve_csv_rows(
    csv_path: str,
    query: str | None = None,
    columns: list[str] | None = None,
    limit: int = 20,
) -> dict[str, Any]:
    """Read rows from a CSV file with optional keyword matching."""
    path = _resolve_csv_path(csv_path)
    rows = _read_csv(path)
    selected_rows = []
    query_value = _normalize_text(query)

    for row in rows:
        if query_value and not _row_matches_query(row, query_value):
            continue
        selected_rows.append(_select_columns(row, columns))
        if len(selected_rows) >= limit:
            break

    return {
        "source": str(path),
        "total_rows": len(rows),
        "matched_rows": len(selected_rows),
        "rows": selected_rows,
    }


def retrieve_food_options(
    query: str | None = None,
    budget: int | None = 60000,
    max_delivery_time_min: int | None = 30,
    avoid_spicy: bool = True,
    only_open: bool = True,
    only_available: bool = True,
    limit: int = 3,
    csv_path: str | None = None,
) -> dict[str, Any]:
    """Retrieve ShopeeFood-style menu options that satisfy user constraints."""
    path = _resolve_csv_path(csv_path) if csv_path else DEFAULT_RECOMMENDATION_CSV
    rows = _read_csv(path)
    query_value = _normalize_text(query)
    candidates = []
    rejected_count = 0

    for row in rows:
        normalized = _normalize_food_row(row)
        violations = _constraint_violations(
            normalized,
            budget=budget,
            max_delivery_time_min=max_delivery_time_min,
            avoid_spicy=avoid_spicy,
            only_open=only_open,
            only_available=only_available,
        )

        if query_value and not _row_matches_query(row, query_value):
            rejected_count += 1
            continue

        if violations:
            rejected_count += 1
            continue

        candidates.append(normalized)

    ranked = sorted(
        candidates,
        key=lambda item: (
            item["recommendation_score"],
            item["shop_rating"],
            -item["total_price"],
            -item["delivery_time_min"],
        ),
        reverse=True,
    )
    recommendations = [_with_reason(item, budget, max_delivery_time_min, avoid_spicy) for item in ranked[:limit]]

    return {
        "source": str(path),
        "constraints": {
            "query": query,
            "budget": budget,
            "max_delivery_time_min": max_delivery_time_min,
            "avoid_spicy": avoid_spicy,
            "only_open": only_open,
            "only_available": only_available,
            "limit": limit,
        },
        "total_rows": len(rows),
        "matched_rows": len(candidates),
        "rejected_rows": rejected_count,
        "recommendations": recommendations,
        "needs_clarification": len(recommendations) == 0,
        "clarification_question": (
            "Mình chưa tìm được món phù hợp. Bạn muốn nới ngân sách, thời gian giao, "
            "hay đổi điều kiện không cay không?"
            if len(recommendations) == 0
            else None
        ),
    }


def _resolve_csv_path(csv_path: str) -> Path:
    path = Path(csv_path)
    if not path.is_absolute():
        path = BACKEND_DIR / path
    if not path.exists():
        raise FileNotFoundError(f"CSV file not found: {path}")
    if path.suffix.lower() != ".csv":
        raise ValueError(f"Expected a .csv file: {path}")
    return path


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as file:
        return list(csv.DictReader(file))


def _select_columns(row: dict[str, str], columns: list[str] | None) -> dict[str, str]:
    if not columns:
        return dict(row)
    return {column: row.get(column, "") for column in columns}


def _row_matches_query(row: dict[str, str], query: str) -> bool:
    searchable = " ".join(str(value) for value in row.values())
    return query in _normalize_text(searchable)


def _normalize_food_row(row: dict[str, str]) -> dict[str, Any]:
    effective_price = _to_int(row.get("effective_price")) or _to_int(row.get("base_price"))
    delivery_fee = _to_int(row.get("estimated_delivery_fee"))
    total_price = effective_price + delivery_fee

    return {
        "item_id": row.get("item_id", ""),
        "item_name": row.get("item_name", ""),
        "shop_id": row.get("shop_id", ""),
        "shop_name": row.get("shop_name", ""),
        "category_name": row.get("category_name", ""),
        "base_price": _to_int(row.get("base_price")),
        "effective_price": effective_price,
        "delivery_fee": delivery_fee,
        "total_price": total_price,
        "item_rating": _to_float(row.get("item_rating")),
        "shop_rating": _to_float(row.get("shop_rating")),
        "sold_count": _to_int(row.get("item_sold_count")),
        "spicy_level": _to_int(row.get("spicy_level")),
        "delivery_time_min": _to_int(row.get("avg_delivery_time_min")),
        "is_available": _to_bool(row.get("is_available")),
        "shop_status": row.get("shop_status", ""),
        "address": row.get("full_address", ""),
        "recommendation_score": _to_float(row.get("recommendation_score")),
        "image_url": row.get("image_url") or None,
    }


def _constraint_violations(
    item: dict[str, Any],
    budget: int | None,
    max_delivery_time_min: int | None,
    avoid_spicy: bool,
    only_open: bool,
    only_available: bool,
) -> list[str]:
    violations = []
    if budget is not None and item["total_price"] > budget:
        violations.append("over_budget")
    if max_delivery_time_min is not None and item["delivery_time_min"] > max_delivery_time_min:
        violations.append("delivery_too_slow")
    if avoid_spicy and item["spicy_level"] > 0:
        violations.append("spicy")
    if only_open and item["shop_status"] != "open":
        violations.append("shop_closed")
    if only_available and not item["is_available"]:
        violations.append("unavailable")
    return violations


def _with_reason(
    item: dict[str, Any],
    budget: int | None,
    max_delivery_time_min: int | None,
    avoid_spicy: bool,
) -> dict[str, Any]:
    reasons = []
    if budget is not None:
        reasons.append(f"tong gia {item['total_price']} <= ngan sach {budget}")
    if max_delivery_time_min is not None:
        reasons.append(f"giao trong {item['delivery_time_min']} phut")
    if avoid_spicy:
        reasons.append("khong cay")
    reasons.append(f"rating quan {item['shop_rating']}")

    return {
        **item,
        "reason": "; ".join(reasons),
    }


def _normalize_text(value: str | None) -> str:
    normalized = unicodedata.normalize("NFD", (value or "").strip().lower())
    return "".join(char for char in normalized if unicodedata.category(char) != "Mn")


def _to_int(value: str | None) -> int:
    if value in (None, ""):
        return 0
    return int(float(value))


def _to_float(value: str | None) -> float:
    if value in (None, ""):
        return 0.0
    return float(value)


def _to_bool(value: str | None) -> bool:
    return str(value).strip().lower() in {"1", "true", "yes", "y"}
