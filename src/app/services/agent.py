from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_groq import ChatGroq

from app.config.settings import get_settings
from app.models import Message


SYSTEM_PROMPTS = {
    "engineer": (
        "You are a helpful engineering assistant. Explain technical and "
        "engineering questions clearly and practically."
    ),
    "doctor": (
        "You are a helpful medical information assistant. Provide general "
        "educational medical information. For serious or personal medical "
        "concerns, remind the user to consult a qualified healthcare professional."
    ),
    "lawyer": (
        "You are a helpful legal information assistant. Provide general legal "
        "information. Laws vary by jurisdiction and the response is not a "
        "substitute for professional legal advice."
    ),
}


def get_assistant_response(
    chatbot_type: str,
    previous_messages: list[Message],
    user_message: str,
) -> str:
    settings = get_settings()
    if not settings.groq_api_key:
        raise RuntimeError("Groq API key is not configured")

    messages = [SystemMessage(content=SYSTEM_PROMPTS[chatbot_type])]
    for message in previous_messages:
        if message.role == "user":
            messages.append(HumanMessage(content=message.content))
        elif message.role == "assistant":
            messages.append(AIMessage(content=message.content))

    messages.append(HumanMessage(content=user_message))

    llm = ChatGroq(
        api_key=settings.groq_api_key,
        model=settings.groq_model,
    )
    response = llm.invoke(messages)

    return str(response.content)
