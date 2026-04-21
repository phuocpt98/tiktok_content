"""
Build Day 1 theo 14-day calendar: Phonk macro close-up (Que Cay).

Plan: `plans/260424-1030-pel-pel-14day-calendar/plan.md` § Day 1.

Flow (voice-first như v4):
  1. TTS 3 segment (hook + body + CTA) qua Gemini TTS (Kore nữ) hoặc edge-tts (NamMinh nam fallback)
  2. Scan 2 folder scene sources (scene-library + competitor-scenes/*/)
  3. Pick scene keyword-match + duration ≥ voice_dur
  4. Trim → concat → mux audio
  5. Output `final/<caption>.mp4` (silent video version, anh add Phonk trên TikTok editor)
"""
from __future__ import annotations

import asyncio
import json
import os
import shutil
import subprocess
import time
import wave
from pathlib import Path

from dotenv import load_dotenv
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")

PRODUCT_DIR = ROOT / "assets" / "products" / "que-cay"
SCENE_SOURCES = [
    ROOT / "assets" / "scene-library" / "que_cay",
    ROOT / "assets" / "products" / "que-cay" / "competitor-scenes",
]
OUTPUT_DIR = PRODUCT_DIR / "output"
FINAL_DIR = OUTPUT_DIR / "final"
TMP_DIR = OUTPUT_DIR / "_tmp_day1"

CAPTION = "Đừng xem nếu bạn sợ cay #quecay #anvat #quecayhangdai #doanvat #anvattuoitho"
FINAL_NAME = f"{CAPTION}.mp4"

LABEL_TEXT = "QUE CAY • PEL PEL"
LABEL_Y = 280

# Silent mode: không gen TTS. Anh gõ text_voice làm caption TikTok,
# editor TikTok đọc bằng TTS AI. Subtitle burn-in giúp algorithm parse content.
SILENT_MODE = True  # TTS engines đều fail hôm nay (Gemini quota + edge-tts block)
SEGMENTS = [
    {
        "text_voice":    "Đừng xem nếu bạn sợ cay!",
        "text_subtitle": "Đừng xem nếu bạn sợ cay!",
        "keywords":      ["quecay", "que cay"],
        "prefer_views":  3_000_000,
        "fixed_duration": 2.5,  # dùng khi SILENT_MODE
    },
    {
        "text_voice":    "Que cay siêu dài, dầu ớt tứa ra, cắn giòn rụm!",
        "text_subtitle": "Siêu dài • Giòn rụm • Cay nồng",
        "keywords":      ["hangdai", "hằng đại", "siu siu", "thần long", "to dài"],
        "prefer_views":  1_000_000,
        "fixed_duration": 5.0,
    },
    {
        "text_voice":    "Thử thách bản thân, vào giỏ hàng mua ngay!",
        "text_subtitle": "Bấm giỏ hàng MUA NGAY",
        "keywords":      ["quecay", "ngon"],
        "prefer_views":  100_000,
        "fixed_duration": 3.0,
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
    draw.rounded_rectangle([(0, 0), (width - 1, height - 1)], radius=height // 2, fill=(255, 107, 0, 220))
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
    draw.rounded_rectangle([(20, box_top - 20), (width - 20, box_top + total_h)],
                           radius=25, fill=(0, 0, 0, 180))
    for i, line in enumerate(lines):
        bbox = draw.textbbox((0, 0), line, font=font)
        tx = (width - (bbox[2] - bbox[0])) // 2
        ty = box_top + i * line_h
        draw.text((tx, ty), line, font=font, fill=(255, 255, 255, 255),
                  stroke_width=2, stroke_fill=(0, 0, 0, 255))
    img.save(out, "PNG")


# ── TTS: Gemini (nữ Kore) → fallback edge-tts (NamMinh nam) ────────────

def tts_gemini(text: str, out_wav: Path) -> bool:
    """Thử Gemini TTS Kore (nữ). Trả True nếu thành công."""
    try:
        from google import genai
        from google.genai import types
    except ImportError:
        return False
    try:
        client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
        resp = client.models.generate_content(
            model="gemini-2.5-flash-preview-tts", contents=text,
            config=types.GenerateContentConfig(
                response_modalities=["AUDIO"],
                speech_config=types.SpeechConfig(
                    voice_config=types.VoiceConfig(
                        prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name="Kore")
                    )
                ),
            ),
        )
        pcm = None
        for p in resp.candidates[0].content.parts:
            if hasattr(p, "inline_data") and p.inline_data:
                pcm = p.inline_data.data; break
        if pcm is None: return False
        with wave.open(str(out_wav), "wb") as wf:
            wf.setnchannels(1); wf.setsampwidth(2); wf.setframerate(24000)
            wf.writeframes(pcm)
        return True
    except Exception as e:
        print(f"    ⚠ Gemini TTS fail: {str(e)[:80]}")
        return False


def tts_edge(text: str, out_mp3: Path) -> None:
    """Fallback edge-tts NamMinh (nam)."""
    import edge_tts
    async def _gen():
        c = edge_tts.Communicate(text, "vi-VN-NamMinhNeural", rate="+10%")
        await c.save(str(out_mp3))
    asyncio.run(_gen())


def tts(text: str, out_dir: Path, idx: int) -> Path:
    """Gen voice, ưu tiên Gemini (nữ). Trả path file audio."""
    wav_path = out_dir / f"voice_{idx:02d}.wav"
    mp3_path = out_dir / f"voice_{idx:02d}.mp3"
    # Cache check
    for p in [wav_path, mp3_path]:
        if p.exists() and p.stat().st_size > 1000:
            return p
    # Try Gemini
    if tts_gemini(text, wav_path):
        return wav_path
    # Fallback edge-tts
    tts_edge(text, mp3_path)
    return mp3_path


def audio_duration(path: Path) -> float:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(path)],
        capture_output=True, text=True,
    ).stdout.strip()
    return float(out) if out else 0.0


