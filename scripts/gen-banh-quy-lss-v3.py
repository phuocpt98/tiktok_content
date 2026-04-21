"""
Gen video ngắn 15s cho Bánh Quy LSS — 8 vị.
Voice: vi-VN-NamMinhNeural (nam, khác với default HoaiMy).
Dùng các scene đã cắt từ video gốc, nối theo timeline 4 đoạn TTS.

Usage:  python3 scripts/gen-banh-quy-lss-v1.py
Yêu cầu: ffmpeg, edge-tts trong PATH/python.
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
PROD = ROOT / "assets" / "products" / "banh-quy-lss"
VIDS = PROD / "videos"
OUT = PROD / "output"
OUT_AUDIO = OUT / "audio"
OUT_FINAL = OUT / "final"
OUT_TMP = OUT / "_tmp_v3"
for d in (OUT_AUDIO, OUT_FINAL, OUT_TMP):
    d.mkdir(parents=True, exist_ok=True)

VOICE = "vi-VN-HoaiMyNeural"    # Giọng nữ miền Nam
RATE_TRIES = ["+25%", "+30%", "+45%"]  # thử rate tăng dần để voice fit target (tránh +35% hay lỗi)
TTS_RETRIES = 3                  # retry khi edge-tts trả về rỗng
TAIL_PAD = 0.25                  # đệm silence cuối mỗi đoạn (breathing)
W, H = 1080, 1920
FPS = 30

FONT = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"  # VN-capable bold

# ---- TIMELINE (v3: thêm greet công chúa + CTA follow/tym) ----
# (label, target_duration, voice_text, subtitle_text, [scenes])
SEGMENTS = [
    ("greet", 2.5,
     "Chào công chúa xinh đẹp nhất thế gian!",
     "CHÀO CÔNG CHÚA\nxinh đẹp nhất thế gian!",
     ["scene-006.mp4", "scene-008.mp4"]),
    ("hook", 3.0,
     "Ơ, cái này là gì mà nhìn ngon vậy trời?!",
     "Ơ cái này là gì\nmà nhìn ngon vậy trời?!",
     ["scene-001.mp4", "scene-002.mp4"]),
    ("intro", 5.0,
     "Bánh quy LSS — 8 vị siêu đỉnh! Socola chip, tart việt quất, "
     "nhân sữa chảy tan miệng, hình gấu cute nữa.",
     "BÁNH QUY LSS — 8 VỊ\nSocola chip, tart việt quất\nnhân sữa chảy, gấu cute...",
     ["scene-004.mp4", "scene-005.mp4"]),
    ("experience", 4.0,
     "Mỗi miếng cắn ra là một bất ngờ — béo, ngọt, chua ngọt đủ cả!",
     "Mỗi miếng — một bất ngờ!\nBéo, ngọt, chua ngọt đủ cả!",
     ["scene-007.mp4", "scene-010.mp4", "scene-013.mp4"]),
    ("price", 3.5,
     "130 nghìn một ký thôi, có bán lẻ luôn nha — inbox mình ngay!",
     "130K/KG — CÓ BÁN LẺ\nInbox mình ngay nha!",
     ["scene-015.mp4", "scene-017.mp4"]),
    ("follow", 3.0,
     "Thả tym và follow để ủng hộ mình nha công chúa!",
     "Thả tym + follow nha\ncông chúa ơi!",
     ["scene-011.mp4", "scene-014.mp4", "scene-016.mp4"]),
]

TOTAL = sum(s[1] for s in SEGMENTS)  # ~21s


def run(cmd, check=True):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if check and r.returncode != 0:
        print("CMD FAILED:", " ".join(map(str, cmd)))
        print(r.stderr[-1500:])
        raise SystemExit(1)
    return r


def probe_duration(path: Path) -> float:
    r = run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "json", str(path)])
    return float(json.loads(r.stdout)["format"]["duration"])


def gen_voice_raw(text: str, rate: str, out_path: Path):
    last_err = ""
    for attempt in range(1, TTS_RETRIES + 1):
        r = run([sys.executable, "-m", "edge_tts",
                 "--voice", VOICE, "--rate", rate,
                 "--text", text, "--write-media", str(out_path)],
                check=False)
        if r.returncode == 0 and out_path.exists() and out_path.stat().st_size > 1000:
            return
        last_err = r.stderr[-400:]
        print(f"    retry {attempt}/{TTS_RETRIES} rate={rate}")
    raise SystemExit(f"edge-tts failed sau {TTS_RETRIES} lần rate={rate}: {last_err}")


def gen_voice_fit(text: str, target: float, label: str) -> tuple[Path, float]:
    """Thử các rate tăng dần để voice vừa target+0.3s.
    Trả về (path, duration) của bản đạt được (hoặc bản nhanh nhất nếu vẫn quá dài).
    """
    best: tuple[Path, float] | None = None
    for rate in RATE_TRIES:
        raw = OUT_TMP / f"voice_{label}_raw_{rate.replace('+','p').replace('%','')}.mp3"
        gen_voice_raw(text, rate, raw)
        dur = probe_duration(raw)
        print(f"  rate {rate} → {dur:.2f}s")
        if dur <= target + 0.3:
            return raw, dur
        best = (raw, dur)
    print(f"  ! dù đã {RATE_TRIES[-1]} vẫn {best[1]:.2f}s > target {target}s — sẽ co giãn timeline")
    return best


def fit_audio_segment(src: Path, target: float, dst: Path) -> float:
    """Đảm bảo segment audio có duration >= target (pad silence) hoặc giữ nguyên nếu dài hơn.
    Trả về duration thực tế của segment.
    """
    dur = probe_duration(src)
    # Luôn thêm TAIL_PAD để có khoảng nghỉ giữa các đoạn
    actual_target = max(target, dur + TAIL_PAD)
    pad = actual_target - dur
    run(["ffmpeg", "-y", "-i", str(src),
         "-af", f"apad=pad_dur={pad:.3f}",
         "-t", f"{actual_target:.3f}",
         "-c:a", "aac", "-b:a", "192k", str(dst)])
    return actual_target


def render_subtitle_png(subtitle: str, out_png: Path,
                        font_size: int = 62, y_frac: float = 0.70):
    """Render subtitle text thành 1 PNG transparent 1080x1920.
    Style: chữ trắng đậm + outline đen dày + hộp nền bán trong."""
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype(FONT, font_size)

    lines = [ln.strip() for ln in subtitle.split("\n") if ln.strip()]
    widths, heights = [], []
    for ln in lines:
        bbox = draw.textbbox((0, 0), ln, font=font)
        widths.append(bbox[2] - bbox[0])
        heights.append(bbox[3] - bbox[1])

    line_h = max(heights) + 18               # line spacing
    total_h = line_h * len(lines)
    max_w = max(widths)

    y_start = int(H * y_frac)
    x_center = W // 2
    pad = 34

    # Semi-transparent rounded background
    box = [x_center - max_w // 2 - pad, y_start - pad,
           x_center + max_w // 2 + pad, y_start + total_h - 18 + pad]
    draw.rounded_rectangle(box, radius=28, fill=(0, 0, 0, 160))

    # Text with outline (faux-bold via stroke) + white fill
    for i, ln in enumerate(lines):
        x = x_center - widths[i] // 2
        y = y_start + i * line_h - 6
        draw.text((x, y), ln, font=font,
                  fill=(255, 255, 255, 255),
                  stroke_width=5, stroke_fill=(0, 0, 0, 255))

    img.save(out_png)


def build_video_segment(scenes: list[str], target: float, subtitle: str, out_path: Path):
    """Concat scenes, scale/pad về 1080x1920, cắt/loop cho đúng target, overlay subtitle."""
    # Scale từng scene về 1080x1920 (fit contain + pad đen), loại bỏ audio.
    scaled = []
    for idx, s in enumerate(scenes):
        src = VIDS / s
        if not src.exists():
            raise SystemExit(f"Thiếu scene: {src}")
        dst = OUT_TMP / f"scaled_{out_path.stem}_{idx:02d}.mp4"
        run([
            "ffmpeg", "-y", "-i", str(src),
            "-vf",
            f"scale={W}:{H}:force_original_aspect_ratio=decrease,"
            f"pad={W}:{H}:(ow-iw)/2:(oh-ih)/2:color=black,"
            f"setsar=1,fps={FPS}",
            "-an", "-c:v", "libx264", "-preset", "veryfast",
            "-pix_fmt", "yuv420p", str(dst)
        ])
        scaled.append(dst)

    # Concat
    concat_list = OUT_TMP / f"concat_{out_path.stem}.txt"
    concat_list.write_text(
        "\n".join(f"file '{p.as_posix()}'" for p in scaled) + "\n")
    raw = OUT_TMP / f"raw_{out_path.stem}.mp4"
    run(["ffmpeg", "-y", "-f", "concat", "-safe", "0",
         "-i", str(concat_list),
         "-c:v", "libx264", "-preset", "veryfast",
         "-pix_fmt", "yuv420p", "-an", str(raw)])

    # Trim hoặc freeze-frame để đạt target
    timed = OUT_TMP / f"timed_{out_path.stem}.mp4"
    dur = probe_duration(raw)
    if abs(dur - target) < 0.05:
        shutil.copyfile(raw, timed)
    elif dur > target:
        run(["ffmpeg", "-y", "-i", str(raw), "-t", f"{target}",
             "-c:v", "libx264", "-preset", "veryfast",
             "-pix_fmt", "yuv420p", "-an", str(timed)])
    else:
        extra = target - dur
        run(["ffmpeg", "-y", "-i", str(raw),
             "-vf", f"tpad=stop_mode=clone:stop_duration={extra:.3f},fps={FPS}",
             "-c:v", "libx264", "-preset", "veryfast",
             "-pix_fmt", "yuv420p", "-an", str(timed)])

    # Overlay subtitle bằng PIL (render PNG transparent) + ffmpeg overlay
    sub_png = OUT_TMP / f"sub_{out_path.stem}.png"
    render_subtitle_png(subtitle, sub_png)
    run([
        "ffmpeg", "-y",
        "-i", str(timed), "-i", str(sub_png),
        "-filter_complex", "[0:v][1:v]overlay=0:0",
        "-c:v", "libx264", "-preset", "veryfast",
        "-pix_fmt", "yuv420p", "-an", str(out_path)
    ])


def main():
    print(f"== Gen video Bánh Quy LSS v1 — ~15s — voice {VOICE} (rate tries {RATE_TRIES}) ==\n")

    # 1) VOICE — gen & tính actual duration mỗi segment
    voice_parts = []
    actual_durations: list[float] = []
    for label, target, text, _sub, _scenes in SEGMENTS:
        print(f"[VOICE] {label} target={target}s")
        raw, raw_dur = gen_voice_fit(text, target, label)
        padded = OUT_TMP / f"voice_{label}.m4a"
        actual = fit_audio_segment(raw, target, padded)
        actual_durations.append(actual)
        print(f"  → actual duration: {actual:.2f}s")
        voice_parts.append(padded)

    audio_list = OUT_TMP / "audio_concat.txt"
    audio_list.write_text("\n".join(f"file '{p.as_posix()}'" for p in voice_parts) + "\n")
    voiceover = OUT_AUDIO / "v1-voiceover.m4a"
    run(["ffmpeg", "-y", "-f", "concat", "-safe", "0",
         "-i", str(audio_list),
         "-c:a", "aac", "-b:a", "192k", str(voiceover)])
    vo_dur = probe_duration(voiceover)
    print(f"  → voiceover: {voiceover} ({vo_dur:.2f}s)")

    # 2) VIDEO SEGMENTS — mỗi segment match duration audio tương ứng + subtitle
    vid_parts = []
    for (label, _target, _text, subtitle, scenes), dur in zip(SEGMENTS, actual_durations):
        print(f"[VIDEO] {label} duration={dur:.2f}s  scenes={scenes}")
        seg_out = OUT_TMP / f"seg_{label}.mp4"
        build_video_segment(scenes, dur, subtitle, seg_out)
        vid_parts.append(seg_out)

    # 3) CONCAT video
    vlist = OUT_TMP / "video_concat.txt"
    vlist.write_text("\n".join(f"file '{p.as_posix()}'" for p in vid_parts) + "\n")
    merged_video = OUT_TMP / "merged_video.mp4"
    run(["ffmpeg", "-y", "-f", "concat", "-safe", "0",
         "-i", str(vlist),
         "-c:v", "libx264", "-preset", "veryfast",
         "-pix_fmt", "yuv420p", "-an", str(merged_video)])
    print(f"  → merged video: {probe_duration(merged_video):.2f}s")

    # 4) MUX audio + video
    final = OUT_FINAL / "260422-banh-quy-lss-v3-greet-follow.mp4"
    run(["ffmpeg", "-y",
         "-i", str(merged_video), "-i", str(voiceover),
         "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
         "-map", "0:v:0", "-map", "1:a:0",
         "-shortest", str(final)])

    print(f"\n✓ FINAL: {final}")
    print(f"  duration: {probe_duration(final):.2f}s")
    print(f"  size: {final.stat().st_size/1024:.1f} KB")


if __name__ == "__main__":
    main()
