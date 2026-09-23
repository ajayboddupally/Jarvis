"""Backward-compatible imports for the model provider API."""

from intelligence.models import GenerationRequest, GenerationResult, ModelProvider
from intelligence.models.http import HTTPModelProvider
from intelligence.models.local import JarvisLocalProvider
from intelligence.models.router import ModelRouter
from intelligence.models.transformers import TransformersModelProvider

LocalProvider = JarvisLocalProvider
ExternalHTTPProvider = HTTPModelProvider


def get_provider(model: str) -> ModelProvider:
    return ModelRouter().resolve(model)


__all__ = [
    "GenerationRequest",
    "GenerationResult",
    "ModelProvider",
    "ModelRouter",
    "TransformersModelProvider",
    "LocalProvider",
    "ExternalHTTPProvider",
    "get_provider",
]
