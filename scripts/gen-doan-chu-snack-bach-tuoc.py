# Pilot video "Đuổi hình bắt chữ — Mời đoán món"
# Product: Snack Bạch Tuộc | 15s | 1080x1920 | HoaiMyNeural +30%
# Cấu trúc: Hook → Clue1 → Clue2 → Reveal → CTA

import asyncio
import os
import edge_tts
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
from moviepy import (
    ImageClip, VideoFileClip, AudioFileClip,
    concatenate_videoclips, CompositeVideoClip
)
from moviepy.video.fx import FadeIn, FadeOut

# === CONFIG ===
BASE = "D:/project/demo/content"
SLUG = "snack-bach-tuoc"
PHOTOS = f"{BASE}/assets/products/{SLUG}/photos"
VIDEOS = f"{BASE}/assets/products/{SLUG}/videos"
OUT_BASE = f"{BASE}/assets/products/{SLUG}/output"
OUT_SLIDES = f"{OUT_BASE}/slides"
OUT_AUDIO = f"{OUT_BASE}/audio"
OUT_FINAL = f"{OUT_BASE}/final"

FONT_BOLD = "C:/Windows/Fonts/arialbd.ttf"
FONT_REG = "C:/Windows/Fonts/arial.ttf"
W, H = 1080, 1920
VOICE = "vi-VN-HoaiMyNeural"
CROSSFADE = 0.3

# Ghi chú: từ "snack bạch tuộc" = 3 từ, bắt đầu "S"
# Assets chọn:
#   - Hook (zoom cực gần): Untitled10.png crop center
#   - Clue 1 (ASMR): ASMR_Bóp_Vỡ_Snack_Bạch_Tuộc.mp4
#   - Clue 2 (close-up): kling close-up
#   - Reveal (flat lay full): Untitled9.png
#   - CTA (ảnh sáng): Untitled.png

VOICE_SCRIPT = (
    "Mời các bạn đoán xem đây là món gì nào. "
    "Gợi ý nè, ba từ, tên loài hải sản tám chân, vị cay cay giòn rụm. "
    "Bắt đầu bằng chữ ét-xì nha. Đoán ra chưa? "
    "Chính xác, snack bạch tuộc! "
    "Comment đoán đúng chưa, follow em đoán món mới mỗi ngày!"
)


def brighten(img, factor=1.15):
    return ImageEnhance.Brightness(img).enhance(factor)


def fit_fill(img_path, zoom=1.0, brightness=1.0):
    img = Image.open(img_path).convert("RGB")
    ratio = max(W / img.width, H / img.height) * zoom
    nw, nh = int(img.width * ratio), int(img.height * ratio)
    img = img.resize((nw, nh), Image.LANCZOS)
    x, y = (nw - W) // 2, (nh - H) // 2
    img = img.crop((x, y, x + W, y + H))
    if brightness != 1.0:
        img = brighten(img, brightness)
    return img


def draw_text_strip(canvas, lines, y_base, strip_color=(255, 255, 255, 220), pad=28):
    """Vẽ strip mờ trắng + text bold căn giữa. lines = [{text, size, color, bold}]"""
    draw = ImageDraw.Draw(canvas, "RGBA")
    total_h = sum(l["size"] + 18 for l in lines) + pad * 2
    max_w = 0
    font_cache = {}
    for l in lines:
        fp = FONT_BOLD if l.get("bold") else FONT_REG
        font = ImageFont.truetype(fp, l["size"])
        font_cache[l["text"]] = font
        bbox = draw.textbbox((0, 0), l["text"], font=font)
        max_w = max(max_w, bbox[2] - bbox[0])

    strip_w = max_w + pad * 2
    strip_x = (W - strip_w) // 2
    draw.rounded_rectangle(
        [(strip_x, y_base - pad), (strip_x + strip_w, y_base + total_h - pad)],
        radius=32, fill=strip_color,
    )

    cy = y_base
    for l in lines:
        font = font_cache[l["text"]]
        bbox = draw.textbbox((0, 0), l["text"], font=font)
        tw = bbox[2] - bbox[0]
        x = (W - tw) // 2
        color = l["color"]
        if isinstance(color, str):
            r, g, b = tuple(int(color.lstrip("#")[i:i+2], 16) for i in (0, 2, 4))
            color = (r, g, b, 255)
        draw.text((x, cy), l["text"], fill=color, font=font)
        cy += l["size"] + 18


def make_slide(img_path, lines, y_base, brightness=1.15, zoom=1.0):
    bg = fit_fill(img_path, zoom=zoom, brightness=brightness)
    canvas = bg.convert("RGBA")
    draw_text_strip(canvas, lines, y_base)
    return canvas.convert("RGB")


def prep_video(path, dur, zoom_wm=1.1):
    clip = VideoFileClip(path)
    if clip.duration > dur:
        clip = clip.subclipped(0, dur)
    cw, ch = clip.size
    ratio = max(W / cw, H / ch) * zoom_wm
    nw, nh = int(cw * ratio), int(ch * ratio)
    clip = clip.resized((nw, nh))
    x, y = (nw - W) // 2, (nh - H) // 2
    return clip.cropped(x1=x, y1=y, x2=x + W, y2=y + H)


def text_overlay_clip(lines, y_base, dur):
    """Transparent PNG overlay with text strip — dùng trên video."""
    canvas = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw_text_strip(canvas, lines, y_base)
    path = f"{OUT_SLIDES}/doan-chu-overlay-{y_base}.png"
    canvas.save(path, "PNG")
    return ImageClip(path, duration=dur, transparent=True)


async def gen_voice(text, out_path):
    comm = edge_tts.Communicate(text, VOICE, rate="+30%")
    await comm.save(out_path)
    print(f"  Voice: {os.path.basename(out_path)}")


