# Generate TikTok video: Hạt Hỗn Hợp Ganyuan — Healthy snack vibe rich kid Hàn
# Concept: K-girl morning routine, guilt-free indulgence
# Target: nữ 20-30, aesthetic pastel xanh-vàng
# Output: assets/products/hat-hon-hop-ganyuan/output/v-new/final/260420-hat-hon-hop-vnew-aesthetic.mp4

import asyncio
import edge_tts
import os
from PIL import Image, ImageDraw, ImageFont
from moviepy import (
    ImageClip, VideoFileClip, AudioFileClip,
    concatenate_videoclips, CompositeVideoClip
)
from moviepy.video.fx import FadeIn, FadeOut
from moviepy.audio.fx import MultiplyVolume
from moviepy import CompositeAudioClip

# === CONFIG ===
PHOTOS = "assets/products/hat-hon-hop-ganyuan/photos"
VIDEOS = "assets/products/hat-hon-hop-ganyuan/photos"  # video stored in photos folder

OUTPUT_SLIDES = "assets/products/hat-hon-hop-ganyuan/output/v-new/slides"
OUTPUT_AUDIO  = "assets/products/hat-hon-hop-ganyuan/output/v-new/audio"
OUTPUT_FINAL  = "assets/products/hat-hon-hop-ganyuan/output/v-new/final"
OUTPUT_FILE   = os.path.join(OUTPUT_FINAL, "260420-hat-hon-hop-vnew-aesthetic.mp4")

FONT_BOLD    = "C:/Windows/Fonts/segoeuib.ttf"
FONT_REGULAR = "C:/Windows/Fonts/segoeui.ttf"

W, H = 1080, 1920
FPS  = 30
VOICE    = "vi-VN-HoaiMyNeural"
CROSSFADE = 0.4

# Brand palette — pastel xanh-vàng Ganyuan
BG_MAIN   = "#D6EAD0"   # xanh bạc hà pastel
BG_ACCENT = "#FFF8DC"   # kem vàng nhạt
TEXT_HEAD  = "#2D6A4F"  # xanh lá đậm
TEXT_SUB   = "#F4A261"  # cam ấm
TEXT_WHITE = "#FFFFFF"
TEXT_GOLD  = "#D4AC0D"

# Voice script — ngày 3, CTA follow
VOICE_SCRIPT = (
    "Ngày của một đứa Gen Z healthy: "
    "laptop, bình nước, một chén hạt Ganyuan. "
    "Hạt hỗn hợp đậu, hạt sen, nho khô, đậu phộng — "
    "ngọt nhẹ, giòn tan, ăn vặt mà không tội lỗi. "
    "Đây là sự xa xỉ chill nhất tuổi hai mươi! "
    "Gửi cho đứa bạn đang ép cân — cứu nó với! "
    "Hành trình xây kênh ngày thứ 3, "
    "hãy tim, comment, follow để đồng hành cùng mình!"
)


def create_image_slide(image_path, text_lines, bg_color=BG_MAIN, style="center"):
    """Create 1080x1920 slide from product photo + text overlay."""
    canvas = Image.new("RGB", (W, H), bg_color)
    img = Image.open(image_path).convert("RGB")

    if style == "center":
        ratio = W / img.width
        new_h = int(img.height * ratio)
        img = img.resize((W, new_h), Image.LANCZOS)
        y_offset = (H - new_h) // 2
        canvas.paste(img, (0, y_offset))
    elif style == "top":
        target_h = int(H * 0.62)
        ratio = max(W / img.width, target_h / img.height)
        new_w, new_h = int(img.width * ratio), int(img.height * ratio)
        img = img.resize((new_w, new_h), Image.LANCZOS)
        x_off = (new_w - W) // 2
        y_off = (new_h - target_h) // 2
        img = img.crop((x_off, y_off, x_off + W, y_off + target_h))
        canvas.paste(img, (0, 0))
    elif style == "zoom":
        # Ken Burns — fill entire canvas at 120%
        ratio = max(W / img.width, H / img.height) * 1.2
        new_w, new_h = int(img.width * ratio), int(img.height * ratio)
        img = img.resize((new_w, new_h), Image.LANCZOS)
        x_off = (new_w - W) // 2
        y_off = (new_h - H) // 2
        img = img.crop((x_off, y_off, x_off + W, y_off + H))
        canvas.paste(img, (0, 0))
    elif style == "fill":
        # Fill entire frame
        ratio = max(W / img.width, H / img.height)
        new_w, new_h = int(img.width * ratio), int(img.height * ratio)
        img = img.resize((new_w, new_h), Image.LANCZOS)
        x_off = (new_w - W) // 2
        y_off = (new_h - H) // 2
        img = img.crop((x_off, y_off, x_off + W, y_off + H))
        canvas.paste(img, (0, 0))

    # Draw text overlay with drop shadow
    draw = ImageDraw.Draw(canvas)
    for t in text_lines:
        font_path = FONT_BOLD if t.get("bold") else FONT_REGULAR
        font = ImageFont.truetype(font_path, t["size"])
        bbox = draw.textbbox((0, 0), t["text"], font=font)
        tw = bbox[2] - bbox[0]
        x = (W - tw) // 2
        # Drop shadow
        shadow_color = t.get("shadow", "black")
        draw.text((x + 3, t["y"] + 3), t["text"], fill=shadow_color, font=font)
        draw.text((x, t["y"]), t["text"], fill=t["color"], font=font)

    return canvas


