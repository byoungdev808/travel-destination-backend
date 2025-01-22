import os
from app.helper.vector_store import retrieve_document
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import AIMessage
from langchain_core.runnables import chain
from langgraph.prebuilt import ToolNode
from langchain_core.tools import tool
from langchain_core.messages import SystemMessage
from langgraph.prebuilt import create_react_agent, ToolNode
from datetime import datetime, timezone
from langgraph.graph import StateGraph, MessagesState, START, END

from langgraph.checkpoint.postgres import PostgresSaver
from psycopg_pool import ConnectionPool, AsyncConnectionPool
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver

from app.database import SessionLocal

from app.helper.destination import get_destinations
from app.helper.knowledge_base import get_knowledge_bases_for_destination
from app.helper.weather import get_weather

from app.schemas import ChatInputType
from typing import Annotated
import json

from dotenv import load_dotenv
load_dotenv()

DATABASE_URL = os.environ['DATABASE_URL']

@tool
def get_destination_tool():
    """Get all location or destination saved by the user
    
        Returns:
        A list saved location or destination in dictionary format
    """
    with SessionLocal() as db:
        results = get_destinations(db)
        destinations = [result.__dict__ for result in results]
        return destinations

@tool
def get_weather_tool(location: Annotated[str, "name of location or destination"]):
    """Get the current weather information such as temperature for a location
        
        Returns:
        Current weather information such as temperature in fahrenheit
    """
    return get_weather(location)

@tool
def get_knowledge_bases_for_destination_tool(destination_id: Annotated[str, "ID of location or destination"]):
    """Get all saved knowledge base or notes of a given location

        Returns:
        A list of knowledge base/notes of a saved location
    """
    with SessionLocal() as db:
        results = get_knowledge_bases_for_destination(db, destination_id)
        knowledge_bases = [result.content for result in results]
        return knowledge_bases

@tool
def search_knowledge_base_content_tool(text: Annotated[str, "Text query to be searched"]):
    """Search content on all knowledge bases using text query

        Returns:
        A list knowledge base/notes relevant to the text query
    """
    return retrieve_document(text)


tools = [get_destination_tool, get_weather_tool, get_knowledge_bases_for_destination_tool, search_knowledge_base_content_tool]
tool_node = ToolNode(tools)

model_with_tools = ChatOpenAI(model="gpt-4o", temperature=0).bind_tools(tools)

def should_continue(state: MessagesState):
    messages = state["messages"]
    last_message = messages[-1]
    if last_message.tool_calls:
        return "tools"
    return END


def call_model(state: MessagesState):
    messages = state["messages"]
    response = model_with_tools.invoke(messages)
    print(response)
    return {"messages": [response]}


def create_graph(checkpointer):
    workflow = StateGraph(MessagesState)

    # Define the two nodes we will cycle between
    workflow.add_node("agent", call_model)
    workflow.add_node("tools", tool_node)

    workflow.add_edge(START, "agent")
    workflow.add_conditional_edges("agent", should_continue, ["tools", END])
    workflow.add_edge("tools", "agent")

    graph = workflow.compile()
    return graph

@chain
async def agent_executor(input: ChatInputType):
    messages = input['messages']
    print(messages)
    # thread_id = input['thread_id']

    connection_kwargs = {
        "autocommit": True,
        "prepare_threshold": 0,
    }

    inputs = {
        "messages": messages
    }

    async with AsyncConnectionPool(
        # Example configuration
        conninfo=DATABASE_URL,
        max_size=20,
        kwargs=connection_kwargs,) as pool:
        checkpointer = AsyncPostgresSaver(pool)

        # NOTE: you need to call .setup() the first time you're using your checkpointer
        #await checkpointer.setup()

        graph = create_graph(checkpointer=checkpointer)

        async for chunk in graph.astream(inputs):
            if 'agent' in chunk:
                yield chunk


