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
SFX_DIR = ROOT / "assets" / "audio" / "sfx"
OUTPUT_DIR = ROOT / "assets" / "products" / PRODUCT_SLUG / "output"
FINAL_DIR = OUTPUT_DIR / "final"
TMP_DIR = OUTPUT_DIR / "_tmp_v2_asmr"

LABEL_TEXT = "QUE CAY • PEL PEL"
LABEL_Y = 280
TTS_VOICE = "vi-VN-HoaiMyNeural"
TTS_RATE = "+15%"

CAPTION = "Review que cay cực phẩm kèm ASMR đỉnh chóp 🔥 #quecay #anvat #pelpel #asmr #doanvat"
FINAL_NAME = f"{CAPTION}.mp4"

SEGMENTS = [
    {
        "text_voice": "Team mê que cay mà bỏ qua 3 cực phẩm này là dở rồi nha!",
        "text_subtitle": "Team mê que cay bỏ qua là dở rồi!",
        "keywords": ["que cay"],
        "sfx": "asmr_xe_tui.mp3",
        "sfx_vol": 0.8
    },
    {
        "text_voice": "Đầu tiên là Vương Thần Long, dai dai cay nồng, ăn là ghiền á.",
        "text_subtitle": "Vương Thần Long — dai dai cay nồng",
        "keywords": ["thần long"],
        "sfx": "asmr_nhai_gion.mp3",
        "sfx_vol": 1.0
    },
    {
        "text_voice": "Kế đến là Hàng Đại huyền thoại, vị mặn ngọt cực kỳ đưa miệng luôn.",
        "text_subtitle": "Hàng Đại huyền thoại — vị cực cuốn",
        "keywords": ["hằng đại"],
        "sfx": "asmr_soat_soat.mp3",
        "sfx_vol": 0.6
    },
    {
        "text_voice": "Giỏ hàng Pel Pel đang có đủ combo nha. Chốt đơn thôi cưng ơi!",
        "text_subtitle": "Đang có đủ combo — Chốt đơn thôi!",
        "keywords": ["anvat"],
        "sfx": None
    }
]

def run(cmd):
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

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
    draw.text(((900-(bbox[2]-bbox[0]))//2, (140-(bbox[3]-bbox[1]))//2-bbox[1]), text, font=font, fill=(255, 255, 255, 255), stroke_width=3, stroke_fill=(0, 0, 0, 255))
    img.save(out, "PNG")

def render_subtitle_png(text: str, out: Path):
    img = Image.new("RGBA", (1000, 200), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    font = find_vi_font(62)
    draw.rounded_rectangle([(20, 60), (980, 160)], radius=25, fill=(0, 0, 0, 180))
    bbox = draw.textbbox((0, 0), text, font=font)
    draw.text(((1000-(bbox[2]-bbox[0]))//2, (200-(bbox[3]-bbox[1]))//2-bbox[1]), text, font=font, fill=(255, 255, 255, 255), stroke_width=2, stroke_fill=(0, 0, 0, 255))
    img.save(out, "PNG")

async def tts_async(text, out_path):
    await edge_tts.Communicate(text, TTS_VOICE, rate=TTS_RATE).save(out_path)

def audio_duration(path: Path) -> float:
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", str(path)], capture_output=True, text=True).stdout.strip() or 0)

def process_clip_with_asmr(src, dur, label_png, sub_png, voice_mp3, sfx_name, sfx_vol, out):
    vf = "scale=-1:1920:force_original_aspect_ratio=increase,crop=1080:1920:(iw-1080)/2:0,setsar=1,fps=30"
    tmp_v = out.with_name(f"{out.stem}_v.mp4")
    # 1. Render Video (Label + Sub)
    run(["ffmpeg", "-y", "-i", str(src), "-i", str(label_png), "-i", str(sub_png), "-t", str(dur), "-filter_complex", f"scale=-1:1920:force_original_aspect_ratio=increase,crop=1080:1920:(iw-1080)/2:0,setsar=1,fps=30[bg];[bg][1:v]overlay=(main_w-overlay_w)/2:{LABEL_Y}[v1];[v1][2:v]overlay=(main_w-overlay_w)/2:1580[vo]", "-map", "[vo]", "-c:v", "libx264", "-preset", "fast", "-crf", "21", "-an", str(tmp_v)])
    
    # 2. Mix Audio (Voice + SFX)
    if sfx_name:
        sfx_path = SFX_DIR / sfx_name
        run(["ffmpeg", "-y", "-i", str(voice_mp3), "-i", str(sfx_path), "-filter_complex", f"[0:a]volume=1.0[v];[1:a]volume={sfx_vol}[s];[v][s]amix=inputs=2:duration=first[a]", "-map", "[a]", "-c:a", "aac", str(out.with_suffix(".m4a"))])
    else:
        run(["ffmpeg", "-y", "-i", str(voice_mp3), "-c:a", "aac", str(out.with_suffix(".m4a"))])
    
    # 3. Mux
    run(["ffmpeg", "-y", "-i", str(tmp_v), "-i", str(out.with_suffix(".m4a")), "-c:v", "copy", "-c:a", "copy", str(out)])

async def main():
    FINAL_DIR.mkdir(parents=True, exist_ok=True)
    TMP_DIR.mkdir(parents=True, exist_ok=True)
    label_png = TMP_DIR / "label.png"
    render_label_png(LABEL_TEXT, label_png)
    scenes = list(SCENE_LIB.glob("*.mp4"))
    clip_paths = []
    
    for i, seg in enumerate(SEGMENTS, 1):
        voice_path = TMP_DIR / f"voice_{i:02d}.mp3"
        await tts_async(seg["text_voice"], str(voice_path))
        dur = audio_duration(voice_path)
        sub_png = TMP_DIR / f"sub_{i:02d}.png"
        render_subtitle_png(seg["text_subtitle"], sub_png)
        clip_path = TMP_DIR / f"clip_{i:02d}.mp4"
        process_clip_with_asmr(scenes[i % len(scenes)], dur, label_png, sub_png, voice_path, seg["sfx"], seg.get("sfx_vol", 0.5), clip_path)
        clip_paths.append(clip_path)
        print(f"Segment {i} ASMR done")

    v_list = TMP_DIR / "v.txt"
    with v_list.open("w") as f:
        for p in clip_paths: f.write(f"file '{p.resolve()}'\n")
    final_path = FINAL_DIR / FINAL_NAME
    run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(v_list), "-c", "copy", "-movflags", "+faststart", str(final_path)])
    print(f"\n✅ Video ASMR Ready: {final_path.relative_to(ROOT)}")

if __name__ == "__main__":
    asyncio.run(main())
