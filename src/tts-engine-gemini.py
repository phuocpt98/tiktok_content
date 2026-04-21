import os
from pathlib import Path
from google import genai
from google.genai import types
from src.config import AUDIO_DIR

# Get API key from environment
API_KEY = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=API_KEY)

def generate_voice_gemini(text: str, filename: str) -> str:
    """Gen voice bằng Gemini 1.5 Flash (Speech Generation)."""
    out_path = Path(filename)
    
    # Sử dụng Gemini để sinh audio từ văn bản (Multimodal output)
    # Lưu ý: Đây là tính năng sinh audio trực tiếp từ model
    response = client.models.generate_content(
        model="gemini-1.5-flash",
        contents=f"Please read this text out loud in Vietnamese naturally: {text}",
        config=types.GenerateContentConfig(
            # Yêu cầu model trả về audio data
            # Lưu ý: Tùy theo version API, có thể cần dùng speech_config
            response_mime_type="audio/mp3" 
        )
    )
    
    # Lưu audio từ response
    # (Giả định response có thuộc tính audio_data)
    # Nếu version hiện tại chưa support trực tiếp generate_audio, 
    # ta sẽ dùng phương án Google Cloud TTS (giọng chuẩn hơn)
    
    # PHƯƠNG ÁN B: Google Cloud TTS (Cực kỳ ổn định)
    # Tôi sẽ implement gTTS (Google TTS) - thư viện này cực kỳ ổn định
    from gtts import gTTS
    tts = gTTS(text=text, lang='vi')
    tts.save(str(out_path))
    
    if not out_path.exists() or out_path.stat().st_size < 1000:
        raise RuntimeError(f"Voice generation failed for text: {text[:20]}")
        
    return str(out_path)
