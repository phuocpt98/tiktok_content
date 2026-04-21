"""Generate mascot cross-follow video — big text overlay throughout."""
import subprocess
import os
from pathlib import Path

os.environ["PYTHONIOENCODING"] = "utf-8"

PROJECT = Path(__file__).parent.parent
FFMPEG = r"C:\Users\phuocpt5\AppData\Local\Microsoft\WinGet\Links\ffmpeg.exe"
FONT = r"C\:/Windows/Fonts/arialbd.ttf"
OUT_DIR = PROJECT / "output" / "mascot-story" / "v2-cross-follow"

# Character images
CHARS = {
    "pelpel": PROJECT / "avatar.png",
    "bobo": PROJECT / "bo bo.png",
    "mitmit": PROJECT / "mitmit.png",
    "cookie": PROJECT / "Gemini_Generated_Image_aop58oaop58oaop5.png",
}

# Slides: (bg_color, char_key, big_text, sub_text, duration)
# Big text = chữ to đè lên, sub_text = dòng phụ nhỏ hơn
SLIDES = [
    ("FF6B35", "pelpel", "AI MỚI XÂY KÊNH", "GIỐNG TUI KHÔNG?", 2.5),
    ("4ECDC4", "bobo",   "FOLLOW CHÉO ĐI!", "TUI FOLLOW LẠI 100%", 2.5),
    ("FFE66D", "mitmit", "COMMENT TÊN", "KÊNH CỦA BẠN BÊN DƯỚI", 3.0),
    ("D2691E", "cookie", "TUI SẼ QUA", "XEM + FOLLOW + LIKE", 2.5),
    ("FF69B4", "pelpel", "CÙNG NHAU", "LÊN 1000 FOLLOW NHA!", 3.0),
    ("FF4500", None,     "FOLLOW NGAY", "RỒI COMMENT - TUI TRẢ HẾT!", 4.0),
]

W, H = 1080, 1920
FPS = 30


def make_slide(idx, bg_color, char_key, big_text, sub_text, duration):
    """Create slide with character (transparent bg) + big text overlay."""
    out_path = OUT_DIR / f"slide-{idx:02d}.png"

    # Write text to temp files for Vietnamese support
    txt1 = OUT_DIR / f"_t1_{idx}.txt"
    txt2 = OUT_DIR / f"_t2_{idx}.txt"
    txt1.write_text(big_text, encoding="utf-8")
    txt2.write_text(sub_text, encoding="utf-8")
    t1ff = str(txt1).replace("\\", "/").replace(":", r"\:")
    t2ff = str(txt2).replace("\\", "/").replace(":", r"\:")

    if char_key and char_key in CHARS:
        char_path = str(CHARS[char_key])
        # Remove white background using colorkey, then overlay on colored bg
        # Character at center, slightly up (y=300)
        filter_complex = (
            f"color=c=#{bg_color}:s={W}x{H}:d=1[bg];"
            # Remove white bg from character PNG
            f"[1:v]colorkey=white:0.3:0.2,scale=550:-1[char];"
            # Place character upper-center
            f"[bg][char]overlay=(W-w)/2:300[base];"
            # BIG TEXT — fontsize 100, center, y=850 (overlaps character bottom)
            f"[base]drawtext=fontfile='{FONT}':"
            f"textfile='{t1ff}':fontcolor=white:fontsize=100:"
            f"borderw=5:bordercolor=black:"
            f"x=(w-text_w)/2:y=850[t1];"
            # Sub text — fontsize 70, below
            f"[t1]drawtext=fontfile='{FONT}':"
            f"textfile='{t2ff}':fontcolor=#FFFF00:fontsize=70:"
            f"borderw=4:bordercolor=black:"
            f"x=(w-text_w)/2:y=1000[out]"
        )
        extra = ["-i", char_path]
    else:
        # No character — just bg + big text centered
        filter_complex = (
            f"color=c=#{bg_color}:s={W}x{H}:d=1[bg];"
            f"[bg]drawtext=fontfile='{FONT}':"
            f"textfile='{t1ff}':fontcolor=white:fontsize=120:"
            f"borderw=6:bordercolor=black:"
            f"x=(w-text_w)/2:y=750[t1];"
            f"[t1]drawtext=fontfile='{FONT}':"
            f"textfile='{t2ff}':fontcolor=#FFFF00:fontsize=80:"
            f"borderw=4:bordercolor=black:"
            f"x=(w-text_w)/2:y=920[out]"
        )
        extra = []

    cmd = [
        FFMPEG, "-y",
        "-f", "lavfi", "-i", f"color=c=#{bg_color}:s={W}x{H}:d=1",
        *extra,
        "-filter_complex", filter_complex,
        "-map", "[out]", "-frames:v", "1",
        str(out_path)
    ]

    result = subprocess.run(cmd, capture_output=True, text=True,
                            encoding="utf-8", errors="replace")
    txt1.unlink(missing_ok=True)
    txt2.unlink(missing_ok=True)

    if result.returncode != 0:
        print(f"ERROR slide {idx}: {result.stderr[-400:]}")
        return None
    print(f"OK: {out_path.name}")
    return str(out_path)


