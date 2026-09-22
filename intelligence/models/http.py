import httpx

from intelligence.config import settings
from intelligence.models.provider import (
    GenerationRequest,
    GenerationResult,
    ModelProvider,
)


class HTTPModelProvider(ModelProvider):
    """Adapter for an OpenAI-compatible chat-completions endpoint."""

    name = "http-compatible"

    async def generate(self, request: GenerationRequest) -> GenerationResult:
        if not settings.external_model_url:
            raise RuntimeError("EXTERNAL_MODEL_URL is not configured")

        headers = {"Content-Type": "application/json"}

        if settings.external_model_api_key:
            headers["Authorization"] = f"Bearer {settings.external_model_api_key}"

        payload = {
            "model": request.model,
            "messages": request.messages,
            "temperature": request.temperature,
            "max_tokens": request.max_tokens,
        }

        async with httpx.AsyncClient(
            timeout=settings.model_timeout_seconds
        ) as client:
            response = await client.post(
                settings.external_model_url,
                json=payload,
                headers=headers,
            )
            response.raise_for_status()
            data = response.json()

        text = _extract_text(data)
        usage = data.get("usage") or {}

        return GenerationResult(
            text=text,
            input_tokens=int(
                usage.get("prompt_tokens", usage.get("input_tokens", 0))
            ),
            output_tokens=int(
                usage.get("completion_tokens", usage.get("output_tokens", 0))
            ),
            finish_reason=_extract_finish_reason(data),
            raw=data,
        )


def _extract_text(data: dict) -> str:
    if isinstance(data.get("choices"), list) and data["choices"]:
        choice = data["choices"][0]
        message = choice.get("message") or {}
        content = message.get("content")

        if isinstance(content, str):
            return content

        if isinstance(content, list):
            parts = [
                item.get("text", "")
                for item in content
                if isinstance(item, dict)
            ]
            text = "".join(parts)
            if text:
                return text

    for key in ("response", "output_text", "content"):
        if isinstance(data.get(key), str):
            return data[key]

    raise RuntimeError("Model response did not contain text")


def _extract_finish_reason(data: dict) -> str:
    choices = data.get("choices")

    if isinstance(choices, list) and choices:
        return str(choices[0].get("finish_reason") or "stop")

    return "stop"
