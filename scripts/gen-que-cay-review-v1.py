#!/usr/bin/env python3
import asyncio
import edge_tts
import json
import os
import subprocess
import time
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

# --- CONFIGURATION ---
ROOT = Path(__file__).resolve().parent.parent
PRODUCT_SLUG = "que-cay"
SCENE_LIB = ROOT / "assets" / "scene-library" / "que_cay"
OUTPUT_DIR = ROOT / "assets" / "products" / PRODUCT_SLUG / "output"
FINAL_DIR = OUTPUT_DIR / "final"
TMP_DIR = OUTPUT_DIR / "_tmp_v1_review"

LABEL_TEXT = "QUE CAY • PEL PEL"
LABEL_Y = 280
TTS_VOICE = "vi-VN-HoaiMyNeural" # Giọng nữ ngọt
TTS_RATE = "+15%"

CAPTION = "Review 3 loại que cay quốc dân cực phẩm cho team ăn vặt 🔥 #quecay #anvat #pelpel #doanvat #xuhuong"
FINAL_NAME = f"{CAPTION}.mp4"

SEGMENTS = [
    {
        "text_voice": "Team mê que cay mà bỏ qua 3 cực phẩm này là dở rồi nha!",
        "text_subtitle": "Team mê que cay bỏ qua là dở rồi!",
        "keywords": ["que cay", "quecay"]
    },
    {
        "text_voice": "Đầu tiên là Vương Thần Long, dai dai cay nồng, ăn là ghiền á.",
        "text_subtitle": "Vương Thần Long — dai dai cay nồng",
        "keywords": ["thanlong", "thần long"]
    },
    {
        "text_voice": "Kế đến là Hàng Đại huyền thoại, vị mặn ngọt cực kỳ đưa miệng luôn.",
        "text_subtitle": "Hàng Đại huyền thoại — vị cực cuốn",
        "keywords": ["hangdai", "hằng đại"]
    },
    {
        "text_voice": "Giỏ hàng Pel Pel đang có đủ combo nha. Chốt đơn thôi cưng ơi!",
        "text_subtitle": "Đang có đủ combo — Chốt đơn thôi!",
        "keywords": ["anvat", "pelpel"]
    }
]

# --- UTILS ---
def run(cmd):
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def find_vi_font(size: int) -> ImageFont.FreeTypeFont:
    for p in [
        "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
        "/System/Library/Fonts/HelveticaNeue.ttc",
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", # Linux fallback
    ]:
        if Path(p).exists():
            try: return ImageFont.truetype(p, size)
            except Exception: continue
    return ImageFont.load_default()

def render_label_png(text: str, out: Path):
    width, height = 900, 140
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    radius = height // 2
    draw.rounded_rectangle([(0, 0), (width - 1, height - 1)], radius=radius, fill=(255, 107, 0, 220))
    font = find_vi_font(58)
    bbox = draw.textbbox((0, 0), text, font=font)
    tx = (width - (bbox[2] - bbox[0])) // 2
    ty = (height - (bbox[3] - bbox[1])) // 2 - bbox[1]
    draw.text((tx, ty), text, font=font, fill=(255, 255, 255, 255), stroke_width=3, stroke_fill=(0, 0, 0, 255))
    img.save(out, "PNG")

def render_subtitle_png(text: str, out: Path):
    width, height = 1000, 200
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    font = find_vi_font(62)
    max_w = width - 60
    words = text.split()
    lines, cur = [], ""
    for w in words:
        test = (cur + " " + w).strip()
        if draw.textlength(test, font=font) <= max_w: cur = test
        else:
            if cur: lines.append(cur)
            cur = w
    if cur: lines.append(cur)
    line_h = 74
    total_h = line_h * len(lines) + 20
    box_top = (height - total_h) // 2
    draw.rounded_rectangle([(20, box_top - 20), (width - 20, box_top + total_h)], radius=25, fill=(0, 0, 0, 180))
    for i, line in enumerate(lines):
        bbox = draw.textbbox((0, 0), line, font=font)
        tx = (width - (bbox[2] - bbox[0])) // 2
        ty = box_top + i * line_h
        draw.text((tx, ty), line, font=font, fill=(255, 255, 255, 255), stroke_width=2, stroke_fill=(0, 0, 0, 255))
    img.save(out, "PNG")

async def tts_async(text, out_path):
    communicate = edge_tts.Communicate(text, TTS_VOICE, rate=TTS_RATE)
    await communicate.save(out_path)

