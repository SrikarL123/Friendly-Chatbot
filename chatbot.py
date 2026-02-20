from flask import Flask, request, jsonify, send_file
from groq import Groq
from dotenv import load_dotenv
import os

load_dotenv()

# Proper static folder configuration
app = Flask(__name__, static_folder="static")

# Load API key from environment
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Conversation memory (resets if server restarts)
messages = [
    {
        "role": "system",
        "content": "You are a helpful assistant. Give short, clear, and concise answers unless the user explicitly asks for detailed explanation."
    }
]

# -------------------------------
# ROUTES
# -------------------------------

@app.route("/")
def start():
    return send_file(os.path.join(BASE_DIR, "start.html"))

@app.route("/chatbot")
def chatbot():
    return send_file(os.path.join(BASE_DIR, "chat.html"))

@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json()
        user_message = data.get("message", "").strip()

        if not user_message:
            return jsonify({"reply": "Please enter a valid message."})

        messages.append({"role": "user", "content": user_message})

        # Trim memory to avoid huge prompt
        MAX_MESSAGES = 25
        if len(messages) > MAX_MESSAGES:
            messages.pop(1)  # keep system message at index 0

        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=messages,
            max_tokens=150
        )

        reply = response.choices[0].message.content

        messages.append({"role": "assistant", "content": reply})

        return jsonify({"reply": reply})

    except Exception as e:
        print("Error:", str(e))
        return jsonify({"reply": "Something went wrong. Please try again."}), 500


# -------------------------------
# LOCAL DEV ONLY
# -------------------------------

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
