# -*- coding: utf-8 -*-
import speech_recognition as sr
import sqlite3
import subprocess
from datetime import datetime
import os

# Memory DB
conn = sqlite3.connect("memory.db")
cursor = conn.cursor()
cursor.execute("""CREATE TABLE IF NOT EXISTS chats (
                  id INTEGER PRIMARY KEY,
                  user TEXT,
                  ai TEXT,
                  ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP)""")
conn.commit()

# AI Brain (simple offline rules for now)
def ai_brain(user_input):
    cursor.execute("SELECT ai FROM chats WHERE user LIKE ?", ('%' + user_input + '%',))
    past = cursor.fetchall()
    if past:
        return f"You told me before: {past[0][0]}"
    return "I remember that now."

# Speak text using Termux TTS
def speak(text):
    subprocess.run(["termux-tts-speak", text])

# Listen from mic using Termux API
def listen():
    # Record 5 seconds of audio
    if os.path.exists("input.wav"):
        os.remove("input.wav")
    subprocess.run(["termux-microphone-record", "-l", "5", "input.wav"])

    # Recognize speech from the saved WAV file
    r = sr.Recognizer()
    with sr.AudioFile("input.wav") as source:
        audio = r.record(source)
    try:
        text = r.recognize_sphinx(audio)  # offline STT
        print("YOU:", text)
        return text
    except sr.UnknownValueError:
        return ""
    except Exception as e:
        print("Error:", e)
        return ""

# Main loop
while True:
    user_input = listen()
    if not user_input:
        continue
    ai_reply = ai_brain(user_input)
    print("AI:", ai_reply)
    cursor.execute("INSERT INTO chats (user, ai) VALUES (?, ?)", (user_input, ai_reply))
    conn.commit()
    speak(ai_reply)
