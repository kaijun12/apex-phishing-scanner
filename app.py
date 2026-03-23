import os
import time
import easyocr
import requests
from flask import Flask, request, jsonify, render_template, send_from_directory
from gtts import gTTS
from database import init_db, save_scan                     

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
AUDIO_FOLDER = 'audio'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(AUDIO_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['AUDIO_FOLDER'] = AUDIO_FOLDER

init_db()                                                

reader = easyocr.Reader(['en'])

OLLAMA_URL = 'http://localhost:11434/api/generate'
OLLAMA_MODEL = 'llama3.2'


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def extract_text(filepath):
    results = reader.readtext(filepath)
    extracted = [text for (_, text, _) in results]
    return '\n'.join(extracted)


def build_prompt(extracted_text):
    return f"""
You are a cybersecurity expert specializing in phishing email detection.

Analyze the following email text and assess whether it is a phishing attempt.

EMAIL TEXT:
{extracted_text}

Respond in this exact format:
RISK LEVEL: <Low / Medium / High>
RISK SCORE: <a number from 0 to 100>
EXPLANATION: <2-3 sentences explaining your assessment in plain English>
RED FLAGS:
- <red flag 1>
- <red flag 2>
- <red flag 3 if applicable>

If the text does not appear to be an email, say so and still give your best assessment.
"""


def analyze_text(extracted_text):
    prompt = build_prompt(extracted_text)
    response = requests.post(OLLAMA_URL, json={
        'model': OLLAMA_MODEL,
        'prompt': prompt,
        'stream': False
    })
    if response.status_code != 200:
        return None, f'Ollama error: {response.status_code}'
    result = response.json()
    return result['response'], None


def extract_explanation(analysis):
    for line in analysis.splitlines():
        if line.startswith('EXPLANATION:'):
            return line.replace('EXPLANATION:', '').strip()
    return analysis


def generate_audio(analysis):
    explanation = extract_explanation(analysis)
    filename = f"audio_{int(time.time())}.mp3"
    filepath = os.path.join(AUDIO_FOLDER, filename)
    tts = gTTS(text=explanation, lang='en')
    tts.save(filepath)
    return filename


def parse_analysis(analysis):                               
    """Parse the raw analysis string into structured fields."""
    parsed = {
        'risk_level': 'Unknown',
        'risk_score': 0,
        'explanation': '',
        'red_flags': []
    }

    lines = analysis.splitlines()
    in_red_flags = False

    for line in lines:
        line = line.strip()
        if line.startswith('RISK LEVEL:'):
            parsed['risk_level'] = line.replace('RISK LEVEL:', '').strip()
        elif line.startswith('RISK SCORE:'):
            score_str = line.replace('RISK SCORE:', '').strip()
            try:
                parsed['risk_score'] = int(score_str)
            except ValueError:
                parsed['risk_score'] = 0
        elif line.startswith('EXPLANATION:'):
            parsed['explanation'] = line.replace('EXPLANATION:', '').strip()
        elif line.startswith('RED FLAGS:'):
            in_red_flags = True
        elif in_red_flags and line.startswith('-'):
            parsed['red_flags'].append(line[1:].strip())

    return parsed


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/audio/<filename>')
def serve_audio(filename):
    return send_from_directory(app.config['AUDIO_FOLDER'], filename)


@app.route('/scan', methods=['POST'])
def scan():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    if not allowed_file(file.filename):
        return jsonify({'error': 'File type not allowed'}), 400

    filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(filepath)

    # Step 3: OCR
    extracted_text = extract_text(filepath)

    # Step 4: LLM Analysis
    analysis, error = analyze_text(extracted_text)
    if error:
        return jsonify({'error': error}), 500

    # Step 5: TTS
    audio_filename = generate_audio(analysis)

    # Step 6: Save to database                              
    save_scan(file.filename, extracted_text, analysis, audio_filename)  

    # Step 6: Parse analysis    
    parsed = parse_analysis(analysis)                     

    return jsonify({
        'message': 'Scan complete',
        'filename': file.filename,
        'extracted_text': extracted_text,
        'parsed': parsed,                                  
        'audio_url': f'/audio/{audio_filename}'
    })


if __name__ == '__main__':
    app.run(debug=True)