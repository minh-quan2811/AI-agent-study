from langgraph.graph import MessagesState, StateGraph
from typing import TypedDict, Annotated
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.graph.message import add_messages
from langchain_community.utilities import GoogleSerperAPIWrapper
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.tools import Tool
from langgraph.checkpoint.memory import MemorySaver
from dotenv import load_dotenv

import os


class State(TypedDict):
    messages: Annotated[list, add_messages]

load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")
os.environ["GOOGLE_API_KEY"] = api_key

def initialize_llm():
    """Initialize and return the LLM client"""
    return ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            temperature=0,
            max_tokens=None,
            timeout=None,
            max_retries=2,
)

llm = initialize_llm()

def chatbot(state: State):
    return {"messages": [llm_with_tools.invoke(state["messages"])]}

search = GoogleSerperAPIWrapper()
search_tool = Tool(
    name="google_search",
    func=search.run,
    description="Use this tool to search Google using Serper API.",
    return_direct=True
)

tools = [search_tool]
llm_with_tools = llm.bind_tools(tools)


memory = MemorySaver()
graph_builder = StateGraph(State)
graph_builder.add_node("chatbot", chatbot)

tool_node = ToolNode(tools=[search_tool])
graph_builder.add_node("tools", tool_node)
graph_builder.add_conditional_edges("chatbot", tools_condition)
graph_builder.add_edge("tools", "chatbot")

graph_builder.set_entry_point("chatbot")
graph_builder.set_finish_point("chatbot")

graph = graph_builder.compile(
    checkpointer=memory,
    interrupt_after=["tools"],
)

config = {"configurable": {"thread_id": "1"}}
