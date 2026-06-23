from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
import os
import requests
import time

app = Flask(__name__)

# Configure upload folder
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'wav', 'mp3', 'ogg', 'm4a', 'flac', 'mp4', 'mpeg', 'mpga'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'file' not in request.files:
            return jsonify({'error': 'No file part'})
        
        file = request.files['file']
        api_key = '2bda6b3bb61d45dfb59776c90f658cf9'
        
        if file.filename == '':
            return jsonify({'error': 'No selected file'})
        
        if not api_key:
            return jsonify({'error': 'No API key provided'})
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            # Upload file to AssemblyAI
            upload_url = upload_file(filepath, api_key)
            if not upload_url:
                return jsonify({'error': 'Failed to upload file to AssemblyAI'})
            
            # Start transcription
            transcript_id = start_transcription(upload_url, api_key)
            if not transcript_id:
                return jsonify({'error': 'Failed to start transcription'})
            
            # Poll for transcription result
            transcript = get_transcription_result(transcript_id, api_key)
            if transcript:
                return jsonify({'transcript': transcript})
            else:
                return jsonify({'error': 'Transcription failed or timed out'})
    
    return render_template('index.html')

def upload_file(filepath, api_key):
    headers = {'authorization': api_key}
    with open(filepath, 'rb') as f:
        response = requests.post('https://api.assemblyai.com/v2/upload', headers=headers, data=f)
    if response.status_code == 200:
        return response.json()['upload_url']
    return None

def start_transcription(audio_url, api_key):
    headers = {
        "authorization": api_key,
        "content-type": "application/json"
        
    }
    json = {
        "audio_url": audio_url,
        "language_code": "pt",
        "punctuate" : "true",
        "format_text" : "true"
        
    }
    response = requests.post("https://api.assemblyai.com/v2/transcript", json=json, headers=headers)
    if response.status_code == 200:
        return response.json()['id']
    return None

def get_transcription_result(transcript_id, api_key):
    headers = {
        "authorization": api_key,
    }
    polling_endpoint = f"https://api.assemblyai.com/v2/transcript/{transcript_id}"
    
    while True:
        response = requests.get(polling_endpoint, headers=headers)
        if response.status_code == 200:
            transcription_result = response.json()
            if transcription_result['status'] == 'completed':
                return transcription_result['text']
            elif transcription_result['status'] == 'error':
                return None
        time.sleep(3)

if __name__ == '__main__':
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    app.run(host="192.168.15.7", debug=True)
