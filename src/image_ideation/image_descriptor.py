from __future__ import annotations

import base64

from openai import OpenAI
from pydantic import ValidationError

from .config import get_settings
from .exceptions import ImageDescriptionError
from .prompts import IMAGE_DESCRIPTION_PROMPT


def _image_bytes_to_data_url(image_bytes: bytes, mime_type: str | None) -> str:
    if not image_bytes:
        raise ValueError("image_bytes must not be empty")

    mime = mime_type or "image/png"
    encoded_image = base64.b64encode(image_bytes).decode("utf-8")
    return f"data:{mime};base64,{encoded_image}"


def describe_image(
    image_bytes: bytes,
    *,
    mime_type: str | None = None,
    model: str | None = None,
) -> str:
    try:
        settings = get_settings()
    except ValidationError as exc:
        raise ImageDescriptionError(
            "Missing OpenAI configuration. Set OPENAI_API_KEY in your environment or .env file."
        ) from exc

    openai_client = OpenAI(api_key=settings.openai_api_key)
    image_data_url = _image_bytes_to_data_url(image_bytes, mime_type)

    try:
        response = openai_client.responses.create(
            model=model or settings.openai_text_model,
            instructions=IMAGE_DESCRIPTION_PROMPT,
            input=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "input_text",
                            "text": "Describe this image in rich detail for use in image generation.",
                        },
                        {
                            "type": "input_image",
                            "image_url": image_data_url,
                        },
                    ],
                }
            ],
        )
    except Exception as exc:
        raise ImageDescriptionError("Failed to generate an image description.") from exc

    description = response.output_text.strip()
    if not description:
        raise ImageDescriptionError("OpenAI returned an empty image description.")

    return description