# ── Scene picker ───────────────────────────────────────────────────────

def load_all_scenes() -> list[dict]:
    scenes = []
    for src in SCENE_SOURCES:
        if not src.exists(): continue
        for j in src.rglob("*.json"):
            try:
                with j.open() as f:
                    d = json.load(f)
                mp4 = j.with_suffix(".mp4")
                if not mp4.exists(): continue
                if (d.get("duration_sec") or 0) < 1.5: continue
                d["_mp4_path"] = mp4
                d["_id_key"] = f"{d.get('source_author')}_{d.get('source_video_id')}_{d.get('scene_index')}"
                scenes.append(d)
            except Exception:
                continue
    return scenes


def pick_scene(scenes: list[dict], keywords: list[str], min_duration: float,
               prefer_views: int, used_ids: set[str]) -> dict | None:
    """Score theo: keyword match + views ≥ prefer. Fallback any scene đủ duration."""
    candidates = []
    for s in scenes:
        if s["_id_key"] in used_ids: continue
        if (s.get("duration_sec") or 0) < min_duration: continue
        caption = (s.get("source_caption") or "").lower()
        hashtags = " ".join(str(s.get("source_caption") or "")).lower()
        text = caption + " " + hashtags
        kw_score = sum(1 for k in keywords if k.lower() in text)
        views = s.get("source_views") or 0
        view_score = 2 if views >= prefer_views else (1 if views >= prefer_views // 10 else 0)
        total = kw_score * 3 + view_score
        if total > 0:
            candidates.append((total, views, s))
    candidates.sort(key=lambda x: (-x[0], -x[1]))
    return candidates[0][2] if candidates else None


# ── Video processing ───────────────────────────────────────────────────

def standardize_portrait(src: Path, duration: float, out: Path) -> None:
    vf = (
        "scale=-1:1920:force_original_aspect_ratio=increase,"
        "crop=1080:1920:(iw-1080)/2:0,setsar=1,fps=30"
    )
    cmd = [
        "ffmpeg", "-y", "-i", str(src), "-t", f"{duration}",
        "-vf", vf, "-an",
        "-c:v", "libx264", "-preset", "fast", "-crf", "21",
        "-pix_fmt", "yuv420p",
        str(out),
    ]
    run(cmd)


def overlay_label_subtitle(video: Path, label_png: Path, subtitle_png: Path, out: Path) -> None:
    cmd = [
        "ffmpeg", "-y",
        "-i", str(video), "-i", str(label_png), "-i", str(subtitle_png),
        "-filter_complex",
        (f"[0:v][1:v]overlay=(main_w-overlay_w)/2:{LABEL_Y}[v1];"
         f"[v1][2:v]overlay=(main_w-overlay_w)/2:1580[vo]"),
        "-map", "[vo]",
        "-c:v", "libx264", "-preset", "fast", "-crf", "21",
        "-pix_fmt", "yuv420p", "-an",
        str(out),
    ]
    run(cmd)


def concat_clips(paths: list[Path], out: Path) -> None:
    listf = TMP_DIR / "concat_v.txt"
    with listf.open("w") as f:
        for p in paths:
            f.write(f"file '{p.resolve()}'\n")
    run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(listf),
         "-c", "copy", str(out)])


