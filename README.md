# Pelton GPT Personal Trainer

A simple Streamlit app that connects to your Peloton account and suggests the next workout to meet your fitness goals. The purpose of this app is to help explore how AI can be used to personalize recommendations.

The app allows a user to define a fitness goal in the `goals.json` file. Each goal has a user defined free text fitness goal along with the fitness disciplines they would want utilize from the app. The goal definition should look like this:

```json
{
    "goal_name": {
        "goal": "Description of your fitness goal",
        "class_types": ["cycling", "yoga", "strength"]
    }
}
```

You can define multiple goals. The name of each goal will be loaded into the `selectbox` of the Streamlit app.

## Configure Credentials

To run the app you must provide an OpenAI API key and your Peloton credentials in the `.env` file. The `.env` file should look like this:

```bash
OPENAI_API_KEY='your_openai_api_key'
PELOTON_USER='your_peloton_username'
PELOTON_PASS='your_peloton_password'
```

## Generating the Workout

Inside `prompts.py` are a set of prompts that are used for generating the workout. 

- `SYSTEM_MSG` instructs the model about its overall objective and includes the user's fitness goal.
- `CLASS_TYPE_PROMPT` is used to generate the class type (e.g. cycling, yoga, strength) for the user given the recent workouts the user has done and the user's goal.
- `CLASS_SUGGEST_PROMPT` selects and returns the specific classes that should be included in the workout.

The app uses a chain-of-thought reasoning approach to generate the workout. First, the model determines what type of workout the user should do (i.e. strength, cycling, running etc.) based on the recent workout history and goals. Available classes for the selected workout type are retrieved from the Peloton API and then the model selects the best classes for the user to achieve their goals within the specified timeframe.

Splitting the tasks up simplifies calls to the Peloton API and helps the model provide a more thoughtful workout instead of having to select from a variety of workouts from different disciplines. It also reduces the size of the context window since only classes from a single discipline are included in the prompt.

## A Couple Notes

Anecdotally the model does recommend classes to seem appropriate to my goal and the reasoning is sound. Personally, what I enjoy most is the ability to offload a decision about what to do for a workout. The model keeps workouts varied and I'm on track to meet my goals. Evaluating the model is tough since it's a subjective task. Add your own goals and let me know what you think!
