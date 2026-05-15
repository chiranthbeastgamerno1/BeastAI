import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai

app = Flask(__name__)
# This allows your Vercel site to talk to this Python backend without errors
CORS(app) 

# --- 1. THE BRAIN CONFIGURATION ---
# Replace 'YOUR_GEMINI_API_KEY' with the key from Google AI Studio.
# Note: This is DIFFERENT from your Firebase key! 🔑
GEMINI_KEY = "YOUR_GEMINI_API_KEY"
genai.configure(api_key=GEMINI_KEY)

# This tells the Beast exactly how to behave. 
# We're making it direct, witty, and super friendly! 🦖💬
SYSTEM_PROMPT = (
    "You are Beast AI, a legendary and high-energy assistant. 🦖✨ "
    "Your personality: Authentic, witty, supportive, and extremely friendly. "
    "Your goal: Give DIRECT and CONCISE answers like ChatGPT. "
    "NO long lectures or boring textbook essays! 🚫📚 Keep it punchy! "
    "Use emojis to make the conversation feel alive and awesome. 🚀🔥 "
    "If a user says 'hi', be welcoming. If they ask a question, answer it "
    "immediately without fluff. Be the smartest, coolest AI in the room."
)

# Initialize the model with our custom personality
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    system_instruction=SYSTEM_PROMPT
)

@app.route('/')
def home():
    return "The Beast Engine is Purring... 🦖🔥 Ready for action!"

# FIXED: Changed 'method' to 'methods' to prevent errors! ✅
@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        # Catching the message sent from your HTML's FormData
        user_message = request.form.get('message')
        
        if not user_message:
            return jsonify({"reply": "The Beast heard nothing but silence... 🤫 Speak up, friend!"}), 400

        # Create a fresh chat session for every request
        # (This keeps the AI focused and fast!)
        chat_session = model.start_chat(history=[])
        
        # Send the message to the brain and get the reply
        response = chat_session.send_message(user_message)
        
        # Send the direct, friendly reply back to your website
        return jsonify({"reply": response.text})

    except Exception as e:
        print(f"Error encountered: {e}")
        return jsonify({"reply": "The connection to the Beast core was severed! ⚡😵 Try again in a second!"}), 500

if __name__ == '__main__':
    # Standard port 5000 for local testing on your PC
    app.run(debug=True, port=5000)
