from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from app.data_store import get_data_store

router = APIRouter(prefix="/menu", tags=["menu"])


class MenuSummaryResponse(BaseModel):
    items: int
    shops: int
    categories: int


class MenuItemResponse(BaseModel):
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


@router.get("/summary", response_model=MenuSummaryResponse)
async def get_menu_summary():
    return get_data_store().summary()


@router.get("/items", response_model=list[MenuItemResponse])
async def list_menu_items(
    limit: int = Query(default=30, ge=1, le=100),
    category: str | None = None,
    shop_id: str | None = None,
):
    store = get_data_store()
    items = store.items

    if category:
        items = store.get_category_items(category)
    if shop_id:
        items = [item for item in items if item.shop_id == shop_id]

    return [item.to_dict() for item in items[:limit]]


@router.get("/items/{item_id}", response_model=MenuItemResponse)
async def get_menu_item(item_id: str):
    item = get_data_store().get_item(item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Menu item not found")
    return item.to_dict()
