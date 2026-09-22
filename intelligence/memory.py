from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from intelligence.config import settings
from intelligence.models import Conversation, Message


async def get_or_create_conversation(
    db: AsyncSession,
    external_id: str | None,
) -> Conversation:
    if external_id:
        result = await db.execute(
            select(Conversation).where(Conversation.external_id == external_id)
        )
        conversation = result.scalar_one_or_none()
        if conversation:
            return conversation

    import uuid

    conversation = Conversation(
        external_id=external_id or f"conv_{uuid.uuid4().hex}",
    )
    db.add(conversation)
    await db.flush()
    return conversation


async def load_context(
    db: AsyncSession,
    conversation_id: UUID,
) -> list[Message]:
    result = await db.execute(
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.desc())
        .limit(settings.max_context_messages)
    )
    return list(reversed(result.scalars().all()))


async def save_message(
    db: AsyncSession,
    conversation_id: UUID,
    role: str,
    content: str,
    token_count: int = 0,
) -> Message:
    message = Message(
        conversation_id=conversation_id,
        role=role,
        content=content,
        token_count=token_count,
    )
    db.add(message)
    await db.flush()
    return message
