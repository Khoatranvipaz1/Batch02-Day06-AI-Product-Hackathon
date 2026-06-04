from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/chat", tags=["chat"])


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    reply: str


@router.post("", response_model=ChatResponse)
async def create_chat(request: ChatRequest):
    # TODO: Call your AI service here.
    return ChatResponse(reply=f"Backend received: {request.message}")
