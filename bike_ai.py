# -*- coding: utf-8 -*-
import speech_recognition as sr
import sqlite3
import subprocess
import os
from datetime import datetime

# === Create / Connect to Local Memory ===
db_path = os.path.join(os.path.dirname(__file__), "memory.db")
conn = sqlite3.connect(db_path)
cursor = conn.cursor()
cursor.execute("""CREATE TABLE IF NOT EXISTS chats (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user TEXT,
    ai TEXT,
    ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)""")
conn.commit()

# === Brain Logic (Simple Memory Recall) ===
def ai_brain(user_input):
    cursor.execute("SELECT ai FROM chats WHERE user LIKE ?", ('%' + user_input + '%',))
    past = cursor.fetchone()
    if past:
        return f"You told me before: {past[0]}"
    return "I remember that now."

# === Text to Speech ===
def speak(text):
    with open("output.txt", "w") as f:
        f.write(text)
    subprocess.run(["termux-tts-speak", text])

# === Voice to Text ===
def listen():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("🎤 Speak now...")
        audio = r.listen(source)
    try:
        text = r.recognize_sphinx(audio)  # offline
        print("YOU:", text)
        return text
    except sr.UnknownValueError:
        print("Could not understand audio.")
        return ""
    except Exception as e:
        print("Error:", str(e))
        return ""

# === Main Loop ===
def main():
    print("🤖 Bike AI Assistant is running (offline mode)")
    while True:
        user_input = listen()
        if not user_input:
            continue
        ai_reply = ai_brain(user_input)
        print("AI:", ai_reply)
        cursor.execute("INSERT INTO chats (user, ai) VALUES (?, ?)", (user_input, ai_reply))
        conn.commit()
        speak(ai_reply)

if __name__ == "__main__":
    main()
