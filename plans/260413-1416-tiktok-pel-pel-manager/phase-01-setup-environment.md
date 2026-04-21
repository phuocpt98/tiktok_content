---
phase: 1
title: "Setup Environment"
status: pending
effort: 3h
priority: P1
---

# Phase 1: Setup Environment

## Context Links
- [Gemini API Quickstart](https://ai.google.dev/gemini-api/docs/quickstart)
- [FFmpeg Download](https://ffmpeg.org/download.html)
- [Python google-genai SDK](https://pypi.org/project/google-genai/)

## Overview
Set up the Python project, install dependencies, configure Gemini API, install FFmpeg, and establish project structure.

## Requirements

### Functional
- Python virtual environment with all dependencies
- Gemini API key configured and tested
- FFmpeg installed and accessible from PATH
- Project folder structure created

### Non-Functional
- Works on Windows 11 local machine
- No Docker or cloud services needed
- Single command to activate environment

## Project Structure
```
pel-pel/
├── .env                    # API keys (gitignored)
├── .gitignore
├── requirements.txt
├── README.md
├── src/
│   ├── __init__.py
│   ├── config.py           # Settings, paths, API config
│   ├── cli.py              # CLI entry point
│   ├── assets/
│   │   ├── __init__.py
│   │   ├── manager.py      # Asset CRUD + search
│   │   └── models.py       # SQLite models
│   ├── content/
│   │   ├── __init__.py
│   │   ├── idea_refiner.py # Idea -> script -> shot list
│   │   ├── image_gen.py    # Gemini image generation
│   │   ├── tts_gen.py      # Gemini TTS generation
│   │   ├── video_gen.py    # Gemini Veo generation
│   │   └── text_gen.py     # Script/caption generation
│   ├── video/
│   │   ├── __init__.py
│   │   └── assembler.py    # FFmpeg video assembly
│   └── publish/
│       ├── __init__.py
│       └── reviewer.py     # Review queue management
├── data/
│   ├── assets.db           # SQLite database
│   ├── images/             # Generated images
│   ├── audio/              # Generated TTS audio
│   ├── video/              # Generated video clips
│   ├── output/             # Final assembled videos
│   └── temp/               # Working directory
└── tests/
    └── ...
```

## Implementation Steps

### 1. Install system dependencies
```bash
# Install Python 3.11+ from python.org (if not installed)
python --version

# Install FFmpeg -- download from https://www.gyan.dev/ffmpeg/builds/
# Extract to C:\ffmpeg, add C:\ffmpeg\bin to PATH
ffmpeg -version
```

### 2. Initialize Python project
```bash
mkdir pel-pel && cd pel-pel
python -m venv .venv
.venv\Scripts\activate
```

### 3. Create requirements.txt
```
google-genai>=1.0.0
python-dotenv>=1.0.0
ffmpeg-python>=0.2.0
Pillow>=10.0.0
click>=8.0.0
rich>=13.0.0
pydantic>=2.0.0
```

### 4. Configure environment
```bash
pip install -r requirements.txt
```

Create `.env`:
```
GEMINI_API_KEY=your_key_here
```

### 5. Create config.py
- Load .env variables
- Define paths (data dirs, output dirs)
- Gemini model names (flash for text, imagen for images, etc.)
- Video settings (1080x1920, 9:16, 30fps)

### 6. Test Gemini API connection
- Simple text generation call
- Verify API key works
- Print available models

### 7. Test FFmpeg
- Generate a 3s black video with FFmpeg to verify installation
- Test ffmpeg-python wrapper

## Todo List
- [ ] Install Python 3.11+
- [ ] Install FFmpeg and add to PATH
- [ ] Create project directory structure
- [ ] Set up virtual environment
- [ ] Install Python dependencies
- [ ] Create .env with Gemini API key
- [ ] Create config.py with all settings
- [ ] Test Gemini API connection
- [ ] Test FFmpeg installation
- [ ] Create .gitignore (exclude .env, data/, .venv/)

## Success Criteria
- `python -c "from google import genai; print('OK')"` works
- `ffmpeg -version` returns valid output
- Config loads API key from .env
- All project directories exist
- Test script generates text via Gemini API

## Risk Assessment
- **FFmpeg PATH issues on Windows**: Mitigation -- document exact steps, test with `where ffmpeg`
- **Gemini API key rate limits on free tier**: Mitigation -- use paid tier ($0 minimum, pay-as-you-go)
- **Python version mismatch**: Mitigation -- require 3.11+, check in config.py
