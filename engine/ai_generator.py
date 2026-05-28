import os
import sys
import json
import time
import urllib.request
import urllib.error
import argparse
import logging

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

def load_env():
    """Load environment variables from .env file if it exists."""
    env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")
    if os.path.exists(env_path):
        with open(env_path, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, val = line.split("=", 1)
                    os.environ[key.strip()] = val.strip().strip('"').strip("'")

def make_post_request(url, headers, data):
    """Utility to make a JSON POST request using urllib."""
    req = urllib.request.Request(
        url,
        data=json.dumps(data).encode("utf-8"),
        headers=headers,
        method="POST"
    )
    try:
        with urllib.request.urlopen(req) as res:
            return json.loads(res.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8")
        print(f"HTTP Error: {e.code} - {e.reason}")
        print(f"Response Body: {body}")
        raise e

def make_get_request(url, headers):
    """Utility to make a GET request using urllib."""
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req) as res:
            return json.loads(res.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8")
        print(f"HTTP Error: {e.code} - {e.reason}")
        print(f"Response Body: {body}")
        raise e

def download_file(url, output_path):
    """Download a file from URL to output_path."""
    print(f"Downloading final asset from {url}...")
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response, open(output_path, "wb") as out_file:
            out_file.write(response.read())
        print(f"Asset successfully saved to: {output_path}")
        return True
    except Exception as e:
        print(f"Failed to download asset: {e}")
        return False

def _validate_token(token, name):
    """Validate that a non-empty API token is set."""
    if not token or not token.strip():
        logger.error(f"{name} is not set. Add it to your .env file.")
        return False
    if len(token.strip()) < 10:
        logger.error(f"{name} is too short (< 10 chars) — check your .env file.")
        return False
    return True


def generate_replicate(prompt, asset_type, output_path, model=None):
    """Generate image or video using Replicate API."""
    token = os.getenv("REPLICATE_API_TOKEN")
    if not _validate_token(token, "REPLICATE_API_TOKEN"):
        return False

    headers = {
        "Authorization": f"Token {token}",
        "Content-Type": "application/json"
    }

    # Set default models if not provided
    if asset_type == "video":
        # Using tencent/hunyuan-video or stability-ai/stable-video-diffusion
        model_url = "https://api.replicate.com/v1/models/tencent/hunyuan-video/predictions"
        # Or stability-ai/stable-video-diffusion: "https://api.replicate.com/v1/models/stability-ai/stable-video-diffusion/predictions"
        data = {
            "input": {
                "prompt": prompt,
                "video_size": "544x960", # 9:16 aspect ratio roughly
                "fps": 30,
                "num_frames": 61, # ~2 seconds
                "infer_steps": 30
            }
        }
    else:
        # Default image model is Flux Schnell (fast, high quality)
        model_url = "https://api.replicate.com/v1/models/black-forest-labs/flux-schnell/predictions"
        data = {
            "input": {
                "prompt": prompt,
                "aspect_ratio": "1:1", # Default to square
                "num_outputs": 1,
                "output_format": "webp"
            }
        }

    print(f"Starting Replicate API prediction for model: {model_url}...")
    try:
        prediction = make_post_request(model_url, headers, data)
        pred_id = prediction["id"]
        status_url = f"https://api.replicate.com/v1/predictions/{pred_id}"
        
        print(f"Prediction created (ID: {pred_id}). Polling status...")
        while True:
            status_data = make_get_request(status_url, headers)
            status = status_data["status"]
            print(f"Current status: {status}")
            
            if status == "succeeded":
                output = status_data["output"]
                # output can be a string URL, or a list containing the URL
                url = output[0] if isinstance(output, list) else output
                if not url:
                    print("Error: Replicate completed but returned no output URL.")
                    return False
                return download_file(url, output_path)
            elif status in ["failed", "canceled"]:
                print(f"Replicate generation failed/canceled. Details: {status_data.get('error')}")
                return False
                
            time.sleep(3)
    except Exception as e:
        print(f"Replicate request failed: {e}")
        return False

def generate_openai(prompt, asset_type, output_path):
    """Generate image using OpenAI DALL-E 3 (OpenAI does not have a public text-to-video API yet)."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not _validate_token(api_key, "OPENAI_API_KEY"):
        return False

    if asset_type == "video":
        print("Error: OpenAI API currently only supports image generation. Please use Replicate for video generation.")
        return False

    url = "https://api.openai.com/v1/images/generations"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "dall-e-3",
        "prompt": prompt,
        "n": 1,
        "size": "1024x1024" # Default to square
    }

    print("Requesting OpenAI DALL-E 3 image generation...")
    try:
        res_data = make_post_request(url, headers, data)
        img_url = res_data["data"][0]["url"]
        return download_file(img_url, output_path)
    except Exception as e:
        print(f"OpenAI request failed: {e}")
        return False

def generate_huggingface(prompt, asset_type, output_path):
    """Generate image using Hugging Face Inference API (Free Flux Schnell)."""
    token = os.getenv("HF_API_TOKEN")
    if not _validate_token(token, "HF_API_TOKEN"):
        return False

    if asset_type == "video":
        print("Error: Hugging Face Inference API currently only supports image generation. Please use Replicate for video generation.")
        return False

    # Default to Flux Schnell, which is fast and free
    model_id = "black-forest-labs/FLUX.1-schnell"
    url = f"https://router.huggingface.co/hf-inference/models/{model_id}"
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    data = {
        "inputs": prompt
    }

    print(f"Requesting Hugging Face Image Generation ({model_id})...")
    try:
        req = urllib.request.Request(
            url,
            data=json.dumps(data).encode("utf-8"),
            headers=headers,
            method="POST"
        )
        with urllib.request.urlopen(req) as response:
            content = response.read()
            
        with open(output_path, "wb") as out_file:
            out_file.write(content)
            
        print(f"Image successfully generated and saved to: {output_path}")
        return True
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8")
        print(f"HTTP Error: {e.code} - {e.reason}")
        print(f"Response Body: {body}")
        return False
    except Exception as e:
        print(f"Hugging Face request failed: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="AI Image & Video Generator for Social Media Content")
    parser.add_argument("--prompt", required=True, help="AI prompt for generating the image or video")
    parser.add_argument("--type", choices=["image", "video"], default="image", help="Type of asset to generate")
    parser.add_argument("--provider", choices=["replicate", "openai", "huggingface"], default="replicate", help="API Provider")
    parser.add_argument("--output", required=True, help="File path where the generated asset should be saved")
    
    args = parser.parse_args()
    
    load_env()
    
    # Ensure parent output directory exists
    out_dir = os.path.dirname(os.path.abspath(args.output))
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)

    success = False
    if args.provider == "replicate":
        success = generate_replicate(args.prompt, args.type, args.output)
    elif args.provider == "openai":
        success = generate_openai(args.prompt, args.type, args.output)
    elif args.provider == "huggingface":
        success = generate_huggingface(args.prompt, args.type, args.output)
        
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()
