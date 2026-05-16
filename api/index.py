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

# --- THE MODEL CASCADE (Auto-Switcher) ---
# The Beast will try these in order. If one is tired, it moves to the next!
TEXT_MODELS = [
    'gemini-2.5-flash', 
    'gemini-2.0-flash', 
    'gemini-2.5-pro'
]

@app.route('/')
def home():
    return "Beast AI Core is Online with Auto-Switching! 🦖✨"

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        message = request.form.get("message", "")
        mode = request.form.get("mode", "chat")
        file = request.files.get("file")

        if not message and not file:
            return jsonify({"reply": "The Beast hears only silence. 🤫"}), 200

        if not valid_keys:
            return jsonify({"reply": "System Error: No keys found! ⚠️"}), 200

        selected_key = random.choice(valid_keys)
        client = genai.Client(api_key=selected_key)

        # --- GOOGLE IMAGEN GENERATOR ---
        if mode == 'image':
            try:
                aspect = "16:9" if "landscape" in message.lower() else "9:16"
                # You can also add a list of Imagen models here if you want an image fallback!
                result = client.models.generate_images(
                    model='imagen-4.0-generate-001', # Updated to the latest from your screenshot
                    prompt=message + ", masterpiece, high quality, 8k",
                    config=types.GenerateImagesConfig(
                        number_of_images=1,
                        aspect_ratio=aspect,
                        output_mime_type="image/jpeg"
                    )
                )
                
                import base64
                img_bytes = result.generated_images[0].image.image_bytes
                img_b64 = base64.b64encode(img_bytes).decode('utf-8')
                return jsonify({"reply": f"data:image/jpeg;base64,{img_b64}"}), 200
            
            except Exception as e:
                 # If Google Imagen fails or limits out, fallback to Pollinations (Free/Unlimited)
                 seed = random.randint(1, 9999999)
                 safe_prompt = urllib.parse.quote(message + ", masterpiece, highly detailed, 8k")
                 image_url = f"https://image.pollinations.ai/prompt/{safe_prompt}?model=flux&nologo=true&seed={seed}"
                 return jsonify({"reply": image_url}), 200

        # --- BEAST AI TEXT/VISION BRAIN ---
        system_instruction = (
            "You are Beast AI, a friendly and witty assistant. 🦖✨ "
            "Created by Chiranth G (CGBEASTGAMER), a brilliant developer, in May 2026. "
            "STYLE: Be conversational but DIRECT. Give short answers like ChatGPT. "
            "Always use at least one emoji! 🚀🔥"
        )

        content_parts = [message] if message else []
        if file:
            img_bytes = file.read()
            content_parts.append(types.Part.from_bytes(data=img_bytes, mime_type=file.content_type))

        # --- THE FALLBACK LOOP ---
        final_response_text = None
        
        for current_model in TEXT_MODELS:
            try:
                response = client.models.generate_content(
                    model=current_model,
                    contents=content_parts,
                    config=types.GenerateContentConfig(system_instruction=system_instruction)
                )
                final_response_text = response.text
                break # Success! Break out of the loop and stop trying other models.
                
            except Exception as model_error:
                error_str = str(model_error).lower()
                # If this specific model hit a quota limit, loop continues to the next model
                if "429" in error_str or "quota" in error_str or "exhausted" in error_str:
                    print(f"Model {current_model} exhausted. Switching to backup...")
                    continue 
                else:
                    # If it's a completely different error (like a safety block), raise it immediately
                    raise model_error

        # If the loop finishes and we STILL don't have text, it means ALL models are exhausted
        if not final_response_text:
             return jsonify({"reply": "The Beast is resting! 💤 All backup brains have reached their daily limit. Come back tomorrow! 🦖✨"}), 200

        return jsonify({"reply": final_response_text}), 200

    except Exception as e:
        error_msg = str(e).lower()
        if "safety" in error_msg:
             return jsonify({"reply": "The Beast cannot manifest that vision due to safety protocols. Try a different prompt! 🛡️✨"}), 200
             
        return jsonify({"reply": "The Beast is momentarily offline for a tune-up. 🛠️"}), 200

if __name__ == "__main__":
    app.run(debug=True)
