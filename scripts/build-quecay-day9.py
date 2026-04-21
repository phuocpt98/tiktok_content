"""
Build Day 9: "Top 3 cung hoàng đạo nghiện ăn cay" (Que Cay).

Plan: `plans/260424-1030-pel-pel-14day-calendar/plan.md` § Day 9.

Format slide-first (graphic-heavy):
  - Slide hook (2.5s): "TOP 3 CUNG NGHIỆN ĂN CAY"
  - Slide + scene (2s × 3): Bạch Dương / Bọ Cạp / Sư Tử
  - Slide CTA (2.5s): "BẠN CUNG GÌ? COMMENT!"

Silent (anh add voice + nhạc trend trên TikTok editor).
"""
from __future__ import annotations

import json
import subprocess
import time
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent

PRODUCT_DIR = ROOT / "assets" / "products" / "que-cay"
SCENE_SOURCES = [
    ROOT / "assets" / "scene-library" / "que_cay",
    ROOT / "assets" / "products" / "que-cay" / "competitor-scenes",
]
OUTPUT_DIR = PRODUCT_DIR / "output"
FINAL_DIR = OUTPUT_DIR / "final"
TMP_DIR = OUTPUT_DIR / "_tmp_day9"

CAPTION = "Top 3 cung hoàng đạo nghiện ăn cay! Bạn có mặt? #quecay #cunghoangdao #anvat #fyp #xuhuong"
FINAL_NAME = f"{CAPTION}.mp4"

LABEL_TEXT = "QUE CAY • PEL PEL"
LABEL_Y = 280

