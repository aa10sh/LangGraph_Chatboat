from langgraph.graph import StateGraph, START, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage
from typing import TypedDict
from dotenv import load_dotenv
import os

## Load environment variables
load_dotenv()
print("Api key loaded")
## Define model
model=ChatOpenAI()

## Defining state of the Graph
class ChatState(TypedDict):
    user_message: str
    ai_message: str

def llm_response(state: ChatState):
    prompt=f'return a short, precise answer of the user query: {state["user_message"]}'
    ai_message=model.invoke(prompt).content
    return {'ai_message': ai_message}


## Define Graph
graph=StateGraph(ChatState)
graph.add_node('llm_response',llm_response)
graph.add_edge(START,'llm_response')
graph.add_edge('llm_response',END)
workflow=graph.compile()

result=workflow.invoke({'user_message':'What is Photosynthesis?'})
print(result)