"""
Build 3 concept que-cay (scene-driven format, khác CAT 12 vua-tiếng-việt).

Concept 1: "3 ông vua que cay — team nào đây?"  (ranking 3 brand)
Concept 2: "Cái này dài tới mức nào?"            (visual flex + ASMR)
Concept 3: "Hint anh ơi, em thèm..."              (cute share cho nữ GenZ)

Usage:
  python3 scripts/build-quecay-concepts-1-2-3.py --concept 1
  python3 scripts/build-quecay-concepts-1-2-3.py --concept 2
  python3 scripts/build-quecay-concepts-1-2-3.py --concept 3

Voice: edge-tts NamMinh (HoaiMy nữ bị MS block), 3-tier fallback:
  (1) Edge direct → (2) Edge chunking → (3) Gemini TTS Kore (10 req/day).

Scene: mix 2 kênh beheobu + yen, dedup video_id (chống pHash TikTok match).
Bò Cay fixed scene: `assets/products/que-cay/videos/Appetizing_Beef_Stick_Slow_Motion.mp4`.
"""
from __future__ import annotations

import argparse
import json
import os
import random
import re
import subprocess
import sys
import wave
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parent.parent

# Load .env
_env = ROOT / ".env"
if _env.exists():
    for line in _env.read_text().splitlines():
        if "=" in line and not line.strip().startswith("#"):
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())

PRODUCT = ROOT / "assets" / "products" / "que-cay"
COMP_BEHEOBU = ROOT / "assets" / "scene-library" / "que_cay"
COMP_YEN = PRODUCT / "competitor-scenes" / "yen_doanvathot"
BOCAY_VIDEO = PRODUCT / "videos" / "Appetizing_Beef_Stick_Slow_Motion.mp4"
FINAL = PRODUCT / "output" / "final"

W, H = 1080, 1920
FPS = 30
FONT = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"

TTS_VOICE = "vi-VN-NamMinhNeural"
TTS_RATE = "+10%"

# Canonical spec (docs/video-production-format.md)
PRODUCT_LABEL = "QUE CAY - PEL PEL"
LABEL_CANVAS = (900, 140)
LABEL_COLOR = (255, 107, 0, 220)
LABEL_FONT_SIZE = 58
LABEL_Y = 280

SUBTITLE_CANVAS = (1000, 200)
SUBTITLE_BG = (0, 0, 0, 180)
SUBTITLE_FONT_SIZE = 62
SUBTITLE_Y = 1580


