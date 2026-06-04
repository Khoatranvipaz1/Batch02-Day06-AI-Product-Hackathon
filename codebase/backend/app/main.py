from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import chat, menu, menu_items

app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router, prefix="/api")
app.include_router(menu_items.router, prefix="/api")
app.include_router(menu.router, prefix="/api")


@app.get("/health")
def health_check():
    return {"status": "ok", "env": settings.app_env}
