from pathlib import Path
import sys
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from starlette.concurrency import run_in_threadpool

from app.config import settings

PROJECT_ROOT = Path(__file__).resolve().parents[4]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from codebase.chatbot_parser.openai_parser import OpenAIParserError  # noqa: E402
from codebase.food_chatbot.answerer import FinalAnswerError  # noqa: E402
from codebase.food_chatbot.pipeline import run_food_chatbot  # noqa: E402

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


class ChatResponse(BaseModel):
    reply: str
    intent: dict[str, Any] = Field(default_factory=dict)
    clarifying_question: str | None = None
    warnings: list[str] = Field(default_factory=list)
    recommendations: list[RecommendationItem] = Field(default_factory=list)


@router.post("", response_model=ChatResponse)
async def create_chat(request: ChatRequest):
    try:
        result = await run_in_threadpool(
            run_food_chatbot,
            request.message,
            parse_mode="api",
            answer_mode="api",
            model=settings.ai_model,
            fallback_rules=False,
            fallback_template=False,
        )
    except (OpenAIParserError, FinalAnswerError) as exc:
        raise HTTPException(
            status_code=502,
            detail=f"OpenAI chatbot API call failed: {exc}",
        ) from exc

    task = result["task"]
    retrieved_data = result["retrieved_data"]
    return ChatResponse(
        reply=result["answer"],
        intent=task,
        clarifying_question=_first_clarifying_question(task),
        warnings=_collect_warnings(retrieved_data),
        recommendations=_to_recommendations(retrieved_data),
    )


def _first_clarifying_question(task: dict[str, Any]) -> str | None:
    questions = task.get("clarifying_questions")
    if isinstance(questions, list) and questions:
        return str(questions[0])
    return None


def _collect_warnings(retrieved_data: dict[str, Any]) -> list[str]:
    warnings = retrieved_data.get("warnings") or []
    return [str(warning) for warning in warnings]


def _to_recommendations(retrieved_data: dict[str, Any]) -> list[RecommendationItem]:
    rows = (
        retrieved_data.get("items")
        or retrieved_data.get("near_misses")
        or retrieved_data.get("fallback_items")
        or []
    )

    return [_to_recommendation(row) for row in rows[:3]]


def _to_recommendation(row: dict[str, Any]) -> RecommendationItem:
    effective_price = _to_int(row.get("effective_price"))
    delivery_fee = _to_int(row.get("estimated_delivery_fee"))

    return RecommendationItem(
        item_id=str(row.get("item_id", "")),
        item_name=str(row.get("item_name", "")),
        shop_name=str(row.get("shop_name", "")),
        category_name=str(row.get("category_name", "")),
        effective_price=effective_price,
        delivery_fee=delivery_fee,
        total_price=effective_price + delivery_fee,
        delivery_time_min=_to_int(row.get("avg_delivery_time_min")),
        item_rating=_to_float(row.get("item_rating")),
        shop_rating=_to_float(row.get("shop_rating")),
        spicy_level=_to_int(row.get("spicy_level")),
        score=_to_float(row.get("recommendation_score")),
        reasons=[str(reason) for reason in row.get("match_reasons", [])],
    )


def _to_int(value: Any) -> int:
    if value in (None, ""):
        return 0
    return int(float(value))


def _to_float(value: Any) -> float:
    if value in (None, ""):
        return 0
    return float(value)