CONCEPTS = {
    1: {
        "slug": "3-ong-vua-que-cay",
        "tint": (200, 140, 20),       # vàng ấm signature
        "hue_shift": 3,
        "caption": "3 ông vua que cay team nào đây cưng 🔥 Comment 1, 2 hoặc 3 nha #quecay #quecayvuongthanlong #quecayhangdai #anvat #fyp #xuhuong",
        "segments": [
            {
                "voice": "Ba ông vua que cay nè, team nào đây công chúa ơi?",
                "subtitle": "3 ÔNG VUA QUE CAY\nTEAM NÀO ĐÂY?",
                "keywords": ["quecay", "que cay"],
                "fixed_scene": None,
            },
            {
                "voice": "Số một, Hằng Đại, siu siu dài, huyền thoại tuổi thơ!",
                "subtitle": "SỐ 1: HẰNG ĐẠI\nHUYỀN THOẠI TUỔI THƠ",
                "keywords": ["hangdai", "hằng đại", "siu siu", "siu"],
                "fixed_scene": None,
            },
            {
                "voice": "Số hai, Vương Thần Long, sổ nách flex dài luôn!",
                "subtitle": "SỐ 2: VƯƠNG THẦN LONG\nSỔ NÁCH FLEX DÀI",
                "keywords": ["thần long", "thanlong", "than long", "to dài"],
                "fixed_scene": None,
            },
            {
                "voice": "Số ba, Bò Cay Pel Pel, em chủ kênh tự luyện nè!",
                "subtitle": "SỐ 3: BÒ CAY\nPEL PEL TỰ LUYỆN",
                "keywords": ["bo cay", "bò cay", "beef"],
                "fixed_scene": BOCAY_VIDEO,
            },
            {
                "voice": "Team nào cưng ơi, comment một hai ba nha! Thả tym cộng follow em để mỗi ngày tìm món ngon cho mấy công chúa xinh đẹp!",
                "subtitle": "COMMENT 1, 2 HAY 3?\nTHẢ TYM + FOLLOW!",
                "keywords": ["quecay"],
                "fixed_scene": None,
            },
        ],
    },
    2: {
        "slug": "dai-toi-muc-nao",
        "tint": (30, 110, 30),        # xanh lá signature
        "hue_shift": -5,
        "caption": "Trời ơi cái này dài tới mức nào 🔥 ASMR cắn giòn tan luôn 🤤 #sonachvuongthanlong #quecayvuongthanlong #quecaydai #anvat #asmr #mlem #fyp",
        "segments": [
            {
                "voice": "Trời ơi cái này dài tới cỡ nào vậy công chúa?",
                "subtitle": "TRỜI ƠI...\nDÀI CỠ NÀY LÀ THẬT?",
                "keywords": ["dài", "sổ nách", "thần long"],
                "fixed_scene": None,
            },
            {
                "voice": "Sổ nách nó ra luôn nè, dài như dây chuyền vàng vậy đó!",
                "subtitle": "SỔ NÁCH RA LUÔN!\nDÀI NHƯ DÂY CHUYỀN",
                "keywords": ["sổ nách", "sonach", "thần long"],
                "fixed_scene": None,
            },
            {
                "voice": "Cắn một miếng giòn rụm, cay tê đầu lưỡi luôn nè!",
                "subtitle": "GIÒN RỤM!\nCAY TÊ ĐẦU LƯỠI",
                "keywords": ["cay", "giòn", "quecay"],
                "fixed_scene": None,
            },
            {
                "voice": "Cưng nào thấy dài ơi là dài thì tag đứa bạn mê đồ dài nha! Thả tym cộng follow em, mỗi ngày một snack siêu đỉnh!",
                "subtitle": "TAG ĐỨA BẠN MÊ ĐỒ DÀI!\nTHẢ TYM + FOLLOW",
                "keywords": ["quecay"],
                "fixed_scene": None,
            },
        ],
    },
    3: {
        "slug": "hint-anh-oi",
        "tint": (230, 80, 140),       # hồng signature (cute hint)
        "hue_shift": 10,
        "caption": "Anh ơi em thèm cái này 🥺 Gửi cho người yêu - nếu anh xứng đáng ✨ #quecay #hintnguoiyeu #anvat #couplegoals #fyp #xuhuong",
        "segments": [
            {
                "voice": "Anh ơi... em thèm cái này quá à!",
                "subtitle": "ANH ƠI...\nEM THÈM QUÁ",
                "keywords": ["quecay", "cay"],
                "fixed_scene": None,
            },
            {
                "voice": "Không biết đứa nào đang coi video này nha!",
                "subtitle": "KHÔNG BIẾT ĐỨA NÀO\nĐANG COI VIDEO NÀY",
                "keywords": ["quecay"],
                "fixed_scene": None,
            },
            {
                "voice": "Em không đòi gì đâu, chỉ cần một bịch que cay thôi!",
                "subtitle": "EM KHÔNG ĐÒI GÌ ĐÂU\nCHỈ 1 BỊCH THÔI",
                "keywords": ["quecay"],
                "fixed_scene": None,
            },
            {
                "voice": "Gửi cho người yêu, nếu anh xứng đáng thì mai có bịch ngay!",
                "subtitle": "GỬI CHO NGƯỜI YÊU\nXỨNG ĐÁNG = MAI CÓ BỊCH",
                "keywords": ["quecay"],
                "fixed_scene": None,
            },
            {
                "voice": "Ai độc thân thả tym cộng follow em, em ghép đôi với que cay ngon ngon mỗi ngày nha!",
                "subtitle": "ĐỘC THÂN? THẢ TYM + FOLLOW\nGHÉP ĐÔI VỚI QUE CAY!",
                "keywords": ["quecay"],
                "fixed_scene": None,
            },
        ],
    },
}


