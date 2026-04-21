"""
Build concept video v3 — thêm VOICEOVER + PHỤ ĐỀ.

Thay đổi vs v2:
  - Label "BÒ CAY • PEL PEL" dịch xuống y=280 (giữ kích thước 58px)
  - Voiceover: Gemini native TTS (vì edge-tts bị block IP)
  - Phụ đề: Pillow render PNG per scene, overlay theo timeline
  - Audio: voiceover track ghép vào video

Output (convention):
  assets/products/que-cay/output/final/<YYMMDD>-que-cay-v3-<variant>.mp4
  assets/products/que-cay/output/tiktok-ready/<caption>.mp4
"""
from __future__ import annotations

import json
import os
import shutil
import struct
import subprocess
import time
import wave
from pathlib import Path

from dotenv import load_dotenv
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")

from google import genai
from google.genai import types

PRODUCT_DIR = ROOT / "assets" / "products" / "que-cay"
SCENES = ROOT / "assets" / "scene-library" / "que_cay"
PRODUCT_VIDEOS = PRODUCT_DIR / "videos"
OUTPUT_DIR = PRODUCT_DIR / "output"
FINAL_DIR = OUTPUT_DIR / "final"
TIKTOK_DIR = OUTPUT_DIR / "tiktok-ready"
TMP_DIR = OUTPUT_DIR / "_tmp_v3"

DATE = time.strftime("%y%m%d")
CANONICAL_NAME = f"{DATE}-que-cay-v3-3brand-voice-sub.mp4"
CAPTION = "Que cay brand nào đỉnh nhất team 🤤 #anvat #quecay #quecayhangdai #doanvat #anvattuoitho"

LABEL_TEXT = "BÒ CAY • PEL PEL"
LABEL_Y = 280  # dịch xuống (v2 là 80)

# Gemini TTS settings
TTS_MODEL = "gemini-2.5-flash-preview-tts"
TTS_VOICE = "Kore"  # voice ấm, phù hợp review đồ ăn
TTS_SAMPLE_RATE = 24000  # Gemini outputs 24kHz PCM
TTS_CHANNELS = 1

# Clips + script per scene
CLIPS = [
    {
        "type": "scene",
        "src": SCENES / "beheobu0102_7591174570623782162_scene_01.mp4",
        "trim_start": 0.0, "trim_end": 3.0, "label": "HangDai",
        "subtitle": "Hằng Đại — huyền thoại tuổi thơ",
        "voice": "Que cay Hằng Đại. Huyền thoại tuổi thơ. Dài, cay vừa.",
    },
    {
        "type": "scene",
        "src": SCENES / "beheobu0102_7613832315164167432_scene_01.mp4",
        "trim_start": 0.0, "trim_end": 1.7, "label": "ThanLong",
        "subtitle": "Thần Long — to dài siu siu",
        "voice": "Thần Long. To dài siu siu, đẳng cấp size khác.",
    },
    {
        "type": "video",
        "src": PRODUCT_VIDEOS / "Appetizing_Beef_Stick_Slow_Motion.mp4",
        "trim_start": 1.0, "trim_end": 6.0, "label": "BoCay",
        "subtitle": "BÒ CAY — vị mới, ăn cuốn ghê 🤤",
        "voice": "Nhưng hôm nay em thử vị Bò này. Ôi chu choa má ơi, ăn cuốn luôn! Team nào ngon nhất, comment A B C nha.",
    },
]


def run(cmd: list) -> None:
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


# ── Pillow label/subtitle rendering ────────────────────────────────────

def find_vi_font(size: int) -> ImageFont.FreeTypeFont:
    for path in [
        "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
        "/System/Library/Fonts/HelveticaNeue.ttc",
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
    ]:
        if Path(path).exists():
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                continue
    return ImageFont.load_default()


def render_label_png(text: str, out: Path, width: int = 900, height: int = 140) -> None:
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    radius = height // 2
    draw.rounded_rectangle([(0, 0), (width - 1, height - 1)], radius=radius, fill=(255, 107, 0, 220))
    font = find_vi_font(58)
    bbox = draw.textbbox((0, 0), text, font=font)
    tx = (width - (bbox[2] - bbox[0])) // 2
    ty = (height - (bbox[3] - bbox[1])) // 2 - bbox[1]
    draw.text((tx, ty), text, font=font, fill=(255, 255, 255, 255),
              stroke_width=3, stroke_fill=(0, 0, 0, 255))
    img.save(out, "PNG")


