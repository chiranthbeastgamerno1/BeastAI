import json
import os
import random
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime
from zoneinfo import ZoneInfo

from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

GEMINI_MODELS = ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash"]


def now_ist():
    try:
        return datetime.now(ZoneInfo("Asia/Kolkata")).strftime("%A, %d %B %Y, %I:%M %p IST")
    except Exception:
        return datetime.utcnow().isoformat() + "Z"


def system_instruction(user_name=None):
    extra = f"- You are speaking to {user_name}. Address them naturally by name sometimes.\n" if user_name else ""
    return (
        "You are Beast AI, a friendly, witty and slightly playful assistant with a confident beast-like personality.\n"
        f"- Current live time: {now_ist()}.\n"
        f"{extra}"
        "- NEVER use italics (*text* or _text_). Always keep text completely normal unless using **bold**.\n"
        "- Use markdown formatting when helpful.\n"
        "RULES: If the user says 'hi', say hello normally. Keep answers direct, warm and helpful."
    )


def fetch_json(url, payload=None, headers=None, timeout=18):
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers or {})
    with urllib.request.urlopen(req, timeout=timeout) as res:
        text = res.read().decode("utf-8")
        return json.loads(text) if text else {}


def fetch_text(url, headers=None, timeout=18):
    req = urllib.request.Request(url, headers=headers or {})
    with urllib.request.urlopen(req, timeout=timeout) as res:
        return res.read().decode("utf-8")


