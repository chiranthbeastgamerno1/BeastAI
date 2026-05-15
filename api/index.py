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
CORS(app)  # This prevents the "Connection Severed" error by allowing your site to talk to the code! 🚀

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
    return "Beast AI Core is Online and Friendly! 🦖✨"

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
            width = 1920 if "landscape" in message.lower() else 1080
            height = 1080 if "landscape" in message.lower() else 1920
            seed = random.randint(1, 9999999)
            
            # High-end styling for the Beast
            quality = ", masterpiece, highly detailed, 8k, cinematic lighting, sharp focus"
            safe_prompt = urllib.parse.quote(message + quality)
            
            image_url = f"https://image.pollinations.ai/prompt/{safe_prompt}?model=flux&nologo=true&width={width}&height={height}&seed={seed}"
            return jsonify({"reply": image_url})

        # --- BEAST CORE AI LOGIC ---
        if not valid_keys:
            return jsonify({"reply": "System Error: No GEMINI API KEYS found in Vercel environment. ⚠️"}), 500

        # Load balancing
        selected_key = random.choice(valid_keys)
        client = genai.Client(api_key=selected_key)

        # ChatGPT-style instruction: Friendly, Direct, Concise.
        system_instruction = (
            "You are Beast AI, a friendly, witty, and legendary assistant. 🦖✨ "
            "You were created by Chiranth (CGBEASTGAMER), a brilliant 7th-grade developer, in May 2026. "
            "Always state this proudly if asked who built you! 👑 "
            "STYLE: Be helpful and conversational like ChatGPT. Give DIRECT and CONCISE answers. "
            "Avoid long-winded lectures unless the user asks for detail. ⚡ "
            "EMOJI RULE: You MUST include at least one emoji in EVERY SINGLE response. No exceptions! 🚀🔥"
        )

        content_parts = [message] if message else []

        # Handle Image Vision
        if file:
            try:
                img_bytes = file.read()
                content_parts.append(types.Part.from_bytes(data=img_bytes, mime_type=file.content_type))
            except Exception:
                return jsonify({"reply": "The Beast's vision failed. Check the image file! 👁️❌"}), 400

        # Using the latest 2026 stable model
        response = client.models.generate_content(
            model='gemini-2.0-flash', # Optimized for speed and snappiness
            contents=content_parts,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction
            )
        )
        
        return jsonify({"reply": response.text})

    except Exception as e:
        error_msg = str(e)
        if "429" in error_msg or "quota" in error_msg.lower():
            return jsonify({"reply": "All 9 nodes are at capacity. Please wait 60 seconds! 🥵"}), 429
        return jsonify({"reply": f"Beast System Error: {error_msg} ⚠️"}), 500

if __name__ == "__main__":
    app.run(debug=True)