# ─────────────────────────────────────────────────────────────────────
# Helpers (reuse pattern từ vua-tieng-viet)
# ─────────────────────────────────────────────────────────────────────
def run(cmd, check=True):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if check and r.returncode != 0:
        print("CMD FAIL:", " ".join(map(str, cmd)))
        print(r.stderr[-1000:])
        raise SystemExit(1)
    return r


def probe_dur(path: Path) -> float:
    r = run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "json", str(path)])
    return float(json.loads(r.stdout)["format"]["duration"])


def _tts_single(text: str, voice: str, rate: str | None, out_path: Path, retries: int = 3) -> bool:
    import time as _time
    for attempt in range(retries):
        cmd = [sys.executable, "-m", "edge_tts", "--voice", voice]
        if rate:
            cmd += ["--rate", rate]
        cmd += ["--text", text, "--write-media", str(out_path)]
        r = run(cmd, check=False)
        if r.returncode == 0 and out_path.exists() and out_path.stat().st_size > 1000:
            return True
        _time.sleep(2 + attempt * 2)
    return False


def _gemini_tts(text: str, out_path: Path) -> bool:
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
            wf.setnchannels(1); wf.setsampwidth(2); wf.setframerate(24000)
            wf.writeframes(pcm)
        run(["ffmpeg", "-y", "-i", str(wav_tmp), "-c:a", "libmp3lame", "-b:a", "192k", str(out_path)])
        wav_tmp.unlink(missing_ok=True)
        return out_path.exists() and out_path.stat().st_size > 1000
    except Exception as e:
        print(f"    Gemini TTS error: {type(e).__name__}: {str(e)[:80]}")
        return False


def gen_voice(text: str, out_path: Path):
    """3-tier fallback: Edge direct → Edge chunking → Gemini TTS."""
    if _tts_single(text, TTS_VOICE, TTS_RATE, out_path, retries=2):
        return

    print(f"    [chunking] text len={len(text)}")
    chunks = [c.strip() for c in re.split(r"[.!?—]+", text) if c.strip()]
    if len(chunks) <= 1:
        chunks = [c.strip() for c in text.split(",") if c.strip()]

    ok_all = len(chunks) > 0
    chunk_mp3s = []
    tmp = out_path.parent
    for i, ck in enumerate(chunks):
        ck_ = ck if ck.endswith((".", "!", "?")) else ck + "."
        co = tmp / f"{out_path.stem}_ck{i:02d}.mp3"
        if not _tts_single(ck_, TTS_VOICE, TTS_RATE, co, retries=3):
            if not _tts_single(ck_, "vi-VN-NamMinhNeural", None, co, retries=3):
                ok_all = False
                break
        chunk_mp3s.append(co)

    if ok_all and chunk_mp3s:
        lf = tmp / f"{out_path.stem}_list.txt"
        lf.write_text("\n".join(f"file '{p.as_posix()}'" for p in chunk_mp3s) + "\n")
        run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(lf),
             "-c:a", "copy", str(out_path)])
        return

    print(f"    [Gemini TTS]")
    if _gemini_tts(text, out_path):
        return

    # SILENT fallback (canonical docs/video-production-format.md)
    # Gen silence MP3 với duration ước lượng theo text length (~13 char/s VN)
    est_dur = max(2.0, len(text) / 13.0)
    print(f"    [SILENT fallback: dur={est_dur:.1f}s, user add voice trên TikTok]")
    run(["ffmpeg", "-y", "-f", "lavfi", "-i", f"anullsrc=r=44100:cl=mono",
         "-t", f"{est_dur:.3f}", "-c:a", "libmp3lame", "-b:a", "128k",
         str(out_path)])


