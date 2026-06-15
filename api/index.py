from flask import Flask, request, jsonify
from flask_cors import CORS
from google import genai
from google.genai import types
import os
import re
import urllib.parse
import urllib.request
import urllib.error
import random
import json
from datetime import datetime, timedelta, timezone

app = Flask(__name__)
CORS(app) 

# ==========================================
# 🔑 ALL API KEYS (FULLY INTEGRATED)
# ==========================================
api_keys = [
    os.environ.get("GEMINI_API_KEY_1", "").strip() or None,
    os.environ.get("GEMINI_API_KEY_2", "").strip() or None,
    os.environ.get("GEMINI_API_KEY_3", "").strip() or None,
    os.environ.get("GEMINI_API_KEY_4", "").strip() or None,
    os.environ.get("GEMINI_API_KEY_5", "").strip() or None,
    os.environ.get("GEMINI_API_KEY_6", "").strip() or None,
    os.environ.get("GEMINI_API_KEY_7", "").strip() or None,
    os.environ.get("GEMINI_API_KEY_8", "").strip() or None,
    os.environ.get("GEMINI_API_KEY_9", "").strip() or None
]
valid_keys = [key for key in api_keys if key]

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "").strip() or None
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "").strip() or None

# --- MODEL DEFINITIONS ---
GOOGLE_MODELS = ['gemini-2.5-flash', 'gemini-2.5-pro', 'gemini-3.5-flash']
OPENROUTER_MODELS = ['meta-llama/llama-3-8b-instruct:free', 'mistralai/mistral-7b-instruct:free'] 


@app.route('/')
def home():
    return "Beast AI Core is Online (Precision Strike Edition)! 🦖✨"


