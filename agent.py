from tools import (
    get_peloton_classes,
    get_recent_user_workouts
)
from langchain.tools.render import format_tool_to_openai_function
from langchain.chat_models import ChatOpenAI
from langchain.prompts import MessagesPlaceholder, ChatPromptTemplate


class PeloAgent:

    def __init__(self):

        # Define the LLM to use.
        llm = ChatOpenAI(
            model="gpt-4-1106-preview",
            temperature=0
        )

        # Bind the tools to the LLM.
        tools = [get_peloton_classes, get_recent_user_workouts]
        openai_tools = [format_tool_to_openai_function(t) for t in tools]
        llm_with_tools = llm.bind_tools(openai_tools)

        
