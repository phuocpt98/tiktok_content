"""
Build concept "Vua Tiếng Việt" cho que cay (CAT 12 format, 4-part).

Cấu trúc: Hook question slide → Review scenes → Answer slide → Invite slide.
Voice: vi-VN-HoaiMyNeural (nữ miền Nam, brand Pel Pel "công chúa").

Usage:
  python3 scripts/build-quecay-vua-tieng-viet.py --concept 4
  python3 scripts/build-quecay-vua-tieng-viet.py --concept 5

Output: assets/products/que-cay/output/final/<CAPTION>.mp4
"""
from __future__ import annotations

import argparse
import json
import random
import subprocess
import sys
import tempfile
from pathlib import Path

import os
import wave
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parent.parent

# Load .env cho GEMINI_API_KEY
_env = ROOT / ".env"
if _env.exists():
    for line in _env.read_text().splitlines():
        if "=" in line and not line.strip().startswith("#"):
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())
PRODUCT = ROOT / "assets" / "products" / "que-cay"
PHOTOS = PRODUCT / "photos"
COMP_BEHEOBU = ROOT / "assets" / "scene-library" / "que_cay"  # 296 scenes
COMP_YEN = PRODUCT / "competitor-scenes" / "yen_doanvathot"  # 27 scenes
FINAL = PRODUCT / "output" / "final"

W, H = 1080, 1920
FPS = 30
FONT = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"

TTS_VOICE = "vi-VN-NamMinhNeural"   # HoaiMy (nữ) bị MS block cho text dài → fallback NamMinh (nam)
TTS_RATE = "+10%"                    # nói hơi nhanh, NamMinh xử lý rate OK

# Product label + subtitle canonical spec (docs/video-production-format.md)
PRODUCT_LABEL = "QUE CAY - PEL PEL"
LABEL_CANVAS = (900, 140)            # PNG size
LABEL_COLOR = (255, 107, 0, 220)     # cam Pel Pel (rgba)
LABEL_FONT_SIZE = 58
LABEL_Y = 280                         # overlay y absolute

SUBTITLE_CANVAS = (1000, 200)
SUBTITLE_BG = (0, 0, 0, 180)
SUBTITLE_FONT_SIZE = 62
SUBTITLE_Y = 1580                     # overlay y absolute

# ─────────────────────────────────────────────────────────────────────
# CONCEPT CONFIGS
# ─────────────────────────────────────────────────────────────────────
CONCEPTS = {
    4: {
        "slug": "xuyt-xoa-suyt-xoa",
        "tint": (180, 40, 30),       # đỏ cam signature
        "hue_shift": 5,               # scene hue +5°
        "slide_seeds": [4001, 4002, 4003],   # 3 slide khác photo
        "caption": "XUÝT XOA hay SUÝT XOA khi cay quá - 90% người viết sai 👑 #vuativiet #chinhta #quecay #doanvat #fyp",
        "hook_lines": ["XUÝT XOA", "hay", "SUÝT XOA?"],
        "answer_lines": ["✅  XUÝT XOA", "❌  SUÝT XOA"],
        "answer_explain": "Xuýt = âm huýt qua răng khi cay",
        "invite_lines": ["Thả TYM + FOLLOW", "để mỗi ngày 1 câu đố!", "Comment đáp án nha cưng 💕"],
        "voice": {
            "hook":   "Đố các đỉnh cao tiếng Việt nha — ăn cay quá thốt lên XUÝT XOA hay SUÝT XOA mới đúng?",
            "review": "Que cay Vương Thần Long nè — dài ngoằng, cay tê lưỡi luôn. Nàng nào ăn mà vẫn viết đúng chính tả là đẳng cấp ngôn ngữ đó công chúa!",
            "answer": "Đáp án là XUÝT XOA nha! Xuýt là âm huýt qua răng khi cay quá chịu không nổi đó!",
            "invite": "Ai viết đúng comment XUÝT XOA nha cưng! Thả tym và bấm follow em để mỗi ngày một câu đố vui đỉnh cao nha mấy nàng!",
        },
    },
    5: {
        "slug": "cay-xe-cay-xe",
        "tint": (90, 30, 130),        # tím signature (khác concept 4)
        "hue_shift": -8,              # scene hue -8° (ngược concept 4)
        "slide_seeds": [5101, 5202, 5303],
        "caption": "CAY XÉ hay CAY XÈ lưỡi - cả 2 đều đúng á 🌶️ #vuativiet #quecay #minigame #doanvat #fyp",
        "hook_lines": ["Ăn que cay xong:", "CAY XÉ", "hay CAY XÈ?"],
        "answer_lines": ["CẢ 2 ĐỀU ĐÚNG 😎"],
        "answer_explain": "XÉ = mức độ mạnh.  XÈ = cảm giác tê lan",
        "invite_lines": ["Team XÉ hay team XÈ?", "Thả TYM + FOLLOW", "mỗi ngày 1 câu đố vui 💕"],
        "voice": {
            "hook":   "Ăn que cay xong thốt lên CAY XÉ hay CAY XÈ lưỡi — công chúa nào biết đáp án nè?",
            "review": "Que cay thần long cay tới mức mờ lem mờ lem luôn! Ăn xong miệng tê rát — nàng nào sành mới biết phân biệt hai chữ này đó!",
            "answer": "Bất ngờ chưa — cả hai đều đúng! Xé là mức độ mạnh như xé lưỡi, còn xè là cảm giác tê lan toả!",
            "invite": "Team Xé hay team Xè comment team mình nha cưng! Thả tym và follow để mỗi ngày một câu đố vui đỉnh cao nhé!",
        },
    },
}


