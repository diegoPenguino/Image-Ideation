from __future__ import annotations

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

DEFAULT_TEXT_MODEL = "gpt-5-nano"
DEFAULT_IMAGE_MODEL = "gpt-image-1-mini"

class Settings(BaseSettings):
    openai_api_key: str
    openai_text_model: str = Field(default=DEFAULT_TEXT_MODEL)
    openai_image_model: str = Field(default=DEFAULT_IMAGE_MODEL)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
