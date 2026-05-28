"""
Flask backend server — enables end-to-end AI generation from the browser UI.

Endpoints:
  GET  /api/status          — health check + provider availability
  POST /api/generate-image  — generate AI image (HuggingFace)
  POST /api/render-post     — render a post PNG via create_post.py
  GET  /api/preview/<path>  — serve generated assets

Usage:
  pip install flask flask-cors
  python3 server.py
"""

import os
import sys
import json
import subprocess
import tempfile
import threading
from pathlib import Path

from flask import Flask, request, jsonify, send_file, after_this_request
from flask_cors import CORS

# ── App setup ──────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).parent
ENGINE_DIR = BASE_DIR / "engine"
ENV_FILE = BASE_DIR / ".env"

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Upload / output directories
AI_ASSETS_DIR = BASE_DIR / "ai_assets"
POSTS_DIR = BASE_DIR / "posts"
AI_ASSETS_DIR.mkdir(exist_ok=True)
POSTS_DIR.mkdir(exist_ok=True)

# ── Helpers ────────────────────────────────────────────────────────────

def load_env():
    """Load .env into os.environ."""
    if ENV_FILE.exists():
        for line in ENV_FILE.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


def run_engine(script, args: list[str], timeout: int = 120) -> dict:
    """Run an engine script and return {success, output, error}."""
    cmd = [sys.executable, str(ENGINE_DIR / script)] + args
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=timeout,
            cwd=str(BASE_DIR),
        )
        return {
            "success": result.returncode == 0,
            "output": result.stdout.strip(),
            "error": result.stderr.strip(),
        }
    except subprocess.TimeoutExpired:
        return {"success": False, "output": "", "error": f"Timed out after {timeout}s"}
    except Exception as exc:
        return {"success": False, "output": "", "error": str(exc)}


# ── Routes ─────────────────────────────────────────────────────────────

@app.route("/api/status")
def status():
    load_env()
    return jsonify({
        "status": "ok",
        "providers": {
            "huggingface": bool(os.getenv("HF_API_TOKEN")),
            "replicate": bool(os.getenv("REPLICATE_API_TOKEN")),
            "openai": bool(os.getenv("OPENAI_API_KEY")),
        },
        "ffmpeg": _check_ffmpeg(),
    })


def _check_ffmpeg():
    try:
        r = subprocess.run(["ffmpeg", "-version"], capture_output=True, text=True, timeout=5)
        return r.returncode == 0
    except Exception:
        return False


@app.route("/api/generate-image", methods=["POST"])
def generate_image():
    """Generate an AI image and return the file URL."""
    data = request.get_json(force=True)
    prompt = data.get("prompt", "").strip()
    provider = data.get("provider", "huggingface")
    aspect_ratio = data.get("aspect_ratio", "1:1")

    if not prompt:
        return jsonify({"error": "Prompt is required"}), 400

    load_env()

    # Choose model / aspect mapping per provider
    ext = "png"
    filename = f"generated_{int(time_ns())}.{ext}"
    output_path = str(AI_ASSETS_DIR / filename)

    if provider == "huggingface":
        args = ["--prompt", prompt, "--type", "image", "--provider", "huggingface", "--output", output_path]
    elif provider == "replicate":
        args = ["--prompt", prompt, "--type", "image", "--provider", "replicate", "--output", output_path]
    elif provider == "openai":
        args = ["--prompt", prompt, "--type", "image", "--provider", "openai", "--output", output_path]
    else:
        return jsonify({"error": f"Unknown provider: {provider}"}), 400

    # Use threading for async feel — but for simplicity run synchronously
    # with generous timeout
    result = run_engine("ai_generator.py", args, timeout=180)

    if not result["success"]:
        return jsonify({
            "error": "Generation failed",
            "detail": result["error"] or result["output"],
        }), 502

    return jsonify({
        "success": True,
        "url": f"/api/preview/ai_assets/{filename}",
        "filename": filename,
    })


@app.route("/api/render-post", methods=["POST"])
def render_post():
    """Render a social media post PNG from the given parameters."""
    data = request.get_json(force=True)

    filename = f"post_{int(time_ns())}.png"
    output_path = str(POSTS_DIR / filename)

    args = [
        "--template", data.get("template", "quote"),
        "--ratio", data.get("ratio", "1:1"),
        "--title", data.get("title", ""),
        "--body", data.get("body", ""),
        "--watermark", data.get("watermark", ""),
        "--bg_start", data.get("bg_start", "#1a1c29"),
        "--bg_end", data.get("bg_end", "#0c0d14"),
        "--bg_overlay", str(data.get("bg_overlay", 30)),
        "--card_color", data.get("card_color", "#ffffff"),
        "--card_opacity", str(data.get("card_opacity", 15)),
        "--output", output_path,
    ]

    if data.get("no_card"):
        args.append("--no_card")

    if data.get("bg_image"):
        args += ["--bg_image", data["bg_image"]]

    if data.get("offset_x"):
        args += ["--offset_x", str(data["offset_x"])]
    if data.get("offset_y"):
        args += ["--offset_y", str(data["offset_y"])]

    result = run_engine("create_post.py", args, timeout=60)

    if not result["success"]:
        return jsonify({
            "error": "Render failed",
            "detail": result["error"] or result["output"],
        }), 502

    return jsonify({
        "success": True,
        "url": f"/api/preview/posts/{filename}",
        "filename": filename,
    })


@app.route("/api/preview/<path:filepath>")
def preview(filepath):
    """Serve generated asset files."""
    safe_path = BASE_DIR / filepath
    # Prevent directory traversal
    try:
        safe_path.resolve().relative_to(BASE_DIR.resolve())
    except ValueError:
        return jsonify({"error": "Forbidden"}), 403

    if not safe_path.exists():
        return jsonify({"error": "Not found"}), 404

    return send_file(str(safe_path))


# ── Misc ───────────────────────────────────────────────────────────────

def time_ns():
    import time
    return int(time.time() * 1000)


# ── Main ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    load_env()
    print("AuraForge server → http://127.0.0.1:5000")
    app.run(debug=True, port=5000)
