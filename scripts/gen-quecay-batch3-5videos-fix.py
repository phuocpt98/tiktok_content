"""
Generate ONLY Vua Tieng Viet 1 (Sặc sỡ hay Xặc xỡ) with modified text to fix TTS block.
"""
import json
import os
import subprocess
import time
import asyncio
import edge_tts
import re
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from google import genai
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")

SCENE_LIB = ROOT / "assets" / "scene-library" / "que_cay"
OUTPUT_DIR = ROOT / "assets" / "products" / "que-cay" / "output"
FINAL_DIR = OUTPUT_DIR / "final"
LABEL_Y = 280

VOICES = ["vi-VN-NamMinhNeural", "vi-VN-HoaiMyNeural"]
TTS_RATE = "+10%"

GEMINI_KEY = os.getenv("GEMINI_API_KEY")
gemini_client = genai.Client(api_key=GEMINI_KEY) if GEMINI_KEY else None

# Chỉ định duy nhất 1 video cần sửa
VIDEOS_CONFIG = [
    {
        "name": "vua_tv_sac_so_fixed",
        "caption": "SẶC SỠ hay XẶC XỠ? 🤔 Bò cay này cũng sặc sỡ mà ngon lắm nha! #vuatiengviet #quecay #anvat #pelpel #fyp",
        "label": "VUA TIẾNG VIỆT • PEL PEL",
        "segments": [
            {"text_voice": "Đố các bạn biết, trong hai từ này thì từ nào mới viết đúng chính tả đây?", "text_subtitle": "SẶC SỠ hay XẶC XỠ? 🤔", "keywords": ["quecay"], "scene_id": "beheobu0102_7487206549224459526_scene_01", "min_dur": 4.5},
            {"text_voice": "Trong lúc chờ đợi thì cùng mình xem qua gói bò cay Pel Pel này nhé.", "text_subtitle": "Đang nghĩ thì xem mình review nha!", "keywords": ["quecay"], "scene_id": "beheobu0102_7507637747360812295_scene_01"},
            {"text_voice": "Vị bò cay đậm đà, sợi dai giòn, ăn một que là mê chữ ê kéo dài luôn.", "text_subtitle": "Bò cay đậm đà - Ăn là nghiện 🤤", "keywords": ["quecay"], "scene_id": "beheobu0102_7587471944946076936_scene_01"},
            {"text_voice": "Và đáp án chính xác của chúng ta là: SẶC SỠ!", "text_subtitle": "Đáp án: SẶC SỠ ✅", "keywords": ["quecay"], "scene_id": "beheobu0102_7591174570623782162_scene_01", "min_dur": 3.0},
            {"text_voice": "Bạn nào trả lời đúng thì thả tim cho mình biết với nhé. Follow mình ngay nha!", "text_subtitle": "Comment 'đỉnh' nếu bạn đúng! ✌️", "keywords": ["quecay"], "scene_id": "beheobu0102_7591563909870390546_scene_01", "min_dur": 4.0},
        ]
    }
]

def clean_text(text: str) -> str:
    return re.sub(r'[^a-zA-Z0-9àáảãạâầấẩẫậăằắẳẵặèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵ\s,.]', '', text)

def find_vi_font(size: int) -> ImageFont.FreeTypeFont:
    for p in ["/System/Library/Fonts/Supplemental/Arial Unicode.ttf", "/System/Library/Fonts/HelveticaNeue.ttc"]:
        if Path(p).exists(): return ImageFont.truetype(p, size)
    return ImageFont.load_default()

