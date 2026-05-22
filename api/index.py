from flask import Flask, request, jsonify
from flask_cors import CORS
from google import genai
from google.genai import types
import os
import urllib.parse
import random
from datetime import datetime, timedelta, timezone # NEW: We imported the clock! ⏰

app = Flask(__name__)
CORS(app) 

# --- SECURE 9-KEY LOAD BALANCER ---
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

TEXT_MODELS = ['gemini-2.5-flash', 'gemini-2.0-flash', 'gemini-2.5-pro']

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

        if not valid_keys:
            return jsonify({"reply": "System Error: No keys found in Vercel! ⚠️"}), 200

        selected_key = random.choice(valid_keys)
        client = genai.Client(api_key=selected_key)

        # --- GOOGLE IMAGEN WITH FLUX FALLBACK ---
        if mode == 'image':
            try:
                aspect = "16:9" if "landscape" in message.lower() else "9:16"
                result = client.models.generate_images(
                    model='imagen-4.0-generate-001', 
                    prompt=message + ", masterpiece, high quality, 8k",
                    config=types.GenerateImagesConfig(number_of_images=1, aspect_ratio=aspect, output_mime_type="image/jpeg")
                )
                import base64
                img_b64 = base64.b64encode(result.generated_images[0].image.image_bytes).decode('utf-8')
                return jsonify({"reply": f"data:image/jpeg;base64,{img_b64}"}), 200
            except Exception:
                 seed = random.randint(1, 9999999)
                 safe_prompt = urllib.parse.quote(message + ", masterpiece, highly detailed, 8k")
                 return jsonify({"reply": f"https://image.pollinations.ai/prompt/{safe_prompt}?model=flux&nologo=true&seed={seed}"}), 200

        # --- GET CURRENT LIVE TIME IN IST ---
        ist = timezone(timedelta(hours=5, minutes=30))
        live_time = datetime.now(ist).strftime("%A, %d %B %Y, %I:%M %p IST")

        # --- TEXT/VISION BRAIN ---
        system_instruction = (
            "You are Beast AI, a friendly and witty assistant. 🦖✨ "
            "You were created by Chiranth G (CGBEASTGAMER), a brilliant 7th-grade developer, in May 2026. "
            f"The current live date and time is exactly: {live_time}. " # Injection!
            "STYLE: Be conversational but DIRECT. Give short answers like ChatGPT. "
            "Always use at least one emoji! 🚀🔥"
        )

        content_parts = [message] if message else []
        if file:
            content_parts.append(types.Part.from_bytes(data=file.read(), mime_type=file.content_type))

        final_response_text = None
        for current_model in TEXT_MODELS:
            try:
                response = client.models.generate_content(
                    model=current_model, contents=content_parts,
                    config=types.GenerateContentConfig(system_instruction=system_instruction)
                )
                final_response_text = response.text
                break
            except Exception as model_error:
                error_str = str(model_error).lower()
                if "429" in error_str or "quota" in error_str or "exhausted" in error_str:
                    continue 
                raise model_error

        if not final_response_text:
             return jsonify({"reply": "The Beast is resting! 💤 Daily limit reached. Come back tomorrow! 🦖✨"}), 200

        return jsonify({"reply": final_response_text}), 200

    except Exception as e:
        if "safety" in str(e).lower():
             return jsonify({"reply": "The Beast cannot manifest that vision due to safety protocols! 🛡️✨"}), 200
        return jsonify({"reply": "The connection to the Beast core was severed! ⚡😵"}), 200

if __name__ == "__main__":
    app.run(debug=True)
