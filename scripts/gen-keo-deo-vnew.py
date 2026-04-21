# Generate TikTok slideshow video: Kẹo Dẻo Sữa Chua Hoa Quả — PMS concept
# Concept: "Hộp cứu PMS — kỳ kinh nguyệt phiên bản tạp hóa"
# Target: nữ 18-30, tone pastel hồng-xanh, period-talk relatable, hài hước con gái
# Output: assets/products/keo-deo-sua-chua-hoa-qua/output/v-new/final/260420-keo-deo-vnew-pms.mp4

import asyncio
import edge_tts
import os
from PIL import Image, ImageDraw, ImageFont
from moviepy import (
    ImageClip, VideoFileClip, AudioFileClip,
    concatenate_videoclips, CompositeVideoClip
)
from moviepy.video.fx import FadeIn, FadeOut

# === CONFIG ===
BASE = "assets/products/keo-deo-sua-chua-hoa-qua"
PHOTOS = f"{BASE}/photos"
VIDEOS = f"{BASE}/videos"

OUTPUT_SLIDES = "assets/products/keo-deo-sua-chua-hoa-qua/output/v-new/slides"
OUTPUT_AUDIO  = "assets/products/keo-deo-sua-chua-hoa-qua/output/v-new/audio"
OUTPUT_FINAL  = "assets/products/keo-deo-sua-chua-hoa-qua/output/v-new/final"
OUTPUT_FILE   = f"{OUTPUT_FINAL}/260420-keo-deo-vnew-pms.mp4"

FONT_BOLD    = "C:/Windows/Fonts/segoeuib.ttf"
FONT_REGULAR = "C:/Windows/Fonts/segoeui.ttf"

W, H = 1080, 1920
VOICE     = "vi-VN-HoaiMyNeural"
CROSSFADE = 0.4

# Pastel tone: hồng - xanh pastel (period-friendly)
COLOR_BG_PINK  = "#FFE4EC"   # nền hồng pastel
COLOR_BG_TEAL  = "#E0F4F4"   # nền xanh pastel
COLOR_DARK     = "#2D1B2E"   # tím đậm (readable trên pastel)
COLOR_HOT_PINK = "#E91E8C"   # hồng đậm — CTA, highlight
COLOR_MINT     = "#00B894"   # xanh mint — accent
COLOR_WHITE    = "#FFFFFF"
COLOR_SHADOW   = "#00000066" # semi-transparent shadow cho legibility

# Voice script — day 3 CTA, HoaiMy +50%
VOICE_SCRIPT = (
    "Ngày đèn đỏ chỉ cần ba thứ: chăn ấm, trà đào, và hộp kẹo dẻo sữa chua này! "
    "Viên trong veo, dai bouncy, nhân hoa quả thật chảy trong miệng — "
    "đào, xoài, dâu, việt quất. "
    "Ba viên là tâm trạng hồi sinh luôn á! "
    "Tag hội bestie, gửi cho đứa nào sắp tới ngày! "
    "Hành trình xây kênh ngày thứ 3, hãy tim, comment, follow để đồng hành cùng mình!"
)


def draw_text_with_shadow(draw, text, font, y, color, shadow_color="#000000", shadow_offset=3):
    """Draw centered text with drop shadow for legibility on any bg."""
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    x = (W - tw) // 2
    # Shadow
    draw.text((x + shadow_offset, y + shadow_offset), text, fill=shadow_color, font=font)
    # Main text
    draw.text((x, y), text, fill=color, font=font)


def draw_pill_badge(draw, text, font, cy, bg_color, text_color, pad_x=32, pad_y=14, radius=28):
    """Draw a rounded-rectangle badge centered at cy."""
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    bw = tw + pad_x * 2
    bh = th + pad_y * 2
    x0 = (W - bw) // 2
    y0 = cy - bh // 2
    x1 = x0 + bw
    y1 = y0 + bh
    draw.rounded_rectangle([x0, y0, x1, y1], radius=radius, fill=bg_color)
    draw.text((x0 + pad_x, y0 + pad_y), text, fill=text_color, font=font)