# ─────────────────────────────────────────────────────────────────────
# Scene picking
# ─────────────────────────────────────────────────────────────────────
def load_all_scenes() -> dict:
    """Return {author: [(views, dur, video_id, mp4_path, caption), ...]}"""
    pools = {"beheobu0102": [], "yen_doanvathot": []}
    for d in (COMP_BEHEOBU, COMP_YEN):
        if not d.exists():
            continue
        for j in d.glob("*.json"):
            try:
                m = json.loads(j.read_text())
                a = m.get("source_author")
                if a not in pools:
                    continue
                mp4 = j.with_suffix(".mp4")
                if not mp4.exists():
                    continue
                pools[a].append((
                    m.get("source_views") or 0,
                    m.get("duration_sec") or 0,
                    m.get("source_video_id"),
                    mp4,
                    (m.get("source_caption") or "").lower(),
                ))
            except Exception:
                continue
    for a in pools:
        pools[a].sort(key=lambda x: x[0], reverse=True)
    return pools


def pick_scene(pools: dict, keywords: list[str], used_vids: set,
               alternate: str, seed: int) -> Path | None:
    """Pick 1 scene match keywords, alternate 2 authors, dedup video_id."""
    rng = random.Random(seed)
    authors_order = (["yen_doanvathot", "beheobu0102"] if alternate == "yen"
                     else ["beheobu0102", "yen_doanvathot"])
    for author in authors_order:
        # Match keywords
        matches = [e for e in pools[author]
                   if e[2] not in used_vids
                   and any(k.lower() in e[4] for k in keywords)]
        if matches:
            # Random 1 trong top 10 để đa dạng
            pick = rng.choice(matches[:10])
            used_vids.add(pick[2])
            return pick[3]
    # Fallback: any scene chưa dùng
    for author in authors_order:
        avail = [e for e in pools[author] if e[2] not in used_vids]
        if avail:
            pick = rng.choice(avail[:10])
            used_vids.add(pick[2])
            return pick[3]
    return None


