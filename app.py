import json
import os
from flask import Flask, render_template
from flask_socketio import SocketIO, emit

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

DB_FILE = "messages.json"

def load_messages():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            try: return json.load(f)
            except: return []
    return []

def save_message(msg):
    messages = load_messages()
    messages.append(msg)
    if len(messages) > 100: messages = messages[-100:]
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(messages, f, ensure_ascii=False, indent=4)

@app.route("/")
def index():
    return render_template("index.html")

@socketio.on("send_msg")
def handle_msg(data):
    user = data.get("user", "Аноним")[:20]
    text = data.get("text", "")[:500]
    if text.strip():
        new_msg = {"user": user, "text": text}
        save_message(new_msg)
        emit("receive_msg", new_msg, broadcast=True)

@socketio.on("connect")
def on_connect():
    for msg in load_messages():
        emit("receive_msg", msg)

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000)