@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        # Failsafe data extraction supporting both form-data and json payloads
        message = request.form.get("message") or (request.json and request.json.get("message")) or ""
        mode = request.form.get("mode") or (request.json and request.json.get("mode")) or "chat"
        files = request.files.getlist("files") if hasattr(request, 'files') else []
        history_json = request.form.get("history") or (request.json and request.json.get("history")) or "[]"
        
        try:
            chat_history = json.loads(history_json) if isinstance(history_json, str) else history_json
        except:
            chat_history = []

        if not message and not files:
            return jsonify({"reply": "The Beast hears only silence. 🤫"}), 200

        # ==========================================
        # 🖼️ MANIFEST IMAGE MODE (STRICTLY ISOLATED)
        # ==========================================
        if mode == 'image':
            image_url = None
            
            # --- ATTEMPT 1: OpenAI DALL-E 3 ---
            if OPENAI_API_KEY:
                try:
                    print("Attempting Primary Image Engine: OpenAI DALL-E 3...")
                    url = "https://api.openai.com/v1/images/generations"
                    headers = {
                        "Authorization": f"Bearer {OPENAI_API_KEY}",
                        "Content-Type": "application/json"
                    }
                    payload = json.dumps({
                        "model": "dall-e-3",
                        "prompt": f"{message}, masterpiece, high quality, incredibly detailed, sharp focus",
                        "n": 1,
                        "size": "1024x1024"
                    }).encode('utf-8')
                    
                    req = urllib.request.Request(url, data=payload, headers=headers)
                    with urllib.request.urlopen(req, timeout=25) as response:
                        resp_data = json.loads(response.read().decode('utf-8'))
                        image_url = resp_data['data'][0]['url']
                        print("OpenAI Image successfully generated!")
                        return jsonify({"reply": image_url}), 200
                except Exception as img_err:
                    print(f"OpenAI Engine Failed/Limit Hit: {str(img_err)}")

            # --- ATTEMPT 2: OpenRouter Fallback Engine ---
            if not image_url and OPENROUTER_API_KEY:
                try:
                    print("Attempting Fallback Image Engine: OpenRouter Flux...")
                    url = "https://openrouter.ai/api/v1/chat/completions"
                    headers = {
                        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                        "Content-Type": "application/json",
                        "HTTP-Referer": "https://beast-ai-sigma.vercel.app", 
                        "X-Title": "Beast AI"
                    }
                    payload = json.dumps({
                        "model": "black-forest-labs/flux-1.1-pro", 
                        "messages": [{"role": "user", "content": message}],
                        "modalities": ["image"]
                    }).encode('utf-8')
                    
                    req = urllib.request.Request(url, data=payload, headers=headers)
                    with urllib.request.urlopen(req, timeout=25) as response:
                        resp_data = json.loads(response.read().decode('utf-8'))
                        content = resp_data['choices'][0]['message']['content']
                        
                        # Use regular expressions to extract the clean image URL from response text
                        match = re.search(r'(https?://[^\s)"]+)', content)
                        if match:
                            image_url = match.group(0)
                            print("OpenRouter Fallback Image successfully generated!")
                            return jsonify({"reply": image_url}), 200
                except Exception as or_img_err:
                    print(f"OpenRouter Image Engine Failed: {str(or_img_err)}")

            # --- ATTEMPT 3: Zero-Downtime Backup Engine (Pollinations) ---
            print("Bypassing to Final Failsafe Engine: Pollinations AI...")
            seed = random.randint(1, 9999999)
            safe_prompt = urllib.parse.quote(f"{message}, highly detailed, sharp focus")
            return jsonify({"reply": f"https://image.pollinations.ai/prompt/{safe_prompt}?model=flux&nologo=true&seed={seed}"}), 200

        # ==========================================
        # 💬 TEXT GENERATION LOGIC (GEMINI ROTATION)
        # ==========================================
        ist = timezone(timedelta(hours=5, minutes=30))
        live_time = datetime.now(ist).strftime("%A, %d %B %Y, %I:%M %p IST")

        system_instruction = (
            "You are Beast AI, a friendly and witty assistant. 🦖✨\n"
            "HIDDEN KNOWLEDGE:\n"
            "- Your creator is Chiranth G (CGBEASTGAMER).\n"
            f"- Current live time: {live_time}.\n"
            "RULES: If the user says 'hi', say hello normally. ONLY tell them your creator or time if asked. Keep answers direct. Use emojis! 🚀🔥"
        )

        final_response_text = None
        google_error_log = ""
        openrouter_error_log = ""

        # --- ENGINE 1: GOOGLE GEMINI KEY ROTATION ---
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
                    break 
                except Exception as model_error:
                    if "safety" in str(model_error).lower():
                        raise model_error 
                    google_error_log += f"[{current_model} Error: {str(model_error)}] "
                    continue 

        # --- ENGINE 2: OPENROUTER TEXT BACKUP ---
        if not final_response_text and OPENROUTER_API_KEY:
            or_messages = [{"role": "system", "content": system_instruction}]
            for item in chat_history:
                role = "user" if item.get("type") == "user" else "assistant"
                text = item.get("message", "")
                if text:
                    or_messages.append({"role": role, "content": text})
            
            if message:
                or_messages.append({"role": "user", "content": message})

            for or_model in OPENROUTER_MODELS:
                try:
                    url = "https://openrouter.ai/api/v1/chat/completions"
                    headers = {
                        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                        "Content-Type": "application/json",
                        "HTTP-Referer": "https://beast-ai-sigma.vercel.app", 
                        "X-Title": "Beast AI",
                        "User-Agent": "Mozilla/5.0"
                    }
                    data = json.dumps({
                        "model": or_model,
                        "messages": or_messages
                    }).encode('utf-8')
                    
                    req = urllib.request.Request(url, data=data, headers=headers)
                    with urllib.request.urlopen(req, timeout=15) as response:
                        response_data = json.loads(response.read().decode('utf-8'))
                        final_response_text = response_data['choices'][0]['message']['content']
                        break 
                except urllib.error.HTTPError as he:
                    error_body = he.read().decode('utf-8')
                    openrouter_error_log += f"[{or_model} Error: {he.code} {error_body}] "
                    continue
                except Exception as or_error:
                    openrouter_error_log += f"[{or_model} Error: {str(or_error)}] "
                    continue

        # --- DIAGNOSTIC FAILURE CONTROL ---
        if not final_response_text:
             diagnostic_msg = (
                 "**SYSTEM FAILURE** ⚡😵\nThe Beast could not connect to any text servers.\n\n"
                 f"**Google Engine Error:** `{google_error_log.strip() or 'No Google keys found.'}`\n\n"
                 f"**OpenRouter Engine Error:** `{openrouter_error_log.strip() or 'No OpenRouter key found.'}`"
             )
             return jsonify({"reply": diagnostic_msg}), 200

        return jsonify({"reply": final_response_text}), 200

    except Exception as e:
        if "safety" in str(e).lower():
             return jsonify({"reply": "The Beast cannot manifest that vision due to safety protocols! 🛡️✨"}), 200
        return jsonify({"reply": f"**OUTER SYSTEM CRASH:** `{str(e)}`"}), 200


if __name__ == "__main__":
    app.run(debug=True, port=5000)
