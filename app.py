import tkinter as tk
from tkinter import scrolledtext
import requests
import json
import os
import uuid

# === CONFIG ===
API_KEY = 'YOUR-GROQ-API-KEY'
API_URL = 'https://api.groq.com/openai/v1/chat/completions'
MODEL_NAME = 'llama3-70b-8192'
CHAT_DIR = "chats"

# === HEADERS & SYSTEM PROMPT ===  a smart, coding-focused assistant. Be helpful, clear, and efficient. and explain everything and what it does.
HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

SYSTEM_PROMPT = {
    "role": "system",
    "content": "a smart, coding-focused assistant. Be helpful, clear, and efficient."
}

# === INITIAL SETUP ===
if not os.path.exists(CHAT_DIR):
    os.makedirs(CHAT_DIR)

chat_history = []
chat_file = None

# === FUNCTIONS ===

def create_new_chat():
    chat_id = str(uuid.uuid4())[:8]
    filename = f"{CHAT_DIR}/chat_{chat_id}.json"
    with open(filename, "w") as f:
        json.dump([SYSTEM_PROMPT], f, indent=4)
    return filename

def load_chat(filename):
    path = os.path.join(CHAT_DIR, filename)
    with open(path, "r") as f:
        return json.load(f), path

def save_chat():
    if chat_file:
        with open(chat_file, "w") as f:
            json.dump(chat_history, f, indent=4)

def get_chat_files():
    return sorted(os.listdir(CHAT_DIR))

def display_chat(history):
    chat_log.config(state='normal')
    chat_log.delete(1.0, tk.END)
    for msg in history[1:]:  # Skip system prompt
        sender = "You" if msg["role"] == "user" else "ConradAI"
        tag = 'user' if msg["role"] == "user" else 'bot'
        chat_log.insert(tk.END, f"{sender}: {msg['content']}\n", tag)
    chat_log.config(state='disabled')
    chat_log.yview(tk.END)

def refresh_chat_list():
    chat_listbox.delete(0, tk.END)
    for file in get_chat_files():
        chat_listbox.insert(tk.END, file.replace(".json", ""))

def on_chat_select(event):
    global chat_history, chat_file
    selection = chat_listbox.curselection()
    if not selection:
        return
    selected_file = chat_listbox.get(selection[0]) + ".json"
    chat_history, chat_file = load_chat(selected_file)
    display_chat(chat_history)

def start_new_chat():
    global chat_history, chat_file
    chat_file = create_new_chat()
    chat_history = [SYSTEM_PROMPT]
    display_chat(chat_history)
    refresh_chat_list()

def ask_conradai(user_input):
    global chat_history
    chat_history.append({"role": "user", "content": user_input})

    data = {
        "model": MODEL_NAME,
        "messages": chat_history,
        "temperature": 0.7
    }

    try:
        response = requests.post(API_URL, headers=HEADERS, json=data)
        if response.status_code == 200:
            bot_response = response.json()['choices'][0]['message']['content']
            chat_history.append({"role": "assistant", "content": bot_response})
            save_chat()
            return bot_response
        else:
            return f"Error: {response.status_code}, {response.text}"
    except Exception as e:
        return f"Exception occurred: {str(e)}"

def send_message():
    user_input = user_entry.get()
    if not user_input.strip():
        return
    chat_log.config(state='normal')
    chat_log.insert(tk.END, f"You: {user_input}\n", 'user')
    user_entry.delete(0, tk.END)

    response = ask_conradai(user_input)
    chat_log.insert(tk.END, f"ConradAI: {response}\n\n", 'bot')
    chat_log.config(state='disabled')
    chat_log.yview(tk.END)

# === UI SETUP ===
window = tk.Tk()
window.title("ConradAI - Code & Chat Assistant")
window.geometry("800x600")

main_frame = tk.Frame(window)
main_frame.pack(fill=tk.BOTH, expand=True)

# Sidebar
sidebar = tk.Frame(main_frame, width=200, bg="#f0f0f0")
sidebar.pack(side=tk.LEFT, fill=tk.Y)

chat_listbox = tk.Listbox(sidebar, bg="#f0f0f0", font=("Consolas", 10))
chat_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
chat_listbox.bind("<<ListboxSelect>>", on_chat_select)

new_chat_button = tk.Button(sidebar, text="New Chat", command=start_new_chat)
new_chat_button.pack(fill=tk.X, padx=5, pady=5)

# Chat Area
chat_area = tk.Frame(main_frame)
chat_area.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

chat_log = scrolledtext.ScrolledText(chat_area, wrap=tk.WORD, state='disabled', font=("Consolas", 11))
chat_log.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

user_entry = tk.Entry(chat_area, font=("Consolas", 12))
user_entry.pack(padx=10, pady=(0,10), fill=tk.X)
user_entry.bind("<Return>", lambda event: send_message())

send_button = tk.Button(chat_area, text="Send", command=send_message)
send_button.pack(pady=(0,10))

chat_log.tag_config('user', foreground='blue')
chat_log.tag_config('bot', foreground='green')

# === INITIAL LOAD ===
chat_files = get_chat_files()
if chat_files:
    chat_history, chat_file = load_chat(chat_files[-1])
else:
    chat_file = create_new_chat()
    chat_history = [SYSTEM_PROMPT]

display_chat(chat_history)
refresh_chat_list()

# === START ===
window.mainloop()
