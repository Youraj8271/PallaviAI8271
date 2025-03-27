
import openai
import os
import pyttsx3
import speech_recognition as sr
import json
import requests
import time
from threading import Thread

# Initialize OpenAI GPT-4
openai.api_key = 'YOUR_OPENAI_API_KEY'

# Initialize Text-to-Speech
engine = pyttsx3.init()
engine.setProperty('rate', 150)

# Self-Learning Database (JSON File)
LEARNING_FILE = 'learning_data.json'


def save_learning(data):
    with open(LEARNING_FILE, 'w') as file:
        json.dump(data, file)


def load_learning():
    if os.path.exists(LEARNING_FILE):
        with open(LEARNING_FILE, 'r') as file:
            return json.load(file)
    return {}


learning_data = load_learning()


def speak(text):
    engine.say(text)
    engine.runAndWait()


def listen():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        audio = recognizer.listen(source)
    try:
        return recognizer.recognize_google(audio, language='hi')
    except Exception as e:
        print("Could not understand audio.")
        return None


def get_ai_response(prompt):
    try:
        if prompt in learning_data:  # Check if prompt is already learned
            return learning_data[prompt]

        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an advanced AI assistant named Pallavi."},
                {"role": "user", "content": prompt}
            ]
        )
        result = response.choices[0].message['content']

        learning_data[prompt] = result  # Save learned response
        save_learning(learning_data)
        return result
    except Exception as e:
        return f"Error: {str(e)}"


def auto_upgrade(new_code):
    try:
        with open(__file__, 'w') as file:
            file.write(new_code)
        speak("I have successfully upgraded myself.")
    except Exception as e:
        speak(f"Upgrade failed: {str(e)}")


def extract_info_from_internet(query):
    try:
        response = requests.get(f'https://api.duckduckgo.com/?q={query}&format=json')
        data = response.json()
        if data.get('AbstractText'):
            return data['AbstractText']
        else:
            return get_ai_response(f"Provide detailed information about {query}")  # Using GPT-4 if no direct data found
    except Exception as e:
        return f"Internet Error: {str(e)}"


def continuous_listen():
    while True:
        user_input = listen()
        if user_input:
            print(f"You said: {user_input}")

            if "exit" in user_input.lower() or "stop" in user_input.lower():
                speak("Goodbye!")
                save_learning(learning_data)
                break

            if "search" in user_input.lower():
                query = user_input.replace('search', '').strip()
                info = extract_info_from_internet(query)
                speak(info)

            if "solve exam" in user_input.lower():
                speak("Please tell me the questions one by one.")
                while True:
                    question = listen()
                    if question.lower() in ["exit", "stop"]:
                        break
                    response = get_ai_response(question)
                    print(f"Pallavi: {response}")
                    speak(response)

            response = get_ai_response(user_input)
            print(f"Pallavi: {response}")
            speak(response)


def main():
    print("Pallavi AI Activated!")
    speak("Hello! I am Pallavi. How can I assist you today?")

    listener_thread = Thread(target=continuous_listen)
    listener_thread.start()
    listener_thread.join()


if __name__ == "__main__":
    main()
