import streamlit as st
from cb_backend import workflow
from langchain_core.messages import HumanMessage, AIMessage
import uuid

## UTILITY FUNCTION

def generate_thread_id():
  return str(uuid.uuid4())

def reset_chat():
    thread_id = generate_thread_id()
    st.session_state['thread_id'] = thread_id
    add_thread(thread_id)  # title = "New Chat"
    st.session_state['message_history'] = []
    st.rerun()

def add_thread(thread_id, title="New Chat"):
    if not any(t["id"] == thread_id for t in st.session_state['chat_threads']):
        st.session_state['chat_threads'].append({
            "id": thread_id,
            "title": title
        })

@st.cache_data(show_spinner=False)
def load_conversation_cached(thread_id):
    state = workflow.get_state(config={'configurable': {'thread_id': thread_id}})
    return state.values.get('messages', [])


# ===========================================
#  Initialize Session State (Clean)
# ===========================================

if 'chat_threads' not in st.session_state:
    thread_id = generate_thread_id()

    st.session_state['thread_id'] = thread_id
    st.session_state['chat_threads'] = [
        {"id": thread_id, "title": "New Chat"}
    ]
    st.session_state['message_history'] = []
# ============================================
#  Load and Display Conversation History
# ============================================
# Display all previous messages from the session 
for message in st.session_state['message_history']:
  with st.chat_message(message['role']): 
   st.text(message['content'])  

# ====================================
# Adding Side bar for previous chats
# ====================================
st.sidebar.title('MultiThread Chatbot')  
if st.sidebar.button('New Chat'):
  reset_chat()

st.sidebar.header('Your Conversations') 

for thread in st.session_state['chat_threads'][::-1]:
    if st.sidebar.button(thread["title"], key=f"thread_{thread['id']}"):
        st.session_state['thread_id'] = thread["id"]

        messages = load_conversation_cached(thread["id"])

        temp_messages = []
        for msg in messages:
            role = 'user' if isinstance(msg, HumanMessage) else 'assistant'
            temp_messages.append({'role': role, 'content': msg.content})

        st.session_state['message_history'] = temp_messages
        st.rerun()


###____MAIN UI___###

# for messages in st.session_state['message_history']:
#   with st.chat_message(messages['role']):
#     st.text(messages['content'])    



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

  # Update title if it's still "New Chat"
  for thread in st.session_state['chat_threads']:
      if thread["id"] == st.session_state['thread_id'] and thread["title"] == "New Chat":
          thread["title"] = user_input[:30]  # first 30 chars   
  
  ## Configure with current thread_id
  CONFIG = {'configurable': {'thread_id': st.session_state['thread_id']}}   

 ## Streaming AI Response from LangGraph
  with st.chat_message("assistant"):
    def ai_only_stream():
      for message_chunk, metadata in workflow.stream(
        {'messages':[HumanMessage(content=user_input)]},
        config=CONFIG,
        stream_mode='messages'
      ):
        if isinstance(message_chunk,AIMessage):
          yield message_chunk.content

    ai_message=st.write_stream(ai_only_stream())

    ## Add AI response to history
  st.session_state['message_history'].append(
    {
      'role':'assistant',
      'content':ai_message
    }
  )        


   
   
  
