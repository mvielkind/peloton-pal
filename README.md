# Pelo-Buddy: Your Peloton AI Personal Trainer

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

Now the app is running and you can get started planning your workouts!

The Langchain agent is capable of a number of different tasks. To get started the sidebar offers some options for quick actions including:

- View recent Peloton classes
- Get a workout suggestion
- View classes in your stack
- Manage your workout preferences

You can tell the bot what your workout preferences are to get more personalized recommendations. When you include your preferences they will be saved in a `goals.txt` file.
