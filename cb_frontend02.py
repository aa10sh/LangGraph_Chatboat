import streamlit as st
from cb_backend02 import workflow, retrieve_all_threads, load_conversation
from langchain_core.messages import HumanMessage, AIMessage
import uuid

##_________Utility Functions_________##

def generate_thread_id():
    """Generate Unique ThreadId"""
    return str(uuid.uuid4())

def reset_chat():
    thread_id = generate_thread_id()

    if thread_id not in [t["id"] for t in st.session_state['chat_threads']]:
        add_thread(thread_id)

    st.session_state['thread_id'] = thread_id
    st.session_state['message_history'] = []
    st.rerun()

def add_thread(thread_id, title="New Chat"):
    """Add a thread to the list if it doesn't already exist"""
    if not any(t["id"] == thread_id for t in st.session_state['chat_threads']):
        st.session_state['chat_threads'].append({
            "id": thread_id,
            "title": title
        })


# BUG FIX #1: Removed @st.cache_data decorator.
# Caching this function meant clicking a sidebar thread always returned
# the stale first-load result — SQLite was never re-queried.
# SQLite reads are fast enough that caching isn't needed here.
def load_conversation_cached(thread_id):
    return load_conversation(thread_id)


def get_thread_title(thread_id):
    messages = load_conversation_cached(thread_id)
    for msg in messages:
        if isinstance(msg, HumanMessage):
            return msg.content[:30]
    return "New Conversation"


# ===========================================
# STEP 1: Initialize Session State
# ===========================================

if 'chat_threads' not in st.session_state:
    thread_ids = retrieve_all_threads()  # already sorted oldest->newest in backend

    if thread_ids:
        st.session_state['chat_threads'] = [
            {"id": tid, "title": get_thread_title(tid)} for tid in thread_ids
        ]

        st.session_state['thread_id'] = thread_ids[-1]  # load most recent thread

        messages = load_conversation_cached(st.session_state['thread_id'])
        st.session_state['message_history'] = [
            {
                "role": "user" if isinstance(m, HumanMessage) else "assistant",
                "content": m.content
            }
            for m in messages
        ]

    else:
        thread_id = generate_thread_id()
        st.session_state['thread_id'] = thread_id
        st.session_state['chat_threads'] = [
            {"id": thread_id, "title": "New Chat"}
        ]
        st.session_state['message_history'] = []


# ============================================
# Load and Display Conversation History
# ============================================
for message in st.session_state['message_history']:
    with st.chat_message(message['role']):
        st.text(message['content'])


# ====================================
# Sidebar for previous chats
# ====================================
st.sidebar.title('MultiThread Chatbot')

if st.sidebar.button('New Chat'):
    reset_chat()

st.sidebar.header('Your Conversations')

for thread in st.session_state['chat_threads'][::-1]:
    if st.sidebar.button(thread["title"], key=f"thread_{thread['id']}"):
        st.session_state['thread_id'] = thread["id"]

        messages = load_conversation_cached(thread["id"])  # no cache: always fresh

        temp_messages = []
        for msg in messages:
            role = 'user' if isinstance(msg, HumanMessage) else 'assistant'
            temp_messages.append({'role': role, 'content': msg.content})

        st.session_state['message_history'] = temp_messages
        st.rerun()


###____MAIN UI___###

# =====================================
# STEP 3: Get User Input
# =====================================
user_input = st.chat_input('Type here')


# ============================================
# STEP 4: Process User Input
# ============================================

if user_input:

    ## Handle user message
    # Add to history
    st.session_state['message_history'].append({
        'role': 'user',
        'content': user_input
    })

    # Display on screen
    with st.chat_message('user'):
        st.text(user_input)

    # Update title if it's still "New Chat"
    for thread in st.session_state['chat_threads']:
        if thread["id"] == st.session_state['thread_id'] and thread["title"] == "New Chat":
            thread["title"] = user_input[:30]  # first 30 chars

    ## Configure with current thread_id
    CONFIG = {'configurable': {'thread_id': st.session_state['thread_id']}}

    # BUG FIX #3: Fixed indentation — the comment and `with` block were misaligned,
    # which would cause an IndentationError at runtime.
    ## Streaming AI Response from LangGraph
    with st.chat_message("assistant"):
        def ai_only_stream():
            for message_chunk, metadata in workflow.stream(
                {'messages': [HumanMessage(content=user_input)]},
                config=CONFIG,
                stream_mode='messages'
            ):
                if isinstance(message_chunk, AIMessage):
                    yield message_chunk.content

        ai_message = st.write_stream(ai_only_stream())

    ## Add AI response to history
    st.session_state['message_history'].append(
        {
            'role': 'assistant',
            'content': ai_message
        }
    )     


   
   
  
