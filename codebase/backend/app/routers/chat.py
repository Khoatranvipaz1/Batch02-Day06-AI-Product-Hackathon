from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.recommendation import format_reply, recommend

router = APIRouter(prefix="/chat", tags=["chat"])


class ChatRequest(BaseModel):
    message: str


class RecommendationItem(BaseModel):
    item_id: str
    item_name: str
    shop_name: str
    category_name: str
    effective_price: int
    delivery_fee: int
    total_price: int
    delivery_time_min: int
    item_rating: float
    shop_rating: float
    spicy_level: int
    score: float
    reasons: list[str]


class IntentResponse(BaseModel):
    budget: int | None
    max_delivery_min: int | None
    no_spicy: bool
    lunch: bool
    healthy: bool
    light: bool
    cheap: bool
    unclear: bool


class ChatResponse(BaseModel):
    reply: str
    intent: IntentResponse
    clarifying_question: str | None = None
    warnings: list[str] = Field(default_factory=list)
    recommendations: list[RecommendationItem] = Field(default_factory=list)


@router.post("", response_model=ChatResponse)
async def create_chat(request: ChatRequest):
    result = recommend(request.message)
    return ChatResponse(reply=format_reply(result), **result)
