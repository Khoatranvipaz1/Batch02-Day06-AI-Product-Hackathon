from fastapi import APIRouter, Query
from pydantic import BaseModel

from app.services.food_image_tool import get_menu_item_images

router = APIRouter(prefix="/menu-items", tags=["menu-items"])


class MenuItemImageResponse(BaseModel):
    id: str
    name: str
    shop_id: str
    base_price: int
    sale_price: int | None
    image_url: str
    image_source: str
    image_title: str | None


@router.get("/images", response_model=list[MenuItemImageResponse])
async def list_menu_item_images(
    query: str | None = Query(default=None, description="Menu item name to search."),
    limit: int = Query(default=20, ge=1, le=300),
    offset: int = Query(default=0, ge=0),
):
    return await get_menu_item_images(query=query, limit=limit, offset=offset)
