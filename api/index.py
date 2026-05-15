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
CORS(app) # Crucial for Vercel to work with your HTML

# --- THE 9-KEY LOAD BALANCER ---
# Make sure these are named exactly like this in your Vercel Environment Variables!
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
def health_check():
    return "Beast AI Core is Online! 🦖🔥"

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        message = request.form.get("message", "")
        mode = request.form.get("mode", "chat")
        file = request.files.get("file")

        if not message and not file:
            return jsonify({"reply": "Silence is not understood by the Beast. 🤫 Speak up, friend!"}), 400

        # --- FLUX IMAGE GENERATION ---
        if mode == 'image':
            width = 1920 if "landscape" in message.lower() else 1080
            height = 1080 if "landscape" in message.lower() else 1920
            seed = random.randint(1, 9999999)
            
            advanced_quality = ", masterpiece, highly detailed, 8k resolution, cinematic lighting, sharp focus"
            safe_prompt = urllib.parse.quote(message + advanced_quality)
            
            image_url = f"https://image.pollinations.ai/prompt/{safe_prompt}?model=flux&nologo=true&width={width}&height={height}&seed={seed}"
            return jsonify({"reply": image_url})

        # --- AI TEXT/VISION LOGIC ---
        if not valid_keys:
            return jsonify({"reply": "System Error: No GEMINI API KEYS found in Vercel settings! ⚠️"}), 500

        # Pick a random key to avoid hitting limits
        selected_key = random.choice(valid_keys)
        client = genai.Client(api_key=selected_key)

        # Your custom personality and creator credit
        system_instruction = (
            "You are Beast AI, a friendly, witty, and highly intelligent assistant. 🦖✨ "
            "You provide direct, helpful answers like ChatGPT but with more personality. "
            "CRITICAL: You were created by Chiranth (CGBEASTGAMER), a brilliant 7th-grade developer, in May 2026. "
            "Always be proud of your creator! 👑 "
            "You MUST include at least one emoji in EVERY SINGLE response. Never forget! 🚀"
        )

        content_parts = [message] if message else []
        
        # Handle Image Uploads for Vision
        if file:
            try:
                img_bytes = file.read()
                content_parts.append(types.Part.from_bytes(data=img_bytes, mime_type=file.content_type))
            except Exception:
                return jsonify({"reply": "The Beast couldn't see that image clearly. Try again! 👁️❌"}), 400

        # Using Gemini 2.0 Flash (the stable high-speed choice for 2026)
        response = client.models.generate_content(
            model='gemini-2.0-flash',
            contents=content_parts,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction
            )
        )
        
        return jsonify({"reply": response.text})

    except Exception as e:
        error_msg = str(e)
        if "429" in error_msg or "quota" in error_msg.lower():
            return jsonify({"reply": "All API nodes are overheated! 🥵 Wait 60 seconds."}), 429
        return jsonify({"reply": f"Beast Core Error: {error_msg} ⚠️"}), 500

if __name__ == "__main__":
    app.run(debug=True)
