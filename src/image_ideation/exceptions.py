from __future__ import annotations


class ImageIdeationError(Exception):
    """Base class for application-specific errors."""


class ImageDescriptionError(ImageIdeationError):
    """Raised when the image description request fails."""


class ImageGenerationError(ImageIdeationError):
    """Raised when the image generation request fails."""