def audio_duration(path: Path) -> float:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", str(path)],
        capture_output=True, text=True
    ).stdout.strip()
    return float(out) if out else 0.0

def load_scenes():
    scenes = []
    for jf in sorted(SCENE_LIB.glob("*.json")):
        with jf.open() as f: data = json.load(f)
        mp4 = SCENE_LIB / f"{jf.stem}.mp4"
        if mp4.exists():
            data["_mp4_path"] = mp4
            scenes.append(data)
    return scenes

def pick_scene(scenes, keywords, min_dur, used):
    candidates = []
    for s in scenes:
        sid = f"{s.get('source_video_id')}_{s.get('scene_index')}"
        if sid in used or (s.get("duration_sec") or 0) < min_dur: continue
        caption = (s.get("source_caption") or "").lower()
        score = sum(1 for k in keywords if k.lower() in caption)
        candidates.append((score, s.get("source_views", 0), s))
    if not candidates: return None
    candidates.sort(key=lambda x: (-x[0], -x[1]))
    return candidates[0][2]

def process_clip(src, dur, label_png, sub_png, out):
    vf = "scale=-1:1920:force_original_aspect_ratio=increase,crop=1080:1920:(iw-1080)/2:0,setsar=1,fps=30"
    tmp_raw = out.with_name(f"{out.stem}_raw.mp4")
    run(["ffmpeg", "-y", "-i", str(src), "-t", str(dur), "-vf", vf, "-an", "-c:v", "libx264", "-preset", "fast", "-crf", "21", "-pix_fmt", "yuv420p", str(tmp_raw)])
    run(["ffmpeg", "-y", "-i", str(tmp_raw), "-i", str(label_png), "-i", str(sub_png), "-filter_complex", f"[0:v][1:v]overlay=(main_w-overlay_w)/2:{LABEL_Y}[v1];[v1][2:v]overlay=(main_w-overlay_w)/2:1580[vo]", "-map", "[vo]", "-c:v", "libx264", "-preset", "fast", "-crf", "21", "-pix_fmt", "yuv420p", "-an", str(out)])

# --- MAIN ---
async def main():
    FINAL_DIR.mkdir(parents=True, exist_ok=True)
    TMP_DIR.mkdir(parents=True, exist_ok=True)
    
    print(f"--- Build {FINAL_NAME} ---")
    label_png = TMP_DIR / "label.png"
    render_label_png(LABEL_TEXT, label_png)
    
    scenes = load_scenes()
    used_ids = set()
    clip_paths = []
    voice_paths = []

    for i, seg in enumerate(SEGMENTS, 1):
        voice_path = TMP_DIR / f"voice_{i:02d}.mp3"
        await tts_async(seg["text_voice"], str(voice_path))
        dur = audio_duration(voice_path)
        
        pick = pick_scene(scenes, seg["keywords"], dur, used_ids)
        if not pick: pick = scenes[i % len(scenes)] # Fallback
        used_ids.add(f"{pick.get('source_video_id')}_{pick.get('scene_index')}")
        
        sub_png = TMP_DIR / f"sub_{i:02d}.png"
        render_subtitle_png(seg["text_subtitle"], sub_png)
        
        clip_path = TMP_DIR / f"clip_{i:02d}.mp4"
        process_clip(pick["_mp4_path"], dur, label_png, sub_png, clip_path)
        
        clip_paths.append(clip_path)
        voice_paths.append(voice_path)
        print(f"Segment {i} done: {dur:.2f}s")

    # Concat
    v_list = TMP_DIR / "v.txt"
    with v_list.open("w") as f: 
        for p in clip_paths: f.write(f"file '{p.resolve()}'\n")
    concat_v = TMP_DIR / "concat_v.mp4"
    run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(v_list), "-c", "copy", str(concat_v)])
    
    a_list = TMP_DIR / "a.txt"
    with a_list.open("w") as f:
        for p in voice_paths: f.write(f"file '{p.resolve()}'\n")
    concat_a = TMP_DIR / "concat_a.mp3"
    run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(a_list), "-c:a", "libmp3lame", "-q:a", "2", str(concat_a)])
    
    final_path = FINAL_DIR / FINAL_NAME
    run(["ffmpeg", "-y", "-i", str(concat_v), "-i", str(concat_a), "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", str(final_path)])
    
    print(f"\n✅ Video sẵn sàng: {final_path.relative_to(ROOT)}")

if __name__ == "__main__":
    asyncio.run(main())
