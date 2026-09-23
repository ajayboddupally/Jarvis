from intelligence.config import settings
from intelligence.models.http import HTTPModelProvider
from intelligence.models.local import JarvisLocalProvider
from intelligence.models.provider import ModelProvider
from intelligence.models.transformers import TransformersModelProvider


class ModelRouter:
    def __init__(self):
        self.mock = JarvisLocalProvider()
        self.http = HTTPModelProvider()
        self.transformers = TransformersModelProvider()

    def resolve(self, model: str) -> ModelProvider:
        if model != settings.default_model:
            if settings.external_model_url and model == settings.external_model_name:
                return self.http
            raise ValueError(f"Model is not available: {model}")

        backend = settings.model_backend.lower()
        if backend == "mock":
            return self.mock
        if backend == "transformers":
            return self.transformers
        if backend == "http":
            if not settings.external_model_url:
                raise RuntimeError("EXTERNAL_MODEL_URL is required for MODEL_BACKEND=http")
            return self.http
        raise ValueError(f"Unsupported MODEL_BACKEND: {settings.model_backend}")

    def available_models(self) -> list[dict]:
        backend = settings.model_backend.lower()
        if backend == "transformers":
            provider = self.transformers.name
            status = "configured" if settings.local_model_name else "missing_configuration"
        elif backend == "http":
            provider = self.http.name
            status = "configured" if settings.external_model_url else "missing_configuration"
        else:
            provider = self.mock.name
            status = "available"

        models = [{
            "id": settings.default_model,
            "provider": provider,
            "backend": backend,
            "status": status,
        }]

        if settings.external_model_url and settings.external_model_name != settings.default_model:
            models.append({
                "id": settings.external_model_name,
                "provider": self.http.name,
                "backend": "http",
                "status": "configured",
            })
        return models
