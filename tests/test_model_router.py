from intelligence.models.local import JarvisLocalProvider
from intelligence.models.router import ModelRouter


def test_default_model_uses_local_provider():
    router = ModelRouter()

    provider = router.resolve("jarvis-local")

    assert isinstance(provider, JarvisLocalProvider)


def test_default_model_is_listed():
    router = ModelRouter()

    models = router.available_models()

    assert any(model["id"] == "jarvis-local" for model in models)
