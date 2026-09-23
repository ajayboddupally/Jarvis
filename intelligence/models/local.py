from intelligence.models.provider import (
    GenerationRequest,
    GenerationResult,
    ModelProvider,
)


class JarvisLocalProvider(ModelProvider):
    """Deterministic development provider used when no real model is configured."""

    name = "mock"

    async def generate(self, request: GenerationRequest) -> GenerationResult:
        latest = request.messages[-1]["content"] if request.messages else ""
        response = (
            "Jarvis development runtime is active. "
            "Configure MODEL_BACKEND=transformers and LOCAL_MODEL_NAME "
            "to enable real local inference. "
            f"Received: {latest[:500]}"
        )
        input_tokens = sum(
            len(message.get("content", "").split())
            for message in request.messages
        )
        return GenerationResult(
            text=response,
            input_tokens=input_tokens,
            output_tokens=len(response.split()),
        )
