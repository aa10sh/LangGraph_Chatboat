import streamlit as st
from cb_backend01 import workflow   # your compiled graph
from langchain_core.messages import HumanMessage, AIMessage

st.set_page_config(page_title="LangGraph Chatbot", page_icon="🤖")

st.title("🤖 LangGraph Chatbot")

# -------------------------------
# Initialize session state
# -------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# -------------------------------
# Display chat history
# -------------------------------
for msg in st.session_state.messages:
    if isinstance(msg, HumanMessage):
        with st.chat_message("user"):
            st.markdown(msg.content)
    elif isinstance(msg, AIMessage):
        with st.chat_message("assistant"):
            st.markdown(msg.content)

# -------------------------------
# User input
# -------------------------------
user_input = st.chat_input("Type your message...")

if user_input:
    # Add user message to session
    human_msg = HumanMessage(content=user_input)
    st.session_state.messages.append(human_msg)

    # Display user message immediately
    with st.chat_message("user"):
        st.markdown(user_input)

    # -------------------------------
    # Call LangGraph workflow
    # -------------------------------
    response = workflow.invoke({
        "messages": st.session_state.messages
    })

    # Extract latest AI message
    ai_msg = response["messages"][-1]

    # Store AI response
    st.session_state.messages.append(ai_msg)

    # Display AI response
    with st.chat_message("assistant"):
        st.markdown(ai_msg.content)