"""
Build Serial chương 1: "Khởi hành — Hằng Đại"

Format: review + storytelling, 4 segment (hook story + story chunk + review + CTA).
Concept: `assets/content-ideas/que-cay-serial-storytelling.md`
Spec format: `docs/video-production-format.md`

Khác `build-quecay-concept-v4.py`:
  - Có series badge `#1` góc trái-dưới (Pillow PNG overlay)
  - Voice tone narrative (slower rate +5%)
  - 4 segment thay 3 (hook + story + review + CTA)
"""
from __future__ import annotations

import asyncio
import json
import os
import subprocess
import time
import wave
from pathlib import Path

import edge_tts
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
TMP_DIR = OUTPUT_DIR / "_tmp_serial_ch1"

SERIES_NAME = "moi-tinh-dau-5-chuong"
CHAPTER_NUM = 1
# Câu đầu RÚT GỌN cho thumbnail + caption (giữ ý chính, dễ scan trong 0.5s)
CHAPTER_FIRST_SENTENCE = "Nếu cả đời này không thể yêu nữa thì sao?"
CAPTION = f"{CHAPTER_FIRST_SENTENCE} #tamsudemkhuya #moitinhdau #review #quecay #anvattuoitho #kechuyendem #pelpel"
FINAL_NAME = f"{CAPTION}.mp4"

# Video sản phẩm dùng làm BG thumbnail (thay nền đen)
THUMBNAIL_BG_VIDEO = ROOT / "assets" / "products" / "que-cay" / "videos" / "Appetizing_Beef_Stick_Slow_Motion.mp4"

LABEL_TEXT = "QUE CAY - PEL PEL"
LABEL_Y = 280

SERIES_BADGE_TEXT = f"#{CHAPTER_NUM}"
SERIES_BADGE_X = 20
SERIES_BADGE_Y = 1740

# Voice ưu tiên nam (drama tone trầm hợp truyện POV nam)
TTS_VOICE_PRIMARY = "vi-VN-NamMinhNeural"
TTS_VOICE_FALLBACK = "vi-VN-HoaiMyNeural"
TTS_RATE = "+25%"  # nhanh, ngắt câu ngắn — TikTok retention cao

SEGMENTS = [
    {
        # Block 0: THUMBNAIL — video sản phẩm làm BG + text overlay câu đầu rút gọn
        "type": "thumbnail_video",
        "name": "thumbnail",
        "text_voice":    CHAPTER_FIRST_SENTENCE,
        "text_subtitle": None,
        "thumbnail_text": CHAPTER_FIRST_SENTENCE,
        "bg_video":      THUMBNAIL_BG_VIDEO,
        "bg_video_start": 1.0,  # skip 1s đầu (cảnh đẹp hơn)
        "duration":      4.0,
    },
    {
        "type": "scene",
        "name": "story_a",
        # Dấu phẩy thay chấm → pause ngắn hơn
        "text_voice":    "Mối tình đầu vỏn vẹn năm tháng, mà đã gần một năm rồi, cơn bão ấy vẫn chưa tan.",
        "text_subtitle": "Năm tháng yêu, gần một năm cơn bão chưa tan",
        "keywords":      ["hangdai", "hằng đại"],
        "prefer_views":  2_000_000,
    },
    {
        "type": "scene",
        "name": "story_b",
        "text_voice":    "Nỗi nhớ len lỏi vào từng ngóc ngách trống trải, biến tình cảm dang dở thành vết thương buộc tôi lớn lên trong tàn nhẫn.",
        "text_subtitle": "Nỗi nhớ thành vết thương buộc tôi lớn lên",
        "keywords":      ["thần long", "than long", "to dài"],
        "prefer_views":  1_000_000,
    },
    {
        "type": "scene",
        "name": "cta",
        "text_voice":    "Tại sao tôi đánh mất em? Phần 2 sẽ tiết lộ — Follow xem tiếp.",
        "text_subtitle": "Tại sao tôi đánh mất em? Follow xem Phần 2",
        "keywords":      ["quecay", "ngon"],
        "prefer_views":  500_000,
    },
]


