"""Video assembler using FFmpeg - combines images + audio into TikTok video."""
import subprocess
import json
from pathlib import Path
from datetime import datetime
from src.config import OUTPUT_DIR, VIDEO_WIDTH, VIDEO_HEIGHT, VIDEO_FPS


def create_slideshow(images: list[str], audio_path: str,
                     output_name: str = None,
                     duration_per_image: float = None) -> str:
    """Create vertical slideshow video from images + audio.

    Args:
        images: List of image file paths
        audio_path: Path to audio/voiceover file
        output_name: Optional output filename
        duration_per_image: Seconds per image (auto-calculated from audio if None)

    Returns: Path to output video file
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    fname = output_name or f"video_{timestamp}.mp4"
    output_path = OUTPUT_DIR / fname

    # Get audio duration to calculate per-image timing
    if duration_per_image is None:
        audio_duration = _get_duration(audio_path)
        duration_per_image = audio_duration / len(images) if images else 5.0

    # Build FFmpeg filter for slideshow with zoom/pan effect
    inputs = []
    filter_parts = []

    for i, img in enumerate(images):
        inputs.extend(["-loop", "1", "-t", str(duration_per_image), "-i", img])
        # Scale + crop to 9:16, add subtle zoom effect
        filter_parts.append(
            f"[{i}:v]scale={VIDEO_WIDTH}:{VIDEO_HEIGHT}:force_original_aspect_ratio=decrease,"
            f"pad={VIDEO_WIDTH}:{VIDEO_HEIGHT}:(ow-iw)/2:(oh-ih)/2:color=black,"
            f"zoompan=z='min(zoom+0.001,1.05)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
            f":d={int(duration_per_image * VIDEO_FPS)}:s={VIDEO_WIDTH}x{VIDEO_HEIGHT}:fps={VIDEO_FPS}"
            f"[v{i}]"
        )

    # Concatenate all video segments
    concat_inputs = "".join(f"[v{i}]" for i in range(len(images)))
    filter_complex = ";".join(filter_parts)
    filter_complex += f";{concat_inputs}concat=n={len(images)}:v=1:a=0[outv]"

    cmd = [
        "ffmpeg", "-y",
        *inputs,
        "-i", audio_path,
        "-filter_complex", filter_complex,
        "-map", "[outv]", "-map", f"{len(images)}:a",
        "-c:v", "libx264", "-preset", "medium", "-crf", "23",
        "-c:a", "aac", "-b:a", "128k",
        "-shortest",
        "-pix_fmt", "yuv420p",
        str(output_path)
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"FFmpeg error: {result.stderr[:500]}")

    return str(output_path)


def add_background_music(video_path: str, music_path: str,
                         music_volume: float = 0.15) -> str:
    """Add background music to existing video. Returns new video path."""
    output_path = Path(video_path).with_suffix(".final.mp4")

    cmd = [
        "ffmpeg", "-y",
        "-i", video_path,
        "-i", music_path,
        "-filter_complex",
        f"[1:a]volume={music_volume}[bg];[0:a][bg]amix=inputs=2:duration=first[outa]",
        "-map", "0:v", "-map", "[outa]",
        "-c:v", "copy", "-c:a", "aac", "-b:a", "128k",
        "-shortest",
        str(output_path)
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"FFmpeg error: {result.stderr[:500]}")

    return str(output_path)


def _get_duration(file_path: str) -> float:
    """Get media file duration in seconds using ffprobe."""
    cmd = [
        "ffprobe", "-v", "quiet",
        "-print_format", "json",
        "-show_format",
        file_path
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        return 30.0  # fallback 30s

    data = json.loads(result.stdout)
    return float(data.get("format", {}).get("duration", 30.0))