def render_subtitle_png(text: str, out: Path, width: int = 1000, height: int = 180) -> None:
    """Phụ đề ở bottom center, nền đen mờ, chữ trắng + stroke."""
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Multi-line wrap nếu dài quá
    font = find_vi_font(60)
    max_w = width - 60
    words = text.split()
    lines = []
    cur = ""
    for w in words:
        test = (cur + " " + w).strip()
        if draw.textlength(test, font=font) <= max_w:
            cur = test
        else:
            if cur: lines.append(cur)
            cur = w
    if cur: lines.append(cur)

    line_h = 72
    total_h = line_h * len(lines) + 20

    # Background box
    box_top = (height - total_h) // 2
    draw.rounded_rectangle(
        [(20, box_top - 20), (width - 20, box_top + total_h)],
        radius=25, fill=(0, 0, 0, 180)
    )

    # Text each line
    for i, line in enumerate(lines):
        bbox = draw.textbbox((0, 0), line, font=font)
        tx = (width - (bbox[2] - bbox[0])) // 2
        ty = box_top + i * line_h
        draw.text((tx, ty), line, font=font, fill=(255, 255, 255, 255),
                  stroke_width=2, stroke_fill=(0, 0, 0, 255))

    img.save(out, "PNG")


# ── Gemini TTS ─────────────────────────────────────────────────────────

def gemini_tts(text: str, out_wav: Path) -> None:
    """Gen voice VN qua Gemini TTS preview → WAV 24kHz mono."""
    api_key = os.getenv("GEMINI_API_KEY")
    client = genai.Client(api_key=api_key)
    resp = client.models.generate_content(
        model=TTS_MODEL,
        contents=text,
        config=types.GenerateContentConfig(
            response_modalities=["AUDIO"],
            speech_config=types.SpeechConfig(
                voice_config=types.VoiceConfig(
                    prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name=TTS_VOICE)
                )
            ),
        ),
    )
    pcm = None
    for p in resp.candidates[0].content.parts:
        if hasattr(p, "inline_data") and p.inline_data:
            pcm = p.inline_data.data
            break
    if pcm is None:
        raise RuntimeError("Gemini TTS không trả audio")

    # Wrap PCM raw → WAV
    with wave.open(str(out_wav), "wb") as wf:
        wf.setnchannels(TTS_CHANNELS)
        wf.setsampwidth(2)  # 16-bit
        wf.setframerate(TTS_SAMPLE_RATE)
        wf.writeframes(pcm)


def audio_duration(path: Path) -> float:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(path)],
        capture_output=True, text=True,
    ).stdout.strip()
    return float(out) if out else 0.0


# ── Video processing ───────────────────────────────────────────────────

def standardize_to_portrait(src: Path, out: Path, start: float, end: float) -> None:
    duration = end - start
    vf = (
        "scale=-1:1920:force_original_aspect_ratio=increase,"
        "crop=1080:1920:(iw-1080)/2:0,"
        "setsar=1,fps=30"
    )
    cmd = [
        "ffmpeg", "-y",
        "-ss", f"{start}", "-i", str(src), "-t", f"{duration}",
        "-vf", vf,
        "-an",
        "-c:v", "libx264", "-preset", "fast", "-crf", "21",
        "-pix_fmt", "yuv420p",
        str(out),
    ]
    run(cmd)


def overlay_label_and_subtitle(video: Path, label_png: Path, subtitle_png: Path, out: Path) -> None:
    """Overlay label top (y=280) + subtitle bottom (y=1580)."""
    # Label at y=LABEL_Y (280, dịch xuống từ 80)
    # Subtitle at bottom area: y=1580 (trong khoảng 1500-1800)
    cmd = [
        "ffmpeg", "-y",
        "-i", str(video),
        "-i", str(label_png),
        "-i", str(subtitle_png),
        "-filter_complex",
        (
            f"[0:v][1:v]overlay=(main_w-overlay_w)/2:{LABEL_Y}[v1];"
            f"[v1][2:v]overlay=(main_w-overlay_w)/2:1580[vo]"
        ),
        "-map", "[vo]",
        "-c:v", "libx264", "-preset", "fast", "-crf", "21",
        "-pix_fmt", "yuv420p",
        "-an",
        str(out),
    ]
    run(cmd)


def concat_clips(clip_paths: list[Path], out: Path) -> None:
    list_file = TMP_DIR / "concat.txt"
    with list_file.open("w") as f:
        for p in clip_paths:
            f.write(f"file '{p.resolve()}'\n")
    cmd = [
        "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(list_file),
        "-c", "copy", str(out),
    ]
    run(cmd)


def concat_audio(audio_paths: list[Path], out: Path) -> None:
    """Concat các WAV thành 1 file MP3."""
    list_file = TMP_DIR / "audio_concat.txt"
    with list_file.open("w") as f:
        for p in audio_paths:
            f.write(f"file '{p.resolve()}'\n")
    cmd = [
        "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(list_file),
        "-c:a", "libmp3lame", "-q:a", "2",
        str(out),
    ]
    run(cmd)