def run(cmd: list) -> None:
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


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
    draw.rounded_rectangle([(0, 0), (width-1, height-1)], radius=height//2, fill=(255, 107, 0, 220))
    font = find_vi_font(58)
    bbox = draw.textbbox((0, 0), text, font=font)
    draw.text(((width-(bbox[2]-bbox[0]))//2, (height-(bbox[3]-bbox[1]))//2-bbox[1]),
              text, font=font, fill=(255, 255, 255), stroke_width=3, stroke_fill=(0, 0, 0))
    img.save(out, "PNG")


def render_series_badge_png(text: str, out: Path, width: int = 140, height: int = 80) -> None:
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.rounded_rectangle([(0, 0), (width-1, height-1)], radius=30, fill=(0, 0, 0, 200))
    font = find_vi_font(56)
    bbox = draw.textbbox((0, 0), text, font=font)
    draw.text(((width-(bbox[2]-bbox[0]))//2, (height-(bbox[3]-bbox[1]))//2-bbox[1]),
              text, font=font, fill=(255, 255, 255), stroke_width=2, stroke_fill=(0, 0, 0))
    img.save(out, "PNG")


def render_thumbnail_text_overlay(text: str, out: Path,
                                    width: int = 1080, height: int = 1920) -> None:
    """Render PNG transparent với text drama lớn + 'TÂM SỰ ĐÊM KHUYA' decoration.
    Dùng overlay lên video sản phẩm (BG)."""
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    font = find_vi_font(82)

    max_w = 920
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

    line_h = 108
    total_h = line_h * len(lines)
    box_top = (height - total_h) // 2

    # Box mờ phủ phía sau text cho readable trên video động
    pad = 40
    draw.rounded_rectangle(
        [(50, box_top - pad - 20), (width - 50, box_top + total_h + pad)],
        radius=30, fill=(0, 0, 0, 165)
    )

    for i, line in enumerate(lines):
        bbox = draw.textbbox((0, 0), line, font=font)
        tx = (width - (bbox[2]-bbox[0])) // 2
        ty = box_top + i * line_h
        draw.text((tx, ty - bbox[1]), line, font=font, fill=(255, 255, 255),
                  stroke_width=4, stroke_fill=(0, 0, 0))

    # Deco "TÂM SỰ ĐÊM KHUYA" pill phía trên
    deco_font = find_vi_font(46)
    deco = "TÂM SỰ ĐÊM KHUYA"
    db = draw.textbbox((0, 0), deco, font=deco_font)
    deco_w = db[2] - db[0] + 60
    deco_h = 78
    deco_x = (width - deco_w) // 2
    deco_y = 460
    draw.rounded_rectangle(
        [(deco_x, deco_y), (deco_x + deco_w, deco_y + deco_h)],
        radius=deco_h // 2, fill=(220, 50, 80, 230)
    )
    draw.text((deco_x + 30, deco_y + (deco_h - (db[3]-db[1]))//2 - db[1]),
              deco, font=deco_font, fill=(255, 255, 255),
              stroke_width=2, stroke_fill=(0, 0, 0))

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
    draw.rounded_rectangle([(20, box_top-20), (width-20, box_top+total_h)],
                           radius=25, fill=(0, 0, 0, 180))
    for i, line in enumerate(lines):
        bbox = draw.textbbox((0, 0), line, font=font)
        tx = (width - (bbox[2]-bbox[0])) // 2
        ty = box_top + i * line_h
        draw.text((tx, ty), line, font=font, fill=(255, 255, 255),
                  stroke_width=2, stroke_fill=(0, 0, 0))
    img.save(out, "PNG")


# ── TTS ────────────────────────────────────────────────────────────────

def tts_edge(text: str, voice: str, out_mp3: Path, retries: int = 3) -> bool:
    for attempt in range(retries):
        try:
            async def _g():
                c = edge_tts.Communicate(text, voice, rate=TTS_RATE)
                await c.save(str(out_mp3))
            asyncio.run(_g())
            if out_mp3.exists() and out_mp3.stat().st_size > 1000:
                return True
        except Exception:
            pass
        if out_mp3.exists() and out_mp3.stat().st_size < 1000:
            out_mp3.unlink()
        time.sleep(2 + attempt * 2)  # backoff 2s, 4s, 6s
    return False


def tts_gemini(text: str, out_wav: Path) -> bool:
    """Fallback Gemini TTS Kore (nữ). 10 req/day free tier."""
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
                        prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name="Charon")  # Charon = nam trầm drama
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
        print(f"    ⚠ Gemini TTS fail: {str(e)[:60]}")
        return False


def tts(text: str, out_dir: Path, idx: int) -> Path | None:
    """Trả path audio nếu OK, None nếu silent. Priority: edge-tts (3 retry) → Gemini → silent."""
    mp3 = out_dir / f"voice_{idx:02d}.mp3"
    wav = out_dir / f"voice_{idx:02d}.wav"
    if mp3.exists() and mp3.stat().st_size > 1000:
        return mp3
    if wav.exists() and wav.stat().st_size > 1000:
        return wav

    # Edge-tts với retry backoff
    for voice in [TTS_VOICE_PRIMARY, TTS_VOICE_FALLBACK]:
        if tts_edge(text, voice, mp3, retries=3):
            print(f"    ✓ edge-tts {voice}")
            return mp3

    # Fallback Gemini TTS
    if tts_gemini(text, wav):
        print(f"    ✓ Gemini Charon")
        return wav

    return None


def audio_duration(path: Path) -> float:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(path)],
        capture_output=True, text=True,
    ).stdout.strip()
    return float(out) if out else 0.0


# ── Scene picker ───────────────────────────────────────────────────────

def load_scenes() -> list[dict]:
    scenes = []
    for src in SCENE_SOURCES:
        if not src.exists(): continue
        for j in src.rglob("*.json"):
            try:
                d = json.load(j.open())
                mp4 = j.with_suffix(".mp4")
                if not mp4.exists() or (d.get("duration_sec") or 0) < 1.5: continue
                d["_mp4_path"] = mp4
                d["_id_key"] = f"{d.get('source_author')}_{d.get('source_video_id')}_{d.get('scene_index')}"
                scenes.append(d)
            except Exception: continue
    return scenes


def pick_scene(scenes, keywords, min_duration, prefer_views, used_ids):
    candidates = []
    for s in scenes:
        if s["_id_key"] in used_ids: continue
        if (s.get("duration_sec") or 0) < min_duration: continue
        cap = (s.get("source_caption") or "").lower()
        kw_score = sum(1 for k in keywords if k.lower() in cap)
        views = s.get("source_views") or 0
        view_score = 2 if views >= prefer_views else (1 if views >= prefer_views // 10 else 0)
        total = kw_score * 3 + view_score
        if total > 0:
            candidates.append((total, views, s))
    candidates.sort(key=lambda x: (-x[0], -x[1]))
    return candidates[0][2] if candidates else None


# ── Video processing ───────────────────────────────────────────────────

def standardize_portrait(src: Path, duration: float, out: Path) -> None:
    vf = ("scale=-1:1920:force_original_aspect_ratio=increase,"
          "crop=1080:1920:(iw-1080)/2:0,setsar=1,fps=30")
    run(["ffmpeg", "-y", "-i", str(src), "-t", f"{duration}",
         "-vf", vf, "-an",
         "-c:v", "libx264", "-preset", "fast", "-crf", "21",
         "-pix_fmt", "yuv420p", str(out)])


def standardize_portrait_from(src: Path, start: float, duration: float, out: Path) -> None:
    """Như standardize_portrait nhưng có start offset."""
    vf = ("scale=-1:1920:force_original_aspect_ratio=increase,"
          "crop=1080:1920:(iw-1080)/2:0,setsar=1,fps=30")
    run(["ffmpeg", "-y", "-ss", f"{start}", "-i", str(src), "-t", f"{duration}",
         "-vf", vf, "-an",
         "-c:v", "libx264", "-preset", "fast", "-crf", "21",
         "-pix_fmt", "yuv420p", str(out)])


def overlay_label_subtitle_badge(video: Path, label_png: Path, subtitle_png: Path,
                                  badge_png: Path, out: Path) -> None:
    """Overlay 3 lớp: label top + subtitle bottom + series badge bottom-left."""
    cmd = [
        "ffmpeg", "-y",
        "-i", str(video),
        "-i", str(label_png),
        "-i", str(subtitle_png),
        "-i", str(badge_png),
        "-filter_complex",
        (f"[0:v][1:v]overlay=(main_w-overlay_w)/2:{LABEL_Y}[v1];"
         f"[v1][2:v]overlay=(main_w-overlay_w)/2:1580[v2];"
         f"[v2][3:v]overlay={SERIES_BADGE_X}:{SERIES_BADGE_Y}[vo]"),
        "-map", "[vo]",
        "-c:v", "libx264", "-preset", "fast", "-crf", "21",
        "-pix_fmt", "yuv420p", "-an",
        str(out),
    ]
    run(cmd)


def concat_clips(paths: list[Path], out: Path) -> None:
    listf = TMP_DIR / "concat_v.txt"
    with listf.open("w") as f:
        for p in paths: f.write(f"file '{p.resolve()}'\n")
    run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(listf),
         "-c", "copy", str(out)])


