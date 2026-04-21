"""Project configuration and path constants."""
import os
import logging
from pathlib import Path
from dotenv import load_dotenv

# Load .env from project root (NOT .env.example)
PROJECT_ROOT = Path(__file__).parent.parent
load_dotenv(PROJECT_ROOT / ".env")

# API Keys — 2 keys for rotation (double free quota)
GEMINI_API_KEYS = [
    k for k in [
        os.getenv("GEMINI_API_KEY", ""),
        os.getenv("GEMINI_API_KEY_2", ""),
    ] if k
]

# Directory paths
ASSETS_DIR = PROJECT_ROOT / "assets"
IMAGES_DIR = ASSETS_DIR / "images"
VIDEOS_DIR = ASSETS_DIR / "videos"
AUDIO_DIR = ASSETS_DIR / "audio"
TEXT_DIR = ASSETS_DIR / "text"
OUTPUT_DIR = PROJECT_ROOT / "output"
TEMPLATES_DIR = PROJECT_ROOT / "templates"
DB_PATH = PROJECT_ROOT / "pelpel.db"

# Ensure directories exist
for d in [IMAGES_DIR, VIDEOS_DIR, AUDIO_DIR, TEXT_DIR, OUTPUT_DIR, TEMPLATES_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# Video settings (TikTok vertical)
VIDEO_WIDTH = 1080
VIDEO_HEIGHT = 1920
VIDEO_FPS = 30

# Edge TTS default voice (Vietnamese female)
TTS_VOICE = "vi-VN-HoaiMyNeural"

# FFmpeg path (winget install location)
FFMPEG_PATH = os.getenv("FFMPEG_PATH", r"C:\Users\phuocpt5\AppData\Local\Microsoft\WinGet\Links\ffmpeg.exe")
FFPROBE_PATH = FFMPEG_PATH.replace("ffmpeg.exe", "ffprobe.exe")

# Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.FileHandler(PROJECT_ROOT / "pelpel.log", encoding="utf-8"),
        logging.StreamHandler(),
    ]
)
