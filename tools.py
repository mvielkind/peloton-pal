import re
from typing import List
import json
import datetime
import random
import streamlit as st
from collections import defaultdict
from langchain.agents import tool


@tool
def get_peloton_classes() -> str:
    """Get recent Peloton classes."""
    response = st.session_state["pelo_interface"].get_recent_classes()

    # response = json.load(open("peloton_classes.json", "r"))

    # Get available classes from the past N days.
    today = datetime.datetime.today().date()
    recent_classes = []
    # Create the instructors lookup.
    instructors = {i['id']: i['name'] for i in response['instructors']}
    for w in response['data']:
        workout_date = datetime.datetime.fromtimestamp(w['original_air_time']).date()

        if (today - workout_date).days > 14:
            break

        recent_classes.append(
            {
                'id': w["id"],
                'description': w['description'],
                'difficulty': w['difficulty_estimate'],
                'duration': w['duration'],
                'instructor': instructors[w['instructor_id']],
                'title': w['title'],
                'disciplie': w['fitness_discipline_display_name']
            }
        )
    random.shuffle(recent_classes)
    return json.dumps(recent_classes)


@tool
def get_recent_user_workouts() -> str:
    """Get the user's Peloton workouts from the past week."""
    # response = json.load(open("user_workouts.json", "r"))

    if "user_workouts" in st.session_state:
        return json.dumps(st.session_state["user_workouts"])

    response = st.session_state["pelo_interface"].get_user_workouts(
        user_id=st.session_state["pelo_user_id"]
    )

    st.session_state["user_workouts"] = response

    return json.dumps(response)


@tool
def add_class_to_stack(recommended_classes: List[str]) -> str:
    """Allows a user to add selected workout to the Peloton stack if the user explicitly asks to.

    recommended_classes: The list of recommended class IDs for the user. Could be one or more classes. ID should align with the classes recommended to the user.
    """
    # Iterate through the classes and add each to my stack.
    for class_id in recommended_classes:
        join_token = st.session_state["pelo_interface"].convert_ride_to_class_id(class_id)
        response = st.session_state["pelo_interface"].stack_class(join_token)

        if response == False:
            return "Sorry something went wrong."

    return "Classes added to your stack."


@tool
def get_classes_in_stack() -> str:
    """Retrieves the classes in the user's Peloton stack."""
    response = st.session_state["pelo_interface"].get_stack()

    if not response:
        return "No classes in your stack."

    return response


@tool
def clear_classes_in_stack() -> str:
    """Clears the classes in the user's Peloton stack."""
    response = st.session_state["pelo_interface"].clear_stack()

    if not response:
        return "No classes in your stack."
    
    return "Stack cleared."


@tool
def get_user_workout_preferences() -> str:
    """Retrieves the user workout preferences from the file system."""
    try:
        with open('goals.txt', 'r') as f:
            return f.read()
    except FileNotFoundError:
        return "No goal found."
    

@tool
def set_user_workout_preferences(preferences: str) -> str:
    """
    Writes the workout preferences from the user to the file system.

    preferences: The user's workout preferences.
    """
    with open('goals.txt', 'w') as f:
        f.write(preferences)
    
    return "Preferences saved."
