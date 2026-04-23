import streamlit as st
from chatboat_backend import model
from langchain_core.messages import HumanMessage

# Input box
user_input = st.chat_input("Type here..")

# Run only when user types something
if user_input:
    
    # Show user message
    with st.chat_message("user"):
        st.text(user_input)

    # Get response
    response = model.invoke([
        HumanMessage(content=user_input)
    ])

    # Show AI response
    with st.chat_message('assistant'): 
        st.text(response.content)