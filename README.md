# apex-phishing-scanner

A locally-run, privacy-first AI pipeline that analyses screenshots of suspicious emails and explains why they might be phishing — in plain English and audio.

## Tech Stack
 
| Layer | Tool |
|---|---|
| Web framework | Flask (Python) |
| OCR | EasyOCR |
| LLM | Ollama — Llama 3.2 (local) |
| Text-to-Speech | gTTS |
| Database | SQLite |
| Frontend | HTML5 + Vanilla JS |
 
---
 
## Prerequisites

- Python 3.9+
- [Ollama](https://ollama.com/download) installed on your machine
- The Llama 3.2 model pulled locally
 
---
 
## Installation
 
### 1. Clone the repository
 
```bash
git clone https://github.com/kaijun12/apex-phishing-scanner.git
cd apex-phishing-scanner
```
 
### 2. Create and activate a virtual environment
 
```bash
# Mac / Linux
python -m venv venv
source venv/bin/activate
 
# Windows
python -m venv venv
venv\Scripts\activate
```
 
### 3. Install Python dependencies
 
```bash
pip install -r requirements.txt
```
 
### 4. Install Ollama and pull the model
 
```bash
# Mac / Linux
curl -fsSL https://ollama.com/install.sh | sh
 
# Windows — download from https://ollama.com/download
```
 
Then pull the model:
 
```bash
ollama pull llama3.2
```
 
---
 
## Running the app

**Terminal 1 — Start Ollama:**
```bash
ollama serve
```
 
**Terminal 2 — Start Flask (with venv active):**
```bash
python app.py
```
 
Open your browser and go to:
```
http://localhost:5000
```
 
---
 
## How to use
 
1. Click the upload zone or drag and drop a screenshot of a suspicious email
2. Click **Analyse**
3. Wait 15–30 seconds while the pipeline runs
4. Read the risk score, explanation, and red flags
5. Click play on the audio player to hear the explanation spoken aloud
 
---
 
## Project structure
 
```
apex-phishing-scanner/
│
├── app.py              # Flask backend — orchestrates the full pipeline
├── database.py         # SQLite logic — saves scan records
├── requirements.txt    # Python dependencies
│
├── templates/
│   └── index.html      # Frontend UI
│
├── uploads/            # Saved image uploads (auto-created)
└── audio/              # Generated TTS audio files (auto-created)
```
 
---