# 5 blocks: hook → 3 cung (mỗi cung scene + overlay slide text) → CTA
BLOCKS = [
    {"type": "slide_only", "title": "TOP 3 CUNG", "sub": "NGHIỆN ĂN CAY NHẤT",
     "duration": 2.5, "bg_color": (220, 50, 50)},

    {"type": "scene_with_text", "rank": "1", "cung": "BẠCH DƯƠNG",
     "desc": "Lửa cháy, ngon tới bến",
     "duration": 2.5, "keywords": ["quecay", "cay"],
     "prefer_views": 3_000_000},

    {"type": "scene_with_text", "rank": "2", "cung": "BỌ CẠP",
     "desc": "Cay đắng là đặc sản",
     "duration": 2.5, "keywords": ["hangdai", "thần long", "siu siu"],
     "prefer_views": 1_000_000},

    {"type": "scene_with_text", "rank": "3", "cung": "SƯ TỬ",
     "desc": "Ăn cay như vua",
     "duration": 2.5, "keywords": ["quecay", "ngon"],
     "prefer_views": 500_000},

    {"type": "slide_only", "title": "CUNG GÌ?", "sub": "COMMENT NGAY NHA!",
     "duration": 2.5, "bg_color": (30, 30, 30)},
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


# ── Full-screen slide (1080×1920) ──────────────────────────────────────

def render_fullscreen_slide(title: str, sub: str, out: Path,
                             bg_color: tuple = (220, 50, 50)) -> None:
    """Slide 1080×1920 full color với title + subtitle center."""
    img = Image.new("RGB", (1080, 1920), bg_color)
    draw = ImageDraw.Draw(img)

    title_font = find_vi_font(160)
    sub_font = find_vi_font(72)

    # Title
    tb = draw.textbbox((0, 0), title, font=title_font)
    tw, th = tb[2]-tb[0], tb[3]-tb[1]
    tx = (1080 - tw) // 2
    ty = (1920 - th) // 2 - 200
    draw.text((tx-8, ty-tb[1]), title, font=title_font, fill=(255, 255, 255),
              stroke_width=6, stroke_fill=(0, 0, 0))

    # Subtitle
    sb = draw.textbbox((0, 0), sub, font=sub_font)
    sw = sb[2]-sb[0]
    sx = (1080 - sw) // 2
    sy = ty + th + 40
    draw.text((sx, sy-sb[1]), sub, font=sub_font, fill=(255, 220, 0),
              stroke_width=4, stroke_fill=(0, 0, 0))

    img.save(out, "PNG", quality=95)


def render_cung_overlay(rank: str, cung: str, desc: str, out: Path) -> None:
    """Overlay transparent chứa 'Top N CUNG' + desc cho scene_with_text.
    Render ở top portion video để scene que cay vẫn visible phía dưới.
    """
    img = Image.new("RGBA", (1080, 700), (0, 0, 0, 0))  # transparent top half
    draw = ImageDraw.Draw(img)

    # Semi-transparent overlay với gradient mờ phần trên
    draw.rectangle([(0, 0), (1080, 620)], fill=(0, 0, 0, 150))

    rank_font = find_vi_font(140)
    cung_font = find_vi_font(120)
    desc_font = find_vi_font(64)

    # Rank circle
    draw.ellipse([(60, 80), (300, 320)], fill=(255, 200, 0), outline=(255, 255, 255), width=8)
    rb = draw.textbbox((0, 0), rank, font=rank_font)
    rx = 60 + (240 - (rb[2]-rb[0])) // 2
    ry = 80 + (240 - (rb[3]-rb[1])) // 2 - rb[1]
    draw.text((rx, ry), rank, font=rank_font, fill=(0, 0, 0))

    # Cung name
    cb = draw.textbbox((0, 0), cung, font=cung_font)
    draw.text((340, 130-cb[1]), cung, font=cung_font, fill=(255, 255, 255),
              stroke_width=5, stroke_fill=(0, 0, 0))

    # Desc
    db = draw.textbbox((0, 0), desc, font=desc_font)
    draw.text((340, 290-db[1]), desc, font=desc_font, fill=(255, 220, 0),
              stroke_width=3, stroke_fill=(0, 0, 0))

    img.save(out, "PNG")


def render_label_png(text: str, out: Path, width: int = 900, height: int = 140) -> None:
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.rounded_rectangle([(0, 0), (width-1, height-1)], radius=height//2, fill=(255, 107, 0, 220))
    font = find_vi_font(58)
    bbox = draw.textbbox((0, 0), text, font=font)
    draw.text(((width-(bbox[2]-bbox[0]))//2, (height-(bbox[3]-bbox[1]))//2-bbox[1]),
              text, font=font, fill=(255, 255, 255), stroke_width=3, stroke_fill=(0, 0, 0))
    img.save(out, "PNG")


# ── Scene load ─────────────────────────────────────────────────────────

def load_all_scenes() -> list[dict]:
    scenes = []
    for src in SCENE_SOURCES:
        if not src.exists(): continue
        for j in src.rglob("*.json"):
            try:
                d = json.load(j.open())
                mp4 = j.with_suffix(".mp4")
                if not mp4.exists(): continue
                if (d.get("duration_sec") or 0) < 1.5: continue
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

def slide_image_to_video(png: Path, duration: float, out: Path) -> None:
    """Convert 1080×1920 PNG → MP4 với duration cố định."""
    cmd = [
        "ffmpeg", "-y", "-loop", "1", "-i", str(png),
        "-t", f"{duration}", "-vf", "fps=30,format=yuv420p",
        "-c:v", "libx264", "-preset", "fast", "-crf", "21",
        str(out),
    ]
    run(cmd)


def scene_with_overlay(src: Path, duration: float, overlay_png: Path,
                       label_png: Path, out: Path) -> None:
    """Trim scene 9:16, overlay cung info ở top + label."""
    vf = (
        "scale=-1:1920:force_original_aspect_ratio=increase,"
        "crop=1080:1920:(iw-1080)/2:0,setsar=1,fps=30"
    )
    cmd = [
        "ffmpeg", "-y",
        "-i", str(src), "-i", str(overlay_png), "-i", str(label_png),
        "-t", f"{duration}",
        "-filter_complex",
        (f"[0:v]{vf}[v0];"
         f"[v0][1:v]overlay=0:0[v1];"
         f"[v1][2:v]overlay=(main_w-overlay_w)/2:{LABEL_Y+600}[vo]"),
        "-map", "[vo]", "-an",
        "-c:v", "libx264", "-preset", "fast", "-crf", "21",
        "-pix_fmt", "yuv420p",
        str(out),
    ]
    run(cmd)


def concat_clips(paths: list[Path], out: Path) -> None:
    listf = TMP_DIR / "concat.txt"
    with listf.open("w") as f:
        for p in paths:
            f.write(f"file '{p.resolve()}'\n")
    run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(listf),
         "-c", "copy", str(out)])


# ── Main ───────────────────────────────────────────────────────────────

def main():
    FINAL_DIR.mkdir(parents=True, exist_ok=True)
    TMP_DIR.mkdir(parents=True, exist_ok=True)

    print("── Build Day 9 — Cung Hoàng Đạo ────────────────")

    label_png = TMP_DIR / "label.png"
    render_label_png(LABEL_TEXT, label_png)

    scenes = load_all_scenes()
    print(f"Library: {len(scenes)} scenes")
    used_ids = set()
    clip_paths = []

    for i, block in enumerate(BLOCKS, 1):
        out_clip = TMP_DIR / f"block_{i:02d}.mp4"

        if block["type"] == "slide_only":
            slide_png = TMP_DIR / f"slide_{i:02d}.png"
            render_fullscreen_slide(block["title"], block["sub"], slide_png,
                                    bg_color=block["bg_color"])
            slide_image_to_video(slide_png, block["duration"], out_clip)
            print(f"  [{i}] slide '{block['title']}' ({block['duration']}s)")

        else:  # scene_with_text
            pick = pick_scene(scenes, block["keywords"], block["duration"],
                              block["prefer_views"], used_ids)
            if not pick:
                raise SystemExit(f"Không pick được scene cho block {i}")
            used_ids.add(pick["_id_key"])

            overlay_png = TMP_DIR / f"cung_{i:02d}.png"
            render_cung_overlay(block["rank"], block["cung"], block["desc"], overlay_png)

            scene_with_overlay(pick["_mp4_path"], block["duration"],
                               overlay_png, label_png, out_clip)
            print(f"  [{i}] scene '{block['cung']}' ← {pick['_mp4_path'].name} "
                  f"({pick.get('source_views'):,}v)")
            block["picked_source"] = str(pick["_mp4_path"].relative_to(ROOT))

        clip_paths.append(out_clip)

    concat_v = TMP_DIR / "concat.mp4"
    concat_clips(clip_paths, concat_v)

    final_path = FINAL_DIR / FINAL_NAME
    run(["ffmpeg", "-y", "-i", str(concat_v), "-c", "copy",
         "-movflags", "+faststart", str(final_path)])

    total_dur = sum(b["duration"] for b in BLOCKS)
    meta = {
        "caption": CAPTION, "day": 9, "concept": "Cung hoàng đạo",
        "total_duration": total_dur,
        "blocks": [
            {"idx": i, **{k: v for k, v in b.items() if k != "keywords"}}
            for i, b in enumerate(BLOCKS, 1)
        ],
    }
    (FINAL_DIR / f"{FINAL_NAME}.meta.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"\n✓ Duration : {total_dur:.1f}s")
    print(f"✓ Final    : {final_path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
