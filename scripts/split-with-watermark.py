"""
Scene split + đè watermark Pel Pel trong 1 lần xử lý.

Usage:
  # Split 1 video, lưu scenes vào assets/scene-library/<category>/
  python scripts/split-with-watermark.py assets/raw/tiktok/beheobu0102/7630875937734855944.mp4 \
      --category que_cay

  # Batch: split tất cả MP4 trong 1 folder
  python scripts/split-with-watermark.py assets/raw/tiktok/beheobu0102/ --category que_cay

  # Tuỳ chỉnh watermark position và size
  python scripts/split-with-watermark.py <input> --category X \
      --wm-position tr --wm-width 0.18

  # Thresholds scene detection
  python scripts/split-with-watermark.py <input> --category X \
      --threshold 27 --min-len 1.5

Output:
  assets/scene-library/<category>/<author>_<video_id>_scene_<n>.mp4
  assets/scene-library/<category>/<author>_<video_id>_scene_<n>.json   (metadata)

Metadata JSON:
  - source_video, source_url, source_author
  - scene_index, start_sec, end_sec, duration
  - watermark: {position, width_pct}

Yêu cầu:
  - ffmpeg trên PATH
  - scenedetect (pip)
  - Watermark: assets/brand/pelpel-watermark.png (đã sinh bởi setup trước)
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Iterator

import cv2
from scenedetect import ContentDetector, SceneManager, open_video

ROOT = Path(__file__).resolve().parent.parent
WATERMARK = ROOT / "assets" / "brand" / "pelpel-watermark.png"
# Default mới (per docs/folder-structure-conventions.md refactor 2026-04-23):
# scene-library đã xoá, default chuyển về competitor-scenes của que-cay.
# Caller nên truyền --out explicit cho category khác.
DEFAULT_OUT = ROOT / "assets" / "products" / "que-cay" / "competitor-scenes"

# Haar cascade để detect mặt người frontal — drop scene nếu có mẫu quay mặt.
_FACE_CASCADE = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)

POSITIONS = {
    "br": "W-w-20:H-h-20",
    "bl": "20:H-h-20",
    "tr": "W-w-20:20",
    "tl": "20:20",
}


def find_author_from_path(video_path: Path) -> str:
    """Đoán author từ parent dir: assets/raw/tiktok/<author>/<id>.mp4."""
    parts = video_path.parts
    if "raw" in parts and "tiktok" in parts:
        idx = parts.index("tiktok")
        if idx + 1 < len(parts):
            return parts[idx + 1]
    return "_unknown"


def load_source_info(video_path: Path) -> dict:
    """Đọc .info.json cùng folder nếu có (từ ingest-tiktok.py)."""
    info_path = video_path.with_suffix(".info.json")
    if info_path.exists():
        try:
            with info_path.open(encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def detect_scenes(video_path: Path, threshold: float, min_sec: float) -> list[tuple[float, float]]:
    """Trả list [(start_sec, end_sec), ...]."""
    video = open_video(str(video_path))
    fps = video.frame_rate
    min_frames = int(min_sec * fps)

    sm = SceneManager()
    sm.add_detector(ContentDetector(threshold=threshold, min_scene_len=min_frames))
    sm.detect_scenes(video)

    scenes = sm.get_scene_list()
    return [(s[0].get_seconds(), s[1].get_seconds()) for s in scenes]


def ffprobe_width(path: Path) -> int:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0",
         "-show_entries", "stream=width", "-of", "csv=p=0", str(path)],
        capture_output=True, text=True,
    ).stdout.strip()
    return int(out) if out else 1080


def scene_has_face(src: Path, start_sec: float, end_sec: float,
                   sample_frames: int = 6, min_hits: int = 2,
                   min_face_size: int = 90) -> bool:
    """Sample vài frame trong [start, end], detect face bằng Haar cascade.
    Trả True nếu >= min_hits frame có face (tức mẫu quay mặt) → nên drop scene.
    """
    cap = cv2.VideoCapture(str(src))
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    start_frame = int(start_sec * fps)
    end_frame = int(end_sec * fps)
    span = max(end_frame - start_frame, 1)
    if span < sample_frames:
        sample_frames = max(span, 1)
    hits = 0
    for i in range(sample_frames):
        pos = start_frame + int(span * (i + 0.5) / sample_frames)
        cap.set(cv2.CAP_PROP_POS_FRAMES, pos)
        ok, frame = cap.read()
        if not ok or frame is None:
            continue
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = _FACE_CASCADE.detectMultiScale(
            gray, scaleFactor=1.1, minNeighbors=5,
            minSize=(min_face_size, min_face_size),
        )
        if len(faces) > 0:
            hits += 1
            if hits >= min_hits:
                cap.release()
                return True
    cap.release()
    return False


def extract_scene_with_watermark(
    src: Path, out: Path,
    start_sec: float, end_sec: float,
    video_width: int, wm_width_pct: float, wm_pos_expr: str,
) -> None:
    """Encode scene [start, end] từ src, đè watermark Pel Pel."""
    wm_w = int(video_width * wm_width_pct)
    duration = end_sec - start_sec

    cmd = [
        "ffmpeg", "-y",
        "-ss", f"{start_sec:.3f}",
        "-i", str(src),
        "-i", str(WATERMARK),
        "-t", f"{duration:.3f}",
        "-filter_complex",
        f"[1:v]scale={wm_w}:-1[wm];[0:v][wm]overlay={wm_pos_expr}",
        "-c:v", "libx264", "-preset", "fast", "-crf", "23",
        "-c:a", "aac", "-b:a", "128k",
        "-movflags", "+faststart",
        str(out),
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def process_video(
    src: Path, category: str,
    threshold: float, min_len: float,
    wm_pos: str, wm_width: float,
    max_scenes: int | None,
    out_dir_base: Path,
    skip_face: bool = True,
) -> tuple[int, int]:
    """Xử lý 1 video. Trả về (số scene đã xuất, số scene bị drop do có mặt)."""
    if not WATERMARK.exists():
        raise SystemExit(f"Không tìm thấy watermark: {WATERMARK}")

    src = src.resolve()
    author = find_author_from_path(src)
    video_id = src.stem
    info = load_source_info(src)

    out_dir = out_dir_base
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"→ {author}/{video_id}: detect scenes...", end=" ", flush=True)
    scenes = detect_scenes(src, threshold, min_len)
    print(f"{len(scenes)} scenes")

    if not scenes:
        return 0, 0

    if max_scenes:
        if len(scenes) > max_scenes:
            step = len(scenes) / max_scenes
            scenes = [scenes[int(i * step)] for i in range(max_scenes)]

    vid_width = ffprobe_width(src)
    wm_pos_expr = POSITIONS[wm_pos]

    count = 0
    dropped_face = 0
    for i, (start, end) in enumerate(scenes, 1):
        base = f"{author}_{video_id}_scene_{i:02d}"
        out_mp4 = out_dir / f"{base}.mp4"
        out_json = out_dir / f"{base}.json"

        if out_mp4.exists():
            print(f"  ⊙ {base} — skip (đã có)")
            continue

        # Drop scene nếu detect mẫu quay mặt (user nhấn mạnh)
        if skip_face and scene_has_face(src, start, end):
            print(f"  ⊘ {base} — DROP (có mặt người) ({start:.1f}-{end:.1f}s)")
            dropped_face += 1
            continue

        try:
            extract_scene_with_watermark(
                src, out_mp4, start, end, vid_width, wm_width, wm_pos_expr,
            )
        except subprocess.CalledProcessError as e:
            print(f"  ✗ {base}: ffmpeg fail")
            continue

        meta = {
            "source_video": str(src.relative_to(ROOT)),
            "source_url": info.get("webpage_url") or info.get("url"),
            "source_author": author,
            "source_video_id": video_id,
            "source_caption": (info.get("title") or "").strip(),
            "source_music": (info.get("music_info") or {}).get("title"),
            "source_views": info.get("play_count"),
            "category": category,
            "scene_index": i,
            "start_sec": round(start, 3),
            "end_sec": round(end, 3),
            "duration_sec": round(end - start, 3),
            "watermark": {"position": wm_pos, "width_pct": wm_width, "source": str(WATERMARK.relative_to(ROOT))},
            "face_check": "passed (no face detected)" if skip_face else "skipped",
        }
        with out_json.open("w", encoding="utf-8") as f:
            json.dump(meta, f, ensure_ascii=False, indent=2)

        print(f"  ✓ {base} ({start:.1f}-{end:.1f}s)")
        count += 1

    return count, dropped_face


def iter_inputs(path: Path) -> Iterator[Path]:
    """Yield .mp4 files từ file đơn hoặc folder."""
    if path.suffix == ".mp4" and path.is_file():
        yield path
    elif path.is_dir():
        yield from sorted(path.glob("*.mp4"))
    else:
        raise SystemExit(f"Path không hợp lệ: {path}")


def iter_inputs_from_ids(ids_file: Path, base_dir: Path) -> Iterator[Path]:
    """Đọc file chứa 1 video_id/dòng, yield paths <base_dir>/<id>.mp4 tồn tại."""
    if not ids_file.exists():
        raise SystemExit(f"Không tìm thấy: {ids_file}")
    ids = [line.strip() for line in ids_file.read_text().splitlines() if line.strip()]
    missing = 0
    for vid_id in ids:
        mp4 = base_dir / f"{vid_id}.mp4"
        if mp4.exists():
            yield mp4
        else:
            missing += 1
    if missing:
        print(f"⚠ {missing}/{len(ids)} video id không có MP4 trong {base_dir}")


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("input", type=Path, nargs="?",
                    help="File .mp4 hoặc folder chứa .mp4 (bỏ qua nếu dùng --ids-from)")
    ap.add_argument("--ids-from", type=Path, default=None,
                    help="File chứa 1 video_id/dòng. Cần kèm --base-dir")
    ap.add_argument("--base-dir", type=Path, default=None,
                    help="Folder chứa MP4 để build path từ ID (bắt buộc nếu --ids-from)")
    ap.add_argument("--category", required=True,
                    help="Category để phân loại scene (vd: que_cay, snack, mi)")
    ap.add_argument("--threshold", type=float, default=27.0,
                    help="Scene detection threshold (default 27, cao hơn = ít cut hơn)")
    ap.add_argument("--min-len", type=float, default=1.0,
                    help="Độ dài tối thiểu 1 scene (giây, default 1.0)")
    ap.add_argument("--wm-position", choices=list(POSITIONS.keys()), default="br",
                    help="Vị trí watermark (default br)")
    ap.add_argument("--wm-width", type=float, default=0.22,
                    help="Watermark width tỷ lệ với video width (default 0.22 = 22%%)")
    ap.add_argument("--max-scenes", type=int, default=None,
                    help="Tối đa scene/video (sample đều nếu video dài)")
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT,
                    help=f"Output base dir (default: {DEFAULT_OUT.relative_to(ROOT)})")
    ap.add_argument("--keep-face", action="store_true",
                    help="KHÔNG drop scene có mặt người (default: drop)")
    args = ap.parse_args()

    if not WATERMARK.exists():
        raise SystemExit(f"Watermark chưa có: {WATERMARK}\n"
                         f"Tạo bằng: python -c \"from PIL import Image; "
                         f"Image.open('avatar.png').resize((512,512)).save('{WATERMARK}')\"")

    if args.ids_from:
        if not args.base_dir:
            raise SystemExit("--ids-from cần kèm --base-dir <folder chứa MP4>")
        inputs = list(iter_inputs_from_ids(args.ids_from, args.base_dir))
    elif args.input:
        inputs = list(iter_inputs(args.input))
    else:
        raise SystemExit("Cần truyền <input> hoặc --ids-from")
    skip_face = not args.keep_face
    out_dir = args.out.resolve()

    print(f"── Split with watermark ──────────────────────────")
    print(f"Inputs    : {len(inputs)} file")
    print(f"Category  : {args.category} (metadata, không ảnh hưởng path)")
    print(f"Out dir   : {out_dir}")
    print(f"WM pos    : {args.wm_position} ({args.wm_width*100:.0f}% width)")
    print(f"Face-drop : {'ON (drop scene có mặt)' if skip_face else 'OFF (giữ cả)'}")
    print(f"──────────────────────────────────────────────────")

    total_kept = 0
    total_dropped = 0
    for src in inputs:
        try:
            kept, dropped = process_video(
                src, args.category, args.threshold, args.min_len,
                args.wm_position, args.wm_width, args.max_scenes,
                out_dir, skip_face,
            )
            total_kept += kept
            total_dropped += dropped
        except Exception as e:
            print(f"✗ {src.name}: {e}")

    print(f"\n✓ Tổng: {total_kept} scenes giữ lại, {total_dropped} drop (có mặt)")
    print(f"  → {out_dir}")


if __name__ == "__main__":
    main()
