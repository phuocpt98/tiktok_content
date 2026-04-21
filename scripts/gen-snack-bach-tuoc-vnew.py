# Generate TikTok video V-NEW: Snack Bạch Tuộc — "Test xem mày dám thử không?"
# Concept: Drama cute vs ghê reaction + ASMR cắn giòn
# Target: nữ 14-30 | 7 segments | 12-15s | 1080x1920 | HoaiMy +50% | Day 3 CTA

import asyncio
import edge_tts
import os
from PIL import Image, ImageDraw, ImageFont
from moviepy import (
    ImageClip, VideoFileClip, AudioFileClip,
    concatenate_videoclips, CompositeVideoClip
)
from moviepy.audio.fx import MultiplyVolume
from moviepy import CompositeAudioClip
from moviepy.video.fx import FadeIn, FadeOut

# === CONFIG ===
BASE = "D:/project/demo/content"
PHOTOS = f"{BASE}/assets/products/snack-bach-tuoc/photos"
VIDEOS = f"{BASE}/assets/products/snack-bach-tuoc/videos"
OUTPUT_SLIDES = f"{BASE}/output/snack-bach-tuoc/v-new/slides"
OUTPUT_AUDIO = f"{BASE}/output/snack-bach-tuoc/v-new/audio"
OUTPUT_FINAL = f"{BASE}/output/snack-bach-tuoc/v-new/final"

FONT_BOLD = "C:/Windows/Fonts/segoeuib.ttf"
FONT_REGULAR = "C:/Windows/Fonts/segoeui.ttf"

W, H = 1080, 1920
VOICE = "vi-VN-HoaiMyNeural"
CROSSFADE = 0.4

# Voice script — dùng nguyên văn, CTA day 3
VOICE_SCRIPT = (
    "Ê! Đố bạn nha — nhìn em này cute hay nhìn ghê? "
    "Snack bạch tuộc mini, giòn rụm cay nồng, "
    "bóc gói ra là thơm lừng. "
    "Đứa nào sợ thì nhắm mắt ăn, đứa nào liều thì cắn liền! "
    "Tag con bạn sợ bạch tuộc xem nó dám thử không! "
    "Hành trình xây kênh ngày thứ 3, "
    "hãy tim, comment, follow để đồng hành cùng mình!"
)


def create_image_slide(image_path, text_lines, bg_color="#1a1a1a", style="center"):
    """Create 9:16 slide from photo with text overlay. style: center|zoom|fill"""
    canvas = Image.new("RGB", (W, H), bg_color)
    img = Image.open(image_path).convert("RGB")

    if style == "center":
        # Scale to full width, center vertically
        ratio = W / img.width
        new_h = int(img.height * ratio)
        img = img.resize((W, new_h), Image.LANCZOS)
        y_offset = (H - new_h) // 2
        canvas.paste(img, (0, y_offset))

    elif style == "fill":
        # Scale to fill entire frame, center crop
        ratio = max(W / img.width, H / img.height)
        new_w = int(img.width * ratio)
        new_h = int(img.height * ratio)
        img = img.resize((new_w, new_h), Image.LANCZOS)
        x_off = (new_w - W) // 2
        y_off = (new_h - H) // 2
        img = img.crop((x_off, y_off, x_off + W, y_off + H))
        canvas.paste(img, (0, 0))

    elif style == "zoom":
        # Ken Burns — scale 120%, center crop (zoomed in feel)
        ratio = max(W / img.width, H / img.height) * 1.2
        new_w = int(img.width * ratio)
        new_h = int(img.height * ratio)
        img = img.resize((new_w, new_h), Image.LANCZOS)
        x_off = (new_w - W) // 2
        y_off = (new_h - H) // 2
        img = img.crop((x_off, y_off, x_off + W, y_off + H))
        canvas.paste(img, (0, 0))

    draw = ImageDraw.Draw(canvas)
    for t in text_lines:
        font_path = FONT_BOLD if t.get("bold") else FONT_REGULAR
        font = ImageFont.truetype(font_path, t["size"])
        bbox = draw.textbbox((0, 0), t["text"], font=font)
        tw = bbox[2] - bbox[0]
        x = (W - tw) // 2

        # Drop shadow
        draw.text((x + 3, t["y"] + 3), t["text"], fill="black", font=font)
        draw.text((x, t["y"]), t["text"], fill=t["color"], font=font)

    return canvas


def prepare_video_clip(video_path, duration, crop_watermark=False):
    """Load, resize/crop video to 1080x1920. crop_watermark zooms 110% to hide corner watermarks."""
    clip = VideoFileClip(video_path)
    if clip.duration > duration:
        clip = clip.subclipped(0, duration)

    clip_w, clip_h = clip.size
    target_ratio = W / H
    clip_ratio = clip_w / clip_h

    # Determine zoom factor: extra 10% if removing watermark
    zoom = 1.1 if crop_watermark else 1.0

    if clip_ratio > target_ratio:
        new_h = H
        new_w = int(clip_w * (new_h / clip_h))
    else:
        new_w = W
        new_h = int(clip_h * (new_w / clip_w))

    new_w = int(new_w * zoom)
    new_h = int(new_h * zoom)

    clip = clip.resized((new_w, new_h))
    x_off = (new_w - W) // 2
    y_off = (new_h - H) // 2
    clip = clip.cropped(x1=x_off, y1=y_off, x2=x_off + W, y2=y_off + H)

    return clip