# ─────────────────────────────────────────────────────────────────────
# Video processing
# ─────────────────────────────────────────────────────────────────────
def render_product_label(text: str, out_png: Path):
    """Canonical: 900×140, pill cam rgba(255,107,0,220), Arial 58pt trắng stroke 3px đen."""
    cw, ch = LABEL_CANVAS
    img = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    font = ImageFont.truetype(FONT, LABEL_FONT_SIZE)
    d.rounded_rectangle([0, 0, cw - 1, ch - 1], radius=ch // 2, fill=LABEL_COLOR)
    bbox = d.textbbox((0, 0), text, font=font, stroke_width=3)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    x = (cw - tw) // 2; y = (ch - th) // 2 - 4
    d.text((x, y), text, font=font, fill=(255, 255, 255, 255),
           stroke_width=3, stroke_fill=(0, 0, 0, 255))
    img.save(out_png)


def render_subtitle_png(text: str, out: Path, font_size: int = SUBTITLE_FONT_SIZE):
    """Canonical: 1000×200, pill đen rgba(0,0,0,180), font 62pt trắng stroke 2px."""
    cw, ch = SUBTITLE_CANVAS
    img = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    font = ImageFont.truetype(FONT, font_size)
    d.rounded_rectangle([0, 0, cw - 1, ch - 1], radius=25, fill=SUBTITLE_BG)
    lines = text.split("\n")
    widths, heights = [], []
    for ln in lines:
        b = d.textbbox((0, 0), ln, font=font, stroke_width=2)
        widths.append(b[2] - b[0]); heights.append(b[3] - b[1])
    line_h = 74
    total_h = line_h * len(lines)
    y_start = (ch - total_h) // 2
    for i, ln in enumerate(lines):
        x = (cw - widths[i]) // 2
        y = y_start + i * line_h
        d.text((x, y), ln, font=font, fill=(255, 255, 255, 255),
               stroke_width=2, stroke_fill=(0, 0, 0, 255))
    img.save(out)


def scene_to_canvas_trim(src: Path, duration: float, out: Path,
                          hue_shift: int = 0, zoom: float = 1.0):
    """Scale src → 1080x1920, trim/extend to `duration`, no audio.
    hue_shift + zoom = concept signature chống pHash detect."""
    src_dur = probe_dur(src)
    vf = (f"scale={W}:{H}:force_original_aspect_ratio=decrease,"
          f"pad={W}:{H}:(ow-iw)/2:(oh-ih)/2:color=black,"
          f"setsar=1,fps={FPS}")
    if zoom != 1.0:
        zw = int(W * zoom); zh = int(H * zoom)
        vf += f",scale={zw}:{zh},crop={W}:{H}:{(zw-W)//2}:{(zh-H)//2}"
    if hue_shift:
        vf += f",hue=h={hue_shift}"
    if src_dur >= duration:
        run(["ffmpeg", "-y", "-i", str(src), "-t", f"{duration:.3f}",
             "-vf", vf, "-an", "-c:v", "libx264", "-preset", "veryfast",
             "-pix_fmt", "yuv420p", str(out)])
    else:
        # Cần extend: concat copy của scene cho tới đủ duration
        repeat = int(duration / src_dur) + 1
        tmp = out.parent / f"_loop_{src.stem}.mp4"
        list_f = out.parent / f"_loop_{src.stem}.txt"
        list_f.write_text(f"file '{src.as_posix()}'\n" * repeat)
        run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(list_f),
             "-c:v", "libx264", "-preset", "veryfast", "-pix_fmt", "yuv420p",
             "-an", str(tmp)])
        run(["ffmpeg", "-y", "-i", str(tmp), "-t", f"{duration:.3f}",
             "-vf", vf, "-an", "-c:v", "libx264", "-preset", "veryfast",
             "-pix_fmt", "yuv420p", str(out)])


def overlay_subtitle(video: Path, sub_png: Path, out: Path):
    """Overlay subtitle PNG tại y=1580 (canonical bottom)."""
    run([
        "ffmpeg", "-y", "-i", str(video), "-i", str(sub_png),
        "-filter_complex", f"[0:v][1:v]overlay=(W-w)/2:{SUBTITLE_Y}",
        "-c:v", "libx264", "-preset", "veryfast", "-pix_fmt", "yuv420p",
        "-an", str(out)
    ])


def concat_videos(parts: list[Path], out: Path, tmp: Path):
    lf = tmp / "v_concat.txt"
    lf.write_text("\n".join(f"file '{p.as_posix()}'" for p in parts) + "\n")
    run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(lf),
         "-c:v", "libx264", "-preset", "veryfast", "-pix_fmt", "yuv420p",
         "-an", str(out)])


