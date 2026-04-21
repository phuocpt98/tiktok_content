"""Convert images to TikTok-style trending videos with transitions."""
import subprocess
import json
import logging
from pathlib import Path
from datetime import datetime
from src.config import OUTPUT_DIR, VIDEO_WIDTH, VIDEO_HEIGHT, VIDEO_FPS, FFMPEG_PATH

log = logging.getLogger(__name__)

# Trending transition presets
TRANSITIONS = {
    "zoom_in": (
        "zoompan=z='min(zoom+0.003,1.3)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
        f":d={{frames}}:s={VIDEO_WIDTH}x{VIDEO_HEIGHT}:fps={VIDEO_FPS}"
    ),
    "zoom_out": (
        "zoompan=z='if(lte(zoom,1.0),1.3,max(1.001,zoom-0.003))':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
        f":d={{frames}}:s={VIDEO_WIDTH}x{VIDEO_HEIGHT}:fps={VIDEO_FPS}"
    ),
    "pan_left": (
        "zoompan=z='1.1':x='if(lte(on,1),(iw-iw/zoom)*0.8,(iw-iw/zoom)*0.8-on*2)':y='(ih-ih/zoom)/2'"
        f":d={{frames}}:s={VIDEO_WIDTH}x{VIDEO_HEIGHT}:fps={VIDEO_FPS}"
    ),
    "pan_right": (
        "zoompan=z='1.1':x='if(lte(on,1),0,on*2)':y='(ih-ih/zoom)/2'"
        f":d={{frames}}:s={VIDEO_WIDTH}x{VIDEO_HEIGHT}:fps={VIDEO_FPS}"
    ),
    "static": (
        "zoompan=z='1':x='(iw-iw/zoom)/2':y='(ih-ih/zoom)/2'"
        f":d={{frames}}:s={VIDEO_WIDTH}x{VIDEO_HEIGHT}:fps={VIDEO_FPS}"
    ),
}


def images_to_trend_video(images: list[str],
                          audio_path: str = None,
                          duration_per_image: float = 3.0,
                          transition: str = "zoom_in",
                          crossfade: float = 0.5,
                          output_name: str = None) -> str:
    """Create trending TikTok video from 2+ images.

    Args:
        images: List of image paths (2+ images)
        audio_path: Optional audio/music path
        duration_per_image: Seconds each image shows
        transition: Effect preset (zoom_in, zoom_out, pan_left, pan_right, static)
        crossfade: Seconds of crossfade between images
        output_name: Optional output filename

    Returns: Path to output video
    """
    if len(images) < 1:
        raise ValueError("Need at least 1 image")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    fname = output_name or f"trend_{timestamp}.mp4"
    output_path = OUTPUT_DIR / fname

    frames = int(duration_per_image * VIDEO_FPS)

    # Alternate transitions for visual variety
    transition_list = ["zoom_in", "zoom_out", "pan_left", "pan_right"]
    if transition == "mix":
        effects = [transition_list[i % len(transition_list)] for i in range(len(images))]
    else:
        effects = [transition] * len(images)

    # Build FFmpeg command
    inputs = []
    filter_parts = []

    for i, img in enumerate(images):
        inputs.extend(["-loop", "1", "-t", str(duration_per_image), "-i", img])
        # Scale to fit 9:16 first, then apply transition
        effect = TRANSITIONS[effects[i]].format(frames=frames)
        filter_parts.append(
            f"[{i}:v]scale={VIDEO_WIDTH}:{VIDEO_HEIGHT}:force_original_aspect_ratio=decrease,"
            f"pad={VIDEO_WIDTH}:{VIDEO_HEIGHT}:(ow-iw)/2:(oh-ih)/2:color=black,"
            f"{effect},"
            f"setpts=PTS-STARTPTS,format=yuva420p[v{i}]"
        )

    # Crossfade between segments
    if len(images) == 1:
        filter_complex = f"{filter_parts[0].replace(f'[v0]', '[outv]')}"
    elif len(images) == 2:
        filter_complex = ";".join(filter_parts)
        cf_start = duration_per_image - crossfade
        filter_complex += (
            f";[v0][v1]xfade=transition=fadeblack:duration={crossfade}"
            f":offset={cf_start}[outv]"
        )
    else:
        # Chain multiple crossfades
        filter_complex = ";".join(filter_parts)
        prev = "v0"
        for i in range(1, len(images)):
            cf_start = (duration_per_image - crossfade) * i
            out = "outv" if i == len(images) - 1 else f"cf{i}"
            filter_complex += (
                f";[{prev}][v{i}]xfade=transition=fadeblack:duration={crossfade}"
                f":offset={cf_start}[{out}]"
            )
            prev = out

    # Build full command
    cmd = [
        FFMPEG_PATH, "-y",
        *inputs,
    ]

    if audio_path:
        cmd.extend(["-i", audio_path])

    cmd.extend([
        "-filter_complex", filter_complex,
        "-map", "[outv]",
    ])

    if audio_path:
        cmd.extend(["-map", f"{len(images)}:a", "-shortest"])

    cmd.extend([
        "-c:v", "libx264", "-preset", "medium", "-crf", "23",
        "-c:a", "aac", "-b:a", "128k",
        "-pix_fmt", "yuv420p",
        "-t", str(duration_per_image * len(images)),
        str(output_path)
    ])

    log.info(f"Creating trend video: {len(images)} images, transition={transition}")
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        log.error(f"FFmpeg error: {result.stderr[:300]}")
        raise RuntimeError(f"FFmpeg error: {result.stderr[:300]}")

    log.info(f"Video created: {output_path}")
    return str(output_path)


def two_image_trend(image1: str, image2: str,
                    audio_path: str = None,
                    style: str = "before_after") -> str:
    """Create the popular '2 image trend' video.

    Styles:
        before_after: zoom out from img1, crossfade to zoom in on img2
        compare: side by side then full screen each
        reveal: static img1, dramatic zoom into img2
    """
    if style == "before_after":
        return images_to_trend_video(
            [image1, image2], audio_path,
            duration_per_image=2.5, transition="mix", crossfade=0.8
        )
    elif style == "compare":
        return images_to_trend_video(
            [image1, image2], audio_path,
            duration_per_image=3.0, transition="static", crossfade=0.3
        )
    elif style == "reveal":
        return images_to_trend_video(
            [image1, image2], audio_path,
            duration_per_image=2.0, transition="zoom_in", crossfade=1.0
        )
    else:
        return images_to_trend_video(
            [image1, image2], audio_path,
            duration_per_image=2.5, transition=style, crossfade=0.5
        )
