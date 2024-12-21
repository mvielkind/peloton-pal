import json
import datetime
import streamlit as st
from openai import OpenAI
from pydantic_ai import Agent
from schemas import (
    RecentUserClasses,
    PelotonClass,
    UserWorkoutPreferences,
    RecentUserSummary
)
from prompts import AGENT_SYSTEM_MSG, RECENT_WORKOUT_SUMMARY
import interface


peloton_agent = Agent(
    'openai:gpt-4o-mini',
    system_prompt=AGENT_SYSTEM_MSG
)


client = OpenAI()


@peloton_agent.tool_plain
async def user_workout_preferences() -> UserWorkoutPreferences:
    """Get the user workout preferences.
    """
    return st.session_state["user_preferences"]


@peloton_agent.tool_plain
async def recent_user_workouts(user_preferences: UserWorkoutPreferences) -> list[RecentUserClasses]:
    """Gets the recent Peloton classes the user has taken.

    Recent user workouts can be used to determine the trend of user classes. Do not add classes to a workout from this list.
    """
    response = interface.get_user_workouts(
        st.session_state["pelo_interface"], 
        st.session_state["pelo_user_id"]
    )

    # Get the instructor map to.
    instructor_map = interface.get_instructor_list(st.session_state["pelo_interface"])

    # Get important attributes from the classes.
    recent_classes = []
    test = []
    for cl in response["data"][:30]:
        if cl["peloton"]:
            description = cl["peloton"]["ride"]["description"]
            title = cl["peloton"]["ride"]["title"]
            class_id = cl["peloton"]["ride"]["id"]
            try:
                instructor = instructor_map[cl["peloton"]["ride"]["instructor_id"]]
            except KeyError:
                instructor = ""
        else:
            description = cl["ride"]["title"]
            title = cl["ride"]["title"]
            instructor = cl["ride"]["instructor"]["name"]
            class_id = cl["ride"]["id"]

        user_class = RecentUserClasses(
            id=class_id,
            fitness_discipline=cl["fitness_discipline"],
            name=cl["name"],
            class_date=datetime.datetime.fromtimestamp(cl["start_time"]).strftime("%Y-%m-%d"),
            description=description,
            title=title,
            instructor=instructor
        )

        # Convert to a string to include in the next query.
        class_str = f"<class>{json.dumps(user_class.model_dump_json())}</class>"

        recent_classes.append(user_class)
        test.append(class_str)


    pr = RECENT_WORKOUT_SUMMARY.format(
        RECENT_USER_CLASSES=json.dumps(test),
        USER_PREFERENCES=f"Fitness goals: {user_preferences.fitness_goals}"
    )

    chat_completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "user",
                "content": pr
            }
        ]
    )

    summary = RecentUserSummary(
        recent_class_ids=[cl.id for cl in recent_classes],
        summary=chat_completion.choices[0].message.content
    )

    return summary


@peloton_agent.tool_plain
async def get_available_classes(recent_classes: RecentUserSummary) -> list[PelotonClass]:
    """Gets the list of available Peloton classes to choose from.

    Args:
        recent_classes: list of recent classes taken by the user that will be excluded from the available classes.

    Classes for a workout should be selected from this list of available classes.
    """
    # all_class_data = json.load(open("available_classes.json", "r"))
    all_class_data = interface.get_available_classes(st.session_state["pelo_interface"])

    # Create a lookup for the instructors.
    instructors = {i['id']: i['name'] for i in all_class_data['instructors']}

    # List of IDs to remove.
    # exclude_recent_classes = [cl for cl in recent_classes.recent_class_ids]

    available_classes = []
    for cl in all_class_data["data"][:50]:
        if cl["id"] in recent_classes.recent_class_ids:
            continue

        pelo_class = PelotonClass(
            id=cl["id"],
            title=cl["title"],
            description=cl["description"],
            duration=cl["duration"]/60,
            difficulty=cl["difficulty_rating_avg"],
            fitness_discipline=cl["fitness_discipline"],
            instructor=instructors[cl['instructor_id']]
        )
        available_classes.append(pelo_class)
    
    return available_classes


@peloton_agent.tool_plain
async def add_class_to_stack(class_ids: list[str]) -> bool:
    """Adds classes to the user's stack.

    This is after the user gets recommended classes by using the 
    ID of the class.

    Args:
        class_ids: the class IDs of the recommended classes.
    """
    for class_id in class_ids:
        join_token = st.session_state["pelo_interface"].convert_ride_to_class_id(class_id)

        success = st.session_state["pelo_interface"].stack_class(join_token)

    return success