# ─────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────
def run(cmd, check=True):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if check and r.returncode != 0:
        print("CMD FAIL:", " ".join(map(str, cmd)))
        print(r.stderr[-1200:])
        raise SystemExit(1)
    return r


def probe_dur(path: Path) -> float:
    r = run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "json", str(path)])
    return float(json.loads(r.stdout)["format"]["duration"])


def _tts_single(text: str, voice: str, rate: str | None, out_path: Path, retries: int = 5) -> bool:
    """1 TTS call + retry sleep. Return True nếu OK."""
    import time as _time
    for attempt in range(retries):
        cmd = [sys.executable, "-m", "edge_tts", "--voice", voice]
        if rate:
            cmd += ["--rate", rate]
        cmd += ["--text", text, "--write-media", str(out_path)]
        r = run(cmd, check=False)
        if r.returncode == 0 and out_path.exists() and out_path.stat().st_size > 1000:
            return True
        _time.sleep(2 + attempt * 2)  # 2, 4, 6, 8, 10
    return False


def _gemini_tts(text: str, out_path: Path) -> bool:
    """Fallback: Gemini TTS (voice Kore, model gemini-2.5-flash-preview-tts).
    10 req/day free tier. Output 24kHz PCM → wrap WAV → convert to MP3."""
    try:
        from google import genai
        from google.genai import types
    except ImportError:
        return False
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return False
    try:
        client = genai.Client(api_key=api_key)
        resp = client.models.generate_content(
            model="gemini-2.5-flash-preview-tts",
            contents=text,
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
                pcm = p.inline_data.data
                break
        if not pcm:
            return False
        wav_tmp = out_path.with_suffix(".gemini.wav")
        with wave.open(str(wav_tmp), "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(24000)
            wf.writeframes(pcm)
        # Convert wav → mp3 để compatible concat pipeline
        run(["ffmpeg", "-y", "-i", str(wav_tmp),
             "-c:a", "libmp3lame", "-b:a", "192k", str(out_path)])
        wav_tmp.unlink(missing_ok=True)
        return out_path.exists() and out_path.stat().st_size > 1000
    except Exception as e:
        print(f"    Gemini TTS error: {type(e).__name__}: {str(e)[:100]}")
        return False


def gen_voice(text: str, out_path: Path):
    """3 fallback: (1) Edge TTS direct, (2) Edge chunking, (3) Gemini TTS."""
    # Strategy 1: Edge direct
    if _tts_single(text, TTS_VOICE, TTS_RATE, out_path, retries=2):
        return

    # Strategy 2: Edge chunking
    print(f"    [fallback] edge chunking...")
    import re as _re
    chunks = [c.strip() for c in _re.split(r"[.!?—]+", text) if c.strip()]
    if len(chunks) <= 1:
        chunks = [c.strip() for c in text.split(",") if c.strip()]

    all_ok = len(chunks) > 0
    chunk_mp3s = []
    tmp_dir = out_path.parent
    for i, ck in enumerate(chunks):
        ck_with_dot = ck if ck.endswith((".", "!", "?")) else ck + "."
        chunk_out = tmp_dir / f"{out_path.stem}_chunk_{i:02d}.mp3"
        ok = _tts_single(ck_with_dot, TTS_VOICE, TTS_RATE, chunk_out, retries=3)
        if not ok:
            ok = _tts_single(ck_with_dot, "vi-VN-NamMinhNeural", None, chunk_out, retries=3)
        if not ok:
            all_ok = False
            break
        chunk_mp3s.append(chunk_out)

    if all_ok and chunk_mp3s:
        list_f = tmp_dir / f"{out_path.stem}_chunks.txt"
        list_f.write_text("\n".join(f"file '{p.as_posix()}'" for p in chunk_mp3s) + "\n")
        run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(list_f),
             "-c:a", "copy", str(out_path)])
        print(f"    [edge chunked OK] {len(chunks)} câu")
        return

    # Strategy 3: Gemini TTS (quota 10/day)
    print(f"    [fallback] Gemini TTS...")
    if _gemini_tts(text, out_path):
        print(f"    [Gemini OK]")
        return

    # SILENT fallback (canonical): render silence MP3 với estimate duration
    est_dur = max(2.0, len(text) / 13.0)
    print(f"    [SILENT fallback: dur={est_dur:.1f}s]")
    run(["ffmpeg", "-y", "-f", "lavfi", "-i", f"anullsrc=r=44100:cl=mono",
         "-t", f"{est_dur:.3f}", "-c:a", "libmp3lame", "-b:a", "128k",
         str(out_path)])


