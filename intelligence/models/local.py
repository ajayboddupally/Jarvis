from intelligence.models.provider import (
    GenerationRequest,
    GenerationResult,
    ModelProvider,
)


class JarvisLocalProvider(ModelProvider):
    """Development provider used until a real inference runtime is connected."""

    name = "jarvis-local"

    async def generate(self, request: GenerationRequest) -> GenerationResult:
        latest = request.messages[-1]["content"] if request.messages else ""

        response = (
            "Jarvis inference runtime is ready for model integration. "
            f"Received: {latest[:500]}"
        )

        input_tokens = sum(len(message["content"].split()) for message in request.messages)
        output_tokens = len(response.split())

        return GenerationResult(
            text=response,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
        )
