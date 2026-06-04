import csv
import html
from functools import lru_cache
from pathlib import Path

import httpx
from fastapi import APIRouter, HTTPException, Query, Response
from fastapi.responses import RedirectResponse
from pydantic import BaseModel

from app.services.food_image_tool import resolve_food_image

router = APIRouter(prefix="/menu-items", tags=["menu"])

DATA_DIR = (
    Path(__file__).resolve().parents[3]
    / "mock_data"
    / "shopee_food_db_hcm_q1"
)


class MenuItem(BaseModel):
    id: str
    name: str
    description: str
    base_price: int
    sale_price: int | None
    effective_price: int
    image_url: str
    source_image_url: str
    rating_avg: float
    rating_count: int
    sold_count: int
    prepare_time_min: int
    spicy_level: int
    calories_estimate: int
    portion_size: str
    is_available: bool
    is_signature: bool
    is_combo: bool
    category_id: str
    category_name: str
    shop_id: str
    shop_name: str
    shop_rating: float
    shop_status: str


class MenuResponse(BaseModel):
    items: list[MenuItem]
    categories: list[str]
    total: int


def _read_csv(filename: str) -> list[dict[str, str]]:
    path = DATA_DIR / filename
    if not path.exists():
        raise FileNotFoundError(f"Missing mock data file: {path}")

    with path.open(encoding="utf-8-sig", newline="") as file:
        return list(csv.DictReader(file))


def _to_int(value: str | None, default: int = 0) -> int:
    if value in (None, ""):
        return default
    return int(float(value))


def _to_float(value: str | None, default: float = 0) -> float:
    if value in (None, ""):
        return default
    return float(value)


def _to_bool(value: str | None) -> bool:
    return value == "1" or value == "true"


@lru_cache(maxsize=1)
def load_menu_items() -> list[MenuItem]:
    shops = {row["id"]: row for row in _read_csv("shops.csv")}
    categories = {row["id"]: row for row in _read_csv("menu_categories.csv")}
    items: list[MenuItem] = []

    for row in _read_csv("menu_items.csv"):
        category = categories.get(row["category_id"], {})
        shop = shops.get(row["shop_id"], {})
        sale_price = _to_int(row.get("sale_price")) if row.get("sale_price") else None

        items.append(
            MenuItem(
                id=row["id"],
                name=row["name"],
                description=row.get("description", ""),
                base_price=_to_int(row.get("base_price")),
                sale_price=sale_price,
                effective_price=sale_price or _to_int(row.get("base_price")),
                image_url=f"/api/menu-items/{row['id']}/image",
                source_image_url=row.get("image_url", ""),
                rating_avg=_to_float(row.get("rating_avg")),
                rating_count=_to_int(row.get("rating_count")),
                sold_count=_to_int(row.get("sold_count")),
                prepare_time_min=_to_int(row.get("prepare_time_min")),
                spicy_level=_to_int(row.get("spicy_level")),
                calories_estimate=_to_int(row.get("calories_estimate")),
                portion_size=row.get("portion_size", ""),
                is_available=_to_bool(row.get("is_available")),
                is_signature=_to_bool(row.get("is_signature")),
                is_combo=_to_bool(row.get("is_combo")),
                category_id=row["category_id"],
                category_name=category.get("name", "Khác"),
                shop_id=row["shop_id"],
                shop_name=shop.get("name", "Quán chưa rõ"),
                shop_rating=_to_float(shop.get("rating_avg")),
                shop_status=shop.get("status", "unknown"),
            )
        )

    return items


@router.get("", response_model=MenuResponse)
async def list_menu_items(
    search: str = "",
    category: str = "",
    available_only: bool = True,
    limit: int = Query(default=120, ge=1, le=300),
    offset: int = Query(default=0, ge=0),
):
    items = load_menu_items()
    normalized_search = search.casefold().strip()
    normalized_category = category.casefold().strip()

    if available_only:
        items = [item for item in items if item.is_available]

    if normalized_category and normalized_category != "all":
        items = [
            item
            for item in items
            if item.category_name.casefold() == normalized_category
        ]

    if normalized_search:
        items = [
            item
            for item in items
            if normalized_search in item.name.casefold()
            or normalized_search in item.shop_name.casefold()
            or normalized_search in item.description.casefold()
        ]

    items = sorted(
        items,
        key=lambda item: (item.sold_count, item.rating_avg),
        reverse=True,
    )
    categories = sorted({item.category_name for item in load_menu_items()})
    return MenuResponse(
        items=items[offset : offset + limit],
        categories=categories,
        total=len(items),
    )