# ─────────────────────────────────────────────────────────────────────
# Slide rendering (PIL)
# ─────────────────────────────────────────────────────────────────────
# Track đã chọn photo nào trong session (để mỗi slide pick DIFFERENT photo)
_BG_USED_IN_SESSION: list[Path] = []


def load_blur_background(seed: int, tint: tuple[int, int, int] = None) -> Image.Image:
    """Chọn 1 ảnh product làm background. Deterministic theo seed. Skip ảnh đã dùng.
    tint: RGB tuple cho color overlay signature (e.g. đỏ cho concept 4, tím cho 5).
    """
    candidates = (list(PHOTOS.glob("*.webp")) + list(PHOTOS.glob("*.jpg"))
                  + list(PHOTOS.glob("*.png")))
    candidates = sorted([p for p in candidates if not p.name.startswith("cover-")])
    if not candidates:
        raise SystemExit("Không có ảnh product để làm background")

    # Ưu tiên pick photo chưa dùng trong session
    unused = [p for p in candidates if p not in _BG_USED_IN_SESSION]
    pool = unused if unused else candidates
    rng = random.Random(seed)
    chosen = rng.choice(pool)
    _BG_USED_IN_SESSION.append(chosen)

    img = Image.open(chosen).convert("RGB")
    ratio = max(W / img.width, H / img.height)
    img = img.resize((int(img.width * ratio), int(img.height * ratio)), Image.LANCZOS)
    x = (img.width - W) // 2
    y = (img.height - H) // 2
    img = img.crop((x, y, x + W, y + H))
    img = img.filter(ImageFilter.GaussianBlur(radius=40))
    # Darken 35%
    dark = Image.new("RGB", (W, H), (0, 0, 0))
    img = Image.blend(img, dark, 0.35)
    # Color tint signature per concept (subtle 12%)
    if tint:
        tint_layer = Image.new("RGB", (W, H), tint)
        img = Image.blend(img, tint_layer, 0.12)
    return img


