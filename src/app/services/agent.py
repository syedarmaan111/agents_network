from langchain_core.messages import (
    AIMessage,
    HumanMessage,
    SystemMessage,
    ToolMessage,
)
from langchain_groq import ChatGroq
from langchain_tavily import TavilySearch

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

    if not settings.tavily_api_key:
        raise RuntimeError("Tavily API key is not configured")

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

    tavily_search = TavilySearch(
        max_results=5,
        tavily_api_key=settings.tavily_api_key,
    )

    tools = {
        tavily_search.name: tavily_search,
    }

    llm_with_tools = llm.bind_tools(list(tools.values()))

    response = llm_with_tools.invoke(messages)

    while response.tool_calls:
        messages.append(response)

        for tool_call in response.tool_calls:
            tool = tools[tool_call["name"]]

            tool_result = tool.invoke(tool_call["args"])

            messages.append(
                ToolMessage(
                    content=str(tool_result),
                    tool_call_id=tool_call["id"],
                )
            )

        response = llm_with_tools.invoke(messages)

    return str(response.content)