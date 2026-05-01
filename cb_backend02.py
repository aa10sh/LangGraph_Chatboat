from langgraph.graph import StateGraph, START, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from typing import TypedDict, Annotated
from langgraph.graph.message import add_messages 
from dotenv import load_dotenv
from langgraph.checkpoint.sqlite import SqliteSaver
import sqlite3
import os

## Load environment variables
load_dotenv()
print("Api key loaded")

## Define model
model = ChatOpenAI()

class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    ## The add_messages annotation ensures messages are appended rather than replaced.

# def llm_response(state: ChatState):
#     """
#     Chat node function that processes messages through the LLM.
#     Args:
#     state: Current state containing message history
#     Returns:
#     Dictionary with the LLM's response message
#     """
#     return {'messages': [model.invoke(state['messages'])]}

def llm_response(state: ChatState):
    response = model.invoke(state['messages'])

    return {
        "messages": state["messages"] + [response]
    }

## SQLite Connection
conn = sqlite3.connect(database='chatbot.db', check_same_thread=False)

checkpointer = SqliteSaver(conn=conn)

## Define Graph
graph = StateGraph(ChatState)

graph.add_node('llm_response', llm_response)

graph.add_edge(START, 'llm_response')
graph.add_edge('llm_response', END)

workflow = graph.compile(checkpointer=checkpointer)


# def retrieve_all_threads():
#     """
#     BUG FIX #5: Previously sorted UUIDs lexicographically (sorted(set(...))),
#     which does NOT reflect creation order. Now tracks the latest timestamp
#     per thread and sorts by it, so the most recent thread loads on startup.
#     """
#     thread_map = {}  # thread_id -> latest timestamp string
#     for cp in checkpointer.list(None):
#         tid = cp.config['configurable']['thread_id']
#         ts = (cp.metadata or {}).get('created_at', '') or ''
#         if tid not in thread_map or ts > thread_map[tid]:
#             thread_map[tid] = ts
#     # Return thread_ids sorted oldest -> newest
#     return sorted(thread_map.keys(), key=lambda t: thread_map[t])

def retrieve_all_threads():
    thread_map = {}

    for cp in checkpointer.list(None):
        tid = cp.config.get('configurable', {}).get('thread_id')
        if not tid:
            continue

        ts = (cp.metadata or {}).get('created_at', '') or ''

        if tid not in thread_map or ts > thread_map[tid]:
            thread_map[tid] = ts

    return sorted(thread_map.keys(), key=lambda t: thread_map[t])

# def load_conversation(thread_id):
#     """
#     BUG FIX #2: checkpointer.list() returns checkpoints newest-first.
#     Previously, deduplication via `seen` set kept the first-encountered
#     (newest) copy of each message, resulting in scrambled order.
#     Fix: reverse the list so we process oldest-first, preserving correct order.
#     """
#     messages = []
#     seen = set()

#     # Collect all checkpoints and reverse to process oldest first
#     checkpoints = list(checkpointer.list(
#         {"configurable": {"thread_id": thread_id}}
#     ))
#     checkpoints.reverse()  # oldest checkpoint first

#     for cp in checkpoints:
#         checkpoint_data = cp.checkpoint or {}
#         state = checkpoint_data.get("values", {})
#         msgs = state.get("messages", [])

#         for msg in msgs:
#             key = (msg.type, msg.content)
#             if key not in seen:
#                 seen.add(key)
#                 messages.append(msg)

#     return messages

def load_conversation(thread_id):
    checkpoints = list(checkpointer.list(
        {"configurable": {"thread_id": thread_id}}
    ))

    if not checkpoints:
        return []

    # ✅ Always take the LATEST checkpoint only
    latest_cp = checkpoints[0]  # newest first

    checkpoint_data = latest_cp.checkpoint or {}
    state = checkpoint_data.get("values", {})

    return state.get("messages", [])