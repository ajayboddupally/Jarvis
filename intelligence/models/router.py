from intelligence.config import settings
from intelligence.models.http import HTTPModelProvider
from intelligence.models.local import JarvisLocalProvider
from intelligence.models.provider import ModelProvider


class ModelRouter:
    def __init__(self):
        self.local = JarvisLocalProvider()
        self.http = HTTPModelProvider()

    def resolve(self, model: str) -> ModelProvider:
        if model == settings.default_model:
            return self.local

        if settings.external_model_url:
            return self.http

        raise ValueError(f"Model is not available: {model}")

    def available_models(self) -> list[dict]:
        models = [
            {
                "id": settings.default_model,
                "provider": self.local.name,
                "status": "available",
            }
        ]

        if settings.external_model_url:
            models.append(
                {
                    "id": settings.external_model_name,
                    "provider": self.http.name,
                    "status": "configured",
                }
            )

        return models
