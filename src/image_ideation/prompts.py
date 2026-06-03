"""Prompts used."""

IMAGE_DESCRIPTION_PROMPT = """
You are helping describe an uploaded image for later image generation.

Write a concise but rich paragraph that focuses on:
- objects and subjects
- scene context
- colors
- composition
- visual style
- lighting
- mood
- likely intent or use

Only describe what is visible or strongly implied.
Do not use markdown, bullets, or headings.
Return a single polished paragraph suitable for an image-generation prompt.
""".strip()


def build_image_generation_prompt(description: str) -> str:
    cleaned_description = description.strip()
    if not cleaned_description:
        raise ValueError("description must not be empty")

    return (
        "Create a brand-new, high-quality image based on the description below. "
        "Preserve the core subjects, composition, and mood, while turning it into a polished visual concept.\n\n"
        f"Description: {cleaned_description}"
    )
