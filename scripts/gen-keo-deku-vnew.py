# Generate TikTok video V-NEW: Kẹo Deku Sữa — "Vị tuổi thơ cấp 2"
# Concept: Nostalgia bait — kẹo sữa cấp 2, kéo bạn cũ tag nhau
# Target: nữ 22-30 | 7 segments | 12-15s | 1080x1920 | HoaiMy +50% | Day 3 CTA

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
PHOTOS = f"{BASE}/assets/products/keo-deku-sua/photos"
VIDEOS = f"{BASE}/assets/products/keo-deku-sua/videos"
OUTPUT_SLIDES = f"{BASE}/output/keo-deku-sua/v-new/slides"
OUTPUT_AUDIO = f"{BASE}/output/keo-deku-sua/v-new/audio"
OUTPUT_FINAL = f"{BASE}/output/keo-deku-sua/v-new/final"

FONT_BOLD = "C:/Windows/Fonts/segoeuib.ttf"
FONT_REGULAR = "C:/Windows/Fonts/segoeui.ttf"

W, H = 1080, 1920
VOICE = "vi-VN-HoaiMyNeural"
CROSSFADE = 0.4

VOICE_SCRIPT = (
    "Ai còn nhớ vị kẹo sữa hồi cấp hai không? "
    "Lọ Deku này đó nha — viên nhỏ xíu, ngọt dịu, "
    "tan trong miệng như sữa thật. "
    "Hồi đó hai nghìn mua được một nắm, "
    "giờ ba mươi nghìn một lọ nhưng vẫn rẻ hơn ly trà sữa! "
    "Gửi cho đứa bạn cấp hai ngày xưa, "
    "hỏi nó còn nhớ vị này không! "
    "Hành trình xây kênh ngày thứ 3, "
    "hãy tim, comment, follow để đồng hành cùng mình!"
)


def create_image_slide(image_path, text_lines, bg_color="#1a1a1a", style="fill"):
    canvas = Image.new("RGB", (W, H), bg_color)
    img = Image.open(image_path).convert("RGB")

    if style == "center":
        ratio = W / img.width
        new_h = int(img.height * ratio)
        img = img.resize((W, new_h), Image.LANCZOS)
        y_offset = (H - new_h) // 2
        canvas.paste(img, (0, y_offset))
    elif style == "fill":
        ratio = max(W / img.width, H / img.height)
        new_w = int(img.width * ratio)
        new_h = int(img.height * ratio)
        img = img.resize((new_w, new_h), Image.LANCZOS)
        x_off = (new_w - W) // 2
        y_off = (new_h - H) // 2
        img = img.crop((x_off, y_off, x_off + W, y_off + H))
        canvas.paste(img, (0, 0))
    elif style == "zoom":
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