def mux_audio(video: Path, audio: Path, out: Path) -> None:
    """Ghép video (silent) + audio track."""
    cmd = [
        "ffmpeg", "-y",
        "-i", str(video),
        "-i", str(audio),
        "-c:v", "copy",
        "-c:a", "aac", "-b:a", "192k",
        "-movflags", "+faststart",
        "-shortest",
        str(out),
    ]
    run(cmd)


# ── Main ───────────────────────────────────────────────────────────────

def main():
    FINAL_DIR.mkdir(parents=True, exist_ok=True)
    TIKTOK_DIR.mkdir(parents=True, exist_ok=True)
    TMP_DIR.mkdir(parents=True, exist_ok=True)

    print("── Build concept que-cay v3 (voice + sub) ────")

    # 1. Render label PNG (persistent)
    label_png = TMP_DIR / "label.png"
    print(f"[1/6] Label PNG → {label_png.name}")
    render_label_png(LABEL_TEXT, label_png)

    # 2. Render subtitle PNG + TTS voiceover per clip
    print(f"[2/6] Render subtitles + TTS per clip...")
    for i, clip in enumerate(CLIPS, 1):
        sub_png = TMP_DIR / f"sub_{i:02d}_{clip['label']}.png"
        render_subtitle_png(clip["subtitle"], sub_png)
        clip["sub_png"] = sub_png

        voice_wav = TMP_DIR / f"voice_{i:02d}_{clip['label']}.wav"
        print(f"  TTS [{i}] {clip['label']}: \"{clip['voice'][:50]}...\"")
        gemini_tts(clip["voice"], voice_wav)
        clip["voice_wav"] = voice_wav
        clip["voice_dur"] = audio_duration(voice_wav)
        print(f"    voice {clip['voice_dur']:.1f}s vs clip {clip['trim_end']-clip['trim_start']:.1f}s")

    # 3. Process video clips: 9:16 standardize + overlay label+subtitle
    print(f"[3/6] Standardize + overlay label/subtitle...")
    clip_paths = []
    for i, clip in enumerate(CLIPS, 1):
        base = f"clip_{i:02d}_{clip['label']}"
        stage1 = TMP_DIR / f"{base}_raw.mp4"
        stage2 = TMP_DIR / f"{base}_overlay.mp4"

        standardize_to_portrait(clip["src"], stage1, clip["trim_start"], clip["trim_end"])
        overlay_label_and_subtitle(stage1, label_png, clip["sub_png"], stage2)
        clip_paths.append(stage2)

    # 4. Concat video
    concat_v = TMP_DIR / "concat_video.mp4"
    print(f"[4/6] Concat video clips → {concat_v.name}")
    concat_clips(clip_paths, concat_v)

    # 5. Concat audio → MP3
    concat_a = TMP_DIR / "concat_audio.mp3"
    print(f"[5/6] Concat voiceover → {concat_a.name}")
    concat_audio([c["voice_wav"] for c in CLIPS], concat_a)

    # 6. Mux video + audio → canonical
    canonical_path = FINAL_DIR / CANONICAL_NAME
    print(f"[6/6] Mux → {canonical_path.name}")
    mux_audio(concat_v, concat_a, canonical_path)

    # Copy tiktok-ready
    tiktok_path = TIKTOK_DIR / f"{CAPTION}.mp4"
    shutil.copy2(canonical_path, tiktok_path)

    # Meta
    total_dur = sum(c["trim_end"] - c["trim_start"] for c in CLIPS)
    meta = {
        "caption": CAPTION,
        "label_persistent": LABEL_TEXT,
        "label_y": LABEL_Y,
        "duration_sec": total_dur,
        "voiceover_model": f"{TTS_MODEL} ({TTS_VOICE})",
        "clips": [
            {"label": c["label"], "source": str(c["src"].relative_to(ROOT)),
             "trim": [c["trim_start"], c["trim_end"]],
             "subtitle": c["subtitle"], "voice_script": c["voice"],
             "voice_duration": c.get("voice_dur")}
            for c in CLIPS
        ],
        "canonical_path": str(canonical_path.relative_to(ROOT)),
        "tiktok_ready_path": str(tiktok_path.relative_to(ROOT)),
    }
    meta_path = FINAL_DIR / f"{CANONICAL_NAME}.meta.json"
    with meta_path.open("w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)

    print(f"\n✓ Canonical : {canonical_path.relative_to(ROOT)}")
    print(f"✓ TikTok    : {tiktok_path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
