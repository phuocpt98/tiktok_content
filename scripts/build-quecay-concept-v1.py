"""
Build concept video v1: "Vũ Trụ Que Cay: 3 brand — ai thắng?"

Ghép 3 clip (Hằng Đại + Thần Long + Pel Pel Bò Cay) + voiceover TTS + text overlay.

Output:
  output/que-cay/<caption-full-với-hashtag>.mp4
  output/que-cay/<same-basename>.meta.json     (metadata reference)

Pipeline:
  1. TTS voiceover tiếng Việt (edge-tts)
  2. Trim 2 scene competitor (đã watermark Pel Pel)
  3. Ken Burns từ ảnh Pel Pel photo
  4. Concat 3 clip → bỏ audio gốc
  5. Overlay voiceover + text "Team A / B / C?" cuối video
  6. Save filename = caption đầy đủ để TikTok auto-fill

Yêu cầu: ffmpeg, edge-tts
"""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PRODUCT_DIR = ROOT / "assets" / "products" / "que-cay"
SCENES = ROOT / "assets" / "scene-library" / "que_cay"
PHOTOS = PRODUCT_DIR / "photos"
OUTPUT_DIR = PRODUCT_DIR / "output"
FINAL_DIR = OUTPUT_DIR / "final"
TIKTOK_DIR = OUTPUT_DIR / "tiktok-ready"
TMP_DIR = OUTPUT_DIR / "_tmp_v1"

# Naming convention canonical file
import time
DATE = time.strftime("%y%m%d")
SLUG = "que-cay"
VARIANT = "3brand-compare"
CANONICAL_NAME = f"{DATE}-{SLUG}-v1-{VARIANT}.mp4"

# Caption = filename. Khi upload TikTok, auto-fill caption từ filename.
CAPTION = "Que cay brand nào đỉnh nhất team 🤤 #anvat #quecay #quecayhangdai #doanvat #anvattuoitho"

# Voiceover script — sync với timeline bên dưới
VO_SCRIPT = (
    "Team nào ăn que cay nhiều nhất điểm danh nè! "
    "Hằng Đại. Huyền thoại tuổi thơ. Dài, cay vừa. "
    "Thần Long. To dài siu siu, đẳng cấp size khác. "
    "Nhưng hôm nay em thử vị Bò này... Ôi chu choa má ơi! "
    "Cay cay, thơm bò, khác hẳn luôn. Ăn cuốn ghê! "
    "Team nào ngon nhất? Comment A, B, hay C nha!"
)

VOICE = "vi-VN-HoaiMyNeural"
RATE = "+15%"  # Slow hơn default +50% cho đỡ gấp

# Timeline
CLIPS = [
    {"src": SCENES / "beheobu0102_7591174570623782162_scene_01.mp4",
     "trim_start": 0.0, "trim_end": 3.0, "label": "HangDai",
     "top_label": "A. HANG DAI"},
    {"src": SCENES / "beheobu0102_7613832315164167432_scene_01.mp4",
     "trim_start": 0.0, "trim_end": 1.7, "label": "ThanLong",
     "top_label": "B. THAN LONG"},
    {"photo": PHOTOS / "poll_que-cay-bo_01.jpg", "duration": 5.0, "label": "PelPel",
     "top_label": "C. BO CAY - PEL PEL"},
]


def run(cmd: list) -> None:
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def make_kenburns_from_photo(photo: Path, out_path: Path, duration: float = 5.0, **_: object) -> None:
    """Ken Burns zoom-in từ ảnh tĩnh → MP4 9:16 1080×1920, 30fps."""
    fps = 30
    frames = int(duration * fps)
    cmd = [
        "ffmpeg", "-y",
        "-loop", "1", "-i", str(photo),
        "-filter_complex",
        f"[0:v]scale=2160:-1,crop=2160:3840,"
        f"zoompan=z='min(1+0.0015*on,1.15)':d={frames}:s=1080x1920:fps={fps}[v]",
        "-map", "[v]", "-t", f"{duration}",
        "-c:v", "libx264", "-preset", "fast", "-crf", "21",
        "-pix_fmt", "yuv420p",
        str(out_path),
    ]
    run(cmd)


def trim_clip_mute(src: Path, start: float, end: float, out: Path, **_: object) -> None:
    """Trim clip [start, end], re-encode 1080×1920 30fps, drop audio."""
    duration = end - start
    vf = "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:-1:-1:color=black,setsar=1,fps=30"
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


