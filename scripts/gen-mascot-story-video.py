"""Generate mascot story video — characters + text overlay + voiceover."""
import subprocess
import os
from pathlib import Path

# Fix encoding for subprocess on Windows
os.environ["PYTHONIOENCODING"] = "utf-8"

# Paths
PROJECT = Path(__file__).parent.parent
FFMPEG = r"C:\Users\phuocpt5\AppData\Local\Microsoft\WinGet\Links\ffmpeg.exe"
FONT = r"C\:/Windows/Fonts/arialbd.ttf"
OUT_DIR = PROJECT / "output" / "mascot-story" / "v1"

# Character images (white bg, will be placed on colored backgrounds)
CHARACTERS = {
    "pelpel": PROJECT / "avatar.png",
    "bobo": PROJECT / "bo bo.png",
    "mitmit": PROJECT / "mitmit.png",
    "cookie": PROJECT / "Gemini_Generated_Image_aop58oaop58oaop5.png",
}

# Slide definitions: (bg_color, character, text_line1, text_line2, duration_sec)
SLIDES = [
    ("FF9B50", "pelpel", "Pel Pel đi chợ", "mua đồ ăn vặt...", 2.5),
    ("90EE90", "bobo", "Bo Bo: Mua gì vậy?", "Cho tui với!", 2.5),
    ("FFE066", "mitmit", "Mit Mit: Khoan khoan!", "Tui cũng muốn!", 2.5),
    ("D2B48C", "cookie", "Cookie: Hết tiền rồi", "nha mấy đứa!", 2.5),
    ("FFB6C1", None, "Thôi vậy đi!", "Ai follow thì Pel Pel mua cho!", 3.5),
    ("FF6B35", None, "FOLLOW + COMMENT", "tên bạn — Pel Pel trả lời hết!", 4.3),
]

W, H = 1080, 1920
FPS = 30

def make_slide(idx, bg_color, char_key, line1, line2, duration):
    """Create one slide image using FFmpeg with textfile for Vietnamese."""
    out_path = OUT_DIR / f"slide-{idx:02d}.png"

    # Write text to temp files (FFmpeg textfile= handles UTF-8 properly)
    txt1_path = OUT_DIR / f"_txt1_{idx}.txt"
    txt2_path = OUT_DIR / f"_txt2_{idx}.txt"
    txt1_path.write_text(line1, encoding="utf-8")
    txt2_path.write_text(line2, encoding="utf-8")
    txt1_ff = str(txt1_path).replace("\\", "/").replace(":", r"\:")
    txt2_ff = str(txt2_path).replace("\\", "/").replace(":", r"\:")

    # Base: solid color background
    filters = [f"color=c=#{bg_color}:s={W}x{H}:d=1[bg]"]

    if char_key and char_key in CHARACTERS:
        # Overlay character centered, upper-middle (y=350 avoids top safe zone)
        filters.append(
            f"[1:v]scale=500:-1[char];"
            f"[bg][char]overlay=(W-w)/2:350[withchar]"
        )
        base = "[withchar]"
        extra_inputs = ["-i", str(CHARACTERS[char_key])]
    else:
        base = "[bg]"
        extra_inputs = []

    # Text line 1 — center of frame (safe zone y=1050)
    filters.append(
        f"{base}drawtext=fontfile='{FONT}':"
        f"textfile='{txt1_ff}':fontcolor=white:fontsize=72:"
        f"borderw=4:bordercolor=black:"
        f"x=(w-text_w)/2:y=1050[t1]"
    )

    # Text line 2 — below line 1
    filters.append(
        f"[t1]drawtext=fontfile='{FONT}':"
        f"textfile='{txt2_ff}':fontcolor=white:fontsize=60:"
        f"borderw=3:bordercolor=black:"
        f"x=(w-text_w)/2:y=1160[out]"
    )

    filter_complex = ";".join(filters)

    cmd = [
        FFMPEG, "-y",
        "-f", "lavfi", "-i", f"color=c=#{bg_color}:s={W}x{H}:d=1",
        *extra_inputs,
        "-filter_complex", filter_complex,
        "-map", "[out]",
        "-frames:v", "1",
        str(out_path)
    ]

    result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    # Cleanup temp text files
    txt1_path.unlink(missing_ok=True)
    txt2_path.unlink(missing_ok=True)

    if result.returncode != 0:
        print(f"ERROR slide {idx}: {result.stderr[-300:]}")
        return None
    print(f"Created: {out_path.name}")
    return str(out_path)


def assemble_video(slides_with_duration, audio_path, output_path):
    """Combine slides with varying durations + audio into final video."""
    inputs = []
    filter_parts = []

    for i, (slide_path, duration) in enumerate(slides_with_duration):
        inputs.extend(["-loop", "1", "-t", str(duration), "-i", slide_path])
        # Subtle zoom effect
        filter_parts.append(
            f"[{i}:v]scale={W}:{H},"
            f"zoompan=z='min(zoom+0.0008,1.04)'"
            f":x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
            f":d={int(duration * FPS)}:s={W}x{H}:fps={FPS}"
            f"[v{i}]"
        )

    # Crossfade transitions between slides (0.3s each)
    n = len(slides_with_duration)
    if n == 1:
        final = "[v0]"
    else:
        # Chain xfade between consecutive clips
        # Calculate offsets based on cumulative durations
        cumulative = 0
        prev = "[v0]"
        for i in range(1, n):
            cumulative += slides_with_duration[i-1][1] - 0.3  # overlap 0.3s
            xf_label = f"[xf{i}]" if i < n-1 else "[outv]"
            filter_parts.append(
                f"{prev}[v{i}]xfade=transition=fade:duration=0.3:offset={cumulative:.1f}{xf_label}"
            )
            prev = xf_label
        final = "[outv]"

    filter_complex = ";".join(filter_parts)

    cmd = [
        FFMPEG, "-y",
        *inputs,
        "-i", str(audio_path),
        "-filter_complex", filter_complex,
        "-map", final, "-map", f"{n}:a",
        "-c:v", "libx264", "-preset", "medium", "-crf", "23",
        "-c:a", "aac", "-b:a", "128k",
        "-shortest",
        "-pix_fmt", "yuv420p",
        str(output_path)
    ]

    result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if result.returncode != 0:
        print(f"ERROR assemble: {result.stderr[-500:]}")
        return None
    print(f"Video created: {output_path}")
    return str(output_path)


if __name__ == "__main__":
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    # Step 1: Generate slides
    slide_results = []
    for i, (bg, char, l1, l2, dur) in enumerate(SLIDES):
        path = make_slide(i+1, bg, char, l1, l2, dur)
        if path:
            slide_results.append((path, dur))

    if not slide_results:
        print("No slides generated!")
        exit(1)

    # Step 2: Assemble video
    audio = OUT_DIR / "voiceover.mp3"
    output = OUT_DIR / "mascot-story-v1.mp4"
    assemble_video(slide_results, audio, output)
