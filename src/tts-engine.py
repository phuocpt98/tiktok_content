"""Text-to-Speech engine using Edge TTS (free, unlimited, Vietnamese)."""
import subprocess
import sys
from pathlib import Path
from datetime import datetime
from src.config import AUDIO_DIR, TTS_VOICE

# Available Vietnamese voices
VN_VOICES = {
    "female_south": "vi-VN-HoaiMyNeural",   # Giọng nữ miền Nam (default)
    "male_south": "vi-VN-NamMinhNeural",     # Giọng nam miền Nam
}


def generate_voice(text: str, voice_key: str = "female_south",
                   filename: str = None) -> str:
    """Generate Vietnamese voiceover from text. Returns file path.

    Uses edge-tts CLI (more reliable on Windows than async Python API).
    """
    voice = VN_VOICES.get(voice_key, TTS_VOICE)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    fname = filename or f"voice_{timestamp}.mp3"
    filepath = AUDIO_DIR / fname

    result = subprocess.run(
        [sys.executable, "-m", "edge_tts",
         "--text", text,
         "--voice", voice,
         "--write-media", str(filepath)],
        capture_output=True, text=True
    )

    if result.returncode != 0:
        raise RuntimeError(f"Edge TTS error: {result.stderr[:300]}")

    if not filepath.exists() or filepath.stat().st_size == 0:
        raise RuntimeError("Edge TTS produced no output")

    return str(filepath)


def list_voices() -> dict:
    """List available Vietnamese voices."""
    return VN_VOICES
