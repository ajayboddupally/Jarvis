from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from intelligence.agent import AgentRuntime
from intelligence.context import build_context
from intelligence.memory import get_or_create_conversation, load_context, save_message
from intelligence.providers import get_provider
from intelligence.schemas import ChatRequest, ChatResponse
from intelligence.tool_context import append_tool_result
from intelligence.tools.registry import create_default_registry


class IntelligenceEngine:
    def __init__(self):
        self.agent = AgentRuntime(create_default_registry())

    async def generate_response(
        self,
        db: AsyncSession,
        request: ChatRequest,
    ) -> ChatResponse:
        conversation = await get_or_create_conversation(
            db,
            request.conversation_id,
        )
        history = await load_context(db, conversation.id)
        context = build_context(history, request.message)

        decision = self.agent.decide(request.message)
        tool_output = await self.agent.execute(decision)
        context = append_tool_result(context, tool_output)

        provider = get_provider(request.model)
        response, input_tokens, output_tokens = await provider.generate(
            model=request.model,
            messages=context,
        )

        await save_message(
            db,
            conversation.id,
            "user",
            request.message,
            input_tokens,
        )

        if tool_output:
            await save_message(
                db,
                conversation.id,
                "tool",
                str(tool_output),
                0,
            )

        await save_message(
            db,
            conversation.id,
            "assistant",
            response,
            output_tokens,
        )

        await db.commit()

        return ChatResponse(
            id=f"resp_{uuid4().hex}",
            model=request.model,
            response=response,
            conversation_id=conversation.external_id,
            usage={
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
            },
        )