async def generate_voice(text, output_path):
    communicate = edge_tts.Communicate(text, VOICE, rate="+50%")
    await communicate.save(output_path)
    print(f"  Voice saved: {os.path.basename(output_path)}")


async def main():
    os.makedirs(OUTPUT_SLIDES, exist_ok=True)
    os.makedirs(OUTPUT_AUDIO, exist_ok=True)
    os.makedirs(OUTPUT_FINAL, exist_ok=True)

    # Step 1: Voiceover
    print("=== GENERATING VOICE ===")
    audio_path = os.path.join(OUTPUT_AUDIO, "voiceover-vnew.mp3")
    await generate_voice(VOICE_SCRIPT, audio_path)

    audio = AudioFileClip(audio_path)
    total_dur = audio.duration
    print(f"  Audio duration: {total_dur:.2f}s")

    # Step 2: Build 7 segments to fill total_dur
    print("\n=== BUILDING CLIPS ===")
    seg_dur = total_dur / 7

    clips = []

    # --- Seg 1: HOOK — ASMR video close-up bạch tuộc ---
    print("  [1] HOOK: ASMR video — close-up bạch tuộc")
    asmr_path = f"{VIDEOS}/ASMR_Bóp_Vỡ_Snack_Bạch_Tuộc.mp4"
    clip1 = prepare_video_clip(asmr_path, seg_dur, crop_watermark=False)
    clip1 = clip1.with_effects([FadeIn(0.3)])

    # Add text overlay on video via composite
    hook_txt_slide = create_image_slide(
        f"{PHOTOS}/Untitled10.png",
        [
            {"text": "ĐỐ BẠN —", "size": 80, "y": 80, "color": "#FFD700", "bold": True},
            {"text": "CUTE HAY GHÊ?", "size": 72, "y": 185, "color": "#FF4444", "bold": True},
        ],
        bg_color="#00000000", style="fill"
    )
    # We'll overlay text as a separate ImageClip composed on top of the video
    hook_txt_path = f"{OUTPUT_SLIDES}/vnew-overlay-01.png"
    hook_txt_slide.save(hook_txt_path)
    txt_clip1 = ImageClip(hook_txt_path, duration=seg_dur).with_opacity(0)

    # Create text-only transparent overlay
    text_canvas = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(text_canvas)
    lines = [
        {"text": "ĐỐ BẠN —", "size": 80, "y": 80, "color": "#FFD700", "bold": True},
        {"text": "CUTE HAY GHÊ?", "size": 72, "y": 185, "color": "#FF4444", "bold": True},
    ]
    for t in lines:
        fp = FONT_BOLD if t.get("bold") else FONT_REGULAR
        font = ImageFont.truetype(fp, t["size"])
        bbox = draw.textbbox((0, 0), t["text"], font=font)
        tw = bbox[2] - bbox[0]
        x = (W - tw) // 2
        # Shadow
        draw.text((x + 3, t["y"] + 3), t["text"], fill=(0, 0, 0, 200), font=font)
        # Main text
        r, g, b = tuple(int(t["color"].lstrip("#")[i:i+2], 16) for i in (0, 2, 4))
        draw.text((x, t["y"]), t["text"], fill=(r, g, b, 255), font=font)

    overlay_path = f"{OUTPUT_SLIDES}/vnew-text-overlay-01.png"
    text_canvas.save(overlay_path, "PNG")
    overlay_clip1 = ImageClip(overlay_path, duration=seg_dur)
    seg1 = CompositeVideoClip([clip1, overlay_clip1])
    clips.append(seg1)

    # --- Seg 2: Slide Untitled10 — food styled cam ---
    print("  [2] Slide — food styled (Untitled10)")
    slide2 = create_image_slide(
        f"{PHOTOS}/Untitled10.png",
        [
            {"text": "Snack bạch tuộc mini", "size": 62, "y": 65, "color": "#FF6B35", "bold": True},
            {"text": "Giòn rụm • Cay nồng", "size": 48, "y": 165, "color": "#FFD700"},
        ],
        bg_color="#1a1a1a", style="fill"
    )
    s2_path = f"{OUTPUT_SLIDES}/vnew-slide-02.png"
    slide2.save(s2_path)
    clip2 = ImageClip(s2_path, duration=seg_dur)
    clip2 = clip2.with_effects([FadeIn(CROSSFADE), FadeOut(CROSSFADE)])
    clips.append(clip2)

    # --- Seg 3: Slide Untitled.png — close-up tay cầm, zoom Ken Burns ---
    print("  [3] Slide — close-up tay cầm zoom (Untitled)")
    slide3 = create_image_slide(
        f"{PHOTOS}/Untitled.png",
        [
            {"text": "Giòn rụm", "size": 75, "y": 70, "color": "white", "bold": True},
            {"text": "Cay nồng", "size": 75, "y": 170, "color": "#FF4444", "bold": True},
        ],
        bg_color="#2d1810", style="zoom"
    )
    s3_path = f"{OUTPUT_SLIDES}/vnew-slide-03.png"
    slide3.save(s3_path)
    clip3 = ImageClip(s3_path, duration=seg_dur)
    clip3 = clip3.with_effects([FadeIn(CROSSFADE), FadeOut(CROSSFADE)])
    clips.append(clip3)

    # --- Seg 4: Video kling_close_up (snack trong chén) — crop watermark ---
    print("  [4] Video — kling close-up snack chén (crop watermark)")
    kling_cup = f"{VIDEOS}/kling_20260417_作品___Close_up_4188_0.mp4"
    clip4 = prepare_video_clip(kling_cup, seg_dur, crop_watermark=True)
    clip4 = clip4.with_effects([FadeIn(CROSSFADE), FadeOut(CROSSFADE)])
    clips.append(clip4)

    # --- Seg 5: Slide Untitled9 — 2 vị studio ---
    print("  [5] Slide — 2 vị (Untitled9)")
    slide5 = create_image_slide(
        f"{PHOTOS}/Untitled9.png",
        [
            {"text": "2 vị:", "size": 60, "y": 55, "color": "#FFD700", "bold": True},
            {"text": "Cay xé  /  Ít cay", "size": 55, "y": 140, "color": "#FF6B35", "bold": True},
        ],
        bg_color="#111111", style="fill"
    )
    s5_path = f"{OUTPUT_SLIDES}/vnew-slide-05.png"
    slide5.save(s5_path)
    clip5 = ImageClip(s5_path, duration=seg_dur)
    clip5 = clip5.with_effects([FadeIn(CROSSFADE), FadeOut(CROSSFADE)])
    clips.append(clip5)

    # --- Seg 6: Slide Untitled7 — real vs snack, share bait ---
    print("  [6] Slide — real vs snack + share bait (Untitled7)")
    slide6 = create_image_slide(
        f"{PHOTOS}/Untitled7.png",
        [
            {"text": "Tag bạn sợ bạch tuộc", "size": 52, "y": 55, "color": "#FFD700", "bold": True},
            {"text": "xem nó dám thử không!", "size": 50, "y": 140, "color": "white", "bold": True},
        ],
        bg_color="#0d0d0d", style="fill"
    )
    s6_path = f"{OUTPUT_SLIDES}/vnew-slide-06.png"
    slide6.save(s6_path)
    clip6 = ImageClip(s6_path, duration=seg_dur)
    clip6 = clip6.with_effects([FadeIn(CROSSFADE), FadeOut(CROSSFADE)])
    clips.append(clip6)

    # --- Seg 7: CTA slide — background Untitled10 ---
    print("  [7] CTA slide — FOLLOW Tạp Hóa Pel Pel")
    slide7 = create_image_slide(
        f"{PHOTOS}/Untitled10.png",
        [
            {"text": "Tim • Comment • Follow", "size": 50, "y": H - 320, "color": "#FFD700", "bold": True},
            {"text": "FOLLOW Tạp Hóa Pel Pel", "size": 55, "y": H - 230, "color": "white", "bold": True},
            {"text": "Hành trình ngày thứ 3 ", "size": 40, "y": H - 150, "color": "#FF6B35"},
        ],
        bg_color="#1a1a1a", style="fill"
    )
    s7_path = f"{OUTPUT_SLIDES}/vnew-slide-07.png"
    slide7.save(s7_path)
    clip7 = ImageClip(s7_path, duration=seg_dur)
    clip7 = clip7.with_effects([FadeIn(CROSSFADE)])
    clips.append(clip7)

    # Step 3: Concatenate
    print("\n=== ASSEMBLING VIDEO ===")
    video = concatenate_videoclips(clips, method="compose")

    # Mix audio: voice 100% + original video audio 30%
    original_audio = video.audio
    if original_audio:
        original_audio = original_audio.with_effects([MultiplyVolume(0.3)])
        mixed_audio = CompositeAudioClip([original_audio, audio])
        video = video.with_audio(mixed_audio)
    else:
        video = video.with_audio(audio)

    # Step 4: Render
    output_file = f"{OUTPUT_FINAL}/260420-snack-bach-tuoc-vnew-test-dare.mp4"
    print(f"  Rendering {total_dur:.2f}s → {output_file}")
    video.write_videofile(
        output_file,
        fps=30,
        codec="libx264",
        audio_codec="aac",
        preset="medium",
        threads=4,
    )

    print(f"\nDone! {output_file}")
    print(f"Duration: {total_dur:.2f}s | {W}x{H} | 30fps")

    audio.close()
    video.close()
    for c in clips:
        c.close()


if __name__ == "__main__":
    asyncio.run(main())
