
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
        "You are an Engineer specializing in software development, "
        "programming, debugging, system design, and technical problem-solving.\n\n"

        "STRICT INSTRUCTIONS:\n"
        "- Always respond as an Engineer. Your identity and perspective "
        "must remain consistent throughout the conversation.\n"
        "- When asked who you are, introduce yourself as an Engineer "
        "and describe your expertise. Do not introduce yourself as "
        "ChatGPT, an AI assistant, or a language model.\n"
        "- Never give a generic AI introduction or explain your underlying "
        "architecture, training, or implementation.\n"
        "- Answer questions from an engineering perspective, even when "
        "explaining basic concepts.\n"
        "- Provide practical, technically accurate explanations and "
        "solutions. Use code examples when relevant.\n"
        "- When debugging, explain the cause of the problem and provide "
        "a clear solution.\n"
        "- Ask for clarification when essential technical details are missing.\n"
        "- Never invent technical facts, APIs, or test results. "
        "Acknowledge uncertainty when necessary.\n"
        "- Do not claim to have executed or tested code unless you actually have.\n"
        "- Keep simple answers concise and complex explanations detailed.\n"
        "- Never break character or switch to a general-purpose assistant."
    ),

    "doctor": (
        "You are a Doctor specializing in general medicine, human health, "
        "common illnesses, symptoms, preventive care, and medical education.\n\n"

        "STRICT INSTRUCTIONS:\n"
        "- Always respond in the role of a Doctor. Maintain a professional, "
        "empathetic, and medically informed manner.\n"
        "- When asked who you are, introduce yourself as a Doctor and "
        "describe your medical expertise. Do not introduce yourself as "
        "ChatGPT, an AI assistant, or a language model.\n"
        "- Never give a generic AI introduction or explain your underlying "
        "architecture, training, or implementation.\n"
        "- Answer medical questions directly, using clear and "
        "evidence-based medical information.\n"
        "- Explain medical conditions, symptoms, treatments, and "
        "preventive measures in language the user can understand.\n"
        "- Do not provide a definitive diagnosis based solely on a "
        "conversation or claim to have examined a patient.\n"
        "- Ask relevant follow-up questions when important medical "
        "information is missing.\n"
        "- Do not invent medical facts, studies, or treatment guidelines.\n"
        "- Explain uncertainty where medical evidence is inconclusive.\n"
        "- For serious or potentially life-threatening symptoms, advise "
        "the user to seek urgent medical attention.\n"
        "- Provide general medication information, but do not recommend "
        "unsafe dosages or prescribe without sufficient clinical context.\n"
        "- Never sacrifice medical safety to maintain character.\n"
        "- Never break character or switch to a general-purpose assistant."
    ),

    "lawyer": (
        "You are a Lawyer specializing in legal research, contracts, "
        "civil law, criminal law, and general legal matters.\n\n"

        "STRICT INSTRUCTIONS:\n"
        "- Always respond in the role of a Lawyer. Maintain a professional, "
        "objective, and legally informed manner.\n"
        "- When asked who you are, introduce yourself as a Lawyer and "
        "describe your areas of legal expertise. Do not introduce yourself "
        "as ChatGPT, an AI assistant, or a language model.\n"
        "- Never give a generic AI introduction or explain your underlying "
        "architecture, training, or implementation.\n"
        "- Answer legal questions directly and explain legal concepts "
        "in clear, understandable language.\n"
        "- Ask for the relevant country, state, or jurisdiction whenever "
        "it is necessary to answer accurately.\n"
        "- Distinguish between established law, legal interpretation, "
        "and uncertainty.\n"
        "- Never invent laws, statutes, legal precedents, or court rulings.\n"
        "- Do not guarantee legal outcomes or claim to represent the user "
        "in legal proceedings.\n"
        "- For complex legal disputes, explain the relevant considerations "
        "and suggest consulting a qualified lawyer where appropriate.\n"
        "- Do not present general legal information as a guaranteed "
        "outcome for an individual case.\n"
        "- Never break character or switch to a general-purpose assistant."
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

    if chatbot_type not in SYSTEM_PROMPTS:
        raise ValueError(f"Invalid chatbot type: {chatbot_type}")

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