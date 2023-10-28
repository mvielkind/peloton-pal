import streamlit as st
from typing import Dict, Text, Any
import json

import llm
from peloton import PelotonAPI


# Set session_state for nested buttons.
if "workout_generate_button" not in st.session_state:
    st.session_state["workout_generate_button"] = False

if "favorite_classes_button" not in st.session_state:
    st.session_state["favorite_classes_button"] = False

@st.cache_data()
def get_peloton_classes(class_type: str) -> Dict[Text, Any]:
    """Retrieves the users Peloton workouts and caches them for easier access."""
    return pelo.get_recent_classes(class_type)


@st.cache_data()
def load_goals() -> Dict[Text, Any]:
    """Loads the user fitness goals defined in goals.json to populate the goals dropdown."""
    return json.load(open('goals.json', 'r'))


def favorite_workouts():
    """Iterates through the suggested classes in the workout and favorites them to easily locate them in the Peloton app."""
    for id in workout['classes']:
        pelo.favorite(id)
    st.session_state["favorite_classes_button"] = True


def reset():
    """Resets the session state and cache."""
    st.session_state["workout_generate_button"] = False
    st.session_state["favorite_classes_button"] = False
    st.cache_data.clear()


st.title("Peloton GPT Personal Trainer")


# Init the Peloton API and load workouts.
pelo = PelotonAPI()
pelo_auth = pelo.authenticate()
user_id = pelo_auth.json()['user_id']
str_recent_classes = json.dumps(pelo.get_user_workouts(user_id))

# Allow user to select goal.
all_goals = load_goals()
if len(all_goals) == 0:
    st.write("No goals defined in goals.json. Define your goals and then continue.")
else:
    goal = st.selectbox(
        "What is your goal?",
        list(all_goals.keys())
    )
    goal_prompt = all_goals[goal]['goal']
    str_goal_categories = ", ".join(all_goals[goal]['class_types'])

    # Get number of minutes from the user.
    n_minutes = st.number_input(
        "How many minutes do you want to workout?", 
        min_value=5, 
        max_value=120, 
        value=30, 
        step=5)


    get_workout = st.button("Generate Workout")
    if get_workout:
        st.session_state["workout_generate_button"] = not st.session_state["workout_generate_button"]

    if st.session_state["workout_generate_button"]:
        # Get the suggested class type.
        class_type_obj = llm.suggest_class_type(str_recent_classes, goal_prompt, str_goal_categories)
        class_type = class_type_obj['class_type']
        st.write(f"Recommended class type: {class_type.capitalize()}")
        st.write(class_type_obj["reasoning"])

        # Get the candidate classes.
        candidate_classes = get_peloton_classes(class_type)

        # Suggest the workout.
        st.header("Suggested Workout")
        workout, err = llm.suggest_workout(str_recent_classes, candidate_classes, n_minutes, goal_prompt)
        if err:
            st.write(err)
            st.stop()

        for id in workout['classes']:
            _class = candidate_classes[id["id"]]

            img, title = st.columns(2)
            with img:
                st.image(_class['image_url'], width=200)
            
            with title:
                st.header(_class['title'])
        
        st.write(workout['reasoning'])

        st.button(
            label="Favorite Classes",
            on_click=favorite_workouts
        )

        if st.session_state["favorite_classes_button"]:
            st.write("Classes Flagged!")
            st.button(
                label="Reset",
                on_click=reset
            )