def try_grok(system, history, message):
    key = os.environ.get("GROK_API_KEY")
    if not key:
        return None
    try:
        messages = [{"role": "system", "content": system}]
        for item in history[-10:]:
            if item.get("message"):
                messages.append({"role": "user" if item.get("type") == "user" else "assistant", "content": item.get("message")})
        if message:
            messages.append({"role": "user", "content": message})
        data = fetch_json(
            "https://api.x.ai/v1/chat/completions",
            {"model": "grok-3-fast", "messages": messages, "temperature": 0.7},
            {"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
            timeout=20,
        )
        return data.get("choices", [{}])[0].get("message", {}).get("content")
    except Exception:
        return None


def try_kira_flash(system, history, message):
    key = os.environ.get("KIRA_FLASH_API_KEY")
    if not key:
        return None
    try:
        messages = [{"role": "system", "content": system}]
        for item in history[-10:]:
            if item.get("message"):
                messages.append({"role": "user" if item.get("type") == "user" else "assistant", "content": item.get("message")})
        if message:
            messages.append({"role": "user", "content": message})
        data = fetch_json(
            "https://api.kira.ai/v1/chat/completions",
            {"model": "kira-3.5-flash", "messages": messages, "temperature": 0.7},
            {"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
            timeout=16,
        )
        return data.get("choices", [{}])[0].get("message", {}).get("content")
    except Exception:
        return None


def try_gemini(system, history, message, files):
    keys = [
        os.environ.get("GEMINI_API_KEY"),
        os.environ.get("GEMINI_API_KEY_1"),
        os.environ.get("GEMINI_API_KEY_2"),
    ]
    keys = [k for k in keys if k]
    if not keys:
        return None

    contents = []
    for item in history[-10:]:
        if item.get("message"):
            contents.append({
                "role": "user" if item.get("type") == "user" else "model",
                "parts": [{"text": item.get("message")}],
            })

    parts = []
    if message:
        parts.append({"text": message})
    for f in files:
        mime = f.get("mimeType", "image/jpeg")
        data = f.get("data")
        if data and (mime.startswith("image/") or mime == "application/pdf"):
            parts.append({"inline_data": {"mime_type": mime, "data": data}})
    if parts:
        contents.append({"role": "user", "parts": parts})

    keys = random.sample(keys, len(keys))
    for model in GEMINI_MODELS:
        for key in keys:
            try:
                data = fetch_json(
                    f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}",
                    {
                        "system_instruction": {"parts": [{"text": system}]},
                        "contents": contents,
                        "generationConfig": {"temperature": 0.8, "maxOutputTokens": 4096},
                    },
                    {"Content-Type": "application/json"},
                    timeout=20,
                )
                parts_out = data.get("candidates", [{}])[0].get("content", {}).get("parts", [])
                text = "".join(part.get("text", "") for part in parts_out).strip()
                if text:
                    return text
            except Exception:
                continue
    return None


def try_pollinations_text(system, history, message):
    convo = "\n".join(
        [f"{'User' if item.get('type') == 'user' else 'Beast AI'}: {item.get('message', '')}" for item in history[-6:] if item.get("message")]
    )
    prompt = f"{convo}\nUser: {message}\nBeast AI:" if convo else message or "Say hello as Beast AI."
    try:
        url = (
            "https://text.pollinations.ai/"
            + urllib.parse.quote(prompt)
            + "?system="
            + urllib.parse.quote(system)
        )
        text = fetch_text(url, {"User-Agent": "BeastAI"}, timeout=16).strip()
        return text or None
    except Exception:
        try:
            req = urllib.request.Request(
                "https://text.pollinations.ai/",
                data=json.dumps({
                    "messages": [
                        {"role": "system", "content": system},
                        {"role": "user", "content": prompt},
                    ],
                    "model": "openai",
                }).encode("utf-8"),
                headers={"Content-Type": "application/json"},
            )
            with urllib.request.urlopen(req, timeout=16) as res:
                text = res.read().decode("utf-8").strip()
                return text or None
        except Exception:
            return None


def generate_image(prompt):
    key = os.environ.get("KIRA_IMAGE_API_KEY")
    if key:
      try:
        data = fetch_json(
            "https://api.kira.ai/v1/images/generations",
            {"model": "kira-3.0-image", "prompt": prompt, "n": 1},
            {"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
            timeout=20,
        )
        url = data.get("data", [{}])[0].get("url")
        if url:
            return url
      except Exception:
        pass
    seed = random.randint(1, 999999)
    return f"https://image.pollinations.ai/prompt/{urllib.parse.quote(prompt)}?nologo=true&seed={seed}&width=1024&height=1024&enhance=true"


def generate_video(prompt, fast=False):
    model = "kira-3.0-video-flash" if fast else "kira-3.0-video"
    key = os.environ.get("KIRA_VIDEO_FLASH_API_KEY" if fast else "KIRA_VIDEO_API_KEY")
    if not key:
        return f"The Beast is missing the **{model}** key. Add `{ 'KIRA_VIDEO_FLASH_API_KEY' if fast else 'KIRA_VIDEO_API_KEY' }` to unleash moving pictures. Until then, my claws can only forge words and images."
    try:
        data = fetch_json(
            "https://api.kira.ai/v1/videos/generations",
            {"model": model, "prompt": prompt},
            {"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
            timeout=40,
        )
        return data.get("url") or data.get("data", [{}])[0].get("url") or "**Kira Video API Error:** the vault returned no footage."
    except urllib.error.HTTPError as e:
        return f"**Kira Video API Error:** `{e.read().decode('utf-8')}`"
    except Exception as e:
        return f"**System Intercept Error:** `{str(e)}`"


@app.route("/")
def home():
    return "Beast AI Core is Online (Vercel Serverless)! 🦖⚡"


@app.route("/api/chat", methods=["POST"])
def chat():
    try:
        body = request.get_json(silent=True) or {}
        message = str(body.get("message", ""))
        mode = str(body.get("mode", "chat"))
        speed = str(body.get("speed", "normal"))
        history = body.get("history", []) if isinstance(body.get("history", []), list) else []
        files = body.get("files", []) if isinstance(body.get("files", []), list) else []
        user_name = body.get("userName")

        if not message.strip() and not files:
            return jsonify({"reply": "The Beast hears only silence."}), 200

        if mode == "image":
            return jsonify({"reply": f"![Manifested Image]({generate_image(message or 'a majestic beast')})"}), 200

        if mode in ["video", "video-fast"]:
            return jsonify({"reply": generate_video(message, fast=(mode == "video-fast"))}), 200

        system = system_instruction(user_name)
        reply = None
        if speed == "pro":
            reply = try_grok(system, history, message) or try_gemini(system, history, message, files)
        elif speed == "fast":
            reply = try_kira_flash(system, history, message) or try_gemini(system, history, message, files)
        else:
            reply = try_gemini(system, history, message, files)

        if not reply:
            reply = try_pollinations_text(system, history, message) or "Beast AI core is currently recalibrating its sub-systems. Please fire your query again! ⚡"

        return jsonify({"reply": reply}), 200
    except Exception as e:
        return jsonify({"reply": f"**System Intercept Error:** `{str(e)}`"}), 200
