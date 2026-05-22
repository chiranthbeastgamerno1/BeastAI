from flask import Flask, request, jsonify
from flask_cors import CORS
from google import genai
from google.genai import types
import os
import urllib.parse
import random
import json # NEW: Needed to parse your memory history
from datetime import datetime, timedelta, timezone

app = Flask(__name__)
CORS(app) 

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
    return "Beast AI Core is Online (Memory Edition)! 🦖✨"

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        message = request.form.get("message", "")
        mode = request.form.get("mode", "chat")
        files = request.files.getlist("files")
        
        # 🧠 MEMORY UPGRADE: Catch the history sent by HTML
        history_json = request.form.get("history", "[]")
        try:
            chat_history = json.loads(history_json)
        except:
            chat_history = []

        if not message and not files:
            return jsonify({"reply": "The Beast hears only silence. 🤫"}), 200

        if not valid_keys:
            return jsonify({"reply": "System Error: No keys found in Vercel! ⚠️"}), 200

        client = genai.Client(api_key=random.choice(valid_keys))

        # --- IMAGE GENERATION ---
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

        ist = timezone(timedelta(hours=5, minutes=30))
        live_time = datetime.now(ist).strftime("%A, %d %B %Y, %I:%M %p IST")

        system_instruction = (
            "You are Beast AI, a friendly and witty assistant. 🦖✨ "
            "You were created by Chiranth G (CGBEASTGAMER), a brilliant 7th-grade developer. "
            f"The current live date and time is: {live_time}. " 
            "STYLE: Be conversational but DIRECT. Give short answers like ChatGPT. "
            "Always use emojis! 🚀🔥"
        )

        # 🧠 BUILD THE CONVERSATION HISTORY FOR THE AI
        api_contents = []
        
        # Add past messages
        for item in chat_history:
            role = "user" if item.get("type") == "user" else "model"
            text = item.get("message", "")
            if text:
                api_contents.append(types.Content(role=role, parts=[types.Part.from_text(text=text)]))
        
        # Add the CURRENT message and any new compressed files!
        current_parts = []
        if message:
            current_parts.append(types.Part.from_text(text=message))
        if files:
            for file in files:
                current_parts.append(types.Part.from_bytes(data=file.read(), mime_type=file.content_type))
                
        if current_parts:
            api_contents.append(types.Content(role="user", parts=current_parts))

        # --- FIRE THE REQUEST ---
        final_response_text = None
        for current_model in TEXT_MODELS:
            try:
                response = client.models.generate_content(
                    model=current_model, 
                    contents=api_contents, # Send the whole memory block!
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
        return jsonify({"reply": f"The connection to the Beast core was severed! ⚡😵"}), 200

if __name__ == "__main__":
    app.run(debug=True)
