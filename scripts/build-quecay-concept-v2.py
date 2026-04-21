"""
Build concept video v2: "Vũ Trụ Que Cay: 3 brand" với label "BÒ CAY • PEL PEL"
persistent trong tất cả frames (để TikTok AI nhận là review sản phẩm).

Thay đổi so v1:
  - Clip 3: dùng video thật `Appetizing_Beef_Stick_Slow_Motion.mp4` thay Ken Burns ảnh AI
  - Pillow render PNG label transparent → overlay ffmpeg (né drawtext filter brew thiếu)
  - Label "BÒ CAY • PEL PEL" xuất hiện mọi frame

Output theo convention `docs/folder-structure-conventions.md`:
  assets/products/que-cay/output/final/<YYMMDD>-que-cay-v2-3brand-label.mp4
  assets/products/que-cay/output/tiktok-ready/<caption>.mp4
"""
from __future__ import annotations

import json
import shutil
import subprocess
import time
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
PRODUCT_DIR = ROOT / "assets" / "products" / "que-cay"
SCENES = ROOT / "assets" / "scene-library" / "que_cay"
PRODUCT_VIDEOS = PRODUCT_DIR / "videos"
OUTPUT_DIR = PRODUCT_DIR / "output"
FINAL_DIR = OUTPUT_DIR / "final"
TIKTOK_DIR = OUTPUT_DIR / "tiktok-ready"
TMP_DIR = OUTPUT_DIR / "_tmp_v2"

DATE = time.strftime("%y%m%d")
CANONICAL_NAME = f"{DATE}-que-cay-v2-3brand-label.mp4"
CAPTION = "Que cay brand nào đỉnh nhất team 🤤 #anvat #quecay #quecayhangdai #doanvat #anvattuoitho"

LABEL_TEXT = "BÒ CAY • PEL PEL"

CLIPS = [
    {"type": "scene", "src": SCENES / "beheobu0102_7591174570623782162_scene_01.mp4",
     "trim_start": 0.0, "trim_end": 3.0, "label": "HangDai"},
    {"type": "scene", "src": SCENES / "beheobu0102_7613832315164167432_scene_01.mp4",
     "trim_start": 0.0, "trim_end": 1.7, "label": "ThanLong"},
    {"type": "video", "src": PRODUCT_VIDEOS / "Appetizing_Beef_Stick_Slow_Motion.mp4",
     "trim_start": 1.0, "trim_end": 6.0, "label": "BoCay"},  # 5s middle cho slow-mo đẹp
]


def run(cmd: list) -> None:
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


# ── Label PNG (Pillow render, transparent background) ──────────────────

def find_vietnamese_font(size: int) -> ImageFont.FreeTypeFont:
    """Tìm font macOS hỗ trợ dấu tiếng Việt."""
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


def render_label_png(text: str, out_path: Path, width: int = 900, height: int = 140) -> None:
    """Render text label trên background bo tròn bán trong suốt → PNG RGBA."""
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Background pill: bo tròn, màu cam Pel Pel + alpha
    radius = height // 2
    pill_color = (255, 107, 0, 220)  # #FF6B00, alpha ~86%
    draw.rounded_rectangle([(0, 0), (width - 1, height - 1)], radius=radius, fill=pill_color)

    # Text
    font = find_vietnamese_font(size=58)
    bbox = draw.textbbox((0, 0), text, font=font)
    tx = (width - (bbox[2] - bbox[0])) // 2
    ty = (height - (bbox[3] - bbox[1])) // 2 - bbox[1]
    # Stroke đen để rõ trên mọi background video
    draw.text((tx, ty), text, font=font, fill=(255, 255, 255, 255),
              stroke_width=3, stroke_fill=(0, 0, 0, 255))

    out_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(out_path, "PNG")


# ── Video processing ───────────────────────────────────────────────────

def standardize_to_portrait(src: Path, out: Path, start: float, end: float) -> None:
    """Trim + ép 9:16 1080×1920. Với source horizontal → crop center portrait."""
    duration = end - start
    # Scale to cover 1080×1920 (fit by height, crop width), sau đó crop middle
    # Dùng crop= 1080:1920 sau khi scale
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


