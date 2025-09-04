import streamlit as st
import os
import uuid
import ast
import dotenv
from langchain_core.messages import HumanMessage, BaseMessage, AIMessage, ToolMessage
from drive_agent import process_messages, State

dotenv.load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

st.title("ONBOARD YOURSELF AT MUK")

# Initialize session state
if "state" not in st.session_state:
    st.session_state.state: State = {"messages": [], "thread_id": str(uuid.uuid4())}

# Display messages
for message in st.session_state.state["messages"]:
    message: BaseMessage

    # Skip ToolMessage entirely (hidden from user)
    if isinstance(message, ToolMessage):
        continue

    # Display only AIMessage or HumanMessage
    with st.chat_message(message.type):
        st.write(message.content)

# Handle user input
if prompt := st.chat_input("Ask something?"):
    # Add user message
    new_msg = HumanMessage(content=prompt)
    st.session_state.state["messages"].append(new_msg)
    with st.chat_message("user"):
        st.write(prompt)

    # Process messages with spinner
    with st.spinner("Thinking..."):
        st.session_state.state = process_messages(st.session_state.state)
        st.rerun()
