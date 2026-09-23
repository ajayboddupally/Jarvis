from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from intelligence.agent import AgentRuntime
from intelligence.context import build_context
from intelligence.memory import get_or_create_conversation, load_context, save_message
from intelligence.models import GenerationRequest, ModelRouter
from intelligence.schemas import ChatRequest, ChatResponse
from intelligence.tool_context import append_tool_result
from intelligence.tools.registry import create_default_registry


class IntelligenceEngine:
    def __init__(self):
        self.agent = AgentRuntime(create_default_registry())
        self.models = ModelRouter()

    async def generate_response(
        self,
        db: AsyncSession,
        request: ChatRequest,
    ) -> ChatResponse:
        conversation = await get_or_create_conversation(db, request.conversation_id)
        history = await load_context(db, conversation.id)
        context = build_context(history, request.message)

        decision = self.agent.decide(request.message)
        tool_output = await self.agent.execute(decision)
        context = append_tool_result(context, tool_output)

        provider = self.models.resolve(request.model)
        result = await provider.generate(
            GenerationRequest(
                model=request.model,
                messages=context,
                temperature=request.temperature,
                max_tokens=request.max_tokens,
            )
        )

        await save_message(db, conversation.id, "user", request.message, result.input_tokens)

        if tool_output:
            await save_message(db, conversation.id, "tool", str(tool_output), 0)

        await save_message(
            db,
            conversation.id,
            "assistant",
            result.text,
            result.output_tokens,
        )
        await db.commit()

        return ChatResponse(
            id=f"resp_{uuid4().hex}",
            model=request.model,
            response=result.text,
            conversation_id=conversation.external_id,
            usage={
                "input_tokens": result.input_tokens,
                "output_tokens": result.output_tokens,
            },
        )