def assemble(slides_dur, audio, output):
    """Combine slides with crossfade + audio."""
    inputs = []
    filters = []

    for i, (path, dur) in enumerate(slides_dur):
        inputs.extend(["-loop", "1", "-t", str(dur), "-i", path])
        filters.append(
            f"[{i}:v]scale={W}:{H},"
            f"zoompan=z='min(zoom+0.001,1.05)'"
            f":x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
            f":d={int(dur * FPS)}:s={W}x{H}:fps={FPS}[v{i}]"
        )

    # Crossfade chain
    n = len(slides_dur)
    cum = 0
    prev = "[v0]"
    for i in range(1, n):
        cum += slides_dur[i-1][1] - 0.3
        label = f"[xf{i}]" if i < n-1 else "[outv]"
        filters.append(
            f"{prev}[v{i}]xfade=transition=fade:duration=0.3"
            f":offset={cum:.1f}{label}"
        )
        prev = label

    cmd = [
        FFMPEG, "-y", *inputs,
        "-i", str(audio),
        "-filter_complex", ";".join(filters),
        "-map", "[outv]", "-map", f"{n}:a",
        "-c:v", "libx264", "-preset", "medium", "-crf", "23",
        "-c:a", "aac", "-b:a", "128k", "-shortest",
        "-pix_fmt", "yuv420p", str(output)
    ]

    result = subprocess.run(cmd, capture_output=True, text=True,
                            encoding="utf-8", errors="replace")
    if result.returncode != 0:
        print(f"ERROR: {result.stderr[-500:]}")
        return None
    print(f"Video: {output}")
    return str(output)


if __name__ == "__main__":
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    # Generate voiceover
    print("Generating voiceover...")
    voice_text = (
        "Ai mới xây kênh giống tui không? "
        "Follow chéo đi! Tui follow lại một trăm phần trăm! "
        "Comment tên kênh của bạn bên dưới nha. "
        "Tui sẽ qua xem, follow, và like cho bạn. "
        "Cùng nhau lên một ngàn follow nha! "
        "Follow ngay rồi comment đi, tui trả hết!"
    )
    audio_path = OUT_DIR / "voiceover.mp3"
    subprocess.run([
        "cmd.exe", "/c",
        f'set PYTHONIOENCODING=utf-8 & cd /d {PROJECT} & '
        f'.venv\\Scripts\\python.exe -m edge_tts '
        f'--text "{voice_text}" '
        f'--voice vi-VN-HoaiMyNeural --rate +50% '
        f'--write-media "{audio_path}"'
    ], capture_output=True)
    print(f"Voice: {audio_path}")

    # Generate slides
    results = []
    for i, (bg, ch, t1, t2, dur) in enumerate(SLIDES):
        path = make_slide(i+1, bg, ch, t1, t2, dur)
        if path:
            results.append((path, dur))

    if not results:
        print("No slides!")
        exit(1)

    # Assemble
    out = OUT_DIR / "cross-follow-v2.mp4"
    assemble(results, audio_path, out)
