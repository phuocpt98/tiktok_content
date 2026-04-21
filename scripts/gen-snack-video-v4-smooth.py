# Generate TikTok video V4: Snack Bạch Tuộc — Smooth transitions + video clips + Ken Burns
# Kết hợp video clips Kling AI + ảnh sản phẩm + voiceover + chuyển cảnh mượt
# Output theo cấu trúc chuẩn: assets/products/snack-bach-tuoc/output/{slides,audio,final}

import asyncio
import edge_tts
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
from moviepy import (
    ImageClip, VideoFileClip, AudioFileClip,
    concatenate_videoclips, CompositeVideoClip, TextClip
)
from moviepy.video.fx import CrossFadeIn, CrossFadeOut, FadeIn, FadeOut

# === CONFIG ===
PHOTOS = "assets/products/snack-bach-tuoc/photos"
VIDEOS = "assets/products/snack-bach-tuoc/videos"
OUTPUT_SLIDES = "assets/products/snack-bach-tuoc/output/slides"
OUTPUT_AUDIO = "assets/products/snack-bach-tuoc/output/audio"
OUTPUT_FINAL = "assets/products/snack-bach-tuoc/output/final"

FONT_BOLD = "C:/Windows/Fonts/segoeuib.ttf"
FONT_REGULAR = "C:/Windows/Fonts/segoeui.ttf"

W, H = 1080, 1920
VOICE = "vi-VN-HoaiMyNeural"
CROSSFADE = 0.4  # crossfade duration between clips

# Voice script — liền mạch, nhanh, punch
VOICE_SCRIPT = (
    "Ê! Nhìn này! "
    "Snack bạch tuộc nướng, giòn rụm cay nồng, "
    "mở bao ra là thơm lừng luôn á! "
    "Kết cấu giòn tan, ăn miếng đầu là dừng không nổi! "
    "Có hai vị nè, đỏ cay xé lưỡi, cam ít cay hơn. "
    "Bạn team nào? Comment đi! "
    "Follow xem thêm đồ ăn vặt ngon mỗi ngày nha!"
)


def create_text_overlay(text_lines, bg_color="#1a1a1a"):
    """Create a text-only slide for overlay or standalone use"""
    canvas = Image.new("RGB", (W, H), bg_color)
    draw = ImageDraw.Draw(canvas)
    for t in text_lines:
        font_path = FONT_BOLD if t.get("bold") else FONT_REGULAR
        font = ImageFont.truetype(font_path, t["size"])
        bbox = draw.textbbox((0, 0), t["text"], font=font)
        tw = bbox[2] - bbox[0]
        x = (W - tw) // 2
        draw.text((x + 3, t["y"] + 3), t["text"], fill="black", font=font)
        draw.text((x, t["y"]), t["text"], fill=t["color"], font=font)
    return canvas


def create_image_slide(image_path, text_lines, bg_color="#1a1a1a", style="center"):
    """Create slide from product photo with text overlay"""
    canvas = Image.new("RGB", (W, H), bg_color)
    img = Image.open(image_path).convert("RGB")

    if style == "center":
        ratio = W / img.width
        new_h = int(img.height * ratio)
        img = img.resize((W, new_h), Image.LANCZOS)
        y_offset = (H - new_h) // 2
        canvas.paste(img, (0, y_offset))
    elif style == "top":
        target_h = int(H * 0.6)
        ratio = max(W / img.width, target_h / img.height)
        new_w = int(img.width * ratio)
        new_h = int(img.height * ratio)
        img = img.resize((new_w, new_h), Image.LANCZOS)
        x_off = (new_w - W) // 2
        y_off = (new_h - target_h) // 2
        img = img.crop((x_off, y_off, x_off + W, y_off + target_h))
        canvas.paste(img, (0, 0))
    elif style == "zoom":
        # Ken Burns — zoom in 120%
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
        draw.text((x + 3, t["y"] + 3), t["text"], fill="black", font=font)
        draw.text((x, t["y"]), t["text"], fill=t["color"], font=font)

    return canvas


