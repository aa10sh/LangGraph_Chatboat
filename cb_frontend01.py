import streamlit as st
from cb_backend01 import workflow
from langchain_core.messages import HumanMessage

# Configuration for LangGraph
# thread_id is required for the checkpointer to maintain memory.
 
CONFIG = {'configurable': {'thread_id': 'thread-1'}}

# ===========================================
# STEP 1: Initialize Session State
# ===========================================
# This only runs once when the session starts 
if 'message_history' not in st.session_state: 
  st.session_state['message_history'] = [] 


# ============================================
# STEP 2: Load and Display Conversation History
# ============================================
# Display all previous messages from the session 
for message in st.session_state['message_history']:
  with st.chat_message(message['role']): 
   st.text(message['content'])  

# =====================================
# STEP 3: Get User Input
# ===================================== 
user_input = st.chat_input('Type here')


# ============================================
# STEP 4: Process User Input
# ============================================ 

if user_input:
  
  ## handle user Message
  # Add to history
  st.session_state['message_history'].append({ 
    'role': 'user',
    'content': user_input
    })
    # Display on screen 
  with st.chat_message('user'): 
     st.text(user_input)

 ## Get AI Response from LangGraph
 # Invoke the chatbot with the user's message 
  with st.chat_message('assistant'):
    ai_message=st.write_stream(
      message_chunk.content
        for message_chunk, metadata in workflow.stream(
          {'messages':[HumanMessage(content=user_input)]},
          config=CONFIG,
          stream_mode='messages'
        )
    )  
  
  ## Handle AI Message
  # Add to history
  st.session_state['message_history'].append({ 
  'role': 'assistant',
  'content': ai_message
  })

  # # Display on screen
  # with st.chat_message('assistant'): 
  #  st.text(ai_message)