from __future__ import annotations

import base64

from openai import OpenAI
from pydantic import ValidationError

from .config import get_settings
from .exceptions import ImageGenerationError


def _b64_json_to_bytes(b64_json: str | None) -> bytes:
    if not b64_json:
        raise ImageGenerationError("OpenAI returned an empty generated image payload.")

    try:
        return base64.b64decode(b64_json)
    except ValueError as exc:
        raise ImageGenerationError("OpenAI returned invalid image data.") from exc


def generate_image(
    prompt: str,
    *,
    model: str | None = None,
) -> bytes:
    cleaned_prompt = prompt.strip()
    if not cleaned_prompt:
        raise ValueError("Prompt must not be empty")

    try:
        settings = get_settings()
    except ValidationError as exc:
        raise ImageGenerationError(
            "Missing OpenAI configuration. Set OPENAI_API_KEY in your environment or .env file."
        ) from exc

    openai_client = OpenAI(api_key=settings.openai_api_key)

    try:
        response = openai_client.images.generate(
            model=model or settings.openai_image_model,
            prompt=cleaned_prompt,
            size="1024x1024",
            quality="low"
        )
    except Exception as exc:
        raise ImageGenerationError(f"Failed to generate an image from the prompt: {prompt}. Error: {exc}") from exc

    image_base64 = response.data[0].b64_json
    image_bytes = base64.b64decode(image_base64)
    return image_bytes  
