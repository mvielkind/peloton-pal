from typing import Any, Dict, Text, Optional
import os
import requests
import json
import logging
from dotenv import load_dotenv
load_dotenv()



PELOTON_API_ROOT = "https://api.onepeloton.com"
PELOTON_GRAPHQL_ROOT = "https://gql-graphql-gateway.prod.k8s.onepeloton.com/graphql"


class PelotonAPI:
    """Interface for making calls to the Peloton API.

    A common interface for interacting with the Peloton API. The class sets up 
    a requests Session that once authenticated will be the source of all API 
    calls to Peloton.
    """

    def __init__(self):

        self.sess = requests.Session()

    def authenticate(self) -> requests.Response:
        """Authenticates the user with the Peloton API and creates a new session.

        The user_id in the response is needed to make other API calls.
        """
        payload = {
            "username_or_email": os.environ["PELOTON_USER"],
            "password": os.environ["PELOTON_PASS"]
        }

        response = self.sess.post(
            f"{PELOTON_API_ROOT}/auth/login",
            data=json.dumps(payload)
        )

        return response

    def get_recent_classes(self, fitness_discipline: Optional[str] = None) -> Dict[Text, Any]:
        """Get recent Peloton classes.
        
        Gets a list of the recent Peloton classes offered on the platform. 
        When providing class suggestions the agent will reference the 
        returned classes as the candidates to choose from.
        
        Args:
            fitness_discipline: An optional value to filter the class results 
                to be for a single discipline (i.e. running, cycling, strength 
                etc.)
        
        Returns:
            A JSON object with the class information. The `data` key of the 
            response has a list of the returned class objects.
        """
        params = {
            "limit": 50,
            "sort_by": "original_air_time",
            "desc": True
        }

        if fitness_discipline:
            params['browse_category'] = fitness_discipline

        response = self.sess.get(f"{PELOTON_API_ROOT}/api/v2/ride/archived",
                                 params=params)

        return response.json()

    def get_instructor_list(
            self,
            page_id: int = 0
        ) -> dict:
        """Gets a list of Peloton instructors.
        
        Returns a dictionary with the instructor ID as the key and the name
        for a value.
        """
        instructor_map = {}

        # Results are paginated so loop until all instructors are returned.
        while True:
            params = {
                "page": page_id
            }

            try:
                response = self.sess.get(
                    f"{PELOTON_API_ROOT}/api/instructor",
                    params=params
                )
                response.raise_for_status()
            except Exception as http_err:
                logging.error(
                    f'Error occurred getting Peloton instructors. {http_err}'
                )
                return None

            pelo_response = response.json()

            # Populate the instructors.
            for instructor in pelo_response["data"]:
                id = instructor["id"]
                name = instructor["name"]
                instructor_map[id] = name

            # Check if a new request should be made.
            if pelo_response["show_next"]:
                page_id += 1
            else:
                break

        return instructor_map
        
    def get_user_workouts(
            self, 
            user_id: str, 
            page: int = 0
        ) -> Dict[Text, Any]:
        """Get the latest workouts for the user for the past 7 days.
        
        Uses pagination to make calls to the Peloton user workouts endpoint to 
        retrieve the user workouts for the previous 7 days.

        Different types of workouts have varying schemas for the response. 
        For each workout the title, discipline and difficulty rating are 
        extracted so they can be used to describe the recent classes for the 
        agent.

        Args:
            user_id: The Peloton user ID to build the query string.
            page: the page number for the results to retrieve.
        
        Returns:
            A dictionary where the keys are a date with a list of workout 
            objects that were done on that day.
        """
        show_more = True
        while show_more:
            params = {
                "page": page,
                "limit": 50,
                "joins": "peloton.ride",
                "sort_by": "-created"
            }

            try:
                response = self.sess.get(
                    f"{PELOTON_API_ROOT}/api/user/{user_id}/workouts",
                    params=params
                )
                response.raise_for_status()
            except Exception as http_err:
                logging.error(
                    f'Error occurred getting Peloton workouts. {http_err}'
                )
                return None

            pelo_response = response.json()

            return pelo_response

    def convert_ride_to_class_id(self, ride_id: str) -> str:
        """Get details about a specific class.
        """
        response = self.sess.get(f"{PELOTON_API_ROOT}/api/ride/{ride_id}/details")

        ride_detail = response.json()

        return ride_detail['ride']['join_tokens']['on_demand']

    def favorite(self, id) -> requests.Response:
        """Favorites a class in the Peloton account for the user."""
        payload = {
            "ride_id": id
        }
        response = self.sess.post(f"{PELOTON_API_ROOT}/api/favorites/create",
                                  data=json.dumps(payload))

        return response

    def categories(self) -> Dict[Text, Any]:
        """Gets a list of Peloton fitness disciplines."""
        response = self.sess.get(f"{PELOTON_API_ROOT}/api/browse_categories?library_type=on_demand")
        return response.json()

    def get_stack(self) -> str:
        """Gets the classes currently in the user's stack.
        
        Args:
            None
        
        Returns:
            A string of classes that the user currently has in their Stack.
            Each class is separated by a newline character.
        
        """
        query = {
            "query": "query ViewUserStack {\n  viewUserStack {\n    numClasses\n    totalTime\n    ... on StackResponseSuccess {\n      numClasses\n      totalTime\n      userStack {\n        stackedClassList {\n          playOrder\n          pelotonClass {\n            joinToken\n            title\n            classId\n            fitnessDiscipline {\n              slug\n              __typename\n            }\n            assets {\n              thumbnailImage {\n                location\n                __typename\n              }\n              __typename\n            }\n            duration\n            ... on OnDemandInstructorClass {\n              joinToken\n              title\n              fitnessDiscipline {\n                slug\n                displayName\n                __typename\n              }\n              contentFormat\n              totalUserWorkouts\n              originLocale {\n                language\n                __typename\n              }\n              captions {\n                locales\n                __typename\n              }\n              timeline {\n                startOffset\n                __typename\n              }\n              difficultyLevel {\n                slug\n                displayName\n                __typename\n              }\n              airTime\n              instructor {\n                name\n                __typename\n              }\n              __typename\n            }\n            classTypes {\n              name\n              __typename\n            }\n            playableOnPlatform\n            contentAvailability\n            isLimitedRide\n            freeForLimitedTime\n            __typename\n          }\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n}\n",
            "operationName":"ViewUserStack",
            "variables":{}
        }

        headers = {
            'peloton-platform': 'web'
        }

        response = self.sess.post(PELOTON_GRAPHQL_ROOT, json=query, headers=headers).json()

        if response['data']['viewUserStack']['__typename'] != 'StackResponseSuccess':
            return None

        classes_in_stack = []
        for cl in response['data']['viewUserStack']['userStack']['stackedClassList']:
            classes_in_stack.append(cl["pelotonClass"]['title'])

        return "\n".join(classes_in_stack)

    def clear_stack(self) -> bool:
        """Clears all the classes in a user's Peloton stack.
        
        Args:
            None
        
        Returns:
            True if classes were successfully deleted or False if there is an 
            issue clearing the classes.
        """
        query = {
            "query": "mutation ModifyStack($input: ModifyStackInput!) {\n  modifyStack(input: $input) {\n    numClasses\n    totalTime\n    userStack {\n      stackedClassList {\n        playOrder\n        pelotonClass {\n          ...ClassDetails\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n}\n\nfragment ClassDetails on PelotonClass {\n  joinToken\n  title\n  classId\n  fitnessDiscipline {\n    slug\n    __typename\n  }\n  assets {\n    thumbnailImage {\n      location\n      __typename\n    }\n    __typename\n  }\n  duration\n  ... on OnDemandInstructorClass {\n    title\n    fitnessDiscipline {\n      slug\n      displayName\n      __typename\n    }\n    contentFormat\n    difficultyLevel {\n      slug\n      displayName\n      __typename\n    }\n    airTime\n    instructor {\n      name\n      __typename\n    }\n    __typename\n  }\n  classTypes {\n    name\n    __typename\n  }\n  playableOnPlatform\n  contentAvailability\n  isLimitedRide\n  freeForLimitedTime\n  __typename\n}\n",
            "operationName": "ModifyStack",
            "variables": {
                "input": {
                    "pelotonClassIdList": []
                }
            }
        }

        headers = {
            'peloton-platform': 'web'
        }

        response = self.sess.post(PELOTON_GRAPHQL_ROOT, json=query, headers=headers).json()

        try:
            if response['data']['modifyStack']['__typename'] != 'StackResponseSuccess':
                return False
        except KeyError:
            logging.info(f"There was an issue with the clear_stack request: {response}")
            return False

        return True

    def stack_class(self, class_id: str) -> bool:
        """Adds the specified class_id to the user's Peloton stack.
        
        Args:
            class_id: The ID of the class to add to the stack.
        
        Returns:
            True if adding the class was successful. Otherwise returns False.
        """
        query = {
            "query": "mutation AddClassToStack($input: AddClassToStackInput!) {\n  addClassToStack(input: $input) {\n    numClasses\n    totalTime\n    userStack {\n      stackedClassList {\n        playOrder\n        pelotonClass {\n          ...ClassDetails\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n}\n\nfragment ClassDetails on PelotonClass {\n  joinToken\n  title\n  classId\n  fitnessDiscipline {\n    slug\n    __typename\n  }\n  assets {\n    thumbnailImage {\n      location\n      __typename\n    }\n    __typename\n  }\n  duration\n  ... on OnDemandInstructorClass {\n    title\n    fitnessDiscipline {\n      slug\n      displayName\n      __typename\n    }\n    contentFormat\n    difficultyLevel {\n      slug\n      displayName\n      __typename\n    }\n    airTime\n    instructor {\n      name\n      __typename\n    }\n    __typename\n  }\n  classTypes {\n    name\n    __typename\n  }\n  playableOnPlatform\n  contentAvailability\n  isLimitedRide\n  freeForLimitedTime\n  __typename\n}\n",
            "operationName": "AddClassToStack",
            "variables": {
                "input": {
                    "pelotonClassId": f"{class_id}"
                }
            }
        }

        headers = {
            'peloton-platform': 'web'
        }

        response = self.sess.post(PELOTON_GRAPHQL_ROOT, json=query, headers=headers).json()

        # Check if the class was successfully added to the stack.
        if response['data']['addClassToStack']['__typename'] != 'StackResponseSuccess':
            return False

        return True
