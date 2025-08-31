# app.py
# This is the Python backend for the AI Asset Generator.
# It uses the Flask framework to create a simple API endpoint.
# The backend receives a user's prompt, enhances it, and then
# calls the image generation API.

from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import requests
import os
import spacy

# Load the spaCy English model
# python -m spacy download en_core_web_sm
nlp = spacy.load("en_core_web_sm")

app = Flask(__name__)
# Enable CORS for the front end to communicate with the backend
CORS(app)

# A dictionary to "remember" previous outputs for each user.
user_session_state = {}

def get_enhanced_prompt(user_id, prompt):
    """
    Analyzes the previous response and enhances the new prompt
    with extracted keywords.
    """
    enhanced_prompt = prompt
    
    if user_id in user_session_state and user_session_state[user_id].get("last_response_text"):
        last_text = user_session_state[user_id]["last_response_text"]
        
        # Use spaCy to process the text
        doc = nlp(last_text)
        
        # Extract nouns and adjectives as potential keywords
        keywords = [token.text for token in doc if token.pos_ in ["NOUN", "ADJ"] and len(token.text) > 2]
        
        if keywords:
            # Add the extracted keywords to the new prompt
            enhanced_prompt += f" with these keywords from previous image: {', '.join(keywords)}"

    print(f"Original Prompt: {prompt}")
    print(f"Enhanced Prompt: {enhanced_prompt}")

    return enhanced_prompt

@app.route('/generate-image', methods=['POST'])
def generate_image():
    """
    API endpoint to handle image generation requests.
    """
    data = request.json
    user_prompt = data.get('prompt')
    user_id = data.get('userId', 'anonymous')

    if not user_prompt:
        return jsonify({"error": "Prompt is required."}), 400

    # Get the enhanced prompt
    final_prompt = get_enhanced_prompt(user_id, user_prompt)
    
    try:
        api_key = os.getenv("GEMINI_API_KEY", "")
        api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-preview-image-generation:generateContent?key={api_key}"
        
        payload = {
            "contents": [
                {"role": "user", "parts": [{"text": final_prompt}]}
            ],
            "generationConfig": {
                "responseModalities": ["IMAGE", "TEXT"]
            }
        }

        response = requests.post(api_url, json=payload, headers={'Content-Type': 'application/json'})
        response.raise_for_status()
        
        result = response.json()
        
        if result.get("candidates") and result["candidates"][0].get("content") and result["candidates"][0]["content"].get("parts"):
            text_part = None
            image_data = None
            
            # Find the image and text parts in the response
            for part in result["candidates"][0]["content"]["parts"]:
                if "inlineData" in part:
                    image_data = part["inlineData"].get("data")
                elif "text" in part:
                    text_part = part["text"]

            # Store the text for the next prompt
            if text_part:
                if user_id not in user_session_state:
                    user_session_state[user_id] = {}
                user_session_state[user_id]["last_response_text"] = text_part
            
            if image_data:
                return jsonify({"image": image_data})
        
        return jsonify({"error": "Failed to retrieve image data from API."}), 500

    except requests.exceptions.RequestException as e:
        print(f"API Error: {e}")
        return jsonify({"error": "An error occurred during image generation."}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