def draw_multi_line(draw: ImageDraw.ImageDraw, lines: list[str], fonts: list[ImageFont.FreeTypeFont],
                    colors: list[tuple], y_center: int, line_gap: int = 30,
                    stroke_width: int = 6, stroke_fill=(0, 0, 0)):
    """Vẽ nhiều dòng canh giữa, mỗi dòng có thể khác font/color."""
    assert len(lines) == len(fonts) == len(colors)
    # Measure tổng height
    heights = []
    for ln, fnt in zip(lines, fonts):
        bbox = draw.textbbox((0, 0), ln, font=fnt, stroke_width=stroke_width)
        heights.append(bbox[3] - bbox[1])
    total_h = sum(heights) + line_gap * (len(lines) - 1)
    y = y_center - total_h // 2
    for ln, fnt, col, h in zip(lines, fonts, colors, heights):
        bbox = draw.textbbox((0, 0), ln, font=fnt, stroke_width=stroke_width)
        w = bbox[2] - bbox[0]
        x = (W - w) // 2
        draw.text((x, y), ln, font=fnt, fill=col,
                  stroke_width=stroke_width, stroke_fill=stroke_fill)
        y += h + line_gap


def render_hook_slide(lines: list[str], out_png: Path, seed: int, tint=None):
    img = load_blur_background(seed, tint)
    d = ImageDraw.Draw(img)
    big = ImageFont.truetype(FONT, 130)
    small = ImageFont.truetype(FONT, 70)
    fonts, colors = [], []
    for ln in lines:
        if ln in ("hay", "Ăn que cay xong:", "hay CAY XÈ?"):
            fonts.append(small)
            colors.append((255, 230, 120))
        else:
            fonts.append(big)
            colors.append((255, 255, 255))
    draw_multi_line(d, lines, fonts, colors, y_center=H // 2, line_gap=40)
    img.save(out_png)


def render_answer_slide(lines: list[str], explain: str, out_png: Path, seed: int, tint=None):
    img = load_blur_background(seed, tint)
    d = ImageDraw.Draw(img)
    big = ImageFont.truetype(FONT, 110)
    small = ImageFont.truetype(FONT, 54)
    fonts, colors = [], []
    for ln in lines:
        if ln.startswith("✅") or "ĐÚNG" in ln:
            fonts.append(big)
            colors.append((120, 255, 160))
        elif ln.startswith("❌"):
            fonts.append(big)
            colors.append((255, 130, 130))
        else:
            fonts.append(big)
            colors.append((255, 255, 255))
    draw_multi_line(d, lines, fonts, colors, y_center=int(H * 0.42), line_gap=40)
    # Explain ở dưới
    bbox = d.textbbox((0, 0), explain, font=small, stroke_width=4)
    w = bbox[2] - bbox[0]
    d.text(((W - w) // 2, int(H * 0.70)), explain, font=small,
           fill=(240, 240, 240), stroke_width=4, stroke_fill=(0, 0, 0))
    img.save(out_png)


def render_product_label(text: str, out_png: Path):
    """Canonical: 900×140 PNG, pill cam, Arial 58pt trắng stroke 3px đen."""
    cw, ch = LABEL_CANVAS
    img = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    font = ImageFont.truetype(FONT, LABEL_FONT_SIZE)
    bbox = d.textbbox((0, 0), text, font=font, stroke_width=3)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    # Pill bo tròn toàn canvas
    d.rounded_rectangle([0, 0, cw - 1, ch - 1], radius=ch // 2, fill=LABEL_COLOR)
    # Center text
    x = (cw - tw) // 2
    y = (ch - th) // 2 - 4
    d.text((x, y), text, font=font, fill=(255, 255, 255, 255),
           stroke_width=3, stroke_fill=(0, 0, 0, 255))
    img.save(out_png)


def render_invite_slide(lines: list[str], out_png: Path, seed: int, tint=None):
    img = load_blur_background(seed, tint)
    d = ImageDraw.Draw(img)
    big = ImageFont.truetype(FONT, 90)
    fonts = [big] * len(lines)
    colors = [(255, 230, 120), (255, 255, 255), (255, 255, 255)][:len(lines)]
    while len(colors) < len(lines):
        colors.append((255, 255, 255))
    draw_multi_line(d, lines, fonts, colors, y_center=H // 2, line_gap=50)
    img.save(out_png)


# ─────────────────────────────────────────────────────────────────────
# Scene picking & video building
# ─────────────────────────────────────────────────────────────────────
def pick_review_scenes(target_total_sec: float, seed: int = 0) -> list[Path]:
    """Pick scenes sao cho:
    - Trộn từ CẢ 2 kênh (beheobu + yen) → chống self-similarity
    - KHÔNG lấy 2 scene từ cùng 1 video nguồn → chống pHash TikTok match
    - Ưu tiên top views, alternate author.
    """
    pools_by_author = {"beheobu0102": [], "yen_doanvathot": []}
    for scene_dir in (COMP_BEHEOBU, COMP_YEN):
        if not scene_dir.exists():
            continue
        for j in scene_dir.glob("*.json"):
            try:
                meta = json.loads(j.read_text())
                author = meta.get("source_author")
                views = meta.get("source_views") or 0
                dur = meta.get("duration_sec") or 0
                vid_id = meta.get("source_video_id")
                mp4 = j.with_suffix(".mp4")
                if author in pools_by_author and mp4.exists() and 1.5 <= dur <= 5.0:
                    pools_by_author[author].append((views, dur, vid_id, mp4))
            except Exception:
                continue

    # Sort desc theo views trong mỗi pool, rồi dedup theo video_id (giữ scene view cao nhất/video)
    for author, pool in pools_by_author.items():
        pool.sort(key=lambda x: x[0], reverse=True)
        seen_vids = set()
        dedup = []
        for entry in pool:
            vid_id = entry[2]
            if vid_id not in seen_vids:
                seen_vids.add(vid_id)
                dedup.append(entry)
        pools_by_author[author] = dedup

    # Mix shuffle nhẹ (seed khác nhau cho 2 concept ra 2 bộ scenes khác nhau)
    rng = random.Random(seed)
    for author in pools_by_author:
        # Lấy top 30 rồi shuffle để đa dạng hơn top fixed
        top = pools_by_author[author][:30]
        rng.shuffle(top)
        pools_by_author[author] = top

    # Alternate giữa 2 author: beheobu, yen, beheobu, yen...
    # Force tối thiểu 5 scenes, tối đa 8 (dù target sec thấp) → đa dạng scene nền
    picked = []
    total = 0.0
    a, b = pools_by_author["beheobu0102"], pools_by_author["yen_doanvathot"]
    i_a = i_b = 0
    turn_a = True
    min_scenes = 5
    while (total < target_total_sec or len(picked) < min_scenes) and len(picked) < 8:
        if turn_a and i_a < len(a):
            _, dur, _, mp4 = a[i_a]
            picked.append(mp4)
            total += dur
            i_a += 1
        elif not turn_a and i_b < len(b):
            _, dur, _, mp4 = b[i_b]
            picked.append(mp4)
            total += dur
            i_b += 1
        elif i_a < len(a):
            _, dur, _, mp4 = a[i_a]
            picked.append(mp4)
            total += dur
            i_a += 1
        elif i_b < len(b):
            _, dur, _, mp4 = b[i_b]
            picked.append(mp4)
            total += dur
            i_b += 1
        else:
            break
        turn_a = not turn_a

    print(f"    mix: {sum(1 for p in picked if 'beheobu' in p.name)} beheobu + "
          f"{sum(1 for p in picked if 'yen_' in p.name)} yen")
    return picked


def scale_to_canvas(src: Path, tmp: Path, out: Path, hue_shift: int = 0,
                    zoom: float = 1.0):
    """Scale + pad to 1080x1920, remove audio. Optional hue shift (degrees) + zoom
    để tạo concept-specific signature, chống pHash TikTok detect reup."""
    vf = (f"scale={W}:{H}:force_original_aspect_ratio=decrease,"
          f"pad={W}:{H}:(ow-iw)/2:(oh-ih)/2:color=black,"
          f"setsar=1,fps={FPS}")
    if zoom != 1.0:
        zw = int(W * zoom)
        zh = int(H * zoom)
        crop_x = (zw - W) // 2
        crop_y = (zh - H) // 2
        vf += f",scale={zw}:{zh},crop={W}:{H}:{crop_x}:{crop_y}"
    if hue_shift:
        vf += f",hue=h={hue_shift}"
    run([
        "ffmpeg", "-y", "-i", str(src),
        "-vf", vf,
        "-an", "-c:v", "libx264", "-preset", "veryfast",
        "-pix_fmt", "yuv420p", str(out)
    ])


def slide_to_video(png: Path, duration: float, out: Path):
    """Convert PNG → MP4 with given duration (still image)."""
    run([
        "ffmpeg", "-y", "-loop", "1", "-i", str(png),
        "-t", f"{duration:.3f}", "-r", f"{FPS}",
        "-vf", f"scale={W}:{H}:force_original_aspect_ratio=decrease,"
               f"pad={W}:{H}:(ow-iw)/2:(oh-ih)/2,setsar=1",
        "-c:v", "libx264", "-preset", "veryfast",
        "-pix_fmt", "yuv420p", str(out)
    ])


def concat_videos(parts: list[Path], out: Path, tmp_dir: Path):
    list_f = tmp_dir / "concat.txt"
    list_f.write_text("\n".join(f"file '{p.as_posix()}'" for p in parts) + "\n")
    run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(list_f),
         "-c:v", "libx264", "-preset", "veryfast", "-pix_fmt", "yuv420p",
         "-an", str(out)])


def concat_audios(parts: list[Path], out: Path, tmp_dir: Path):
    """Dùng filter_complex concat (reliable hơn demuxer khi mix codec/silence)."""
    inputs = []
    for p in parts:
        inputs += ["-i", str(p)]
    n = len(parts)
    filter_str = "".join(f"[{i}:a]" for i in range(n)) + f"concat=n={n}:v=0:a=1[out]"
    run(["ffmpeg", "-y"] + inputs +
        ["-filter_complex", filter_str, "-map", "[out]",
         "-c:a", "aac", "-b:a", "192k", str(out)])


# ─────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--concept", type=int, choices=[4, 5], required=True)
    args = ap.parse_args()

    cfg = CONCEPTS[args.concept]
    print(f"── Build concept {args.concept}: {cfg['slug']} ──")

    tmp_dir = PRODUCT / "output" / f"_tmp_vtv{args.concept}"
    tmp_dir.mkdir(parents=True, exist_ok=True)
    FINAL.mkdir(parents=True, exist_ok=True)

    # 1) Generate voice (4 segments)
    voice_paths = {}
    voice_durs = {}
    for seg, text in cfg["voice"].items():
        print(f"  voice [{seg}]: {text[:50]}...")
        mp3 = tmp_dir / f"voice_{seg}.mp3"
        gen_voice(text, mp3)
        voice_paths[seg] = mp3
        voice_durs[seg] = probe_dur(mp3)
        print(f"    → {voice_durs[seg]:.2f}s")

    # 2) Render 3 slides — MỖI slide DIFFERENT background photo (seed riêng)
    # Cộng color tint theo concept → không bao giờ giống visual giữa 2 concept
    _BG_USED_IN_SESSION.clear()
    tint = cfg.get("tint")
    seeds = cfg.get("slide_seeds", [args.concept, args.concept + 100, args.concept + 200])
    hook_png = tmp_dir / "slide_hook.png"
    answer_png = tmp_dir / "slide_answer.png"
    invite_png = tmp_dir / "slide_invite.png"
    render_hook_slide(cfg["hook_lines"], hook_png, seed=seeds[0], tint=tint)
    render_answer_slide(cfg["answer_lines"], cfg["answer_explain"], answer_png,
                        seed=seeds[1], tint=tint)
    render_invite_slide(cfg["invite_lines"], invite_png, seed=seeds[2], tint=tint)
    print(f"  ✓ 3 slides rendered (3 photos khác nhau, tint={tint})")

    # 3) Pick review scenes — seed concept-specific → 2 concept ra 2 bộ scenes khác nhau
    # Force tối thiểu 5 scenes dù voice ngắn → nhiều cảnh nhỏ → khó pHash match
    # Thêm hue_shift signature per concept để chống visual hash duplicate
    hue = cfg.get("hue_shift", 0)
    pick_seed = args.concept * 1000 + 7
    target_review = max(voice_durs["review"] + 0.3, 8.0)   # tối thiểu 8s review (~5 scenes)
    print(f"  pick review scenes target={target_review:.1f}s seed={pick_seed}")
    scenes = pick_review_scenes(target_review, seed=pick_seed)
    print(f"    {len(scenes)} scenes picked, hue_shift={hue}°")
    scaled = []
    for i, s in enumerate(scenes):
        out = tmp_dir / f"scene_{i:02d}.mp4"
        # Subtle zoom per-scene (1.0, 1.03, 1.06, ...) để mỗi clip có framing khác
        zoom = 1.0 + (i * 0.02 if args.concept == 4 else i * 0.025)
        scale_to_canvas(s, tmp_dir, out, hue_shift=hue, zoom=zoom)
        scaled.append(out)

    # 4) Build video parts — each = voice duration + 0.15 tail
    tail = 0.15
    hook_v = tmp_dir / "v_hook.mp4"
    answer_v = tmp_dir / "v_answer.mp4"
    invite_v = tmp_dir / "v_invite.mp4"
    review_v = tmp_dir / "v_review.mp4"
    slide_to_video(hook_png, voice_durs["hook"] + tail, hook_v)
    slide_to_video(answer_png, voice_durs["answer"] + tail, answer_v)
    slide_to_video(invite_png, voice_durs["invite"] + tail, invite_v)

    # Review: concat scaled scenes, then trim/extend to voice duration
    review_concat = tmp_dir / "review_concat.mp4"
    concat_videos(scaled, review_concat, tmp_dir)
    review_dur = probe_dur(review_concat)
    target = voice_durs["review"] + tail
    if review_dur >= target:
        run(["ffmpeg", "-y", "-i", str(review_concat), "-t", f"{target:.3f}",
             "-c:v", "libx264", "-preset", "veryfast", "-pix_fmt", "yuv420p",
             "-an", str(review_v)])
    else:
        extra = target - review_dur
        run(["ffmpeg", "-y", "-i", str(review_concat),
             "-vf", f"tpad=stop_mode=clone:stop_duration={extra:.3f},fps={FPS}",
             "-c:v", "libx264", "-preset", "veryfast", "-pix_fmt", "yuv420p",
             "-an", str(review_v)])

    # 5) Concat video parts
    merged_v = tmp_dir / "merged.mp4"
    concat_videos([hook_v, review_v, answer_v, invite_v], merged_v, tmp_dir)

    # 5.5) Overlay product label pill persistent TOP (canonical y=280)
    label_png = tmp_dir / "product_label.png"
    render_product_label(PRODUCT_LABEL, label_png)
    merged_with_label = tmp_dir / "merged_label.mp4"
    run([
        "ffmpeg", "-y", "-i", str(merged_v), "-i", str(label_png),
        "-filter_complex", f"[0:v][1:v]overlay=(W-w)/2:{LABEL_Y}",
        "-c:v", "libx264", "-preset", "veryfast", "-pix_fmt", "yuv420p",
        "-an", str(merged_with_label)
    ])
    merged_v = merged_with_label
    print(f"  ✓ product label overlaid: {PRODUCT_LABEL} @ y={LABEL_Y}")

    # 6) Concat audio parts (với tail silence để khớp video)
    # Cần convert mp3 → m4a có padding
    padded_audios = []
    for seg in ("hook", "review", "answer", "invite"):
        mp3 = voice_paths[seg]
        m4a = tmp_dir / f"voice_{seg}_padded.m4a"
        run(["ffmpeg", "-y", "-i", str(mp3),
             "-af", f"apad=pad_dur={tail:.3f}",
             "-t", f"{voice_durs[seg] + tail:.3f}",
             "-c:a", "aac", "-b:a", "192k", str(m4a)])
        padded_audios.append(m4a)
    full_audio = tmp_dir / "voice_full.m4a"
    concat_audios(padded_audios, full_audio, tmp_dir)

    # 7) Mux
    final_path = FINAL / f"{cfg['caption']}.mp4"
    run(["ffmpeg", "-y", "-i", str(merged_v), "-i", str(full_audio),
         "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
         "-map", "0:v:0", "-map", "1:a:0", "-shortest", str(final_path)])

    total = probe_dur(final_path)
    print(f"\n✓ FINAL: {final_path.name}")
    print(f"  {total:.2f}s, {final_path.stat().st_size/1024:.1f} KB")


if __name__ == "__main__":
    main()