def fit_image_center(img, canvas_w=W, canvas_h=H):
    """Scale image to fill canvas (cover), center crop."""
    ratio = max(canvas_w / img.width, canvas_h / img.height)
    new_w = int(img.width * ratio)
    new_h = int(img.height * ratio)
    img = img.resize((new_w, new_h), Image.LANCZOS)
    x_off = (new_w - canvas_w) // 2
    y_off = (new_h - canvas_h) // 2
    return img.crop((x_off, y_off, x_off + canvas_w, y_off + canvas_h))


def fit_image_zoom(img, zoom=1.1, canvas_w=W, canvas_h=H):
    """Cover crop + extra zoom for Ken Burns feel (static)."""
    ratio = max(canvas_w / img.width, canvas_h / img.height) * zoom
    new_w = int(img.width * ratio)
    new_h = int(img.height * ratio)
    img = img.resize((new_w, new_h), Image.LANCZOS)
    x_off = (new_w - canvas_w) // 2
    y_off = (new_h - canvas_h) // 2
    return img.crop((x_off, y_off, x_off + canvas_w, y_off + canvas_h))


def crop_watermark_zoom(img, zoom=1.12, canvas_w=W, canvas_h=H):
    """Zoom 112% to push watermarks off frame edges — cho photo-09.webp."""
    return fit_image_zoom(img, zoom=zoom, canvas_w=canvas_w, canvas_h=canvas_h)


def darken_bottom(canvas, strength=0.55, band_h=420):
    """Add dark gradient band at bottom for text legibility."""
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    for i in range(band_h):
        alpha = int(strength * 255 * (i / band_h))
        draw.line([(0, H - band_h + i), (W, H - band_h + i)], fill=(0, 0, 0, alpha))
    base = canvas.convert("RGBA")
    return Image.alpha_composite(base, overlay).convert("RGB")


def darken_top(canvas, strength=0.55, band_h=340):
    """Add dark gradient band at top."""
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    for i in range(band_h):
        alpha = int(strength * 255 * ((band_h - i) / band_h))
        draw.line([(0, i), (W, i)], fill=(0, 0, 0, alpha))
    base = canvas.convert("RGBA")
    return Image.alpha_composite(base, overlay).convert("RGB")


def make_slide_1_hook():
    """Segment 1 — video clip, no static slide needed (handled via VideoFileClip)."""
    pass  # placeholder — video used directly


def make_slide_2(seg_dur, out_path):
    """Slide 2: photo-06.webp — Ngày đèn đỏ cứu tinh (nền xanh pastel)."""
    img = Image.open(f"{PHOTOS}/photo-06.webp").convert("RGB")
    img = fit_image_zoom(img, zoom=1.08)
    img = darken_top(img, strength=0.5, band_h=300)
    img = darken_bottom(img, strength=0.5, band_h=380)

    draw = ImageDraw.Draw(img)
    font_big  = ImageFont.truetype(FONT_BOLD,    80)
    font_sub  = ImageFont.truetype(FONT_REGULAR, 46)

    draw_text_with_shadow(draw, "NGÀY ĐÈN ĐỎ", font_big,  y=90,  color=COLOR_HOT_PINK, shadow_offset=4)
    draw_text_with_shadow(draw, "CỨU TINH ĐÂY!", font_big, y=185, color=COLOR_WHITE, shadow_offset=4)
    draw_text_with_shadow(draw, "Kẹo dẻo sữa chua hoa quả", font_sub, y=H - 200, color=COLOR_WHITE, shadow_offset=2)

    img.save(out_path, quality=95)
    return ImageClip(out_path, duration=seg_dur).with_effects([FadeIn(CROSSFADE), FadeOut(CROSSFADE)])


