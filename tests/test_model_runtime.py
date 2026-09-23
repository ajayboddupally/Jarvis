import pytest

from intelligence.config import settings
from intelligence.models.local import JarvisLocalProvider
from intelligence.models.router import ModelRouter
from intelligence.models.transformers import TransformersModelProvider


def test_default_model_uses_configured_mock_backend(monkeypatch):
    monkeypatch.setattr(settings, "model_backend", "mock")
    router = ModelRouter()

    assert isinstance(router.resolve(settings.default_model), JarvisLocalProvider)


def test_transformers_backend_is_selected(monkeypatch):
    monkeypatch.setattr(settings, "model_backend", "transformers")
    router = ModelRouter()

    assert isinstance(router.resolve(settings.default_model), TransformersModelProvider)


@pytest.mark.asyncio
async def test_transformers_provider_requires_model_name(monkeypatch):
    monkeypatch.setattr(settings, "local_model_name", None)
    provider = TransformersModelProvider()

    with pytest.raises(RuntimeError, match="LOCAL_MODEL_NAME"):
        await provider.warmup()
