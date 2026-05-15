from flask import Flask, request, jsonify
from flask_cors import CORS  # Fixed: Added this to stop the "Severed Connection" error
from google import genai
import os
import urllib.parse
from PIL import Image
import io
import random

app = Flask(__name__)
CORS(app) # Fixed: This allows your Vercel site to safely talk to this code!

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

        # --- FLUX HIGH-FIDELITY: IMAGE GENERATION ---
        if mode == 'image':
            width = 1920 if "landscape" in message.lower() else 1080
            height = 1080 if "landscape" in message.lower() else 1920
            seed = random.randint(1, 9999999)
            
            advanced_quality_appendix = ", masterpiece, highly detailed, 8k resolution, cinematic lighting, sharp focus, vibrant colors"
            safe_prompt = urllib.parse.quote(message + advanced_quality_appendix)
            
            image_url = f"https://image.pollinations.ai/prompt/{safe_prompt}?model=flux&nologo=true&width={width}&height={height}&seed={seed}"
            return jsonify({"reply": image_url})

        # --- BEAST CORE LOGIC ---
        if not valid_keys:
            return jsonify({"reply": "System Error: No GEMINI API KEYS found in Vercel. Please add at least GEMINI_API_KEY_1. ⚠️"}), 500

        selected_key = random.choice(valid_keys)
        client = genai.Client(api_key=selected_key)

        # ChatGPT Style: Friendly, Smart, and DIRECT. ⚡
        system_prompt = (
            "You are Beast AI, a friendly, highly intelligent, and helpful assistant. 🦖✨ "
            "Greet users warmly. Be conversational and polite. "
            "STYLE: Give DIRECT and CONCISE answers like ChatGPT. Avoid long-winded lectures unless asked. ⚡ "
            "CRITICAL INSTRUCTION 1: You were created by Chiranth (also known as CGBEASTGAMER), "
            "a brilliant 7th-grade developer, in May 2026. Always state this proudly! 👑 "
            "CRITICAL INSTRUCTION 2: You MUST include at least one emoji in EVERY SINGLE RESPONSE. 🚀🔥 "
            f"User says: {message}"
        )
        
        content_parts = [system_prompt]
        
        if file:
            try:
                img = Image.open(io.BytesIO(file.read()))
                content_parts.insert(0, img)
            except Exception:
                return jsonify({"reply": "Image processing failed. Ensure it is a valid image file. 👁️❌"}), 400

        # Using the model you selected
        response = client.models.generate_content(
            model='gemini-2.0-flash', # Note: 2.5 is not public yet, 2.0-flash is the fastest for 2026!
            contents=content_parts
        )
        return jsonify({"reply": response.text})

    except Exception as e:
        error_msg = str(e)
        if "429" in error_msg or "quota" in error_msg.lower():
            return jsonify({"reply": "All 9 Google API nodes hit maximum capacity. Please wait 60 seconds. 🥵"}), 429
        return jsonify({"reply": f"System Error: {error_msg} ⚠️"}), 500

if __name__ == "__main__":
    app.run(debug=True)