def make_slide_3(seg_dur, out_path):
    """Slide 3: photo-05.webp — Viên trong veo, dai bouncy."""
    img = Image.open(f"{PHOTOS}/photo-05.webp").convert("RGB")
    img = fit_image_center(img)
    img = darken_top(img, strength=0.55, band_h=320)
    img = darken_bottom(img, strength=0.4, band_h=280)

    draw = ImageDraw.Draw(img)
    font_big = ImageFont.truetype(FONT_BOLD,    72)
    font_sub = ImageFont.truetype(FONT_REGULAR, 44)

    draw_text_with_shadow(draw, "Viên trong veo", font_big, y=80,  color=COLOR_WHITE,    shadow_offset=4)
    draw_text_with_shadow(draw, "dai bouncy",     font_big, y=170, color=COLOR_HOT_PINK, shadow_offset=4)
    draw_text_with_shadow(draw, "Cắn vào là mê ngay!", font_sub, y=H - 190, color=COLOR_WHITE, shadow_offset=2)

    img.save(out_path, quality=95)
    return ImageClip(out_path, duration=seg_dur).with_effects([FadeIn(CROSSFADE), FadeOut(CROSSFADE)])


def make_slide_4(seg_dur, out_path):
    """Slide 4: Gemini_Generated_Image — Nhân hoa quả thật chảy."""
    img = Image.open(f"{PHOTOS}/Gemini_Generated_Image_enlcbkenlcbkenlc.png").convert("RGB")
    img = fit_image_zoom(img, zoom=1.05)
    img = darken_top(img, strength=0.5, band_h=310)
    img = darken_bottom(img, strength=0.45, band_h=300)

    draw = ImageDraw.Draw(img)
    font_big = ImageFont.truetype(FONT_BOLD,    68)
    font_sub = ImageFont.truetype(FONT_REGULAR, 46)

    draw_text_with_shadow(draw, "Nhân hoa quả THẬT", font_big, y=85,  color=COLOR_WHITE,    shadow_offset=4)
    draw_text_with_shadow(draw, "chảy trong miệng!",  font_big, y=170, color=COLOR_HOT_PINK, shadow_offset=4)
    draw_text_with_shadow(draw, "Từ trái cây tươi nguyên chất", font_sub, y=H - 190, color=COLOR_WHITE, shadow_offset=2)

    img.save(out_path, quality=95)
    return ImageClip(out_path, duration=seg_dur).with_effects([FadeIn(CROSSFADE), FadeOut(CROSSFADE)])


def make_slide_5(seg_dur, out_path):
    """Slide 5: photo-04.jpg — 3 vị đào / xoài / dâu / việt quất."""
    img = Image.open(f"{PHOTOS}/photo-04.jpg").convert("RGB")
    img = fit_image_center(img)
    img = darken_top(img, strength=0.55, band_h=320)
    img = darken_bottom(img, strength=0.5, band_h=350)

    draw = ImageDraw.Draw(img)
    font_big  = ImageFont.truetype(FONT_BOLD,    65)
    font_mid  = ImageFont.truetype(FONT_BOLD,    52)
    font_sub  = ImageFont.truetype(FONT_REGULAR, 42)

    draw_text_with_shadow(draw, "4 vị siêu ngon",         font_big, y=80,  color=COLOR_WHITE,    shadow_offset=4)
    draw_text_with_shadow(draw, "Đào · Xoài · Dâu",       font_mid, y=H - 270, color=COLOR_HOT_PINK, shadow_offset=3)
    draw_text_with_shadow(draw, "Việt quất",               font_mid, y=H - 205, color=COLOR_HOT_PINK, shadow_offset=3)
    draw_text_with_shadow(draw, "Mỗi viên một vị riêng!",  font_sub, y=H - 145, color=COLOR_WHITE,    shadow_offset=2)

    img.save(out_path, quality=95)
    return ImageClip(out_path, duration=seg_dur).with_effects([FadeIn(CROSSFADE), FadeOut(CROSSFADE)])


