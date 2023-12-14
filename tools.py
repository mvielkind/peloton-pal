import json
import datetime
from collections import defaultdict
from langchain.agents import tool


@tool
def get_peloton_classes() -> str:
    """Get recent Peloton classes."""
    response = json.load(open("peloton_classes.json", "r'"))

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
                'id': w['id'],
                'description': w['description'],
                'difficulty': w['difficulty_estimate'],
                'duration': w['duration'],
                'instructor': instructors[w['instructor_id']],
                'title': w['title'],
                'disciplie': w['fitness_discipline_display_name']
            }
        )
    return json.dumps(recent_classes)


@tool
def get_recent_user_workouts() -> str:
    """Get the user's Peloton workouts from the past week."""
    response = json.load(open("user_workouts.json", "r"))

    today = datetime.datetime.today().date()
    recent_workouts = defaultdict(list)
    for w in response['data']:
        workout_date = datetime.datetime.fromtimestamp(w['created_at']).date()

        # Only get workouts from the last 7 days.
        if (today - workout_date).days > 14:
            break

        if 'ride' in w:
            title = w['ride']['title']
        elif 'peloton' in w:
            title = w['peloton']['ride']['title']
        else:
            title = "Unknown"
            
        lbl = f"{workout_date}: {title}"

        recent_workouts[str(workout_date)].append(lbl)

    return json.dumps(recent_workouts)