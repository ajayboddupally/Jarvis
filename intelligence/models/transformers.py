import asyncio
from typing import Any

from intelligence.config import settings
from intelligence.models.provider import (
    GenerationRequest,
    GenerationResult,
    ModelProvider,
)


class TransformersModelProvider(ModelProvider):
    """Lazy-loaded Hugging Face Transformers inference backend."""

    name = "transformers"

    def __init__(self):
        self._tokenizer: Any | None = None
        self._model: Any | None = None

    async def generate(self, request: GenerationRequest) -> GenerationResult:
        return await asyncio.to_thread(self._generate_sync, request)

    async def warmup(self) -> None:
        await asyncio.to_thread(self._ensure_loaded)

    def is_loaded(self) -> bool:
        return self._model is not None and self._tokenizer is not None

    def _generate_sync(self, request: GenerationRequest) -> GenerationResult:
        self._ensure_loaded()

        prompt = self._build_inputs(request.messages)
        input_ids = prompt["input_ids"]
        attention_mask = prompt.get("attention_mask")

        input_tokens = int(input_ids.shape[-1])
        max_new_tokens = max(1, min(request.max_tokens, settings.local_max_new_tokens))
        max_context = settings.local_model_max_context

        if input_tokens + max_new_tokens > max_context:
            trim_to = max(1, max_context - max_new_tokens)
            input_ids = input_ids[:, -trim_to:]
            if attention_mask is not None:
                attention_mask = attention_mask[:, -trim_to:]
            input_tokens = int(input_ids.shape[-1])

        generate_kwargs = {
            "input_ids": input_ids,
            "max_new_tokens": max_new_tokens,
            "temperature": max(0.0, request.temperature),
            "top_p": settings.generation_top_p,
            "do_sample": request.temperature > 0,
            "pad_token_id": self._tokenizer.pad_token_id,
        }

        if attention_mask is not None:
            generate_kwargs["attention_mask"] = attention_mask

        import torch

        with torch.inference_mode():
            output_ids = self._model.generate(**generate_kwargs)

        generated_ids = output_ids[:, input_tokens:]
        text = self._tokenizer.decode(
            generated_ids[0],
            skip_special_tokens=True,
        ).strip()

        return GenerationResult(
            text=text,
            input_tokens=input_tokens,
            output_tokens=int(generated_ids.shape[-1]),
            finish_reason="stop",
        )

    def _ensure_loaded(self) -> None:
        if self.is_loaded():
            return

        model_name = settings.local_model_name
        if not model_name:
            raise RuntimeError(
                "LOCAL_MODEL_NAME must be configured when MODEL_BACKEND=transformers"
            )

        try:
            import torch
            from transformers import AutoModelForCausalLM, AutoTokenizer
        except ImportError as exc:
            raise RuntimeError(
                "Transformers runtime is not installed. Install requirements-ml.txt."
            ) from exc

        tokenizer = AutoTokenizer.from_pretrained(
            model_name,
            trust_remote_code=settings.local_model_trust_remote_code,
        )

        if tokenizer.pad_token_id is None:
            tokenizer.pad_token = tokenizer.eos_token

        dtype = self._resolve_dtype(torch)
        model_kwargs: dict[str, Any] = {
            "trust_remote_code": settings.local_model_trust_remote_code,
        }

        if dtype is not None:
            model_kwargs["torch_dtype"] = dtype

        device = self._resolve_device(torch)
        if device == "auto":
            model_kwargs["device_map"] = "auto"

        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            **model_kwargs,
        )

        if device != "auto":
            model = model.to(device)

        model.eval()
        self._tokenizer = tokenizer
        self._model = model

    def _build_inputs(self, messages: list[dict[str, str]]) -> dict[str, Any]:
        if self._tokenizer is None:
            raise RuntimeError("Tokenizer is not loaded")

        if hasattr(self._tokenizer, "apply_chat_template"):
            try:
                encoded = self._tokenizer.apply_chat_template(
                    messages,
                    add_generation_prompt=True,
                    tokenize=True,
                    return_tensors="pt",
                    return_dict=True,
                )
                return self._move_inputs_to_model_device(encoded)
            except (ValueError, TypeError, KeyError):
                pass

        text = "\n".join(
            f"{message.get('role', 'user')}: {message.get('content', '')}"
            for message in messages
        )
        text += "\nassistant:"
        encoded = self._tokenizer(
            text,
            return_tensors="pt",
            truncation=True,
            max_length=settings.local_model_max_context,
        )
        return self._move_inputs_to_model_device(encoded)

    def _move_inputs_to_model_device(self, encoded: Any) -> dict[str, Any]:
        device = self._model_device()
        return {
            key: value.to(device) if hasattr(value, "to") else value
            for key, value in encoded.items()
        }

    def _model_device(self) -> Any:
        if self._model is None:
            raise RuntimeError("Model is not loaded")
        try:
            return self._model.device
        except AttributeError:
            return next(self._model.parameters()).device

    def _resolve_device(self, torch: Any) -> str:
        configured = settings.local_model_device.lower()
        if configured == "auto":
            return "auto" if torch.cuda.is_available() else "cpu"
        if configured.startswith("cuda") and not torch.cuda.is_available():
            raise RuntimeError("LOCAL_MODEL_DEVICE requests CUDA, but CUDA is unavailable")
        return configured

    def _resolve_dtype(self, torch: Any) -> Any:
        configured = settings.local_model_dtype.lower()

        if configured == "auto":
            if torch.cuda.is_available():
                return torch.bfloat16 if torch.cuda.is_bf16_supported() else torch.float16
            return torch.float32

        mapping = {
            "float32": torch.float32,
            "float16": torch.float16,
            "bfloat16": torch.bfloat16,
        }
        if configured not in mapping:
            raise ValueError(
                "LOCAL_MODEL_DTYPE must be auto, float32, float16, or bfloat16"
            )
        return mapping[configured]