def overlay_label(video: Path, label_png: Path, out: Path) -> None:
    """Overlay label PNG ở top center, persistent toàn bộ video."""
    cmd = [
        "ffmpeg", "-y",
        "-i", str(video),
        "-i", str(label_png),
        "-filter_complex",
        "[0:v][1:v]overlay=(main_w-overlay_w)/2:80",
        "-c:v", "libx264", "-preset", "fast", "-crf", "21",
        "-pix_fmt", "yuv420p",
        "-an",
        str(out),
    ]
    run(cmd)


def concat_clips(clip_paths: list[Path], out: Path) -> None:
    list_file = TMP_DIR / "concat.txt"
    list_file.parent.mkdir(parents=True, exist_ok=True)
    with list_file.open("w") as f:
        for p in clip_paths:
            f.write(f"file '{p.resolve()}'\n")
    cmd = [
        "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(list_file),
        "-c", "copy", str(out),
    ]
    run(cmd)


def finalize_copy(video: Path, out: Path) -> None:
    cmd = [
        "ffmpeg", "-y", "-i", str(video),
        "-c", "copy", "-movflags", "+faststart",
        str(out),
    ]
    run(cmd)


# ── Main ───────────────────────────────────────────────────────────────

def main():
    FINAL_DIR.mkdir(parents=True, exist_ok=True)
    TIKTOK_DIR.mkdir(parents=True, exist_ok=True)
    TMP_DIR.mkdir(parents=True, exist_ok=True)

    print("── Build concept que-cay v2 ──────────────────")
    print(f"Final dir     : {FINAL_DIR}")
    print(f"TikTok-ready  : {TIKTOK_DIR}")
    print(f"Label text    : {LABEL_TEXT}")

    # 1. Render label PNG
    label_png = TMP_DIR / "label.png"
    print(f"[1/5] Render label PNG → {label_png.name}")
    render_label_png(LABEL_TEXT, label_png)

    # 2. Process mỗi clip: standardize 9:16 → overlay label
    clip_paths = []
    for i, clip in enumerate(CLIPS, 1):
        base = f"clip_{i:02d}_{clip['label']}"
        stage1 = TMP_DIR / f"{base}_raw.mp4"
        stage2 = TMP_DIR / f"{base}_labeled.mp4"

        print(f"[2/5] {clip['label']}: trim {clip['trim_start']}-{clip['trim_end']}s, 9:16...")
        standardize_to_portrait(clip["src"], stage1, clip["trim_start"], clip["trim_end"])

        print(f"      overlay label...")
        overlay_label(stage1, label_png, stage2)

        clip_paths.append(stage2)

    # 3. Concat
    concat_path = TMP_DIR / "concat.mp4"
    print(f"[3/5] Concat {len(clip_paths)} labeled clips → {concat_path.name}")
    concat_clips(clip_paths, concat_path)

    # 4. Finalize
    canonical_path = FINAL_DIR / CANONICAL_NAME
    print(f"[4/5] Finalize → {canonical_path.name}")
    finalize_copy(concat_path, canonical_path)

    # 5. Copy TikTok-ready (tên = caption)
    tiktok_path = TIKTOK_DIR / f"{CAPTION}.mp4"
    shutil.copy2(canonical_path, tiktok_path)
    print(f"[5/5] TikTok-ready → {tiktok_path.name}")

    # Meta
    total_dur = sum(c["trim_end"] - c["trim_start"] for c in CLIPS)
    meta = {
        "caption": CAPTION,
        "label_persistent": LABEL_TEXT,
        "duration_sec": total_dur,
        "source_clips": [
            {"label": c["label"], "source": str(c["src"].relative_to(ROOT)),
             "trim": [c["trim_start"], c["trim_end"]]}
            for c in CLIPS
        ],
        "canonical_path": str(canonical_path.relative_to(ROOT)),
        "tiktok_ready_path": str(tiktok_path.relative_to(ROOT)),
        "note": "silent — add voice/music trong TikTok editor",
    }
    meta_path = FINAL_DIR / f"{CANONICAL_NAME}.meta.json"
    with meta_path.open("w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)

    print(f"\n✓ Canonical : {canonical_path.relative_to(ROOT)}")
    print(f"✓ TikTok    : {tiktok_path.relative_to(ROOT)}")
    print(f"✓ Meta      : {meta_path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
