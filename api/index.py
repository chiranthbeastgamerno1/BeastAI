from flask import Flask, request, jsonify
from flask_cors import CORS
from google import genai
from google.genai import types
import os
import urllib.parse
import random
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
    return "Beast AI Core is Online (Ultra-High-Resolution)! 🦖✨"

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        message = request.form.get("message", "")
        mode = request.form.get("mode", "chat")
        
        if not message:
            return jsonify({"reply": "The Beast hears only silence. 🤫"}), 200

        if not valid_keys:
            return jsonify({"reply": "System Error: No keys found in Vercel! ⚠️"}), 200

        client = genai.Client(api_key=random.choice(valid_keys))

        # --- THE HIGH-RESOLUTION IMAGE GENERATOR ---
        if mode == 'image':
            try:
                is_landscape = "landscape" in message.lower() or "widescreen" in message.lower()
                aspect = "16:9" if is_landscape else "9:16"
                
                # --- NEW RESOLUTION TARGET: Crisp 1024x1024 ---
                # This closes the quality gap by requesting full detailed assets
                # rather than the default low-res ones.
                
                # We inject powerful quality keywords into the user's prompt
                high_quality_prompt = f"{message}, masterpiece, high quality, incredibly detailed, photorealistic, sharp focus, vibrant colors"
                
                result = client.models.generate_images(
                    model='imagen-3.0-generate-001', 
                    prompt=high_quality_prompt,
                    config=types.GenerateImagesConfig(
                        number_of_images=1, 
                        aspect_ratio=aspect, 
                        output_mime_type="image/jpeg",
                        # 🚀 The Critical Fix: We are explicitly requesting high resolution
                        generation_config={
                            'width': 1024,
                            'height': 1024
                        }
                    )
                )
                import base64
                img_b64 = base64.b64encode(result.generated_images[0].image.image_bytes).decode('utf-8')
                return jsonify({"reply": f"data:image/jpeg;base64,{img_b64}"}), 200
            except Exception as img_err:
                 # Standard text refusal for safety but still attempt backup
                 print(f"Model generation failed: {str(img_err)}")
                 seed = random.randint(1, 9999999)
                 safe_prompt = urllib.parse.quote(f"{message}, highly detailed, sharp focus")
                 # pollination.ai is reliable but default res might look worse when stretched.
                 return jsonify({"reply": f"https://image.pollinations.ai/prompt/{safe_prompt}?model=flux&nologo=true&seed={seed}"}), 200

        ist = timezone(timedelta(hours=5, minutes=30))
        live_time = datetime.now(ist).strftime("%A, %d %B %Y, %I:%M %p IST")

        system_instruction = (
            "You are Beast AI, a friendly and witty assistant. 🦖✨ "
            "You were created by Chiranth G (CGBEASTGAMER), a brilliant developer. "
            f"The current live date and time is exactly: {live_time}. " 
            "STYLE: Be conversational but DIRECT. Give short answers like ChatGPT. "
            "Always use at least one emoji! 🚀🔥"
        )

        final_response_text = None
        for current_model in TEXT_MODELS:
            try:
                response = client.models.generate_content(
                    model=current_model, contents=message,
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
