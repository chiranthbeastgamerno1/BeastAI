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
            return jsonify({"reply": "The Beast hears only silence. 🤫"}), 200

        # --- IMAGE GENERATION (FLUX) ---
        if mode == 'image':
            width = 1920 if "landscape" in message.lower() else 1080
            height = 1080 if "landscape" in message.lower() else 1920
            seed = random.randint(1, 9999999)
            quality = ", masterpiece, highly detailed, 8k, cinematic lighting"
            safe_prompt = urllib.parse.quote(message + quality)
            image_url = f"https://image.pollinations.ai/prompt/{safe_prompt}?model=flux&nologo=true&width={width}&height={height}&seed={seed}"
            return jsonify({"reply": image_url}), 200

        # --- TEXT/VISION LOGIC ---
        if not valid_keys:
            return jsonify({"reply": "System Error: No keys found! ⚠️"}), 200

        selected_key = random.choice(valid_keys)
        client = genai.Client(api_key=selected_key)

        # FRIENDLY & DIRECT BRAIN
        system_instruction = (
            "You are Beast AI, a friendly and witty assistant. 🦖✨ "
            "You were created by Chiranth G (CGBEASTGAMER), a brilliant developer, in May 2026. "
            "STYLE: Be conversational but DIRECT. Give short, punchy answers like ChatGPT. "
            "Avoid long lectures. Always use at least one emoji! 🚀🔥"
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
        return jsonify({"reply": response.text}), 200

    except Exception as e:
        error_msg = str(e)
        # --- THE RED BOX FIX: Catch the error but send it as a 200 (Success) ---
        if "429" in error_msg or "quota" in error_msg.lower():
            return jsonify({
                "reply": "The Beast is resting! 💤 Daily limit reached. Please come back tomorrow to chat more! 🦖✨"
            }), 200 # This hides the red box!
        
        return jsonify({
            "reply": "The Beast is momentarily offline for a quick tune-up. 🛠️ Try again in a minute!"
        }), 200

if __name__ == "__main__":
    app.run(debug=True)