@router.get("/{item_id}", response_model=MenuItem)
async def get_menu_item(item_id: str):
    for item in load_menu_items():
        if item.id == item_id:
            return item

    raise HTTPException(status_code=404, detail="Menu item not found")


@router.get("/{item_id}/image")
async def get_menu_item_image(item_id: str):
    item = next((item for item in load_menu_items() if item.id == item_id), None)
    if item is None:
        raise HTTPException(status_code=404, detail="Menu item not found")

    async with httpx.AsyncClient(timeout=8.0) as client:
        image = await resolve_food_image(
            item_name=item.name,
            existing_image_url=item.source_image_url,
            client=client,
        )

    if image["image_url"]:
        response = RedirectResponse(image["image_url"], status_code=307)
        response.headers["Cache-Control"] = "no-store"
        return response

    name = html.escape(item.name)
    category = html.escape(item.category_name)
    shop = html.escape(item.shop_name)
    price = f"{item.effective_price:,}".replace(",", ".")
    palette = _image_palette(item.category_name)

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="960" height="640" viewBox="0 0 960 640">
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="{palette[0]}"/>
      <stop offset="55%" stop-color="{palette[1]}"/>
      <stop offset="100%" stop-color="{palette[2]}"/>
    </linearGradient>
    <filter id="shadow" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="0" dy="22" stdDeviation="22" flood-color="#101828" flood-opacity=".22"/>
    </filter>
  </defs>
  <rect width="960" height="640" fill="url(#bg)"/>
  <circle cx="785" cy="95" r="126" fill="#ffffff" opacity=".18"/>
  <circle cx="118" cy="548" r="162" fill="#ffffff" opacity=".14"/>
  <g filter="url(#shadow)">
    <ellipse cx="480" cy="322" rx="282" ry="186" fill="#fff8ef"/>
    <ellipse cx="480" cy="322" rx="224" ry="140" fill="#ffffff"/>
    <circle cx="405" cy="295" r="58" fill="{palette[3]}"/>
    <circle cx="515" cy="324" r="74" fill="{palette[4]}"/>
    <circle cx="590" cy="270" r="42" fill="{palette[5]}"/>
    <path d="M297 384 C410 454 559 454 665 380" fill="none" stroke="#2f2a25" stroke-width="18" stroke-linecap="round" opacity=".14"/>
  </g>
  <rect x="48" y="42" width="246" height="48" rx="24" fill="#ffffff" opacity=".92"/>
  <text x="72" y="73" font-family="Arial, sans-serif" font-size="22" font-weight="700" fill="#273142">{category}</text>
  <rect x="48" y="468" width="864" height="124" rx="28" fill="#101828" opacity=".78"/>
  <text x="80" y="512" font-family="Arial, sans-serif" font-size="38" font-weight="800" fill="#ffffff">{name}</text>
  <text x="80" y="552" font-family="Arial, sans-serif" font-size="22" fill="#f4f7fb">{shop}</text>
  <text x="770" y="552" text-anchor="end" font-family="Arial, sans-serif" font-size="30" font-weight="800" fill="#ffffff">{price}d</text>
</svg>"""

    return Response(content=svg, media_type="image/svg+xml")


def _image_palette(category_name: str) -> tuple[str, str, str, str, str, str]:
    palettes = [
        ("#f97316", "#facc15", "#22c55e", "#ef4444", "#f59e0b", "#16a34a"),
        ("#0ea5e9", "#14b8a6", "#f4f4f5", "#fb7185", "#38bdf8", "#fbbf24"),
        ("#a855f7", "#ec4899", "#f97316", "#fbbf24", "#f472b6", "#7dd3fc"),
        ("#22c55e", "#84cc16", "#f8fafc", "#65a30d", "#facc15", "#ef4444"),
        ("#ef4444", "#fb923c", "#fde68a", "#f97316", "#dc2626", "#16a34a"),
        ("#06b6d4", "#3b82f6", "#f8fafc", "#60a5fa", "#f472b6", "#facc15"),
    ]
    index = sum(ord(char) for char in category_name) % len(palettes)
    return palettes[index]
