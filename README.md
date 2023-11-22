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

Within the Streamlit app you can define your fitness goals along with the types of workouts you prefer doing (i.e. strength, cycling, running etc.) You can define multiple goals to switch between if you'd like.

Once you have a goal established from the `Home` screen you can select the goal and how long you'd like to workout. The app will load your recent workout history from the Peloton API and generate a workout based on your goal and the time you have available.

Sometimes you may not be feeling a certain kind of workout on a given day. Using the chat interface you can refine the workout to your liking.

If you click the `Build Stack` button the classes in your workout will be added to your stack in the Peloton app.

## A Couple Notes

Anecdotally the model does recommend classes to seem appropriate to my goal and the reasoning is sound. Personally, what I enjoy most is the ability to offload a decision about what to do for a workout. The model keeps workouts varied and I'm on track to meet my goals.

Right now the chat is only geared to selecting a workout. I'm planning to add some more routes in the chat to interact with the API more and keep the conversation more on topic.