def concat_audios(parts: list[Path], out: Path, tmp: Path):
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
    ap.add_argument("--concept", type=int, choices=[1, 2, 3], required=True)
    args = ap.parse_args()

    cfg = CONCEPTS[args.concept]
    slug = cfg["slug"]
    print(f"── Build concept {args.concept}: {slug} ──")

    tmp = PRODUCT / "output" / f"_tmp_c{args.concept}"
    tmp.mkdir(parents=True, exist_ok=True)
    FINAL.mkdir(parents=True, exist_ok=True)

    # 1) Load scene pools
    pools = load_all_scenes()
    print(f"  pools: {len(pools['beheobu0102'])} beheobu + {len(pools['yen_doanvathot'])} yen")

    # 2) Build each segment
    used_vids = set()
    voice_parts = []
    video_parts = []
    tail = 0.15

    for i, seg in enumerate(cfg["segments"], 1):
        print(f"\n[seg {i}/{len(cfg['segments'])}] voice: {seg['voice'][:60]}")
        # Voice
        voice_mp3 = tmp / f"voice_{i:02d}.mp3"
        gen_voice(seg["voice"], voice_mp3)
        v_dur = probe_dur(voice_mp3)
        print(f"  voice dur: {v_dur:.2f}s")

        # Pad audio với tail silence
        voice_padded = tmp / f"voice_{i:02d}_pad.m4a"
        run(["ffmpeg", "-y", "-i", str(voice_mp3),
             "-af", f"apad=pad_dur={tail:.3f}",
             "-t", f"{v_dur + tail:.3f}",
             "-c:a", "aac", "-b:a", "192k", str(voice_padded)])
        voice_parts.append(voice_padded)

        # Scene
        if seg.get("fixed_scene"):
            scene_src = seg["fixed_scene"]
            if not scene_src.exists():
                print(f"  ⚠ fixed scene missing: {scene_src} — fallback pick")
                scene_src = pick_scene(pools, seg["keywords"], used_vids,
                                       "beheobu" if i % 2 else "yen", args.concept * 100 + i)
        else:
            scene_src = pick_scene(pools, seg["keywords"], used_vids,
                                   "beheobu" if i % 2 else "yen", args.concept * 100 + i)
        if not scene_src:
            raise SystemExit(f"Không pick được scene cho segment {i}")
        print(f"  scene: {scene_src.name}")

        # Trim scene + apply hue + progressive zoom (concept signature)
        scene_trimmed = tmp / f"scene_{i:02d}.mp4"
        hue = cfg.get("hue_shift", 0)
        zoom = 1.0 + (i - 1) * 0.02
        scene_to_canvas_trim(scene_src, v_dur + tail, scene_trimmed,
                             hue_shift=hue, zoom=zoom)

        # Render subtitle + overlay
        sub_png = tmp / f"sub_{i:02d}.png"
        render_subtitle_png(seg["subtitle"], sub_png)
        scene_final = tmp / f"seg_{i:02d}.mp4"
        overlay_subtitle(scene_trimmed, sub_png, scene_final)
        video_parts.append(scene_final)

    # 3) Concat video + audio
    merged_v = tmp / "merged_v.mp4"
    merged_a = tmp / "merged_a.m4a"
    concat_videos(video_parts, merged_v, tmp)
    concat_audios(voice_parts, merged_a, tmp)

    # 3.5) Overlay product label pill TOP (canonical y=280)
    label_png = tmp / "product_label.png"
    render_product_label(PRODUCT_LABEL, label_png)
    merged_v_labeled = tmp / "merged_v_label.mp4"
    run([
        "ffmpeg", "-y", "-i", str(merged_v), "-i", str(label_png),
        "-filter_complex", f"[0:v][1:v]overlay=(W-w)/2:{LABEL_Y}",
        "-c:v", "libx264", "-preset", "veryfast", "-pix_fmt", "yuv420p",
        "-an", str(merged_v_labeled)
    ])
    print(f"  ✓ product label overlaid: {PRODUCT_LABEL}")

    # 4) Mux
    final_path = FINAL / f"{cfg['caption']}.mp4"
    run(["ffmpeg", "-y", "-i", str(merged_v_labeled), "-i", str(merged_a),
         "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
         "-map", "0:v:0", "-map", "1:a:0", "-shortest", str(final_path)])

    total = probe_dur(final_path)
    print(f"\n✓ FINAL: {final_path.name}")
    print(f"  {total:.2f}s, {final_path.stat().st_size/1024:.1f} KB")
    print(f"  scenes used: {len(used_vids)} unique videos")


if __name__ == "__main__":
    main()
