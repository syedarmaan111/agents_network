from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Conversation, Message


def get_conversation(
    database: Session,
    conversation_id: int,
) -> Conversation | None:
    return database.scalar(
        select(Conversation).where(Conversation.id == conversation_id)
    )


def get_conversation_messages(
    database: Session,
    conversation_id: int,
) -> list[Message]:
    return list(
        database.scalars(
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at, Message.id)
        )
    )
