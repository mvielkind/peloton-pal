import streamlit as st
from typing import Dict, Text, Any, List
import json

import llm
from prompts import (
    CLASS_SUGGEST_PROMPT,
    EXTRACT_CLASS_TYPE_PROMPT,
)
from langchain.schema import (
    HumanMessage,
    AIMessage
)
from peloton import PelotonAPI
from agent import PeloAgent


if "messages" not in st.session_state:
    st.session_state["messages"] = []

if "chat" not in st.session_state:
    st.session_state["chat"] = llm.ChatInterface()

if "candidate_classes" not in st.session_state:
    st.session_state["candidate_classes"] = {}

if "cached_class_types" not in st.session_state:
    st.session_state["cached_class_types"] = []

if "agent" not in st.session_state:
    st.session_state["agent"] = PeloAgent()

if "pelo_interface" not in st.session_state:
    pelo = PelotonAPI()
    pelo_auth = pelo.authenticate()
    user_id = pelo_auth.json()['user_id']
    st.session_state["pelo_interface"] = pelo
    st.session_state["pelo_user_id"] = user_id

@st.cache_data()
def get_peloton_classes(class_type: str) -> Dict[Text, Any]:
    """Retrieves the users Peloton workouts and caches them for easier access."""
    _candidates = pelo.get_recent_classes(class_type)
    return _candidates


@st.cache_data()
def load_goals() -> Dict[Text, Any]:
    """Loads the user fitness goals defined in goals.json to populate the goals dropdown."""
    return json.load(open('goals.json', 'r'))


def display_recommended_workout(workout_obj, show_stack_button=False):
    # Display the workout.
    for id in workout_obj['classes']:
        _class = st.session_state["candidate_classes"][id["id"]]

        img, title = st.columns(2)
        with img:
            st.image(_class['image_url'], width=200)
        
        with title:
            st.header(_class['title'])
    
    st.markdown(workout_obj['reasoning'])

    if show_stack_button:
        st.button(
            label="Add to Stack",
            on_click=add_classes_to_stack
        )    


def generate_workout():
    """Two-step process to generate a workout for the client.
    """
    # If there is a user input check to see if the user is overriding their class type preferences.
    if user_input:
        class_type_entity_response = st.session_state['chat'].get_completion([{"role": "user", "content": EXTRACT_CLASS_TYPE_PROMPT.format(user_input=user_input)}])
        class_types = llm.parse_json_response(class_type_entity_response)['class_types']
    else:
        class_types = goal_map[goal]['class_types']

    # Get the candidate classes.
    candidate_classes = {}
    for class_type in class_types:
        if class_type not in st.session_state["cached_class_types"]:
            _candidate_classes = get_peloton_classes(class_type)
            # Add the candidates to the session.
            st.session_state['candidate_classes'] = st.session_state['candidate_classes'] | _candidate_classes
        else:
            _candidate_classes = [c for c in st.session_state["candidate_classes"]]
        candidate_classes = candidate_classes | _candidate_classes

    candidate_classes_str = llm.convert_candidate_classes_to_string(candidate_classes)

    # Suggest the workout.
    workout_prompt = CLASS_SUGGEST_PROMPT.format(str_recent_classes=candidate_classes_str, n_minutes=n_minutes)
    st.session_state["chat"].messages.append({"role": "user", "content": workout_prompt, "name": "background"})
    workout = st.session_state['chat'].get_completion()
    st.session_state["chat"].messages.append({"role": "assistant", "content": workout})

    # Try to convert workout to a JSON object.
    try:
        workout = json.loads(workout)
    except json.decoder.JSONDecodeError:
        workout = llm.parse_json_response(workout)

    return workout


def add_classes_to_stack():
    """Iterates through the suggested classes in the workout and favorites them to easily locate them in the Peloton app."""
    for id in workout["classes"]:
        ride_id = id["id"]
        class_id = st.session_state["candidate_classes"][ride_id]['join_tokens']['on_demand']
        class_added = pelo.stack_class(class_id)

        if not class_added:
            st.toast(
                "Error adding class to stack."
            )
        else:
            st.toast(
                "Class added to your stack!"
            )


def reset():
    """Resets the session state and cache."""
    st.session_state["workout_generate_button"] = False
    st.session_state["favorite_classes_button"] = False
    st.session_state["messages"] = []
    
    st.cache_data.clear()


# Setup the sidebar.
with st.sidebar:
    goal_map = load_goals()
    goal = st.selectbox(
        label="Choose a goal",
        options=list(goal_map.keys()),
        on_change=reset
    )

    n_minutes = st.number_input(
        "How many minutes do you want to workout?", 
        min_value=5, 
        max_value=120, 
        value=30, 
        step=5,
        on_change=reset)
    
    get_workout = st.button("Generate Workout")


st.title("Peloton GPT Personal Trainer")


# Display the chat.
for msg in st.session_state["agent"].chat_history:
    content = msg.content
    if isinstance(msg, HumanMessage):
        with st.chat_message("user"):
            st.markdown(f'*:grey["{content}"]*')
    elif isinstance(msg, AIMessage):
        with st.chat_message("assistant"):
            st.markdown(content)


# Init the Peloton API and load workouts.
# pelo = PelotonAPI()
# pelo_auth = pelo.authenticate()
# user_id = pelo_auth.json()['user_id']
# str_recent_classes = json.dumps(pelo.get_user_workouts(user_id))

user_input = st.chat_input()

if get_workout or user_input:
    if not user_input:
        user_input = "What is my recommended workout today?"

    # Add the user input to the chat.
    with st.chat_message("user"):
        st.markdown(f'*:grey["{user_input}"]*')
        output = st.session_state["agent"].invoke(user_input)
    
    # Generate the workout.
    with st.spinner("Generating your workout..."):
        with st.empty():
            with st.chat_message("assistant"):
                st.markdown(output)
