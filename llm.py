import os
import re
import json
from typing import Dict, Text, Any, List, Optional
import openai
import streamlit as st
from dotenv import load_dotenv
load_dotenv()

import prompts


openai.api_key  = os.environ['OPENAI_API_KEY']


class ChatInterface:

    def __init__(self):
        
        self.messages = []
    
    def get_completion(self, messages=None):
        """Sends the user conversation to OpenAI for the response.
        """

        if messages is None:
            messages = self.messages

        response = openai.ChatCompletion.create(
            model="gpt-4-1106-preview",
            messages=messages,
            temperature=0.0, 
            max_tokens=500, 
        )
        return response.choices[0].message["content"]
    
    def classify_message(self, user_input: str) -> Dict[Text, Any]:
        """Classify the message as either being about choosing a workout or not.
        """
        prompt = prompts.MESSAGE_CLASSIFIER.format(user_input=user_input)
        messages = [
            {"role": "user", "content": prompt}
        ]
        response = self.get_completion(messages)

        try:
            response = parse_json_response(response)
        except json.decoder.JSONDecodeError as err:
            print(response)
            raise(err)

        return response

    def set_system_message(self, goal):
        system_message = {"role": "system", "content": prompts.SYSTEM_MSG.format(str_fitness_goal=goal)}

        if len(self.messages) == 0:
            self.messages.append(system_message)
        elif self.messages[0]["role"] == "system":
            self.messages[0] = system_message
        else:
            self.messages.insert(0, system_message)


def parse_json_response(content: Text) -> Dict[Text, Any]:
    """Parses the JSON response from OpenAI.
    """
    match = re.search(r"```(json)?(.*)```", content, re.DOTALL)

    if match is None:
        return json.loads(content)
    else:
        json_str = match.group(2).strip()
        return json.loads(json_str)


def convert_candidate_classes_to_string(candidate_classes: Dict[Text, Any]):
    """Converts the Peloton class object to a string for the prompt.
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
    
    return json.dumps(candidate_class_list)

