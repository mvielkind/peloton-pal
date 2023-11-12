from typing import List, Text
import json
import streamlit as st


def write_goal(
        goal_title: str,
        goal_description: str,
        goal_class_types: List[Text],
        action_type: str):
    """Writes a user goal to the goals.json file."""
    goals = json.load(open("goals.json"))

    goals[goal_title] = {
        "goal": goal_description,
        "class_types": goal_class_types
    }

    json.dump(goals, open("goals.json", "w"))

    if action_type == "add":
        st.toast("Goal added!", icon="✅")
    else:
        st.toast("Goal updated!", icon="✅")


st.title("Fitness Goal Management")

# Display goals in table.
goals = json.load(open("goals.json"))
goal = st.selectbox(
    label="Choose a goal",
    index=None,
    options=list(goals.keys()) + ["Add a new goal"]
)

if goal:
    st.subheader(goal)

    if goal == "Add a new goal":
        goal_title = st.text_input(
            label="Goal title",
            help="Name to be given to the goal."
        )
        goal_description = st.text_area(
            label="Goal description", 
            height=200,
            help="A description of your goal that will be used to help recommend classes. It's helpful to include the types of classes you like and dislike."
        )
        goal_class_types = st.multiselect(
            "Choose class types",
            options=["strength", "running", "cardio", "cycling", "yoga", "stretching"],
            help="Type of classes you like to take."
        )

        goal_added = st.button(
            "Add goal!",
            on_click=write_goal,
            args=(goal_title, goal_description, goal_class_types, "add")
        )
    else:
        goal_title = goal

        goal_detail = goals[goal]

        goal_description = st.text_area(
            label="Goal description", 
            value=goal_detail["goal"],
            height=200,
            help="A description of your goal that will be used to help recommend classes. It's helpful to include the types of classes you like and dislike."
        )
        
        goal_class_types = st.multiselect(
            "Choose class types",
            options=["strength", "running", "cardio", "cycling", "yoga", "stretching"],
            default=goal_detail["class_types"]
        )

        update_goal = st.button(
            "Update Goal",
            on_click=write_goal,
            args=(goal_title, goal_description, goal_class_types, "update")
        )
