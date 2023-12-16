# Pelton GPT Personal Trainer

A simple Streamlit app that connects to your Peloton account and suggests the next workout to meet your fitness goals.

## Getting Started

To run the app you must provide an OpenAI API key and your Peloton credentials in the `.env` file. The `.env` file should look like this:

```bash
OPENAI_API_KEY='your_openai_api_key'
PELOTON_USER='your_peloton_username'
PELOTON_PASS='your_peloton_password'
```

Then in the terminal you can run the Streamlit app with:

```bash
streamlit run Home.py
```

## Generating a Workout

In the `Manage Goals` screen you can define your fitness goals and preferences for your workouts. These preferences should include the types of classes you enjoy doing and the ones you dislike. You can also set a preferred workout length to default to. Being more specific in this section will result in a better experience.

After you define your preferences you can select them from the left panel of the `Home` screen. These preferences will be used to shape the conversation with the bot to help create the workout.

## Agent Abilities

Right now the agent can help you:

- View recent classes you've taken.
- See the recent Peloton classes.
- Add the workout to your stack in the Peloton app.

I may add more in the future, but for now it's a start.