def make_slide_6(seg_dur, out_path):
    """Slide 6: photo-09.webp (tháp kẹo) — Tag bestie. Zoom 112% crop watermark."""
    img = Image.open(f"{PHOTOS}/photo-09.webp").convert("RGB")
    img = crop_watermark_zoom(img, zoom=1.12)
    img = darken_top(img, strength=0.5, band_h=300)
    img = darken_bottom(img, strength=0.5, band_h=380)

    draw = ImageDraw.Draw(img)
    font_big = ImageFont.truetype(FONT_BOLD,    72)
    font_sub = ImageFont.truetype(FONT_REGULAR, 46)

    draw_text_with_shadow(draw, "Tag bestie",            font_big, y=85,  color=COLOR_WHITE,    shadow_offset=4)
    draw_text_with_shadow(draw, "sắp tới ngày!",         font_big, y=175, color=COLOR_HOT_PINK, shadow_offset=4)
    draw_text_with_shadow(draw, "Gửi cho đứa cần ngay hôm nay", font_sub, y=H - 190, color=COLOR_WHITE, shadow_offset=2)

    img.save(out_path, quality=95)
    return ImageClip(out_path, duration=seg_dur).with_effects([FadeIn(CROSSFADE), FadeOut(CROSSFADE)])


def make_slide_7_cta(seg_dur, out_path):
    """Slide 7: photo-08.webp (khay gỗ 9 viên) — FOLLOW CTA."""
    img = Image.open(f"{PHOTOS}/photo-08.webp").convert("RGB")
    img = fit_image_zoom(img, zoom=1.05)
    img = darken_top(img, strength=0.6, band_h=380)
    img = darken_bottom(img, strength=0.6, band_h=400)

    draw = ImageDraw.Draw(img)
    font_big  = ImageFont.truetype(FONT_BOLD,    82)
    font_mid  = ImageFont.truetype(FONT_BOLD,    54)
    font_sub  = ImageFont.truetype(FONT_REGULAR, 40)

    draw_text_with_shadow(draw, "FOLLOW",             font_big, y=80,  color=COLOR_HOT_PINK, shadow_offset=5)
    draw_text_with_shadow(draw, "Tạp Hóa Pel Pel",   font_mid, y=182, color=COLOR_WHITE,    shadow_offset=4)
    draw_text_with_shadow(draw, "Tim · Comment · Follow",   font_sub, y=H - 220, color=COLOR_WHITE,    shadow_offset=2)
    draw_text_with_shadow(draw, "Ngày thứ 3 xây kênh!",    font_sub, y=H - 165, color=COLOR_HOT_PINK, shadow_offset=2)

    img.save(out_path, quality=95)
    return ImageClip(out_path, duration=seg_dur).with_effects([FadeIn(CROSSFADE)])


def prepare_video_clip(video_path, duration):
    """Load, trim, resize/crop video to 1080x1920."""
    clip = VideoFileClip(video_path)
    if clip.duration > duration:
        clip = clip.subclipped(0, duration)

    clip_w, clip_h = clip.size
    target_ratio = W / H
    clip_ratio   = clip_w / clip_h

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
    print(f"  Voice saved: {output_path}")