def concat_audio(paths: list[Path], out: Path) -> None:
    listf = TMP_DIR / "concat_a.txt"
    with listf.open("w") as f:
        for p in paths: f.write(f"file '{p.resolve()}'\n")
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

    print(f"── Build Serial '{SERIES_NAME}' chương {CHAPTER_NUM} ──")

    label_png = TMP_DIR / "label.png"
    badge_png = TMP_DIR / "badge.png"
    render_label_png(LABEL_TEXT, label_png)
    render_series_badge_png(SERIES_BADGE_TEXT, badge_png)

    print(f"[1/4] TTS (edge-tts retry → Gemini Charon fallback)...")
    silent_mode = False
    for i, seg in enumerate(SEGMENTS, 1):
        voice_path = tts(seg["text_voice"], TMP_DIR, i)
        if voice_path is None:
            silent_mode = True
            seg["voice_path"] = None
            seg["voice_dur"] = seg.get("duration", 4.0)
            print(f"  [{i}] silent {seg['voice_dur']}s — \"{seg['text_voice'][:50]}\"")
        else:
            seg["voice_path"] = voice_path
            seg["voice_dur"] = audio_duration(voice_path)
            print(f"  [{i}] {seg['voice_dur']:.2f}s — \"{seg['text_voice'][:50]}\"")

    print(f"[2/4] Build clips (slide thumbnail + scenes)...")
    scenes = load_scenes()
    print(f"  Library: {len(scenes)} scenes")
    used_ids = set()
    clip_paths = []

    for i, seg in enumerate(SEGMENTS, 1):
        stage_final = TMP_DIR / f"clip_{i:02d}_final.mp4"

        if seg.get("type") == "thumbnail_video":
            # BG = video sản phẩm, overlay text drama center + label + badge
            bg = seg["bg_video"]
            start = seg.get("bg_video_start", 0)
            stage_bg = TMP_DIR / f"clip_{i:02d}_bg.mp4"
            standardize_portrait_from(bg, start, seg["voice_dur"], stage_bg)

            text_png = TMP_DIR / f"thumb_text_{i:02d}.png"
            render_thumbnail_text_overlay(seg["thumbnail_text"], text_png)

            run([
                "ffmpeg", "-y",
                "-i", str(stage_bg),
                "-i", str(label_png),
                "-i", str(text_png),
                "-i", str(badge_png),
                "-filter_complex",
                (f"[0:v][1:v]overlay=(main_w-overlay_w)/2:{LABEL_Y}[v1];"
                 f"[v1][2:v]overlay=0:0[v2];"
                 f"[v2][3:v]overlay={SERIES_BADGE_X}:{SERIES_BADGE_Y}[vo]"),
                "-map", "[vo]",
                "-c:v", "libx264", "-preset", "fast", "-crf", "21",
                "-pix_fmt", "yuv420p", "-an",
                str(stage_final),
            ])
            print(f"  [{i}] {seg['name']:10s} thumbnail BG={bg.name} ({seg['voice_dur']:.2f}s)")

        else:
            pick = pick_scene(scenes, seg["keywords"], seg["voice_dur"],
                              seg["prefer_views"], used_ids)
            if not pick:
                raise SystemExit(f"Không pick được scene cho seg {i} ({seg['name']})")
            used_ids.add(pick["_id_key"])
            mp4 = pick["_mp4_path"]
            print(f"  [{i}] {seg['name']:10s} ← {mp4.name} ({pick.get('source_views'):,}v, {pick.get('duration_sec'):.1f}s → {seg['voice_dur']:.2f}s)")

            stage1 = TMP_DIR / f"clip_{i:02d}_raw.mp4"
            standardize_portrait(mp4, seg["voice_dur"], stage1)

            sub_png = TMP_DIR / f"sub_{i:02d}.png"
            render_subtitle_png(seg["text_subtitle"], sub_png)
            overlay_label_subtitle_badge(stage1, label_png, sub_png, badge_png, stage_final)

            seg["picked_source"] = str(mp4.relative_to(ROOT))

        clip_paths.append(stage_final)

    print(f"[3/4] Concat...")
    concat_v = TMP_DIR / "concat_video.mp4"
    concat_clips(clip_paths, concat_v)

    final_path = FINAL_DIR / FINAL_NAME
    if silent_mode:
        print(f"[4/4] Silent finalize → {final_path.name}")
        run(["ffmpeg", "-y", "-i", str(concat_v),
             "-c", "copy", "-movflags", "+faststart", str(final_path)])
    else:
        concat_a = TMP_DIR / "concat_audio.mp3"
        concat_audio([s["voice_path"] for s in SEGMENTS], concat_a)
        print(f"[4/4] Mux → {final_path.name}")
        mux(concat_v, concat_a, final_path)

    total_dur = sum(s["voice_dur"] for s in SEGMENTS)
    meta = {
        "caption": CAPTION,
        "series_name": SERIES_NAME,
        "chapter_num": CHAPTER_NUM,
        "chapter_title": "Khởi hành — Hằng Đại",
        "total_duration": total_dur,
        "silent_mode": silent_mode,
        "segments": [
            {"idx": i, "name": s["name"], "voice_dur": s["voice_dur"],
             "text_voice": s["text_voice"], "text_subtitle": s["text_subtitle"],
             "picked_scene": s.get("picked_source")}
            for i, s in enumerate(SEGMENTS, 1)
        ],
    }
    (FINAL_DIR / f"{FINAL_NAME}.meta.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"\n✓ Duration : {total_dur:.2f}s ({'silent' if silent_mode else 'with voice'})")
    print(f"✓ Final    : {final_path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
