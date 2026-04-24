import streamlit as st
from cb_backend import workflow
from langchain_core.messages import HumanMessage, AIMessage
import uuid

## UTILITY FUNCTION

def generate_thread_id():
  return str(uuid.uuid4())

def reset_chat():
  """Reset chat: new thread ID, clear history, add to thread list.""" 
  thread_id=generate_thread_id()
  st.session_state['thread_id']=thread_id
  add_thread(st.session_state['thread_id'])
  st.session_state['message_history']=[]

def add_thread(thread_id):
  """Add thread to the threads list if not already present.""" 
  if thread_id not in st.session_state['chat_threads']:
    st.session_state['chat_threads'].append(thread_id)

def load_conversation(thread_id):
  """Load messages for a thread from LangGraph backend."""
  state=workflow.get_state(config={'configurable':{'thread_id': thread_id}})
  return state.values.get('messages',[])


# ===========================================
# STEP 1: Initialize Session State
# ===========================================
# These condition only runs once when the session starts 
if 'message_history' not in st.session_state: 
  st.session_state['message_history'] = [] 

if 'thread_id' not in st.session_state:
  st.session_state['thread_id']=generate_thread_id()
  st.session_state['chat_threads'] = [st.session_state['thread_id']]  


if 'chat_threads' not in st.session_state:
  st.session_state['chat_threads']=[]  

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

for thread_id in st.session_state['chat_threads'][::-1]:
  if st.sidebar.button(str(thread_id)):
    st.session_state['thread_id']=thread_id
    messages=load_conversation(thread_id)

    temp_messages=[]
    for msg in messages:
      if isinstance(msg, HumanMessage):
        role='user'
      else:
        role='assistant'
      temp_messages.append({'role':role, 'content':msg.content})   

    st.session_state['message_history']=temp_messages


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


   
   
  
  ## Handle AI Message
  # Add to history
  
  # # Display on screen
  # with st.chat_message('assistant'): 
  #  st.text(ai_message)