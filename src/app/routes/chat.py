import logging

from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models import Conversation, Message
from app.schemas import ChatRequest, ChatResponse
from app.services.agent import get_assistant_response
from app.services.chat import get_conversation, get_conversation_messages
from app.utils.security import login_required


logger = logging.getLogger(__name__)
router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
@login_required
def chat(
    request: Request,
    chat_data: ChatRequest,
    database: Session = Depends(get_db),
):
    user_id = request.state.user_id

    if chat_data.conversation_id is None:
        conversation = Conversation(
            user_id=user_id,
            chatbot_type=chat_data.chatbot_type,
        )
        database.add(conversation)
        try:
            database.flush()
        except SQLAlchemyError:
            database.rollback()
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"error": True, "message": "Database error"},
            )
        previous_messages = []
    else:
        conversation = get_conversation(database, chat_data.conversation_id)
        if conversation is None:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={"error": True, "message": "Conversation not found"},
            )
        if conversation.user_id != user_id:
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content={"error": True, "message": "Conversation does not belong to user"},
            )
        if conversation.chatbot_type != chat_data.chatbot_type:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"error": True, "message": "Chatbot type does not match conversation"},
            )
        previous_messages = get_conversation_messages(database, conversation.id)

    database.add(
        Message(
            conversation_id=conversation.id,
            role="user",
            content=chat_data.message,
        )
    )

    try:
        assistant_response = get_assistant_response(
            chat_data.chatbot_type,
            previous_messages,
            chat_data.message,
        )
    except Exception:
        logger.exception("Groq request failed")
        database.rollback()
        return JSONResponse(
            status_code=status.HTTP_502_BAD_GATEWAY,
            content={"error": True, "message": "Groq response failure"},
        )

    database.add(
        Message(
            conversation_id=conversation.id,
            role="assistant",
            content=assistant_response,
        )
    )
    try:
        database.commit()
    except SQLAlchemyError:
        database.rollback()
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": True, "message": "Database error"},
        )

    return ChatResponse(
        conversation_id=conversation.id,
        chatbot_type=conversation.chatbot_type,
        response=assistant_response,
    )
