from abc import ABC, abstractmethod

import httpx

from intelligence.config import settings


class ModelProvider(ABC):
    name: str

    @abstractmethod
    async def generate(
        self,
        *,
        model: str,
        messages: list[dict[str, str]],
    ) -> tuple[str, int, int]:
        raise NotImplementedError


class LocalProvider(ModelProvider):
    name = "jarvis-local"

    async def generate(
        self,
        *,
        model: str,
        messages: list[dict[str, str]],
    ) -> tuple[str, int, int]:
        latest = messages[-1]["content"]

        response = (
            "Jarvis local reasoning layer received your request. "
            "The model-runtime layer is not connected yet. "
            f"Request summary: {latest[:500]}"
        )

        input_tokens = sum(len(item["content"].split()) for item in messages)
        output_tokens = len(response.split())

        return response, input_tokens, output_tokens


class ExternalHTTPProvider(ModelProvider):
    name = "external-http"

    async def generate(
        self,
        *,
        model: str,
        messages: list[dict[str, str]],
    ) -> tuple[str, int, int]:
        if not settings.external_model_url:
            raise RuntimeError("External model URL is not configured")

        headers = {}
        if settings.external_model_api_key:
            headers["Authorization"] = f"Bearer {settings.external_model_api_key}"

        payload = {
            "model": model,
            "messages": messages,
        }

        async with httpx.AsyncClient(timeout=settings.model_timeout_seconds) as client:
            response = await client.post(
                settings.external_model_url,
                json=payload,
                headers=headers,
            )
            response.raise_for_status()
            data = response.json()

        text = data.get("response") or data.get("output_text") or data.get("content")
        if not text:
            raise RuntimeError("External model response did not contain text")

        usage = data.get("usage") or {}

        return (
            str(text),
            int(usage.get("input_tokens", 0)),
            int(usage.get("output_tokens", 0)),
        )


def get_provider(model: str) -> ModelProvider:
    if settings.external_model_url and model != settings.default_model:
        return ExternalHTTPProvider()

    return LocalProvider()
