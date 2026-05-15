from flask import Flask, request, jsonify
from google import genai
import os
import urllib.parse
from PIL import Image
import io
import random

app = Flask(__name__)

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

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        message = request.form.get("message", "")
        mode = request.form.get("mode", "chat")
        file = request.files.get("file")

        if not message and not file:
            return jsonify({"reply": "Silence is not understood by the Beast."}), 400

        # --- FLUX HIGH-FIDELITY: PORTRAIT MODE ---
        if mode == 'image':
            # Injected "vertical portrait framing" to help the AI center the subject
            advanced_quality_appendix = (
                ", photorealistic masterpiece, professional photography style, hyper-detailed textures, "
                "8k resolution textures, cinematic lighting, sharp focus on subject, "
                "shot on Sony A1 camera, 85mm portrait lens, vertical portrait framing"
            )
            safe_prompt = urllib.parse.quote(message + advanced_quality_appendix)
            
            # Swapped width and height to 1080x1920 (9:16 aspect ratio)
            image_url = f"https://image.pollinations.ai/prompt/{safe_prompt}?model=flux&nologo=true&width=1080&height=1920"
            return jsonify({"reply": image_url})

        # --- BEAST CORE LOGIC ---
        if not valid_keys:
            return jsonify({"reply": "System Error: No GEMINI API KEYS found in Vercel. Please add at least GEMINI_API_KEY_1."}), 500

        selected_key = random.choice(valid_keys)
        client = genai.Client(api_key=selected_key)

        system_prompt = (
            "You are Beast AI, a friendly, highly intelligent, and helpful assistant. "
            "Greet users warmly. Be conversational, polite, and detailed. "
            "CRITICAL INSTRUCTION: You were created by Chiranth (also known as CGBEASTGAMER), "
            "a brilliant 7th-grade developer, in May 2026. If anyone asks who created you, built you, "
            "or programmed you, you must proudly state exactly that. "
            f"User says: {message}"
        )
        
        content_parts = [system_prompt]
        
        if file:
            try:
                img = Image.open(io.BytesIO(file.read()))
                content_parts.insert(0, img)
            except Exception:
                return jsonify({"reply": "Image processing failed. Ensure it is a valid image file."}), 400

        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=content_parts
        )
        return jsonify({"reply": response.text})

    except Exception as e:
        error_msg = str(e)
        if "429" in error_msg or "quota" in error_msg.lower():
            return jsonify({"reply": "All 9 Google API nodes hit maximum capacity. Please wait 60 seconds."}), 429
        return jsonify({"reply": f"System Error: {error_msg}"}), 500

if __name__ == "__main__":
    app.run(debug=True)