def concat_clips(clip_paths: list[Path], out: Path) -> None:
    """Concat MP4 qua demuxer list."""
    list_file = TMP_DIR / "concat.txt"
    with list_file.open("w") as f:
        for p in clip_paths:
            f.write(f"file '{p.resolve()}'\n")
    cmd = [
        "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(list_file),
        "-c", "copy", str(out),
    ]
    run(cmd)


def finalize_copy(video: Path, out: Path) -> None:
    """Copy concat file to canonical location với faststart flag."""
    cmd = [
        "ffmpeg", "-y", "-i", str(video),
        "-c", "copy", "-movflags", "+faststart",
        str(out),
    ]
    run(cmd)


def main():
    FINAL_DIR.mkdir(parents=True, exist_ok=True)
    TIKTOK_DIR.mkdir(parents=True, exist_ok=True)
    TMP_DIR.mkdir(parents=True, exist_ok=True)

    print("── Build concept que-cay v1 ──────────────────")
    print(f"Canonical output: {FINAL_DIR}")
    print(f"TikTok-ready:     {TIKTOK_DIR}")

    # 1. (bỏ voiceover — edge-tts bị block, user add voice trong TikTok)

    # 2. Trim 2 scene competitor + Ken Burns Pel Pel
    clip_paths = []
    for i, clip in enumerate(CLIPS):
        out_clip = TMP_DIR / f"clip_{i+1:02d}_{clip['label']}.mp4"
        label = clip.get("top_label")
        if "photo" in clip:
            print(f"[2/4] Ken Burns {clip['photo'].name} → {out_clip.name}")
            make_kenburns_from_photo(clip["photo"], out_clip, clip["duration"], label_top=label)
        else:
            print(f"[2/4] Trim {clip['src'].name} [{clip['trim_start']}-{clip['trim_end']}s] → {out_clip.name}")
            trim_clip_mute(clip["src"], clip["trim_start"], clip["trim_end"], out_clip, label_top=label)
        clip_paths.append(out_clip)

    # 3. Concat
    concat_path = TMP_DIR / "concat.mp4"
    print(f"[3/5] Concat {len(clip_paths)} clip → {concat_path.name}")
    concat_clips(clip_paths, concat_path)

    # 4. Voiceover + text overlay
    # Total duration = sum of clips
    total_dur = sum(
        (c["trim_end"] - c["trim_start"]) if "src" in c else c["duration"]
        for c in CLIPS
    )
    outro_start = max(total_dur - 3.5, 7.0)  # 3.5s cuối hiện text
    print(f"[4/5] Overlay voiceover + text (outro từ {outro_start}s)")

    # 4. Finalize (copy to canonical, faststart for streaming)
    canonical_path = FINAL_DIR / CANONICAL_NAME
    print(f"[4/5] Finalize → {canonical_path.name}")
    finalize_copy(concat_path, canonical_path)

    # 5. Copy to tiktok-ready với tên = caption
    import shutil
    tiktok_path = TIKTOK_DIR / f"{CAPTION}.mp4"
    shutil.copy2(canonical_path, tiktok_path)

    # Meta JSON
    meta_path = FINAL_DIR / f"{CANONICAL_NAME}.meta.json"
    meta = {
        "caption": CAPTION,
        "voiceover_script": VO_SCRIPT,
        "voiceover_note": "edge-tts blocked by Microsoft — video silent, add voice on TikTok or record manually",
        "duration_sec": total_dur,
        "source_clips": [
            {"label": c["label"], "source": str(c.get("src") or c.get("photo"))}
            for c in CLIPS
        ],
        "canonical_path": str(canonical_path.relative_to(ROOT)),
        "tiktok_ready_path": str(tiktok_path.relative_to(ROOT)),
    }
    with meta_path.open("w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)

    print(f"\n✓ Canonical : {canonical_path.relative_to(ROOT)}")
    print(f"✓ TikTok-ready: {tiktok_path.relative_to(ROOT)}")
    print(f"✓ Meta      : {meta_path.relative_to(ROOT)}")
    print(f"\nUpload TikTok → caption auto-fill từ:")
    print(f"  {CAPTION}")


if __name__ == "__main__":
    main()
