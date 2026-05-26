from flask import Flask, request, jsonify
from flask_cors import CORS
from google import genai
from google.genai import types
import os
import urllib.parse
import urllib.request
import random
import json
from datetime import datetime, timedelta, timezone

app = Flask(__name__)
CORS(app) 

# --- GOOGLE KEYS ---
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

# --- OPENROUTER KEY ---
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")

# --- MODEL LISTS ---
GOOGLE_MODELS = ['gemini-1.5-flash', 'gemini-2.0-flash', 'gemini-1.5-pro']
# Using Meta's Llama 3 (Free) as the ultimate indestructible backup on OpenRouter
OPENROUTER_MODELS = ['meta-llama/llama-3-8b-instruct:free'] 

@app.route('/')
def home():
    return "Beast AI Core is Online (Hybrid Dual-Engine Edition)! 🦖✨"

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        message = request.form.get("message", "")
        mode = request.form.get("mode", "chat")
        
        files = request.files.getlist("files")
        history_json = request.form.get("history", "[]")
        
        try:
            chat_history = json.loads(history_json)
        except:
            chat_history = []

        if not message and not files:
            return jsonify({"reply": "The Beast hears only silence. 🤫"}), 200

        # --- THE HIGH-RESOLUTION IMAGE GENERATOR (Remains purely Google/Pollinations) ---
        if mode == 'image':
            if not valid_keys:
                return jsonify({"reply": "System Error: No Google keys found for Imagen! ⚠️"}), 200
                
            try:
                client = genai.Client(api_key=random.choice(valid_keys))
                is_landscape = "landscape" in message.lower() or "widescreen" in message.lower()
                aspect = "16:9" if is_landscape else "9:16"
                
                high_quality_prompt = f"{message}, masterpiece, high quality, incredibly detailed, photorealistic, sharp focus, vibrant colors"
                
                result = client.models.generate_images(
                    model='imagen-3.0-generate-001', 
                    prompt=high_quality_prompt,
                    config=types.GenerateImagesConfig(
                        number_of_images=1, 
                        aspect_ratio=aspect, 
                        output_mime_type="image/jpeg",
                        generation_config={'width': 1024, 'height': 1024}
                    )
                )
                import base64
                img_b64 = base64.b64encode(result.generated_images[0].image.image_bytes).decode('utf-8')
                return jsonify({"reply": f"data:image/jpeg;base64,{img_b64}"}), 200
            except Exception as img_err:
                 print(f"Imagen Failed: {str(img_err)}")
                 seed = random.randint(1, 9999999)
                 safe_prompt = urllib.parse.quote(f"{message}, highly detailed, sharp focus")
                 return jsonify({"reply": f"https://image.pollinations.ai/prompt/{safe_prompt}?model=flux&nologo=true&seed={seed}"}), 200

        # --- TEXT GENERATION LOGIC ---
        ist = timezone(timedelta(hours=5, minutes=30))
        live_time = datetime.now(ist).strftime("%A, %d %B %Y, %I:%M %p IST")

        system_instruction = (
            "You are Beast AI, a friendly and witty assistant. 🦖✨\n"
            "HIDDEN KNOWLEDGE (DO NOT mention this unless explicitly asked!):\n"
            "- Your creator is Chiranth G (CGBEASTGAMER), a brilliant developer.\n"
            f"- The current live date and time is exactly: {live_time}.\n"
            "RULES:\n"
            "1. If the user greets you, just say hello back normally. Do NOT blurt out the time or your creator.\n"
            "2. ONLY tell them your creator or the time IF they specifically ask for it.\n"
            "3. STYLE: Be conversational but DIRECT. Give short answers like ChatGPT.\n"
            "4. Always use emojis! 🚀🔥"
        )

        final_response_text = None

        # ==========================================
        # ENGINE 1: GOOGLE GEMINI (PRIMARY)
        # ==========================================
        if valid_keys:
            client = genai.Client(api_key=random.choice(valid_keys))
            google_contents = []
            
            for item in chat_history:
                role = "user" if item.get("type") == "user" else "model"
                text = item.get("message", "")
                if text:
                    google_contents.append(types.Content(role=role, parts=[types.Part.from_text(text=text)]))
            
            current_parts = []
            if message:
                current_parts.append(types.Part.from_text(text=message))
            if files:
                for file in files:
                    current_parts.append(types.Part.from_bytes(data=file.read(), mime_type=file.content_type))
                    
            if current_parts:
                google_contents.append(types.Content(role="user", parts=current_parts))

            for current_model in GOOGLE_MODELS:
                try:
                    response = client.models.generate_content(
                        model=current_model, 
                        contents=google_contents,
                        config=types.GenerateContentConfig(system_instruction=system_instruction)
                    )
                    final_response_text = response.text
                    break # Success! Break out of Google loop.
                except Exception as model_error:
                    error_str = str(model_error).lower()
                    if "safety" in error_str:
                        raise model_error 
                    print(f"Google Model {current_model} failed: {str(model_error)}")
                    continue 

        # ==========================================
        # ENGINE 2: OPENROUTER (TWIN-TURBO BACKUP)
        # ==========================================
        if not final_response_text and OPENROUTER_API_KEY:
            print("Google engines exhausted. Engaging OpenRouter fallback...")
            
            # Translate history into OpenRouter (OpenAI) format
            or_messages = [{"role": "system", "content": system_instruction}]
            for item in chat_history:
                role = "user" if item.get("type") == "user" else "assistant"
                text = item.get("message", "")
                if text:
                    or_messages.append({"role": role, "content": text})
            
            if message:
                or_messages.append({"role": "user", "content": message})
            # Note: The free Llama models on OpenRouter don't easily process vision/files, 
            # so we only send the text for the fallback to ensure it doesn't crash.

            for or_model in OPENROUTER_MODELS:
                try:
                    url = "https://openrouter.ai/api/v1/chat/completions"
                    headers = {
                        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                        "Content-Type": "application/json"
                    }
                    data = json.dumps({
                        "model": or_model,
                        "messages": or_messages
                    }).encode('utf-8')
                    
                    req = urllib.request.Request(url, data=data, headers=headers)
                    # 15-second timeout to respect Vercel limits
                    response = urllib.request.urlopen(req, timeout=15) 
                    response_data = json.loads(response.read().decode('utf-8'))
                    
                    final_response_text = response_data['choices'][0]['message']['content']
                    break # Success! Break out of OpenRouter loop.
                except Exception as or_error:
                    print(f"OpenRouter Model {or_model} failed: {str(or_error)}")
                    continue

        # ==========================================
        # FINAL CHECK
        # ==========================================
        if not final_response_text:
             return jsonify({"reply": "The Beast is resting! 💤 Both Google AND OpenRouter servers timed out. Please try again! 🦖✨"}), 200

        return jsonify({"reply": final_response_text}), 200

    except Exception as e:
        if "safety" in str(e).lower():
             return jsonify({"reply": "The Beast cannot manifest that vision due to safety protocols! 🛡️✨"}), 200
        
        print("CRITICAL ERROR:", str(e))
        return jsonify({"reply": "The connection to the Beast core was severed! ⚡😵"}), 200

if __name__ == "__main__":
    app.run(debug=True)