async def main():
    os.makedirs(OUTPUT_SLIDES, exist_ok=True)
    os.makedirs(OUTPUT_AUDIO,  exist_ok=True)
    os.makedirs(OUTPUT_FINAL,  exist_ok=True)

    # Step 1: Generate voiceover
    print("=== GENERATING VOICE ===")
    audio_path = os.path.join(OUTPUT_AUDIO, "voiceover-pms.mp3")
    await generate_voice(VOICE_SCRIPT, audio_path)

    audio = AudioFileClip(audio_path)
    total_dur = audio.duration
    print(f"  Audio duration: {total_dur:.2f}s")

    # 7 segments — distribute audio duration proportionally
    # Segment 1 (video hook) gets slightly more time: 1.3x weight
    weights = [1.3, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]
    total_w = sum(weights)
    seg_durs = [total_dur * w / total_w for w in weights]

    print("\n=== BUILDING CLIPS ===")
    clips = []

    # Seg 1: Video hook — Kẹo_chảy_nhân_video (crop Veo watermark via prepare_video_clip center crop)
    print("  [1] Video hook — Kẹo chảy nhân")
    video_hook_path = f"{VIDEOS}/Kẹo_chảy_nhân_video_sẵn_sàng.mp4"
    clip1 = prepare_video_clip(video_hook_path, seg_durs[0])

    # Overlay "HỘP CỨU PMS" text badge on top of video frame
    # Build a still overlay image for the text badge
    badge_canvas = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    badge_draw = ImageDraw.Draw(badge_canvas)
    font_badge = ImageFont.truetype(FONT_BOLD, 88)
    font_sub   = ImageFont.truetype(FONT_REGULAR, 46)
    # Top badge: "HỘP CỨU PMS" — hot pink pill
    draw_pill_badge(badge_draw, "HỘP CỨU PMS", font_badge,
                    cy=165, bg_color=COLOR_HOT_PINK, text_color=COLOR_WHITE, pad_x=40, pad_y=18, radius=36)
    # Sub badge bottom
    draw_pill_badge(badge_draw, "kỳ kinh phiên bản tạp hóa", font_sub,
                    cy=H - 160, bg_color="#00000099", text_color=COLOR_WHITE, pad_x=28, pad_y=14, radius=22)

    badge_path = os.path.join(OUTPUT_SLIDES, "vnew-hook-badge.png")
    badge_canvas.save(badge_path, format="PNG")

    badge_clip = ImageClip(badge_path, duration=clip1.duration)
    clip1_composite = CompositeVideoClip([clip1, badge_clip])
    clip1_composite = clip1_composite.with_effects([FadeIn(0.3), FadeOut(CROSSFADE)])
    clips.append(clip1_composite)

    # Seg 2: photo-06.webp Ken Burns zoom slide
    print("  [2] Slide photo-06 — Ngày đèn đỏ cứu tinh")
    s2_path = os.path.join(OUTPUT_SLIDES, "vnew-slide-02.jpg")
    clip2 = make_slide_2(seg_durs[1], s2_path)
    clips.append(clip2)

    # Seg 3: photo-05.webp — Viên trong veo dai bouncy
    print("  [3] Slide photo-05 — Viên trong veo")
    s3_path = os.path.join(OUTPUT_SLIDES, "vnew-slide-03.jpg")
    clip3 = make_slide_3(seg_durs[2], s3_path)
    clips.append(clip3)

    # Seg 4: Gemini AI gen — Nhân hoa quả thật
    print("  [4] Slide Gemini AI — Nhân hoa quả thật")
    s4_path = os.path.join(OUTPUT_SLIDES, "vnew-slide-04.jpg")
    clip4 = make_slide_4(seg_durs[3], s4_path)
    clips.append(clip4)

    # Seg 5: photo-04.jpg — 3 vị
    print("  [5] Slide photo-04 — 4 vị")
    s5_path = os.path.join(OUTPUT_SLIDES, "vnew-slide-05.jpg")
    clip5 = make_slide_5(seg_durs[4], s5_path)
    clips.append(clip5)

    # Seg 6: photo-09.webp — Tag bestie (zoom 112% crop watermark)
    print("  [6] Slide photo-09 — Tag bestie (zoom crop watermark)")
    s6_path = os.path.join(OUTPUT_SLIDES, "vnew-slide-06.jpg")
    clip6 = make_slide_6(seg_durs[5], s6_path)
    clips.append(clip6)

    # Seg 7: photo-08.webp — CTA FOLLOW
    print("  [7] Slide photo-08 — CTA Follow")
    s7_path = os.path.join(OUTPUT_SLIDES, "vnew-slide-07.jpg")
    clip7 = make_slide_7_cta(seg_durs[6], s7_path)
    clips.append(clip7)

    # Step 3: Concatenate
    print("\n=== ASSEMBLING VIDEO ===")
    video = concatenate_videoclips(clips, method="compose")
    video = video.with_audio(audio)

    print(f"  Rendering {total_dur:.2f}s at {W}x{H} 30fps...")
    video.write_videofile(
        OUTPUT_FILE, fps=30, codec="libx264",
        audio_codec="aac", preset="medium", threads=4,
    )

    print(f"\nXong! Output: {OUTPUT_FILE}")
    print(f"Duration: {total_dur:.2f}s | Resolution: {W}x{H}")

    # Cleanup
    audio.close()
    video.close()
    for c in clips:
        c.close()


if __name__ == "__main__":
    asyncio.run(main())
