"""
Cắt video gốc thành nhiều video ngắn theo từng phân cảnh (scene detection).

Usage:
  python scripts/split-video-by-scenes.py <video_path> [--threshold 27] [--min-len 1.0]

Default: tự tìm video trong assets/products/banh-quy-lss/videos/ nếu không truyền arg.

Install:
  pip install "scenedetect[opencv]"

Cần FFmpeg trong PATH (scenedetect dùng ffmpeg để cắt stream copy, nhanh + lossless).
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from scenedetect import ContentDetector, SceneManager, open_video
from scenedetect.video_splitter import split_video_ffmpeg

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_PRODUCT_VIDEOS = ROOT / "assets" / "products" / "banh-quy-lss" / "videos"


def find_default_video() -> Path:
    vids = [p for p in DEFAULT_PRODUCT_VIDEOS.glob("*.mp4") if "scenes" not in p.parts]
    if not vids:
        raise SystemExit(f"Không tìm thấy .mp4 trong {DEFAULT_PRODUCT_VIDEOS}")
    if len(vids) > 1:
        print(f"Có {len(vids)} video, dùng cái đầu tiên: {vids[0].name}")
    return vids[0]


def detect_scenes(video_path: Path, threshold: float, min_scene_sec: float):
    video = open_video(str(video_path))
    fps = video.frame_rate
    min_scene_frames = int(min_scene_sec * fps)

    manager = SceneManager()
    manager.add_detector(ContentDetector(threshold=threshold, min_scene_len=min_scene_frames))
    manager.detect_scenes(video=video, show_progress=True)
    return manager.get_scene_list()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("video", nargs="?", help="Đường dẫn video (bỏ trống = auto tìm trong banh-quy-lss/videos/)")
    ap.add_argument("--threshold", type=float, default=27.0, help="Ngưỡng đổi cảnh (thấp = nhạy, 22-30 hợp lý; default 27)")
    ap.add_argument("--min-len", type=float, default=1.0, help="Độ dài tối thiểu 1 cảnh (giây, default 1.0)")
    ap.add_argument("--output", type=Path, default=None, help="Thư mục output (default: <video_dir>/scenes/)")
    args = ap.parse_args()

    video_path = Path(args.video).resolve() if args.video else find_default_video()
    if not video_path.exists():
        raise SystemExit(f"Video không tồn tại: {video_path}")

    out_dir = args.output or video_path.parent / "scenes"
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"Video   : {video_path}")
    print(f"Output  : {out_dir}")
    print(f"Threshold: {args.threshold}  |  Min scene length: {args.min_len}s")
    print("-" * 60)

    scenes = detect_scenes(video_path, args.threshold, args.min_len)
    if not scenes:
        print("Không detect được scene — video có thể quá đồng nhất. Thử --threshold 18 (nhạy hơn).")
        return 1

    print(f"\nĐã detect {len(scenes)} cảnh:")
    for i, (start, end) in enumerate(scenes, 1):
        dur = (end - start).get_seconds()
        print(f"  Scene {i:02d}: {start.get_timecode()} → {end.get_timecode()}  ({dur:.2f}s)")

    print("\nĐang cắt (stream copy, không re-encode)...")
    out_template = str(out_dir / "scene-$SCENE_NUMBER.mp4")
    split_video_ffmpeg(
        str(video_path),
        scenes,
        output_file_template=out_template,
        show_progress=True,
    )

    print(f"\nXong. {len(scenes)} file trong {out_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
