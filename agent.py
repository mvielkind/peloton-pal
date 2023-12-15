from tools import (
    get_peloton_classes,
    get_recent_user_workouts,
    add_class_to_stack
)
from prompts import (
    AGENT_SYSTEM_MSG
)
from langchain.tools.render import format_tool_to_openai_function
from langchain.chat_models import ChatOpenAI
from langchain.prompts import MessagesPlaceholder, ChatPromptTemplate
from langchain.agents.format_scratchpad import format_to_openai_function_messages
from langchain.agents.output_parsers import OpenAIFunctionsAgentOutputParser
from langchain.schema.messages import AIMessage, HumanMessage
from langchain.agents import AgentExecutor


class PeloAgent:

    def __init__(self):

        # Define the LLM to use.
        llm = ChatOpenAI(
            model="gpt-4-1106-preview",
            temperature=0
        )

        # Bind the tools to the LLM.
        tools = [get_peloton_classes, get_recent_user_workouts, add_class_to_stack]
        openai_tools = [format_tool_to_openai_function(t) for t in tools]
        llm_with_tools = llm.bind(functions=openai_tools)

        MEMORY_KEY = "chat_history"
        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    AGENT_SYSTEM_MSG,
                ),
                MessagesPlaceholder(variable_name=MEMORY_KEY),
                ("user", "{input}"),
                MessagesPlaceholder(variable_name="agent_scratchpad"),
            ]
        )        

        agent = (
            {
                "input": lambda x: x["input"],
                "agent_scratchpad": lambda x: format_to_openai_function_messages(
                    x["intermediate_steps"]
                ),
                "chat_history": lambda x: x["chat_history"],
            }
            | prompt
            | llm_with_tools
            | OpenAIFunctionsAgentOutputParser()
        )
        self.chat_history = []
        self.agent_executor = AgentExecutor(
            agent=agent, 
            tools=tools, 
            verbose=True, 
            return_intermediate_steps=True, 
            handle_parsing_errors="Check your output and make sure it conforms!"
        )

    def invoke(self, user_msg: str) -> str:
        result = self.agent_executor.invoke(
            {
                "input": user_msg,
                "chat_history": self.chat_history
            }
        )

        # Save the response to the history.
        self.chat_history.extend(
            [
                HumanMessage(content=user_msg),
                AIMessage(content=result["output"])
            ]
        )

        return result["output"]
