import streamlit as st
from typing import Dict, Text, Any, List
import json

import llm
from prompts import (
    SYSTEM_MSG,
    CLASS_TYPE_PROMPT,
    CLASS_SUGGEST_PROMPT
)
from peloton import PelotonAPI


if "messages" not in st.session_state:
    st.session_state["messages"] = []

@st.cache_data()
def get_peloton_classes(class_type: str) -> Dict[Text, Any]:
    """Retrieves the users Peloton workouts and caches them for easier access."""
    return pelo.get_recent_classes(class_type)


@st.cache_data()
def load_goals() -> Dict[Text, Any]:
    """Loads the user fitness goals defined in goals.json to populate the goals dropdown."""
    return json.load(open('goals.json', 'r'))


def generate_workout():
    """Two-step process to generate a workout for the client.
    """
    str_goal_categories = ", ".join(goal_map[goal]['class_types'])
    # Ask the model what type of class the user should take.
    class_type_prompt = CLASS_TYPE_PROMPT.format(str_recent_workouts=str_recent_classes, str_candidate_categories=str_goal_categories)
    st.session_state["messages"].append({"role": "user", "content": class_type_prompt})    
    class_type_response = llm.get_completion_from_messages(st.session_state['messages'])
    st.session_state["messages"].append({"role": "assistant", "content": class_type_response})

    # Use the class type to get the candidate classes from Peloton.
    class_type = llm.parse_json_response(class_type_response)['class_type']
    # Get the candidate classes.
    candidate_classes = get_peloton_classes(class_type)
    candidate_classes_str = llm.convert_candidate_classes_to_string(candidate_classes)

    # Suggest the workout.
    workout_prompt = CLASS_SUGGEST_PROMPT.format(str_recent_classes=candidate_classes_str, n_minutes=n_minutes)
    st.session_state["messages"].append({"role": "user", "content": workout_prompt})
    workout = llm.get_completion_from_messages(st.session_state['messages'])
    st.session_state["messages"].append({"role": "assistant", "content": workout})

    # Try to convert workout to a JSON object.
    try:
        workout = json.loads(workout)
    except json.decoder.JSONDecodeError:
        workout = llm.parse_json_response(workout)

    return workout, candidate_classes


def add_classes_to_stack():
    """Iterates through the suggested classes in the workout and favorites them to easily locate them in the Peloton app."""
    for id in workout["classes"]:
        ride_id = id["id"]
        class_id = candidate_classes[ride_id]['join_tokens']['on_demand']
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


# Init the Peloton API and load workouts.
pelo = PelotonAPI()
pelo_auth = pelo.authenticate()
user_id = pelo_auth.json()['user_id']
str_recent_classes = json.dumps(pelo.get_user_workouts(user_id))

if goal:
    st.session_state['messages'].append({"role": "system", "content": SYSTEM_MSG.format(str_fitness_goal=goal)})

user_input = st.chat_input()
if get_workout or user_input:
    # Add the user input to the chat.
    if user_input:
        st.session_state['messages'].append({"role": "user", "content": user_input})
        st.markdown(f'*:grey["{user_input}"]*')
    else:
        st.markdown(f'*:grey["What is my recommended workout today?"]*')
    
    # Generate the workout.
    workout, candidate_classes = generate_workout()
    
    # Display the workout.
    for id in workout['classes']:
        _class = candidate_classes[id["id"]]

        img, title = st.columns(2)
        with img:
            st.image(_class['image_url'], width=200)
        
        with title:
            st.header(_class['title'])
    
    st.write(workout['reasoning'])

    st.button(
        label="Build Stack",
        on_click=add_classes_to_stack
    )
