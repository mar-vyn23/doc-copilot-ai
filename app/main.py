import streamlit as st
import os
import uuid
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, BaseMessage,ToolMessage
from drive_agent import process_messages, State

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

st.title("ONBOARD YOURSELF AT MUK")

if "state" not in st.session_state:
    st.session_state.state: State = {"messages": [], "thread_id": str(uuid.uuid4())}

for message in st.session_state.state["messages"]:
    message: BaseMessage

    if isinstance(message, ToolMessage):
        continue

    with st.chat_message(message.type):
        st.write(message.content)

if prompt := st.chat_input("Ask something?"):
    
    new_msg = HumanMessage(content=prompt)
    st.session_state.state["messages"].append(new_msg)
    with st.chat_message("user"):
        st.write(prompt)

    with st.spinner("Thinking..."):
        st.session_state.state = process_messages(st.session_state.state)
        st.rerun()
