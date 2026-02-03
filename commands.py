import webbrowser
import datetime
import os
import pywhatkit
from sentence_transformers import SentenceTransformer, util

# === Import your custom handlers ===
from diagnostics import get_cpu_usage, get_ram_usage, get_battery_status, get_disk_usage
from powershell_cmds import empty_recycle_bin, open_settings
from app_control import open_app, close_app, list_processes
from memory import remember, recall, forget

import sys
from PyQt5.QtWidgets import QApplication

# === Chat AI model for fallback ===
model = SentenceTransformer("paraphrase-MiniLM-L6-v2")

# === Shutdown handler ===
def shutdown_sam(speak):
    speak("Shutting down. Goodbye.")
    QApplication.quit()
    sys.exit(0)

# === INTENTS ===
INTENTS = {
    "open youtube": lambda speak, cmd: (speak("Opening YouTube."), webbrowser.open("https://youtube.com")),
    "open google": lambda speak, cmd: (speak("Opening Google."), webbrowser.open("https://google.com")),
    "what is the time": lambda speak, cmd: speak("The time is " + datetime.datetime.now().strftime("%I:%M %p")),
    "play music": lambda speak, cmd: (speak("Playing trending music on YouTube."), pywhatkit.playonyt("top trending music")),
    "open notepad": lambda speak, cmd: (speak("Opening Notepad."), os.system("notepad")),
    "search google": lambda speak, cmd: handle_google_search(cmd, speak),

    # System Status
    "check cpu usage": lambda speak, cmd: speak(get_cpu_usage()),
    "check ram usage": lambda speak, cmd: speak(get_ram_usage()),
    "battery status": lambda speak, cmd: speak(get_battery_status()),
    "disk usage": lambda speak, cmd: speak(get_disk_usage()),

    # System Tools
    "empty recycle bin": lambda speak, cmd: speak(empty_recycle_bin()),
    "open windows settings": lambda speak, cmd: speak(open_settings()),

    # App Control
    "open app": lambda speak, cmd: speak(open_app(cmd)),
    "close app": lambda speak, cmd: speak(close_app(cmd)),
    "list running tasks": lambda speak, cmd: speak(list_processes()),

    # Shutdown
    "shutdown": lambda speak, cmd: shutdown_sam(speak),
    "bye": lambda speak, cmd: shutdown_sam(speak),
    "turn off": lambda speak, cmd: shutdown_sam(speak),

    # Memory
    "remember something": lambda speak, cmd: handle_remember(cmd, speak),
    "recall something": lambda speak, cmd: handle_recall(cmd, speak),
    "forget something": lambda speak, cmd: handle_forget(cmd, speak),
}

# === Keyword patterns for intent detection ===
INTENT_PATTERNS = {
    "open youtube": ["youtube"],
    "open google": ["open google", "search google homepage"],
    "what is the time": ["what is the time", "tell me the time", "current time"],
    "play music": ["play music", "play song", "youtube music"],
    "open notepad": ["open notepad"],
    "search google": ["search for", "google this", "look up"],

    "check cpu usage": ["cpu usage", "processor usage"],
    "check ram usage": ["ram usage", "memory usage"],
    "battery status": ["battery status", "battery level"],
    "disk usage": ["disk usage", "storage left"],

    "open app": ["open"],
    "close app": ["close"],
    "list running tasks": ["running tasks", "tasklist", "running programs"],

    "empty recycle bin": ["empty recycle bin", "clear trash"],
    "open windows settings": ["windows settings", "open settings"],

    "shutdown": ["shutdown sam", "turn off", "shut down"],
    "bye": ["bye", "see you", "goodbye"],
    "turn off": ["turn off sam"],

    "remember something": ["remember", "my name is", "store this"],
    "recall something": ["what is my", "do you remember"],
    "forget something": ["forget", "remove memory"]
}

# === Google Search ===
def handle_google_search(command, speak):
    query = command.lower().split("search", 1)[-1].strip()
    if query:
        speak(f"Searching Google for {query}.")
        pywhatkit.search(query)
    else:
        speak("Please specify what you want to search.")

# === Main Command Dispatcher ===
def execute_command(command, speak):
    command = command.lower()
    best_match = get_best_intent_match(command)

    if best_match:
        print(f"Matched intent: {best_match}")
        INTENTS[best_match](speak, command)
    else:
        from chat_ai import generate_reply
        response = generate_reply(command)
        print("ChatAI response:", response)
        speak(response)

# === Intent Matcher ===
def get_best_intent_match(user_input):
    user_input = user_input.lower()

    # 1. Keyword match (fast and rule-based)
    for intent, triggers in INTENT_PATTERNS.items():
        for trigger in triggers:
            if trigger in user_input:
                return intent

    # 2. Fallback to semantic matching
    sentences = list(INTENTS.keys())
    embeddings = model.encode(sentences + [user_input], convert_to_tensor=True)
    cosine_scores = util.pytorch_cos_sim(embeddings[-1], embeddings[:-1])[0]
    best_score = float(cosine_scores.max())
    best_index = int(cosine_scores.argmax())

    if best_score >= 0.6:
        return sentences[best_index]
    return None

# === Memory Handlers ===
def handle_remember(cmd, speak):
    if "my name is" in cmd:
        name = cmd.split("my name is")[-1].strip()
        remember("name", name)
        speak(f"Got it. I will remember your name is {name}.")
    elif "remember" in cmd:
        parts = cmd.split("remember")[-1].strip().split(" is ")
        if len(parts) == 2:
            key, value = parts
            remember(key.strip(), value.strip())
            speak(f"Okay, I’ll remember {key.strip()} is {value.strip()}.")
        else:
            speak("What should I remember?")
    else:
        speak("Sorry, I didn’t understand what to remember.")

def handle_recall(cmd, speak):
    for keyword in ["name", "favorite", "birthday"]:
        if keyword in cmd:
            value = recall(keyword)
            if value:
                speak(f"Your {keyword} is {value}.")
            else:
                speak(f"I don't know your {keyword} yet.")
            return
    speak("I’m not sure what you want me to recall.")

def handle_forget(cmd, speak):
    for keyword in ["name", "favorite", "birthday"]:
        if keyword in cmd:
            success = forget(keyword)
            if success:
                speak(f"Okay, I’ve forgotten your {keyword}.")
            else:
                speak(f"I didn’t have your {keyword} stored.")
            return
    speak("Tell me what to forget.")
