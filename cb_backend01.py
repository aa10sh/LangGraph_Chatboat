from langgraph.graph import StateGraph, START, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage
from typing import TypedDict, Annotated
from langgraph.graph.message import add_messages 
from dotenv import load_dotenv
from langgraph.checkpoint.memory import MemorySaver
import os

## Load environment variables
load_dotenv()
print("Api key loaded")
## Define model
model=ChatOpenAI()

class ChatState(TypedDict):
    messages: Annotated[list, add_messages]
    ## The add_messages annotation ensures messages are appended rather than replaced.

def llm_response(state: ChatState):
    """
    Chat node function that processes messages through the LLM.
    Args:
    state: Current state containing message history
    Returns:
    Dictionary with the LLM's response message
    """
    return {'messages': [model.invoke(state['messages'])]}


## Define Graph
graph=StateGraph(ChatState)

graph.add_node('llm_response',llm_response)

graph.add_edge(START,'llm_response')
graph.add_edge('llm_response',END)
checkpoint=MemorySaver()

workflow=graph.compile(checkpointer=checkpoint)
