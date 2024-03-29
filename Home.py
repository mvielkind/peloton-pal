import streamlit as st
import logging
from typing import Dict, Text, Any
import json

from langchain.schema import (
    HumanMessage,
    AIMessage
)
from peloton import PelotonAPI
from agent import PeloAgent


logging.basicConfig(level=logging.INFO)


@st.cache_data()
def load_goals() -> Dict[Text, Any]:
    """Loads the user fitness goals defined in goals.json to populate the goals dropdown."""
    try:
        return json.load(open('goals.json', 'r'))
    except FileNotFoundError:
        return {}


if "agent" not in st.session_state:
    st.session_state["agent"] = PeloAgent()


if "pelo_interface" not in st.session_state:
    pelo = PelotonAPI()
    pelo_auth = pelo.authenticate()
    user_id = pelo_auth.json()['user_id']
    st.session_state["pelo_interface"] = pelo
    st.session_state["pelo_user_id"] = user_id


user_input = st.chat_input()


# Build the sidebar with quick actions.
with st.sidebar:
    st.title("Peloton Pal")
    st.subheader("An AI project to build personalized Peloton workouts.")
    st.divider()
    st.caption("QUICK ACTIONS")

    if st.button("Set my preferences"):
        user_input = "Set my preferences"

    if st.button("Suggest a workout"):
        user_input = "Suggest a workout"

    if st.button("View Stack"):
        user_input = "What classes are in my stack?"

    if st.button("See Recent Workouts"):
        user_input = "Describe my recent workouts"


# Display the chat.
for msg in st.session_state["agent"].chat_history:
    content = msg.content
    if isinstance(msg, HumanMessage):
        with st.chat_message("user"):
            st.markdown(f'*:grey["{content}"]*')
    elif isinstance(msg, AIMessage):
        with st.chat_message("assistant"):
            st.markdown(content)


if user_input:

    # Add the user input to the chat.
    with st.chat_message("user"):
        st.markdown(f'*:grey["{user_input}"]*')
        output = st.session_state["agent"].invoke(user_input)
    
    with st.empty():
        with st.chat_message("assistant"):
            st.markdown(output)
