# Generate TikTok video V-NEW: Mực Rim Me — "Cứu tinh OT 9h tối"
# 100% ảnh + style zoom (static Ken-Burns look) | 7 segments | 12-15s | Day 3 CTA

import asyncio
import edge_tts
import os
from PIL import Image, ImageDraw, ImageFont
from moviepy import (
    ImageClip, AudioFileClip,
    concatenate_videoclips
)
from moviepy.video.fx import FadeIn, FadeOut

# === CONFIG ===
BASE = "D:/project/demo/content"
PHOTOS = f"{BASE}/assets/products/muc-rim-me/photos"
OUTPUT_SLIDES = f"{BASE}/output/muc-rim-me/v-new/slides"
OUTPUT_AUDIO = f"{BASE}/output/muc-rim-me/v-new/audio"
OUTPUT_FINAL = f"{BASE}/output/muc-rim-me/v-new/final"

FONT_BOLD = "C:/Windows/Fonts/segoeuib.ttf"
FONT_REGULAR = "C:/Windows/Fonts/segoeui.ttf"

W, H = 1080, 1920
VOICE = "vi-VN-HoaiMyNeural"
CROSSFADE = 0.4

VOICE_SCRIPT = (
    "OT đến chín giờ tối, đói meo người, "
    "mở hộp này ra là sống lại! "
    "Mực rim me đặc sản Đà Nẵng, "
    "sợi mực dai ngọt, sốt me chua cay nồng nàn, "
    "mè rang thơm phức. "
    "Một hộp ăn cả tuần OT không chán! "
    "Tag đứa đồng nghiệp đang OT cùng — chia nhau mai khao! "
    "Hành trình xây kênh ngày thứ 3, "
    "hãy tim, comment, follow để đồng hành cùng mình!"
)


def create_image_slide(image_path, text_lines, bg_color="#1a1a1a", style="fill", zoom_factor=1.2):
    canvas = Image.new("RGB", (W, H), bg_color)
    img = Image.open(image_path).convert("RGB")

    if style == "zoom":
        ratio = max(W / img.width, H / img.height) * zoom_factor
    else:
        ratio = max(W / img.width, H / img.height)

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


async def generate_voice(text, output_path):
    communicate = edge_tts.Communicate(text, VOICE, rate="+50%")
    await communicate.save(output_path)
    print(f"  Voice saved: {os.path.basename(output_path)}")


async def main():
    os.makedirs(OUTPUT_SLIDES, exist_ok=True)
    os.makedirs(OUTPUT_AUDIO, exist_ok=True)
    os.makedirs(OUTPUT_FINAL, exist_ok=True)

    print("=== GENERATING VOICE ===")
    audio_path = os.path.join(OUTPUT_AUDIO, "voiceover-vnew.mp3")
    await generate_voice(VOICE_SCRIPT, audio_path)

    audio = AudioFileClip(audio_path)
    total_dur = audio.duration
    print(f"  Audio duration: {total_dur:.2f}s")

    print("\n=== BUILDING CLIPS ===")
    seg_dur = total_dur / 7
    clips = []

    segments = [
        ("Gemini_Generated_Image_3bbdpy3bbdpy3bbd.png",
         [{"text": "OT 9H TỐI?", "size": 80, "y": 70, "color": "#FFD700", "bold": True},
          {"text": "CỨU TINH ĐÂY!", "size": 70, "y": 175, "color": "#FF6B35", "bold": True}],
         "#0d0d0d", "zoom", 1.15),
        ("98637380-muc-rim-me-muc-sot-me-muc-ngao-me-muc-uop-me.jpg",
         [{"text": "Mực rim me", "size": 72, "y": 65, "color": "white", "bold": True},
          {"text": "đặc sản Đà Nẵng", "size": 56, "y": 165, "color": "#FFD700", "bold": True}],
         "#1a0d0d", "fill", 1.0),
        ("muc-rim-me (10).jpg",
         [{"text": "Sợi mực", "size": 80, "y": 70, "color": "#FFD700", "bold": True},
          {"text": "dai ngọt", "size": 80, "y": 180, "color": "white", "bold": True}],
         "#1a0d0d", "zoom", 1.25),
        ("kho-muc-rim-me-thumbnail.jpeg",
         [{"text": "Sốt me chua cay", "size": 62, "y": 60, "color": "#FF6B35", "bold": True},
          {"text": "nồng nàn", "size": 58, "y": 160, "color": "#FFD700", "bold": True}],
         "#1a0d0d", "fill", 1.0),
        ("vn-11134207-7ra0g-m7waqc6sobcec4@resize_w450_nl.webp",
         [{"text": "Đậm vị", "size": 75, "y": 70, "color": "#FFD700", "bold": True},
          {"text": "Ăn cả tuần OT không chán", "size": 44, "y": 175, "color": "white", "bold": True}],
         "#1a0d0d", "zoom", 1.15),
        ("Muc-rim-me-2.jpg",
         [{"text": "Tag đồng nghiệp OT", "size": 56, "y": 60, "color": "#FFD700", "bold": True},
          {"text": "mai khao!", "size": 60, "y": 145, "color": "#FF6B35", "bold": True}],
         "#0d0d0d", "fill", 1.0),
        ("Gemini_Generated_Image_3bbdpy3bbdpy3bbd.png",
         [{"text": "Tim • Comment • Follow", "size": 50, "y": H - 320, "color": "#FFD700", "bold": True},
          {"text": "FOLLOW Tạp Hóa Pel Pel", "size": 55, "y": H - 230, "color": "white", "bold": True},
          {"text": "Hành trình ngày thứ 3 ", "size": 40, "y": H - 150, "color": "#FF6B35"}],
         "#0d0d0d", "fill", 1.0),
    ]

    for i, (img_name, lines, bg, style, zoom) in enumerate(segments, 1):
        print(f"  [{i}] style={style}")
        slide = create_image_slide(f"{PHOTOS}/{img_name}", lines, bg_color=bg, style=style, zoom_factor=zoom)
        slide_path = f"{OUTPUT_SLIDES}/vnew-slide-{i:02d}.png"
        slide.save(slide_path)
        clip = ImageClip(slide_path, duration=seg_dur)
        if i == 1:
            clip = clip.with_effects([FadeIn(0.3), FadeOut(CROSSFADE)])
        elif i == 7:
            clip = clip.with_effects([FadeIn(CROSSFADE)])
        else:
            clip = clip.with_effects([FadeIn(CROSSFADE), FadeOut(CROSSFADE)])
        clips.append(clip)

    print("\n=== ASSEMBLING VIDEO ===")
    video = concatenate_videoclips(clips, method="compose")
    video = video.with_audio(audio)

    output_file = f"{OUTPUT_FINAL}/260420-muc-rim-me-vnew-ot.mp4"
    print(f"  Rendering {total_dur:.2f}s -> {output_file}")
    video.write_videofile(output_file, fps=30, codec="libx264", audio_codec="aac", preset="medium", threads=4)

    print(f"\nDone! {output_file}")
    print(f"Duration: {total_dur:.2f}s | {W}x{H} | 30fps")
    audio.close()
    video.close()
    for c in clips:
        c.close()


if __name__ == "__main__":
    asyncio.run(main())