def concat_audio(paths: list[Path], out: Path) -> None:
    listf = TMP_DIR / "concat_a.txt"
    with listf.open("w") as f:
        for p in paths:
            f.write(f"file '{p.resolve()}'\n")
    run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(listf),
         "-c:a", "libmp3lame", "-q:a", "2", str(out)])


def mux(video: Path, audio: Path, out: Path) -> None:
    run(["ffmpeg", "-y", "-i", str(video), "-i", str(audio),
         "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
         "-movflags", "+faststart", str(out)])


# ── Main ───────────────────────────────────────────────────────────────

def main():
    FINAL_DIR.mkdir(parents=True, exist_ok=True)
    TMP_DIR.mkdir(parents=True, exist_ok=True)

    print("── Build Day 1 — Phonk Macro Close-up ─────────")

    label_png = TMP_DIR / "label.png"
    render_label_png(LABEL_TEXT, label_png)

    if SILENT_MODE:
        print(f"[1/4] SILENT MODE — skip TTS, dùng fixed_duration per segment")
        for i, seg in enumerate(SEGMENTS, 1):
            seg["voice_dur"] = seg["fixed_duration"]
            seg["voice_path"] = None
            print(f"  [{i}] {seg['voice_dur']:.1f}s — \"{seg['text_voice'][:45]}\"")
    else:
        print(f"[1/4] TTS per segment...")
        for i, seg in enumerate(SEGMENTS, 1):
            voice_path = tts(seg["text_voice"], TMP_DIR, i)
            seg["voice_path"] = voice_path
            seg["voice_dur"] = audio_duration(voice_path)
            print(f"  [{i}] {voice_path.suffix} {seg['voice_dur']:.2f}s — \"{seg['text_voice'][:45]}\"")

    print(f"[2/4] Pick + trim scenes...")
    scenes = load_all_scenes()
    print(f"  Library: {len(scenes)} scenes")
    used_ids = set()
    clip_paths = []

    for i, seg in enumerate(SEGMENTS, 1):
        pick = pick_scene(scenes, seg["keywords"], seg["voice_dur"],
                          seg["prefer_views"], used_ids)
        if not pick:
            raise SystemExit(f"Không pick được scene cho seg {i}")
        used_ids.add(pick["_id_key"])

        mp4 = pick["_mp4_path"]
        print(f"  [{i}] {mp4.name} ({pick.get('source_views'):,}v, "
              f"dur {pick.get('duration_sec'):.1f}s → {seg['voice_dur']:.2f}s)")

        stage1 = TMP_DIR / f"clip_{i:02d}_raw.mp4"
        stage2 = TMP_DIR / f"clip_{i:02d}_overlay.mp4"
        standardize_portrait(mp4, seg["voice_dur"], stage1)

        sub_png = TMP_DIR / f"sub_{i:02d}.png"
        render_subtitle_png(seg["text_subtitle"], sub_png)
        overlay_label_subtitle(stage1, label_png, sub_png, stage2)

        clip_paths.append(stage2)
        seg["picked_source"] = str(mp4.relative_to(ROOT))

    print(f"[3/4] Concat video...")
    concat_v = TMP_DIR / "concat_video.mp4"
    concat_clips(clip_paths, concat_v)

    final_path = FINAL_DIR / FINAL_NAME
    if SILENT_MODE:
        print(f"[4/4] Finalize silent → {final_path.name}")
        # Copy + faststart (silent, ready cho TikTok editor add voice/music)
        run(["ffmpeg", "-y", "-i", str(concat_v),
             "-c", "copy", "-movflags", "+faststart", str(final_path)])
    else:
        concat_a = TMP_DIR / "concat_audio.mp3"
        concat_audio([s["voice_path"] for s in SEGMENTS], concat_a)
        print(f"[4/4] Mux → {final_path.name}")
        mux(concat_v, concat_a, final_path)

    total_dur = sum(s["voice_dur"] for s in SEGMENTS)
    meta = {
        "caption": CAPTION, "day": 1, "concept": "Phonk Macro Close-up",
        "total_duration": total_dur,
        "segments": [
            {"idx": i, "voice_dur": s["voice_dur"],
             "text_voice": s["text_voice"], "text_subtitle": s["text_subtitle"],
             "picked_scene": s["picked_source"]}
            for i, s in enumerate(SEGMENTS, 1)
        ],
    }
    (FINAL_DIR / f"{FINAL_NAME}.meta.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"\n✓ Duration : {total_dur:.2f}s")
    print(f"✓ Final    : {final_path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
