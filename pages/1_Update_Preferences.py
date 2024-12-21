import json
from pathlib import Path
import streamlit as st
import interface
from schemas import UserWorkoutPreferences

st.title("Update your Peloton Preferences")


# Initialize session variables for the preferences by loading any
# existing preferences or assigning defaults.
if "user_preferences" not in st.session_state:
    # Try loading the JSON.
    try:
        root_dir = Path(__file__).parent.parent
        preferences = UserWorkoutPreferences(**json.load(open(root_dir / "preferences.json", "r")))
    except FileNotFoundError:
        # if there are no existing preferences then load defaults.
        preferences = UserWorkoutPreferences()
    
    st.session_state["user_preferences"] = preferences

# Descriptions of common class types on Peloton.
class_types = [
    "Barre",
    "Bike Bootcamp",
    "Cardio",
    "Cycling",
    "HIIT Bootcamp",
    "Meditation",
    "Pilates",
    "Rowing",
    "Running",
    "Strength",
    "Stretching",
    "Tread",
    "Tread Bootcamp",
    "Walking",
    "Yoga",
]


duration = st.number_input(
    label="Preferred Workout Duration (minutes)",
    min_value=0,
    max_value=120,
    value=st.session_state["user_preferences"].preferred_duration_minutes,
    step=5,
    help="Your preferred workout duration in minutes."
)


favorite_disciplines = st.multiselect(
    label="Types of classes you like",
    options=class_types,
    default=st.session_state["user_preferences"].fitness_goals,
    help="Types of classes you enjoy on Peloton!"
)

disliked_disciplines = st.multiselect(
    label="Class types to exclude from your recommendation",
    options=class_types,
    default=st.session_state["user_preferences"].excluded_classes,
    help="Some classes aren't your thing and that's okay! Your recommendations will ignore these types of classes.",
)

# get the list of instructors to include in the choices.
instructor_map = interface.get_instructor_list(st.session_state["pelo_interface"])
favorite_instructors = st.multiselect(
    label="Who are your favorite instructors?",
    options=instructor_map.values(),
    default=st.session_state["user_preferences"].favorite_instructors,
    help="Add your favorite instructors to help guide your recommendations."
)

save_btn = st.button(
    label="Save Preferences"
)

if save_btn:
    new_preferences = UserWorkoutPreferences(
        fitness_goals=favorite_disciplines,
        preferred_duration_minutes=duration,
        favorite_instructors=favorite_instructors,
        excluded_classes=disliked_disciplines
    )

    with open("preferences.json", "w") as f:
        json.dump(new_preferences.model_dump(), f)

    st.session_state["user_preferences"] = new_preferences