def prepare_video_clip(video_path, duration, crop_watermark=False):
    clip = VideoFileClip(video_path)
    if clip.duration > duration:
        clip = clip.subclipped(0, duration)

    clip_w, clip_h = clip.size
    target_ratio = W / H
    clip_ratio = clip_w / clip_h
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

    print("=== GENERATING VOICE ===")
    audio_path = os.path.join(OUTPUT_AUDIO, "voiceover-vnew.mp3")
    await generate_voice(VOICE_SCRIPT, audio_path)

    audio = AudioFileClip(audio_path)
    total_dur = audio.duration
    print(f"  Audio duration: {total_dur:.2f}s")

    print("\n=== BUILDING CLIPS ===")
    seg_dur = total_dur / 7
    clips = []

    # Seg 1: HOOK — lọ Deku đổ viên (Ken Burns zoom)
    print("  [1] HOOK: lọ Deku đổ viên zoom")
    slide1 = create_image_slide(
        f"{PHOTOS}/sg-11134201-22120-9oj2s2autmlv41.jpg",
        [
            {"text": "AI CÒN NHỚ", "size": 78, "y": 70, "color": "#FFD700", "bold": True},
            {"text": "KẸO SỮA CẤP 2?", "size": 70, "y": 175, "color": "#FF69B4", "bold": True},
        ],
        bg_color="#1a3d3d", style="zoom"
    )
    s1_path = f"{OUTPUT_SLIDES}/vnew-slide-01.png"
    slide1.save(s1_path)
    clip1 = ImageClip(s1_path, duration=seg_dur).with_effects([FadeIn(0.3), FadeOut(CROSSFADE)])
    clips.append(clip1)

    # Seg 2: 10 lọ flat-lay nền hồng
    print("  [2] 10 lọ flat-lay hồng")
    slide2 = create_image_slide(
        f"{PHOTOS}/Gemini_Generated_Image_cj7okpcj7okpcj7o.png",
        [
            {"text": "Lọ Deku — quen lắm phải không?", "size": 52, "y": 90, "color": "#D946A0", "bold": True},
        ],
        bg_color="#FFE4F0", style="fill"
    )
    s2_path = f"{OUTPUT_SLIDES}/vnew-slide-02.png"
    slide2.save(s2_path)
    clip2 = ImageClip(s2_path, duration=seg_dur).with_effects([FadeIn(CROSSFADE), FadeOut(CROSSFADE)])
    clips.append(clip2)

    # Seg 3: Video Veo lọ đổ viên (crop watermark)
    print("  [3] Video Veo lọ đổ viên (crop watermark)")
    veo_clip = f"{VIDEOS}/Video_Kẹo_Sữa_Dễ_Thương.mp4"
    clip3 = prepare_video_clip(veo_clip, seg_dur, crop_watermark=True)
    clip3 = clip3.with_effects([FadeIn(CROSSFADE), FadeOut(CROSSFADE)])
    clips.append(clip3)

    # Seg 4: Muỗng viên kẹo close-up
    print("  [4] Muỗng viên kẹo")
    slide4 = create_image_slide(
        f"{PHOTOS}/sg-11134201-22120-e7cp50autmlv77.jpg",
        [
            {"text": "Ngọt dịu", "size": 75, "y": 70, "color": "white", "bold": True},
            {"text": "tan trong miệng", "size": 60, "y": 170, "color": "#FFD700", "bold": True},
        ],
        bg_color="#1a3d3d", style="zoom"
    )
    s4_path = f"{OUTPUT_SLIDES}/vnew-slide-04.png"
    slide4.save(s4_path)
    clip4 = ImageClip(s4_path, duration=seg_dur).with_effects([FadeIn(CROSSFADE), FadeOut(CROSSFADE)])
    clips.append(clip4)

    # Seg 5: 2 hũ dâu + sữa
    print("  [5] 2 hũ — 3 vị")
    slide5 = create_image_slide(
        f"{PHOTOS}/vn-11134207-7qukw-li6143jxci4y48.jpg",
        [
            {"text": "3 vị:", "size": 60, "y": 60, "color": "#FFD700", "bold": True},
            {"text": "Sữa  •  Dâu  •  Socola", "size": 50, "y": 145, "color": "white", "bold": True},
        ],
        bg_color="#0d2d2d", style="fill"
    )
    s5_path = f"{OUTPUT_SLIDES}/vnew-slide-05.png"
    slide5.save(s5_path)
    clip5 = ImageClip(s5_path, duration=seg_dur).with_effects([FadeIn(CROSSFADE), FadeOut(CROSSFADE)])
    clips.append(clip5)

    # Seg 6: Vòng tròn 12 lọ — share bait
    print("  [6] Vòng tròn 12 lọ — share bait")
    slide6 = create_image_slide(
        f"{PHOTOS}/sg-11134201-22120-wvze7hbutmlv49.jpg",
        [
            {"text": "Tag bạn cấp 2", "size": 60, "y": 60, "color": "#FF69B4", "bold": True},
            {"text": "còn nhớ vị này không?", "size": 50, "y": 155, "color": "white", "bold": True},
        ],
        bg_color="#1a3d3d", style="fill"
    )
    s6_path = f"{OUTPUT_SLIDES}/vnew-slide-06.png"
    slide6.save(s6_path)
    clip6 = ImageClip(s6_path, duration=seg_dur).with_effects([FadeIn(CROSSFADE), FadeOut(CROSSFADE)])
    clips.append(clip6)

    # Seg 7: CTA
    print("  [7] CTA — FOLLOW Tạp Hóa Pel Pel")
    slide7 = create_image_slide(
        f"{PHOTOS}/Gemini_Generated_Image_cj7okpcj7okpcj7o.png",
        [
            {"text": "Tim • Comment • Follow", "size": 50, "y": H - 320, "color": "#D946A0", "bold": True},
            {"text": "FOLLOW Tạp Hóa Pel Pel", "size": 55, "y": H - 230, "color": "#1a3d3d", "bold": True},
            {"text": "Hành trình ngày thứ 3 ", "size": 40, "y": H - 150, "color": "#FF69B4"},
        ],
        bg_color="#FFE4F0", style="fill"
    )
    s7_path = f"{OUTPUT_SLIDES}/vnew-slide-07.png"
    slide7.save(s7_path)
    clip7 = ImageClip(s7_path, duration=seg_dur).with_effects([FadeIn(CROSSFADE)])
    clips.append(clip7)

    print("\n=== ASSEMBLING VIDEO ===")
    video = concatenate_videoclips(clips, method="compose")

    original_audio = video.audio
    if original_audio:
        original_audio = original_audio.with_effects([MultiplyVolume(0.3)])
        mixed_audio = CompositeAudioClip([original_audio, audio])
        video = video.with_audio(mixed_audio)
    else:
        video = video.with_audio(audio)

    output_file = f"{OUTPUT_FINAL}/260420-keo-deku-vnew-nostalgia.mp4"
    print(f"  Rendering {total_dur:.2f}s -> {output_file}")
    video.write_videofile(
        output_file, fps=30, codec="libx264",
        audio_codec="aac", preset="medium", threads=4,
    )

    print(f"\nDone! {output_file}")
    print(f"Duration: {total_dur:.2f}s | {W}x{H} | 30fps")

    audio.close()
    video.close()
    for c in clips:
        c.close()


if __name__ == "__main__":
    asyncio.run(main())
