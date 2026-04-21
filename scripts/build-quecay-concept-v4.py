"""
Build concept que-cay v4 — voice-first pipeline (không dùng AI-gen video/photo).

Flow:
  1. Define script segments (text Vietnamese)
  2. Gemini TTS từng segment → measure exact duration
  3. Pick scene từ scene-library theo keyword match trong caption
  4. Trim scene = voice duration (video theo voice, KHÔNG để cụt voice)
  5. Concat scenes + concat voice + subtitle PNG overlay theo timing
  6. Mux final

Source scenes: CHỈ từ `assets/scene-library/que_cay/` (competitor thật, có WM Pel Pel)
KHÔNG dùng: Beef Stick AI, photos poll AI, Ken Burns.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import time
import wave
from pathlib import Path

import asyncio
import edge_tts

from dotenv import load_dotenv
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")

PRODUCT_DIR = ROOT / "assets" / "products" / "que-cay"
SCENE_LIB = ROOT / "assets" / "scene-library" / "que_cay"
OUTPUT_DIR = PRODUCT_DIR / "output"
FINAL_DIR = OUTPUT_DIR / "final"
TMP_DIR = OUTPUT_DIR / "_tmp_v4"

# Convention: final/ chứa file tên = caption + hashtag để TikTok auto-fill caption
CAPTION = "Que cay brand nào đỉnh nhất team #anvat #quecay #quecayhangdai #doanvat #anvattuoitho"
FINAL_NAME = f"{CAPTION}.mp4"

LABEL_TEXT = "BÒ CAY • PEL PEL"
LABEL_Y = 280

# edge-tts (Microsoft Edge TTS free, không quota)
# LƯU Ý: voice 'vi-VN-HoaiMyNeural' (nữ) bị Microsoft block. Dùng 'vi-VN-NamMinhNeural' (nam).
TTS_VOICE = "vi-VN-NamMinhNeural"
TTS_RATE = "+10%"  # nói hơi nhanh, phù hợp TikTok

# Script segments — text thuần tiếng Việt, không emoji (tránh render fail)
# Đã rút về 3 segment vì Gemini TTS free tier 10 req/day → 4 seg tốn quota.
# Outro "comment team nào" merge vào subtitle segment 3.
SEGMENTS = [
    {
        "text_voice":    "Que cay nhà nào là đỉnh nhất team?",
        "text_subtitle": "Que cay nhà nào đỉnh nhất?",
        "keywords":      ["quecay", "que cay"],
    },
    {
        "text_voice":    "Hằng Đại — siu siu dài, huyền thoại tuổi thơ!",
        "text_subtitle": "Hằng Đại — huyền thoại",
        "keywords":      ["hangdai", "hằng đại", "siu siu"],
    },
    {
        "text_voice":    "Thần Long — to dài ngon ngon, đẳng cấp khác!",
        "text_subtitle": "Thần Long to dài — Comment team nào?",
        "keywords":      ["thần long", "than long", "thanlong", "to dài"],
    },
]


def run(cmd: list) -> None:
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


# ── Pillow rendering ───────────────────────────────────────────────────

def find_vi_font(size: int) -> ImageFont.FreeTypeFont:
    for p in [
        "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
        "/System/Library/Fonts/HelveticaNeue.ttc",
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
    ]:
        if Path(p).exists():
            try: return ImageFont.truetype(p, size)
            except Exception: continue
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


def render_subtitle_png(text: str, out: Path, width: int = 1000, height: int = 200) -> None:
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    font = find_vi_font(62)
    max_w = width - 60
    # Word wrap
    words = text.split()
    lines, cur = [], ""
    for w in words:
        test = (cur + " " + w).strip()
        if draw.textlength(test, font=font) <= max_w:
            cur = test
        else:
            if cur: lines.append(cur)
            cur = w
    if cur: lines.append(cur)

    line_h = 74
    total_h = line_h * len(lines) + 20
    box_top = (height - total_h) // 2
    draw.rounded_rectangle(
        [(20, box_top - 20), (width - 20, box_top + total_h)],
        radius=25, fill=(0, 0, 0, 180),
    )
    for i, line in enumerate(lines):
        bbox = draw.textbbox((0, 0), line, font=font)
        tx = (width - (bbox[2] - bbox[0])) // 2
        ty = box_top + i * line_h
        draw.text((tx, ty), line, font=font, fill=(255, 255, 255, 255),
                  stroke_width=2, stroke_fill=(0, 0, 0, 255))
    img.save(out, "PNG")


# ── Gemini TTS ─────────────────────────────────────────────────────────

def tts(text: str, out_mp3: Path) -> None:
    """Dùng edge-tts (Microsoft Edge TTS free). Unlimited quota."""
    async def _gen():
        c = edge_tts.Communicate(text, TTS_VOICE, rate=TTS_RATE)
        await c.save(str(out_mp3))
    asyncio.run(_gen())


def audio_duration(path: Path) -> float:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(path)],
        capture_output=True, text=True,
    ).stdout.strip()
    return float(out) if out else 0.0


# ── Scene picker ───────────────────────────────────────────────────────

def load_scene_library() -> list[dict]:
    """Load all scene metadata từ scene-library/que_cay/."""
    scenes = []
    for jf in sorted(SCENE_LIB.glob("*.json")):
        try:
            with jf.open() as f:
                data = json.load(f)
            mp4 = SCENE_LIB / f"{jf.stem}.mp4"
            if not mp4.exists(): continue
            data["_json_path"] = jf
            data["_mp4_path"] = mp4
            scenes.append(data)
        except Exception:
            continue
    return scenes


def pick_scene(scenes: list[dict], keywords: list[str], min_duration: float,
               used_ids: set[str]) -> dict | None:
    """Pick scene match keyword trong caption, duration ≥ min, chưa dùng."""
    candidates = []
    for s in scenes:
        key = f"{s.get('source_video_id')}_{s.get('scene_index')}"
        if key in used_ids: continue
        if (s.get("duration_sec") or 0) < min_duration: continue
        caption = (s.get("source_caption") or "").lower()
        score = sum(1 for k in keywords if k.lower() in caption)
        if score > 0:
            views = s.get("source_views") or 0
            candidates.append((score, views, s))
    if not candidates:
        # Fallback: any scene đủ duration, không cần keyword
        for s in scenes:
            key = f"{s.get('source_video_id')}_{s.get('scene_index')}"
            if key in used_ids: continue
            if (s.get("duration_sec") or 0) < min_duration: continue
            views = s.get("source_views") or 0
            candidates.append((0, views, s))
    if not candidates:
        return None
    candidates.sort(key=lambda x: (-x[0], -x[1]))
    return candidates[0][2]


# ── Video processing ───────────────────────────────────────────────────

def trim_scene_portrait(src: Path, duration: float, out: Path) -> None:
    """Trim scene từ 0 → duration, ép 9:16 1080×1920."""
    vf = (
        "scale=-1:1920:force_original_aspect_ratio=increase,"
        "crop=1080:1920:(iw-1080)/2:0,"
        "setsar=1,fps=30"
    )
    cmd = [
        "ffmpeg", "-y",
        "-i", str(src), "-t", f"{duration}",
        "-vf", vf, "-an",
        "-c:v", "libx264", "-preset", "fast", "-crf", "21",
        "-pix_fmt", "yuv420p",
        str(out),
    ]
    run(cmd)


def overlay_label_and_subtitle(video: Path, label_png: Path, subtitle_png: Path, out: Path) -> None:
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
        "-pix_fmt", "yuv420p", "-an",
        str(out),
    ]
    run(cmd)


def concat_clips(clip_paths: list[Path], out: Path) -> None:
    list_file = TMP_DIR / "concat_v.txt"
    with list_file.open("w") as f:
        for p in clip_paths:
            f.write(f"file '{p.resolve()}'\n")
    cmd = ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(list_file),
           "-c", "copy", str(out)]
    run(cmd)


def concat_audio(audio_paths: list[Path], out: Path) -> None:
    list_file = TMP_DIR / "concat_a.txt"
    with list_file.open("w") as f:
        for p in audio_paths:
            f.write(f"file '{p.resolve()}'\n")
    cmd = ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(list_file),
           "-c:a", "libmp3lame", "-q:a", "2", str(out)]
    run(cmd)


def mux_audio(video: Path, audio: Path, out: Path) -> None:
    cmd = [
        "ffmpeg", "-y",
        "-i", str(video), "-i", str(audio),
        "-c:v", "copy",
        "-c:a", "aac", "-b:a", "192k",
        "-movflags", "+faststart",
        str(out),
    ]
    run(cmd)


# ── Main ───────────────────────────────────────────────────────────────

def main():
    FINAL_DIR.mkdir(parents=True, exist_ok=True)
    TMP_DIR.mkdir(parents=True, exist_ok=True)

    print("── Build concept que-cay v4 (voice-first) ─────")

    # 1. Label PNG (persistent)
    label_png = TMP_DIR / "label.png"
    render_label_png(LABEL_TEXT, label_png)

    # 2. TTS per segment với edge-tts (cache nếu đã gen)
    print(f"[1/4] TTS per segment (edge-tts, voice={TTS_VOICE})...")
    for i, seg in enumerate(SEGMENTS, 1):
        voice_path = TMP_DIR / f"voice_{i:02d}.mp3"
        if voice_path.exists() and voice_path.stat().st_size > 1000:
            print(f"  [{i}] ⊙ cached {voice_path.name}")
        else:
            tts(seg["text_voice"], voice_path)
            print(f"  [{i}] gen  {voice_path.name}")
        seg["voice_wav"] = voice_path  # (vẫn gọi key 'voice_wav' cho tương thích)
        seg["voice_dur"] = audio_duration(voice_path)

    # 3. Pick scene + trim theo voice duration
    print(f"[2/5] Pick scenes + trim theo voice...")
    scenes = load_scene_library()
    print(f"  Library: {len(scenes)} scenes khả dụng")
    used_ids: set[str] = set()
    clip_paths: list[Path] = []

    for i, seg in enumerate(SEGMENTS, 1):
        pick = pick_scene(scenes, seg["keywords"], seg["voice_dur"], used_ids)
        if not pick:
            raise SystemExit(f"Không pick được scene cho segment {i}: {seg['text_subtitle']}")
        used_ids.add(f"{pick.get('source_video_id')}_{pick.get('scene_index')}")

        mp4_path = pick["_mp4_path"]
        print(f"  [{i}] pick {mp4_path.name} ({pick.get('source_views'):,}v, "
              f"dur {pick.get('duration_sec'):.1f}s) trim→ {seg['voice_dur']:.2f}s")

        stage1 = TMP_DIR / f"clip_{i:02d}_raw.mp4"
        stage2 = TMP_DIR / f"clip_{i:02d}_overlay.mp4"

        trim_scene_portrait(mp4_path, seg["voice_dur"], stage1)

        sub_png = TMP_DIR / f"sub_{i:02d}.png"
        render_subtitle_png(seg["text_subtitle"], sub_png)
        overlay_label_and_subtitle(stage1, label_png, sub_png, stage2)

        clip_paths.append(stage2)
        seg["picked_source"] = str(mp4_path.relative_to(ROOT))

    # 4. Concat video + concat audio
    print(f"[3/5] Concat video + audio...")
    concat_v = TMP_DIR / "concat_video.mp4"
    concat_a = TMP_DIR / "concat_audio.mp3"
    concat_clips(clip_paths, concat_v)
    concat_audio([s["voice_wav"] for s in SEGMENTS], concat_a)

    # 5. Mux final — 1 file duy nhất trong final/, tên = caption
    final_path = FINAL_DIR / FINAL_NAME
    print(f"[4/4] Mux → {final_path.name}")
    mux_audio(concat_v, concat_a, final_path)

    # Meta bên cạnh
    total_dur = sum(s["voice_dur"] for s in SEGMENTS)
    meta = {
        "caption": CAPTION,
        "label_persistent": LABEL_TEXT,
        "total_duration": total_dur,
        "build_date": time.strftime("%Y-%m-%d %H:%M"),
        "script_version": "build-quecay-concept-v4.py",
        "segments": [
            {"idx": i, "voice_dur": s["voice_dur"],
             "text_voice": s["text_voice"], "text_subtitle": s["text_subtitle"],
             "keywords": s["keywords"], "picked_scene": s["picked_source"]}
            for i, s in enumerate(SEGMENTS, 1)
        ],
        "final_path": str(final_path.relative_to(ROOT)),
    }
    meta_path = FINAL_DIR / f"{FINAL_NAME}.meta.json"
    with meta_path.open("w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)

    print(f"\n✓ Duration : {total_dur:.2f}s")
    print(f"✓ Final    : {final_path.relative_to(ROOT)}")
    print(f"✓ Meta     : {meta_path.relative_to(ROOT)}")
    print(f"\nUpload thẳng file lên TikTok — caption tự fill từ tên.")


if __name__ == "__main__":
    main()
