import os
from pathlib import Path

from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

ENV_FILE = Path(__file__).resolve().parents[1] / ".env"
load_dotenv(ENV_FILE, override=True)


class Settings(BaseSettings):
    app_name: str = "AI Chatbot Backend"
    app_env: str = "development"
    frontend_origin: str = "http://localhost:5173"
    ai_api_key: str = ""
    ai_base_url: str = "https://api.openai.com/v1"
    ai_model: str = "gpt-4o-mini"

    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()

if settings.ai_api_key:
    os.environ["OPENAI_API_KEY"] = settings.ai_api_key

if settings.ai_model:
    os.environ["OPENAI_MODEL"] = settings.ai_model

if settings.ai_base_url:
    os.environ["OPENAI_API_BASE"] = settings.ai_base_url