def prepare_video_clip(video_path, duration, target_size=(W, H)):
    """Load and resize video clip to 9:16 TikTok format"""
    clip = VideoFileClip(video_path)
    # Trim to desired duration
    if clip.duration > duration:
        clip = clip.subclipped(0, duration)

    # Resize to fill 1080x1920
    clip_w, clip_h = clip.size
    target_ratio = target_size[0] / target_size[1]
    clip_ratio = clip_w / clip_h

    if clip_ratio > target_ratio:
        # Video wider — scale by height, crop width
        new_h = target_size[1]
        new_w = int(clip_w * (new_h / clip_h))
    else:
        # Video taller — scale by width, crop height
        new_w = target_size[0]
        new_h = int(clip_h * (new_w / clip_w))

    clip = clip.resized((new_w, new_h))
    # Center crop
    x_off = (new_w - target_size[0]) // 2
    y_off = (new_h - target_size[1]) // 2
    clip = clip.cropped(x1=x_off, y1=y_off, x2=x_off + target_size[0], y2=y_off + target_size[1])

    return clip


async def generate_voice(text, output_path):
    communicate = edge_tts.Communicate(text, VOICE, rate="+50%")
    await communicate.save(output_path)
    print(f"  Voice: {os.path.basename(output_path)}")


async def main():
    os.makedirs(OUTPUT_SLIDES, exist_ok=True)
    os.makedirs(OUTPUT_AUDIO, exist_ok=True)
    os.makedirs(OUTPUT_FINAL, exist_ok=True)

    # Step 1: Generate voiceover
    print("=== GENERATING VOICE ===")
    audio_path = os.path.join(OUTPUT_AUDIO, "voiceover-v4.mp3")
    await generate_voice(VOICE_SCRIPT, audio_path)

    audio = AudioFileClip(audio_path)
    total_dur = audio.duration
    print(f"  Audio: {total_dur:.1f}s")

    # Step 2: Build clip sequence — mix video clips + image slides
    print("\n=== BUILDING CLIPS ===")

    # Calculate duration per segment (7 segments)
    seg_dur = total_dur / 7

    clips = []

    # Segment 1: Kling close-up video (HOOK)
    print("  [1] Kling close-up video — hook")
    kling_closeup = os.path.join(VIDEOS, "kling_20260417_作品___Close_up_4188_0.mp4")
    clip1 = prepare_video_clip(kling_closeup, seg_dur)
    clip1 = clip1.with_effects([FadeIn(0.3)])
    clips.append(clip1)

    # Segment 2: Image slide — packaging (Untitled_4)
    print("  [2] Packaging slide")
    slide2 = create_image_slide(
        os.path.join(PHOTOS, "Untitled_4.png"),
        [
            {"text": "SNACK BẠCH TUỘC NƯỚNG", "size": 65, "y": 55, "color": "#FF6B35", "bold": True},
            {"text": "Giòn rụm - Cay nồng!", "size": 48, "y": 150, "color": "#FFD700"},
        ],
        bg_color="#1a1a1a", style="center"
    )
    slide2_path = os.path.join(OUTPUT_SLIDES, "v4-slide-02.png")
    slide2.save(slide2_path, quality=95)
    clip2 = ImageClip(slide2_path, duration=seg_dur)
    clip2 = clip2.with_effects([FadeIn(CROSSFADE), FadeOut(CROSSFADE)])
    clips.append(clip2)

    # Segment 3: Kling falling video
    print("  [3] Kling falling video")
    kling_fall = os.path.join(VIDEOS, "kling_20260417_作品_7__R_i_slo_4405_0.mp4")
    clip3 = prepare_video_clip(kling_fall, seg_dur)
    clip3 = clip3.with_effects([FadeIn(CROSSFADE), FadeOut(CROSSFADE)])
    clips.append(clip3)

    # Segment 4: Image slide — close-up texture (Untitled) zoom style
    print("  [4] Close-up texture slide — zoom")
    slide4 = create_image_slide(
        os.path.join(PHOTOS, "Untitled.png"),
        [
            {"text": "Giòn tan từng miếng!", "size": 62, "y": 70, "color": "white", "bold": True},
            {"text": "Ăn là dừng không nổi", "size": 48, "y": H - 180, "color": "#FFD700"},
        ],
        bg_color="#2d1810", style="zoom"
    )
    slide4_path = os.path.join(OUTPUT_SLIDES, "v4-slide-04.png")
    slide4.save(slide4_path, quality=95)
    clip4 = ImageClip(slide4_path, duration=seg_dur)
    clip4 = clip4.with_effects([FadeIn(CROSSFADE), FadeOut(CROSSFADE)])
    clips.append(clip4)

    # Segment 5: ASMR video clip
    print("  [5] ASMR bóp vỡ video")
    asmr_clip_path = os.path.join(VIDEOS, "ASMR_Bóp_Vỡ_Snack_Bạch_Tuộc.mp4")
    clip5 = prepare_video_clip(asmr_clip_path, seg_dur)
    clip5 = clip5.with_effects([FadeIn(CROSSFADE), FadeOut(CROSSFADE)])
    clips.append(clip5)

    # Segment 6: Image slide — 2 vị (Untitled9)
    print("  [6] 2 vị slide")
    slide6 = create_image_slide(
        os.path.join(PHOTOS, "Untitled9.png"),
        [
            {"text": "Đỏ = Cay | Cam = Ít cay", "size": 52, "y": 70, "color": "#FF6B35", "bold": True},
            {"text": "Bạn team nào?", "size": 55, "y": H - 180, "color": "#FFD700"},
        ],
        bg_color="#1a1a1a", style="center"
    )
    slide6_path = os.path.join(OUTPUT_SLIDES, "v4-slide-06.png")
    slide6.save(slide6_path, quality=95)
    clip6 = ImageClip(slide6_path, duration=seg_dur)
    clip6 = clip6.with_effects([FadeIn(CROSSFADE), FadeOut(CROSSFADE)])
    clips.append(clip6)

    # Segment 7: CTA — hero image (Untitled7)
    print("  [7] CTA slide")
    slide7 = create_image_slide(
        os.path.join(PHOTOS, "Untitled7.png"),
        [
            {"text": "FOLLOW xem thêm", "size": 65, "y": 50, "color": "#FFD700", "bold": True},
            {"text": "đồ ăn vặt ngon mỗi ngày!", "size": 42, "y": 145, "color": "white"},
        ],
        bg_color="#1a1a1a", style="center"
    )
    slide7_path = os.path.join(OUTPUT_SLIDES, "v4-slide-07.png")
    slide7.save(slide7_path, quality=95)
    clip7 = ImageClip(slide7_path, duration=seg_dur)
    clip7 = clip7.with_effects([FadeIn(CROSSFADE)])
    clips.append(clip7)

    # Step 3: Concatenate with crossfade
    print("\n=== ASSEMBLING VIDEO ===")
    video = concatenate_videoclips(clips, method="compose")

    # Mix: giữ tiếng ASMR gốc (nhỏ) + voiceover (to)
    # Giảm volume audio gốc video xuống 30%, voice chính 100%
    from moviepy.audio.fx import MultiplyVolume
    original_audio = video.audio
    if original_audio:
        original_audio = original_audio.with_effects([MultiplyVolume(0.3)])
        # Đảm bảo cùng duration
        from moviepy import CompositeAudioClip
        mixed_audio = CompositeAudioClip([original_audio, audio])
        video = video.with_audio(mixed_audio)
    else:
        video = video.with_audio(audio)

    output_file = os.path.join(OUTPUT_FINAL, "snack-bach-tuoc-v4-smooth-tiktok.mp4")
    print(f"  Rendering {total_dur:.1f}s video...")
    video.write_videofile(
        output_file, fps=30, codec="libx264",
        audio_codec="aac", preset="medium", threads=4,
    )

    print(f"\nXong! Video: {output_file}")
    print(f"Duration: {total_dur:.1f}s | Resolution: {W}x{H}")
    print("Clips: 3 video Kling + 4 ảnh slides + crossfade transitions")

    audio.close()
    video.close()
    for c in clips:
        c.close()


if __name__ == "__main__":
    asyncio.run(main())
