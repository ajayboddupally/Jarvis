from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from intelligence.context import build_context
from intelligence.memory import get_or_create_conversation, load_context, save_message
from intelligence.providers import get_provider
from intelligence.reasoning import classify_request
from intelligence.schemas import ChatRequest, ChatResponse


async def generate_response(
    db: AsyncSession,
    request: ChatRequest,
) -> ChatResponse:
    conversation = await get_or_create_conversation(db, request.conversation_id)
    history = await load_context(db, conversation.id)

    plan = classify_request(request.message)
    context = build_context(history, request.message)

    # Tool execution is deliberately separated from model generation.
    # The next layer will use plan.requires_tools to invoke registered tools.
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
