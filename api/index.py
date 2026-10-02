import os
import json
from flask import Flask, request, jsonify
from flask_cors import CORS
from openai import OpenAI
import google.generativeai as genai

app = Flask(__name__)
# Allows your Vercel frontend to communicate with your Render backend
CORS(app) 

# ==========================================
# 1. INITIALIZE API CLIENTS
# ==========================================

# Grok (xAI) Client
grok_client = OpenAI(
    api_key=os.environ.get("GROK_API_KEY", ""),
    base_url="https://api.x.ai/v1"
)

# Kira AI Client (Base setup, keys swap dynamically per request)
# Note: Replace 'https://api.kira.ai/v1' with Kira's actual endpoint url
kira_client = OpenAI(
    api_key="placeholder", 
    base_url="https://api.kira.ai/v1" 
)

# Gemini Client
genai.configure(api_key=os.environ.get("GEMINI_API_KEY", ""))


@app.route('/api/chat', methods=['POST'])
def chat_api():
    # ==========================================
    # 2. CAPTURE DATA FROM FRONTEND HTML
    # ==========================================
    message = request.form.get('message', '')
    mode = request.form.get('mode', 'chat')
    speed = request.form.get('speed', 'normal')
    
    # Extract file attachments if any exist
    # files = request.files.getlist('files')
    
    try:
        # ==========================================
        # 3. ROUTE: IMAGE GENERATION
        # ==========================================
        if mode == 'image':
            kira_client.api_key = os.environ.get("KIRA_IMAGE_API_KEY")
            response = kira_client.images.generate(
                model="kira-3.0-image",
                prompt=message,
                n=1
            )
            image_url = response.data[0].url
            # Returns markdown image format. The UI will render this instantly.
            return jsonify({"reply": f"![Generated Image]({image_url})"})

        # ==========================================
        # 4. ROUTE: VIDEO GENERATION
        # ==========================================
        elif mode == 'video' or mode == 'video-fast':
            # Assign correct model name and key based on if user selected "Fast"
            if mode == 'video':
                video_model = "kira-3.0-video"
                kira_client.api_key = os.environ.get("KIRA_VIDEO_API_KEY")
            else:
                video_model = "kira-3.0-video-flash"
                kira_client.api_key = os.environ.get("KIRA_VIDEO_FLASH_API_KEY")
            
            # OpenAI compatible media generation call
            # (Syntax depends on Kira's specific video endpoint documentation)
            response = kira_client.post("/videos/generations", json={
                "prompt": message, 
                "model": video_model
            })
            
            video_url = response.json().get('url', '')
            # Returns the raw .mp4 link. The custom HTML parser we wrote will turn this into a player.
            return jsonify({"reply": f"{video_url}"})

        # ==========================================
        # 5. ROUTE: TEXT & CODING CHAT
        # ==========================================
        else:
            if speed == 'pro':
                # GROK 4.6 (Pro/Coding)
                response = grok_client.chat.completions.create(
                    model="grok-beta", # Update to specific 4.6 model ID
                    messages=[{"role": "user", "content": message}]
                )
                return jsonify({"reply": response.choices[0].message.content})
            
            elif speed == 'fast':
                # KIRA 3.5 FLASH (Fast Text)
                kira_client.api_key = os.environ.get("KIRA_FLASH_API_KEY")
                response = kira_client.chat.completions.create(
                    model="kira-3.5-flash",
                    messages=[{"role": "user", "content": message}]
                )
                return jsonify({"reply": response.choices[0].message.content})
            
            else:
                # GEMINI (Normal / Daily Text)
                model = genai.GenerativeModel('gemini-1.5-flash')
                response = model.generate_content(message)
                return jsonify({"reply": response.text})

    except Exception as e:
        print(f"Server Error: {str(e)}")
        return jsonify({"reply": f"**System Warning:** The Beast encountered an error processing this request.\n\n`{str(e)}`"}), 500

if __name__ == '__main__':
    # Render binds to the PORT environment variable
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
