from flask import Flask, request, jsonify
from flask_cors import CORS
from google import genai
from google.genai import types
import os
import urllib.parse
from PIL import Image
import io
import random

app = Flask(__name__)
CORS(app) 

# --- THE 9-KEY LOAD BALANCER ---
api_keys = [
    os.environ.get("GEMINI_API_KEY_1"),
    os.environ.get("GEMINI_API_KEY_2"),
    os.environ.get("GEMINI_API_KEY_3"),
    os.environ.get("GEMINI_API_KEY_4"),
    os.environ.get("GEMINI_API_KEY_5"),
    os.environ.get("GEMINI_API_KEY_6"),
    os.environ.get("GEMINI_API_KEY_7"),
    os.environ.get("GEMINI_API_KEY_8"),
    os.environ.get("GEMINI_API_KEY_9")
]
valid_keys = [key for key in api_keys if key]

@app.route('/')
def home():
    return "Beast AI Core is Online! 🦖✨"

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        message = request.form.get("message", "")
        mode = request.form.get("mode", "chat")
        file = request.files.get("file")

        if not message and not file:
            return jsonify({"reply": "Silence is not understood by the Beast. 🤫"}), 400

        # --- FLUX IMAGE GENERATION ---
        if mode == 'image':
            seed = random.randint(1, 9999999)
            safe_prompt = urllib.parse.quote(message + ", high quality, 8k")
            image_url = f"https://image.pollinations.ai/prompt/{safe_prompt}?model=flux&seed={seed}"
            return jsonify({"reply": image_url})

        # --- BEAST AI BRAIN ---
        if not valid_keys:
            return jsonify({"reply": "System Error: No keys found. ⚠️"}), 500

        selected_key = random.choice(valid_keys)
        client = genai.Client(api_key=selected_key)

        system_instruction = (
            "You are Beast AI, a friendly, witty, and direct assistant. 🦖✨ "
            "Created by Chiranth (CGBEASTGAMER), a brilliant 7th-grade developer. "
            "Give direct, concise answers like ChatGPT. Always use emojis! 🚀"
        )

        content_parts = [message] if message else []
        if file:
            img_bytes = file.read()
            content_parts.append(types.Part.from_bytes(data=img_bytes, mime_type=file.content_type))

        response = client.models.generate_content(
            model='gemini-2.0-flash',
            contents=content_parts,
            config=types.GenerateContentConfig(system_instruction=system_instruction)
        )
        return jsonify({"reply": response.text})

    except Exception as e:
        error_msg = str(e)
        # --- THE PANIC FIX: Change scary errors into friendly messages ---
        if "429" in error_msg or "quota" in error_msg.lower():
            return jsonify({"reply": "The Beast is resting! 💤 Daily limit reached. Please come back tomorrow to chat more! 🦖✨"}), 429
        
        return jsonify({"reply": f"The Beast is momentarily offline for maintenance. 🛠️ Try again in a minute!"}), 500

if __name__ == "__main__":
    app.run(debug=True)
