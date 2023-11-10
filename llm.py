import os
import re
import json
from typing import Dict, Text, Any
import openai
import streamlit as st
from dotenv import load_dotenv
load_dotenv()

import prompts


openai.api_key  = os.environ['OPENAI_API_KEY']


def parse_json_response(content: Text) -> Dict[Text, Any]:
    """Parses the JSON response from OpenAI.
    """
    match = re.search(r"```(json)?(.*)```", content, re.DOTALL)

    if match is None:
        return json.loads(content)
    else:
        json_str = match.group(2).strip()
        return json.loads(json_str)


def get_completion_from_messages(messages, 
                                 model="gpt-4-1106-preview", 
                                 temperature=0, 
                                 max_tokens=500):
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=temperature, 
        max_tokens=max_tokens, 
    )
    return response.choices[0].message["content"]


@st.cache_data()
def suggest_class_type(recent_workouts: str, goal_prompt: str, str_goal_categories: str):
    """Suggest the class type given the workout history.
    """
    messages = [
        {"role": "system", "content": prompts.SYSTEM_MSG.format(str_fitness_goal=goal_prompt)},
        {"role": "user", "content": prompts.CLASS_TYPE_PROMPT.format(str_recent_workouts=recent_workouts, str_candidate_categories=str_goal_categories)}
    ]

    class_type_response = get_completion_from_messages(messages)

    # Parse response to get the JSON output.
    # if isinstance(class_type_response, str):
    #     json_obj = json.loads(class_type_response.split("###")[1])
    #     return json_obj
    
    try:
        class_type_response = parse_json_response(class_type_response)
    except json.decoder.JSONDecodeError as err:
        print(class_type_response)
        raise(err)
    
    if isinstance(class_type_response, str):
        json_obj = json.loads(class_type_response.split("###")[1])
        return json_obj
    
    return class_type_response


@st.cache_data()
def suggest_workout(recent_workouts: str, candidate_classes: Dict[Text, Any], n_minutes: int, goal_prompt: str):
    """Determine the best workout.
    """
    # Convert candidate classes into a string.
    candidate_class_list = []
    for id, details in candidate_classes.items():
        if 'ride' in details:
            title = details['ride']['title']
        elif 'peloton' in details:
            title = details['peloton']['ride']['title']
        elif 'title' in details:
            title = details['title']
        else:
            title = "Unknown"
        
        minutes = details['duration'] / 60

        _class = {
            'id': id,
            'title': title,
            'duration': minutes,
            'difficulty': details['difficulty_estimate']
        }
        candidate_class_list.append(_class)

    messages = [
        {"role": "system", "content": prompts.SYSTEM_MSG.format(str_fitness_goal=goal_prompt)},
        {"role": "user", "content": prompts.CLASS_SUGGEST_PROMPT.format(
            str_recent_workouts=recent_workouts, 
            str_recent_classes=json.dumps(candidate_class_list),
            n_minutes=n_minutes)}
    ]

    suggested_workout = get_completion_from_messages(messages)

    if "'''" in suggested_workout:
        workout = json.loads(suggested_workout.split("'''")[1])
        return workout, None

    try:
        workout = parse_json_response(suggested_workout)
        return workout, None
    except json.decoder.JSONDecodeError as err:
        print(suggested_workout)
        return suggested_workout, err
