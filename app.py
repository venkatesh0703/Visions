from flask import Flask, request, send_file, jsonify, render_template
import os
import requests
from PIL import Image
from io import BytesIO
import re
import random

app = Flask(__name__)

# Directory for storing uploaded/generated files
UPLOAD_FOLDER = 'generated_image_video'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure the folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# API Keys for different services
PIXABAY_API_KEY = "47951810-c4682d024220e08ba9848ab4c"  # Replace with your Pixabay API key
UNSPLASH_API_KEY = "d_7ZNBZaK13UAWS7yvKznpyBJFVj0SJvGwGvhlP8EJI"  # Replace with your Unsplash API key
PEXELS_API_KEY = "47951810-c4682d024220e08ba9848ab4c"  # Replace with your Pexels API key

# Helper function to sanitize prompt for filenames
def sanitize_filename(prompt):
    return re.sub(r'[^a-zA-Z0-9_-]', '_', prompt)  # Replaces any non-alphanumeric characters with underscores

# Function to fetch image from Unsplash API (new function)
def fetch_unsplash_image(query):
    url = f"https://api.unsplash.com/photos/random?query={query}&client_id={UNSPLASH_API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if data:
            return data[0]['urls']['regular']
    return None

# Function to fetch image from Pixabay API (with caching)
def fetch_image_from_pixabay(prompt):
    sanitized_prompt = sanitize_filename(prompt)
    img_path = os.path.join(UPLOAD_FOLDER, f"{sanitized_prompt}_pixabay_image.png")
    
    # Check if the image already exists
    if os.path.exists(img_path):
        return img_path

    url = f"https://pixabay.com/api/?key={PIXABAY_API_KEY}&q={prompt}&image_type=photo&orientation=horizontal&per_page=3"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if data['hits']:
            image_url = data['hits'][0]['largeImageURL']  # Fetching a larger image
            image_response = requests.get(image_url)
            img = Image.open(BytesIO(image_response.content))
            img.save(img_path)
            return img_path
        else:
            return None
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return None

# Function to fetch image from Unsplash API (with caching)
def fetch_image_from_unsplash(prompt):
    sanitized_prompt = sanitize_filename(prompt)
    img_path = os.path.join(UPLOAD_FOLDER, f"{sanitized_prompt}_unsplash_image.png")
    
    # Check if the image already exists
    if os.path.exists(img_path):
        return img_path

    image_url = fetch_unsplash_image(prompt)
    if image_url:
        image_response = requests.get(image_url)
        img = Image.open(BytesIO(image_response.content))
        img.save(img_path)
        return img_path
    else:
        return None

# Function to fetch video from Pexels API (with caching)
def fetch_video_from_pexels(prompt):
    sanitized_prompt = sanitize_filename(prompt)
    video_path = os.path.join(UPLOAD_FOLDER, f"{sanitized_prompt}_pexels_video.mp4")

    # Check if the video already exists
    if os.path.exists(video_path):
        return video_path

    url = f"https://api.pexels.com/videos/search?query={prompt}&per_page=1"
    headers = {"Authorization": PEXELS_API_KEY}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        if data['videos']:
            video_url = data['videos'][0]['video_files'][0]['link']
            video_response = requests.get(video_url)
            with open(video_path, 'wb') as video_file:
                video_file.write(video_response.content)
            return video_path
        else:
            return None
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return None

# Function to fetch video from Pixabay API (with caching)
def fetch_video_from_pixabay(prompt):
    sanitized_prompt = sanitize_filename(prompt)
    video_path = os.path.join(UPLOAD_FOLDER, f"{sanitized_prompt}_pixabay_video.mp4")

    # Check if the video already exists
    if os.path.exists(video_path):
        return video_path

    url = f"https://pixabay.com/api/videos/?key={PIXABAY_API_KEY}&q={prompt}&video_type=film&per_page=3"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if data['hits']:
            # Attempt to get a high-resolution video, fallback to medium if high is not found
            video_resolutions = ['high', 'medium', 'low']
            video_url = None

            for resolution in video_resolutions:
                if resolution in data['hits'][0]['videos']:
                    video_url = data['hits'][0]['videos'][resolution]['url']
                    break  # Exit the loop once we find a valid video URL
            
            if video_url:
                video_response = requests.get(video_url)
                with open(video_path, 'wb') as video_file:
                    video_file.write(video_response.content)
                return video_path
            else:
                print("No video resolutions available.")
                return None
        else:
            return None
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return None

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/generate-image', methods=['POST'])
def generate_image_route():
    prompt = request.json.get('prompt', '')

    if not prompt:
        return jsonify({"error": "Prompt is required"}), 400

    # Randomly choose between the APIs for image generation
    api_choice = random.choice(['pixabay', 'unsplash'])

    if api_choice == 'pixabay':
        generated_image = fetch_image_from_pixabay(prompt)
    elif api_choice == 'unsplash':
        generated_image = fetch_image_from_unsplash(prompt)

    if generated_image:
        return jsonify({"image_path": f"/generated-image/{os.path.basename(generated_image)}", "api_used": api_choice}), 200
    else:
        return jsonify({"error": "Failed to fetch image"}), 500

@app.route('/generate-video', methods=['POST'])
def generate_video_route():
    prompt = request.json.get('prompt', '')

    if not prompt:
        return jsonify({"error": "Prompt is required"}), 400

    # Randomly choose between the APIs for video generation
    api_choice = random.choice(['pixabay', 'pexels'])

    if api_choice == 'pixabay':
        generated_video = fetch_video_from_pixabay(prompt)
    elif api_choice == 'pexels':
        generated_video = fetch_video_from_pexels(prompt)

    if generated_video:
        return jsonify({"video_path": f"/generated-video/{os.path.basename(generated_video)}", "api_used": api_choice}), 200
    else:
        return jsonify({"error": "Failed to fetch video"}), 500

@app.route('/generated-image/<filename>', methods=['GET'])
def download_image(filename):
    try:
        return send_file(os.path.join(UPLOAD_FOLDER, filename))
    except FileNotFoundError:
        return jsonify({"error": "File not found"}), 404

@app.route('/generated-video/<filename>', methods=['GET'])
def download_video(filename):
    try:
        return send_file(os.path.join(UPLOAD_FOLDER, filename))
    except FileNotFoundError:
        return jsonify({"error": "File not found"}), 404

if __name__ == '__main__':
    app.run(debug=True)