def prepare_video_clip(video_path, duration, trim_start=0):
    """Load, trim watermark, resize to 9:16 TikTok format."""
    clip = VideoFileClip(video_path)
    # Trim watermark from bottom: crop 90% height (remove bottom 10%)
    crop_h = int(clip.size[1] * 0.90)
    clip = clip.cropped(x1=0, y1=0, x2=clip.size[0], y2=crop_h)

    # Trim to desired duration from trim_start
    end = min(trim_start + duration, clip.duration)
    clip = clip.subclipped(trim_start, end)

    # Resize to fill 1080x1920
    clip_w, clip_h = clip.size
    target_ratio = W / H
    clip_ratio = clip_w / clip_h

    if clip_ratio > target_ratio:
        new_h = H
        new_w = int(clip_w * (new_h / clip_h))
    else:
        new_w = W
        new_h = int(clip_h * (new_w / clip_w))

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

    # === Step 1: Generate voiceover ===
    print("=== GENERATING VOICE ===")
    audio_path = os.path.join(OUTPUT_AUDIO, "voiceover-vnew.mp3")
    await generate_voice(VOICE_SCRIPT, audio_path)

    audio = AudioFileClip(audio_path)
    total_dur = audio.duration
    print(f"  Audio duration: {total_dur:.2f}s")

    # === Step 2: Build 7 segments ===
    print("\n=== BUILDING CLIPS ===")
    seg_dur = total_dur / 7

    clips = []

    # --- Segment 1: Hook — chén hạt flat-lay + Ken Burns zoom ---
    print("  [1] Hook: chén hạt flat-lay (zoom/Ken Burns)")
    slide1 = create_image_slide(
        os.path.join(PHOTOS, "cn-11134207-7ras8-mbz0tw1w8erh24.webp"),
        [
            {"text": "AESTHETIC SNACK", "size": 78, "y": 120, "color": TEXT_HEAD, "bold": True},
            {"text": "CỦA GEN Z", "size": 78, "y": 210, "color": TEXT_GOLD, "bold": True, "shadow": "#6B4500"},
        ],
        bg_color=BG_MAIN, style="zoom"
    )
    path1 = os.path.join(OUTPUT_SLIDES, "vnew-slide-01.png")
    slide1.save(path1, quality=95)
    clip1 = ImageClip(path1, duration=seg_dur).with_effects([FadeIn(0.3)])
    clips.append(clip1)

    # --- Segment 2: Bé gái + ấm trà — lifestyle ---
    print("  [2] Lifestyle: bé gái + ấm trà")
    slide2 = create_image_slide(
        os.path.join(PHOTOS, "vn-11134207-7r98o-lx8dmauzx87t88.webp"),
        [
            {"text": "Sáng healthy", "size": 68, "y": 70, "color": TEXT_WHITE, "bold": True},
            {"text": "nhẹ nhàng ✨", "size": 58, "y": 155, "color": TEXT_GOLD, "bold": False},
        ],
        bg_color=BG_ACCENT, style="center"
    )
    path2 = os.path.join(OUTPUT_SLIDES, "vnew-slide-02.png")
    slide2.save(path2, quality=95)
    clip2 = ImageClip(path2, duration=seg_dur).with_effects([FadeIn(CROSSFADE), FadeOut(CROSSFADE)])
    clips.append(clip2)

    # --- Segment 3: Video ASMR hạt rơi ---
    print("  [3] Video ASMR: hạt rơi vào bát")
    vid_path = os.path.join(VIDEOS, "Video_Hạt_Hỗn_Hợp_Rơi_Vào_Bát.mp4")
    clip3 = prepare_video_clip(vid_path, seg_dur, trim_start=0)
    clip3 = clip3.with_effects([FadeIn(CROSSFADE), FadeOut(CROSSFADE)])
    clips.append(clip3)

    # --- Segment 4: Túi kraft đổ hạt ra gỗ ---
    print("  [4] Túi kraft đổ hạt ra gỗ — hạt tự nhiên")
    slide4 = create_image_slide(
        os.path.join(PHOTOS, "Gemini_Generated_Image_tc1u9utc1u9utc1u.png"),
        [
            {"text": "Đậu · Hạt sen", "size": 58, "y": 60, "color": TEXT_WHITE, "bold": True},
            {"text": "Nho khô · Đậu phộng", "size": 52, "y": H - 200, "color": TEXT_GOLD, "bold": False},
        ],
        bg_color="#3D2B1F", style="fill"
    )
    path4 = os.path.join(OUTPUT_SLIDES, "vnew-slide-04.png")
    slide4.save(path4, quality=95)
    clip4 = ImageClip(path4, duration=seg_dur).with_effects([FadeIn(CROSSFADE), FadeOut(CROSSFADE)])
    clips.append(clip4)

    # --- Segment 5: 4 vị Ganyuan ---
    print("  [5] 4 vị Ganyuan slide")
    slide5 = create_image_slide(
        os.path.join(PHOTOS, "cn-11134207-820l4-mn3qeeh058uafd.webp"),
        [
            {"text": "4 vị để chọn:", "size": 58, "y": 60, "color": TEXT_HEAD, "bold": True},
            {"text": "Hạt thuần · Tôm cay", "size": 46, "y": H - 280, "color": TEXT_WHITE, "bold": False},
            {"text": "Daily · Quả nhân", "size": 46, "y": H - 220, "color": TEXT_GOLD, "bold": False},
        ],
        bg_color=BG_MAIN, style="center"
    )
    path5 = os.path.join(OUTPUT_SLIDES, "vnew-slide-05.png")
    slide5.save(path5, quality=95)
    clip5 = ImageClip(path5, duration=seg_dur).with_effects([FadeIn(CROSSFADE), FadeOut(CROSSFADE)])
    clips.append(clip5)

    # --- Segment 6: Share bait — chén cam vị tôm ---
    print("  [6] Share bait: chén cam vị tôm")
    slide6 = create_image_slide(
        os.path.join(PHOTOS, "cn-11134207-7ras8-md1i85fwcktl7a.webp"),
        [
            {"text": "Gửi đứa bạn ép cân —", "size": 52, "y": 60, "color": TEXT_WHITE, "bold": True},
            {"text": "cứu nó với! 💚", "size": 58, "y": 130, "color": TEXT_GOLD, "bold": True},
        ],
        bg_color=BG_MAIN, style="center"
    )
    path6 = os.path.join(OUTPUT_SLIDES, "vnew-slide-06.png")
    slide6.save(path6, quality=95)
    clip6 = ImageClip(path6, duration=seg_dur).with_effects([FadeIn(CROSSFADE), FadeOut(CROSSFADE)])
    clips.append(clip6)

    # --- Segment 7: CTA Follow ---
    print("  [7] CTA: Follow Tạp Hóa Pel Pel")
    slide7 = create_image_slide(
        os.path.join(PHOTOS, "cn-11134207-7ras8-mbz0tw1w8erh24.webp"),
        [
            {"text": "FOLLOW", "size": 96, "y": 90, "color": TEXT_GOLD, "bold": True, "shadow": "#6B4500"},
            {"text": "Tạp Hóa Pel Pel", "size": 58, "y": 200, "color": TEXT_WHITE, "bold": True},
            {"text": "Tim · Comment · Đồng hành!", "size": 42, "y": H - 160, "color": TEXT_HEAD, "bold": False},
        ],
        bg_color=BG_MAIN, style="zoom"
    )
    path7 = os.path.join(OUTPUT_SLIDES, "vnew-slide-07.png")
    slide7.save(path7, quality=95)
    clip7 = ImageClip(path7, duration=seg_dur).with_effects([FadeIn(CROSSFADE)])
    clips.append(clip7)

    # === Step 3: Concatenate ===
    print("\n=== ASSEMBLING VIDEO ===")
    video = concatenate_videoclips(clips, method="compose")

    # Mix audio: original video audio at 25% + voiceover at 100%
    original_audio = video.audio
    if original_audio:
        original_audio = original_audio.with_effects([MultiplyVolume(0.25)])
        mixed_audio = CompositeAudioClip([original_audio, audio])
        video = video.with_audio(mixed_audio)
    else:
        video = video.with_audio(audio)

    print(f"  Rendering {total_dur:.2f}s video → {OUTPUT_FILE}")
    video.write_videofile(
        OUTPUT_FILE, fps=FPS, codec="libx264",
        audio_codec="aac", preset="medium", threads=4,
    )

    print(f"\nXong! Output: {OUTPUT_FILE}")
    print(f"Duration: {total_dur:.2f}s | Resolution: {W}x{H} | FPS: {FPS}")

    # Cleanup
    audio.close()
    video.close()
    for c in clips:
        c.close()


if __name__ == "__main__":
    asyncio.run(main())
