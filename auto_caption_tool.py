from flask import Flask, request, jsonify
import os
import subprocess
import speech_recognition as sr
from indic_transliteration import sanscript
from indic_transliteration.sanscript import transliterate
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Allow cross-origin requests
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Function to extract audio from video
def extract_audio(video_path, audio_path):
    command = ["ffmpeg", "-i", video_path, "-q:a", "0", "-map", "a", audio_path, "-y"]
    subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

# Function to convert speech to text
def speech_to_text(audio_path):
    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_path) as source:
        audio = recognizer.record(source)
    try:
        text = recognizer.recognize_google(audio, language="hi-IN")
        return text
    except sr.UnknownValueError:
        return "Could not understand audio"
    except sr.RequestError:
        return "API request failed"

@app.route("/upload", methods=["POST"])
def upload_video():
    if "video" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    
    video = request.files["video"]
    video_path = os.path.join(UPLOAD_FOLDER, video.filename)
    audio_path = video_path.replace(".mp4", ".wav")
    
    video.save(video_path)
    extract_audio(video_path, audio_path)
    
    hindi_text = speech_to_text(audio_path)
    roman_text = transliterate(hindi_text, sanscript.DEVANAGARI, sanscript.ITRANS)
    
    return jsonify({"hindi_text": hindi_text, "roman_text": roman_text})

if __name__ == "__main__":
    app.run(debug=True)