async def main():
    for d in (OUT_SLIDES, OUT_AUDIO, OUT_FINAL):
        os.makedirs(d, exist_ok=True)

    # Step 1: Voice
    print("=== VOICE ===")
    audio_path = f"{OUT_AUDIO}/doan-chu-voiceover.mp3"
    await gen_voice(VOICE_SCRIPT, audio_path)
    audio = AudioFileClip(audio_path)
    total = audio.duration
    print(f"  Duration: {total:.2f}s")

    # Step 2: Segments — ratios
    # Hook 20% | Clue1 22% | Clue2 20% | Reveal 22% | CTA 16%
    ratios = [0.20, 0.22, 0.20, 0.22, 0.16]
    durs = [total * r for r in ratios]
    clips = []

    # --- 1. HOOK: ảnh zoom cực gần + text "ĐỐ BẠN MÓN GÌ?" ---
    print("\n[1] HOOK")
    s1 = make_slide(
        f"{PHOTOS}/Untitled10.png",
        [
            {"text": "ĐỐ BẠN —", "size": 80, "color": "#FF3366", "bold": True},
            {"text": "MÓN GÌ?", "size": 96, "color": "#3D2200", "bold": True},
        ],
        y_base=220, brightness=1.20, zoom=1.8,  # zoom 1.8 = crop cực gần
    )
    s1.save(f"{OUT_SLIDES}/doan-chu-s1-hook.png")
    c1 = ImageClip(f"{OUT_SLIDES}/doan-chu-s1-hook.png", duration=durs[0]).with_effects([FadeIn(0.3)])
    clips.append(c1)

    # --- 2. CLUE 1: ASMR video + text "3 TỪ • HẢI SẢN 8 CHÂN" ---
    print("[2] CLUE 1 — ASMR")
    asmr = f"{VIDEOS}/ASMR_Bóp_Vỡ_Snack_Bạch_Tuộc.mp4"
    v2 = prep_video(asmr, durs[1], zoom_wm=1.0).with_effects([FadeIn(CROSSFADE), FadeOut(CROSSFADE)])
    ovl2 = text_overlay_clip(
        [
            {"text": "GỢI Ý 1:", "size": 64, "color": "#FF3366", "bold": True},
            {"text": "3 TỪ • HẢI SẢN 8 CHÂN", "size": 54, "color": "#3D2200", "bold": True},
        ],
        y_base=180, dur=durs[1],
    )
    seg2 = CompositeVideoClip([v2, ovl2]).with_duration(durs[1])
    clips.append(seg2)

    # --- 3. CLUE 2: Kling close-up + text "BẮT ĐẦU BẰNG CHỮ S" ---
    print("[3] CLUE 2 — Kling close-up")
    kling = f"{VIDEOS}/kling_20260417_作品___Close_up_4188_0.mp4"
    v3 = prep_video(kling, durs[2], zoom_wm=1.1).with_effects([FadeIn(CROSSFADE), FadeOut(CROSSFADE)])
    ovl3 = text_overlay_clip(
        [
            {"text": "GỢI Ý 2:", "size": 64, "color": "#FF3366", "bold": True},
            {"text": "BẮT ĐẦU BẰNG  S ", "size": 58, "color": "#3D2200", "bold": True},
        ],
        y_base=180, dur=durs[2],
    )
    seg3 = CompositeVideoClip([v3, ovl3]).with_duration(durs[2])
    clips.append(seg3)

    # --- 4. REVEAL: flat lay full + text to "SNACK BẠCH TUỘC" ---
    print("[4] REVEAL")
    s4 = make_slide(
        f"{PHOTOS}/Untitled9.png",
        [
            {"text": "ĐÁP ÁN:", "size": 60, "color": "#FF3366", "bold": True},
            {"text": "SNACK BẠCH TUỘC!", "size": 76, "color": "#3D2200", "bold": True},
        ],
        y_base=H - 420, brightness=1.22, zoom=1.0,
    )
    s4.save(f"{OUT_SLIDES}/doan-chu-s4-reveal.png")
    c4 = ImageClip(f"{OUT_SLIDES}/doan-chu-s4-reveal.png", duration=durs[3]).with_effects([FadeIn(CROSSFADE), FadeOut(CROSSFADE)])
    clips.append(c4)

    # --- 5. CTA: share bait ---
    print("[5] CTA")
    s5 = make_slide(
        f"{PHOTOS}/Untitled.png",
        [
            {"text": "COMMENT ĐOÁN ĐÚNG CHƯA?", "size": 52, "color": "#FF3366", "bold": True},
            {"text": "FOLLOW ĐOÁN MÓN MỚI MỖI NGÀY  ♡", "size": 46, "color": "#3D2200", "bold": True},
        ],
        y_base=H - 380, brightness=1.22, zoom=1.0,
    )
    s5.save(f"{OUT_SLIDES}/doan-chu-s5-cta.png")
    c5 = ImageClip(f"{OUT_SLIDES}/doan-chu-s5-cta.png", duration=durs[4]).with_effects([FadeIn(CROSSFADE)])
    clips.append(c5)

    # Step 3: Concatenate + audio
    print("\n=== RENDER ===")
    video = concatenate_videoclips(clips, method="chain")
    video = video.with_audio(audio).with_duration(total)

    out_path = f"{OUT_FINAL}/260421-{SLUG}-doan-chu-pilot.mp4"
    video.write_videofile(
        out_path, fps=30, codec="libx264", audio_codec="aac",
        preset="medium", threads=4,
    )
    print(f"\n  DONE: {out_path}")


if __name__ == "__main__":
    asyncio.run(main())
