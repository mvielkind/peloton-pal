import streamlit as st
import logging
from typing import Dict, Text, Any
import json

from pydantic_ai.messages import (
    UserPrompt,
    ModelTextResponse
)
from peloton import PelotonAPI
from agent import peloton_agent
from schemas import UserWorkoutPreferences
import asyncio
from functools import wraps
import nest_asyncio
from concurrent.futures import ThreadPoolExecutor


# Apply nest_asyncio to handle nested event loops from calling the agent run.
nest_asyncio.apply()

def async_handler():
    """
    Decorator to handle async functions in Streamlit.
    Ensures proper event loop handling across threads.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            loop = asyncio.new_event_loop()
            executor = ThreadPoolExecutor(max_workers=1)
            try:
                asyncio.set_event_loop(loop)
                future = asyncio.ensure_future(func(*args, **kwargs), loop=loop)
                return loop.run_until_complete(future)
            finally:
                loop.close()
                executor.shutdown(wait=True)
        return wrapper
    return decorator


@async_handler()
async def run_agent():
    if st.session_state["last_response"]:
            output = st.session_state["agent"].run_sync(user_input, message_history=st.session_state["last_response"].all_messages())
    else:
        output = st.session_state["agent"].run_sync(user_input)
    
    return output



logging.basicConfig(level=logging.INFO)


@st.cache_data()
def load_goals() -> Dict[Text, Any]:
    """Loads the user fitness goals defined in goals.json to populate the goals dropdown."""
    try:
        return json.load(open('goals.json', 'r'))
    except FileNotFoundError:
        return {}


if "agent" not in st.session_state:
    st.session_state["agent"] = peloton_agent
    st.session_state["last_response"] = None
    st.session_state["chat_history"] = []


if "pelo_interface" not in st.session_state:
    pelo = PelotonAPI()
    pelo_auth = pelo.authenticate()
    user_id = pelo_auth.json()['user_id']
    st.session_state["pelo_interface"] = pelo
    st.session_state["pelo_user_id"] = user_id


if "user_preferences" not in st.session_state:
    # Try loading the JSON.
    try:
        preferences = UserWorkoutPreferences(**json.load(open("preferences.json", "r")))
    except FileNotFoundError:
        # if there are no existing preferences then load defaults.
        preferences = UserWorkoutPreferences()
    
    st.session_state["user_preferences"] = preferences

user_input = st.chat_input()


# Build the sidebar with quick actions.
with st.sidebar:
    st.title("Peloton Pal")
    st.subheader("An AI project to build personalized Peloton workouts.")
    st.divider()
    st.caption("QUICK ACTIONS")

    if st.button("Suggest a workout"):
        user_input = "Suggest a workout"

    if st.button("See Recent Workouts"):
        user_input = "Describe my recent workouts"


# Display the chat.
if st.session_state["last_response"]:
    for msg in st.session_state["last_response"].all_messages():
        if isinstance(msg, UserPrompt):
            content = msg.content
            with st.chat_message("user"):
                st.markdown(f'*:grey["{content}"]*')
        elif isinstance(msg, ModelTextResponse):
            content = msg.content
            with st.chat_message("assistant"):
                st.markdown(content)


if user_input:

    # Add the user input to the chat.
    with st.chat_message("user"):
        st.markdown(f'*:grey["{user_input}"]*')

        output = run_agent()
        print(output.all_messages())

        st.session_state["last_response"] = output
    
    with st.empty():
        with st.chat_message("assistant"):
            st.markdown(output.data)
