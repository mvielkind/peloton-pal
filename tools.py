import re
from typing import List
import json
import datetime
import random
from openai import OpenAI
import streamlit as st
from collections import defaultdict
from langchain.agents import tool
from prompts import (
    RECOMMEND_DISCIPLINE
)


CLIENT = OpenAI()


@tool
def determine_fitness_discipline(
    user_workouts: str,
    preferences: str
) -> str:
    """Determine the recommended fitness disciplines for the next workout.

    Utilizes the user's recent workouts and preferences to determine the 
    fitness disciplines that should be the focus of the next workout. The 
    returned disciplines will be used to find candidate classes for the workout.
    """
    prompt = RECOMMEND_DISCIPLINE.format(
        USER_WORKOUTS=user_workouts,
        PREFERENCES=preferences
    )

    chat_completion = CLIENT.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}]
    )

    return chat_completion.choices[0].message.content


@tool
def get_peloton_classes(fitness_discipline: str) -> str:
    """Get recent Peloton classes available on the platform.
    
    fitness_discipline representes the type of class. must be one of strength,
      cycling, stretching, yoga, or cardio.
    """
    response = st.session_state["pelo_interface"].get_recent_classes(fitness_discipline)

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
    """Call the Peloton API to get the recent workouts.

    Use this tool to get a summary of the user's recent Peloton history. 
    """
    # Check if the user has already loaded user workouts in this session. 
    # Since the workouts shouldn't change much load them from the sesion 
    # state if they are available.
    if "user_workouts" in st.session_state:
        return json.dumps(st.session_state["user_workouts"])

    # Otherwise use the PelotonAPI to get the recent workouts for the 
    # user. Cache the results and return the list of workouts.
    try:
        response = st.session_state["pelo_interface"].get_user_workouts(
            user_id=st.session_state["pelo_user_id"]
        )
    except Exception:
        return "There was a problem getting workouts from Peloton. Check \
            the logs for more information."

    st.session_state["user_workouts"] = response

    # Provide better formatting tags to the output.
    user_classes = []
    for k, classes in response.items():
        workouts = []
        for cl in classes:
            class_str = f"<class>{cl}</class"
            workouts.append(class_str)
        workout_str = "\n".join(workouts)
        day_classes = f"<day>Date: {k}\nClasses: {workout_str}</day>"
        user_classes.append(day_classes)

    user_class_str = "\n".join(user_classes)
    return f"These are the recent user workouts for the past week: {user_class_str}"
    # return f"These are the recent user workouts for the past week: {json.dumps(response)}"


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
    """Retrieves the user workout preferences from the file system.
    
    Used to allow the user to review the preferences they have set.
    """
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