def render_label_png(text: str, out: Path):
    img = Image.new("RGBA", (900, 140), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.rounded_rectangle([(0, 0), (899, 139)], radius=70, fill=(255, 107, 0, 220))
    font = find_vi_font(58)
    bbox = draw.textbbox((0, 0), text, font=font)
    draw.text(((900-(bbox[2]-bbox[0]))//2, (140-(bbox[3]-bbox[1]))//2-bbox[1]), text, font=font, fill=(255, 255, 255), stroke_width=3, stroke_fill=(0, 0, 0))
    img.save(out, "PNG")

def render_subtitle_png(text: str, out: Path):
    img = Image.new("RGBA", (1000, 200), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    font = find_vi_font(62)
    lines, cur = [], ""
    for w in text.split():
        if draw.textlength((cur + " " + w).strip(), font=font) <= 940: cur = (cur + " " + w).strip()
        else: lines.append(cur); cur = w
    if cur: lines.append(cur)
    h = 74 * len(lines) + 20
    draw.rounded_rectangle([(20, (200-h)//2-20), (980, (200-h)//2+h)], radius=25, fill=(0, 0, 0, 180))
    for i, line in enumerate(lines):
        bbox = draw.textbbox((0, 0), line, font=font)
        draw.text(((1000-(bbox[2]-bbox[0]))//2, (200-h)//2 + i*74), line, font=font, fill=(255, 255, 255), stroke_width=2, stroke_fill=(0, 0, 0))
    img.save(out, "PNG")

async def tts_edge(text: str, out_mp3: Path):
    text = clean_text(text)
    for voice in VOICES:
        try:
            c = edge_tts.Communicate(text, voice, rate=TTS_RATE)
            await c.save(str(out_mp3))
            if out_mp3.exists() and out_mp3.stat().st_size > 500: return True
        except: pass
    return False

async def tts_gemini(text: str, out_mp3: Path):
    if not gemini_client: return False
    try:
        response = gemini_client.models.generate_content(model="gemini-2.0-flash", contents=f"Đọc: {text}", config={"speech_config": {"voice_config": {"prebuilt_voice_config": {"voice_name": "Kore"}}}})
        if response.audio: out_mp3.write_bytes(response.audio); return True
    except: pass
    return False

async def tts_robust(text: str, out_mp3: Path):
    if await tts_edge(text, out_mp3): return
    if await tts_gemini(text, out_mp3): return
    subprocess.run(["ffmpeg", "-y", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=mono", "-t", "0.5", str(out_mp3)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

async def build_video(config: dict):
    tmp = OUTPUT_DIR / f"_tmp_fix_{config['name']}"
    tmp.mkdir(parents=True, exist_ok=True)
    label_png = tmp / "label.png"
    render_label_png(config["label"], label_png)
    clips, audios = [], []
    for i, seg in enumerate(config["segments"], 1):
        voice = tmp / f"v_{i}.mp3"
        await tts_robust(seg["text_voice"], voice)
        dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", str(voice)], capture_output=True, text=True).stdout.strip() or 0.5)
        render_dur = max(dur, seg.get("min_dur", 2.5))
        scene = SCENE_LIB / f"{seg['scene_id']}.mp4"
        raw = tmp / f"r_{i}.mp4"
        subprocess.run(["ffmpeg", "-y", "-stream_loop", "-1", "-i", str(scene), "-t", str(render_dur), "-vf", "scale=-1:1920:force_original_aspect_ratio=increase,crop=1080:1920:(iw-1080)/2:0,setsar=1,fps=30", "-an", "-c:v", "libx264", "-crf", "21", "-pix_fmt", "yuv420p", str(raw)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if dur < render_dur:
            ext = tmp / f"v_{i}_e.mp3"
            subprocess.run(["ffmpeg", "-y", "-i", str(voice), "-f", "lavfi", "-i", "anullsrc=r=44100:cl=mono", "-filter_complex", "[0:a][1:a]concat=n=2:v=0:a=1", "-t", str(render_dur), str(ext)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            voice = ext
        sub = tmp / f"s_{i}.png"
        render_subtitle_png(seg["text_subtitle"], sub)
        out = tmp / f"f_{i}.mp4"
        subprocess.run(["ffmpeg", "-y", "-i", str(raw), "-i", str(label_png), "-i", str(sub), "-filter_complex", f"[0:v][1:v]overlay=(main_w-overlay_w)/2:{LABEL_Y}[v1];[v1][2:v]overlay=(main_w-overlay_w)/2:1580[vo]", "-map", "[vo]", "-c:v", "libx264", "-crf", "21", "-pix_fmt", "yuv420p", "-an", str(out)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        clips.append(out); audios.append(voice)
    with (tmp/"v.txt").open("w") as f:
        for c in clips: f.write(f"file '{c.resolve()}'\n")
    with (tmp/"a.txt").open("w") as f:
        for a in audios: f.write(f"file '{a.resolve()}'\n")
    cv, ca = tmp/"cv.mp4", tmp/"ca.mp3"
    subprocess.run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(tmp/"v.txt"), "-c", "copy", str(cv)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    subprocess.run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(tmp/"a.txt"), "-c:a", "libmp3lame", "-q:a", "2", str(ca)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    final = FINAL_DIR / f"{config['caption']}.mp4"
    subprocess.run(["ffmpeg", "-y", "-i", str(cv), "-i", str(ca), "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", str(final)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print(f"FIXED: {final.name}")

async def main():
    FINAL_DIR.mkdir(parents=True, exist_ok=True)
    for cfg in VIDEOS_CONFIG: await build_video(cfg)

if __name__ == "__main__":
    asyncio.run(main())
