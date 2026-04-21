# Generate 5 TikTok videos for Que Cay Bo (batch 1) — 2026-04-20 Day 3
# Concepts: V1 Flattery+ASMR | V2 Vua Tieng Viet | V3 Hint nguoi yeu | V4 Diet 12h dem | V5 Challenge
# Spec: 1080x1920, 12-16s, HoaiMy varying rates (+30/+50/+70), Day 3 CTA, bright cover

import asyncio
import edge_tts
import os
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
from moviepy import (
    ImageClip, VideoFileClip, AudioFileClip,
    concatenate_videoclips, CompositeVideoClip, CompositeAudioClip
)
from moviepy.audio.fx import MultiplyVolume
from moviepy.video.fx import FadeIn, FadeOut

# === CONFIG ===
BASE = "D:/project/demo/content"
PHOTOS = f"{BASE}/assets/products/que-cay-bo/photos"
VIDEOS = f"{BASE}/assets/products/que-cay-bo/videos"
OUTPUT_BASE = f"{BASE}/assets/products/que-cay-bo/output"

FONT_BOLD = "C:/Windows/Fonts/segoeuib.ttf"
FONT_REGULAR = "C:/Windows/Fonts/segoeui.ttf"

W, H = 1080, 1920
VOICE = "vi-VN-HoaiMyNeural"
CROSSFADE = 0.4

# === ASSET PATHS ===
# 5 bright covers (Pillow-generated variants) — each DISTINCT, all SÁNG
COVER_V1 = f"{PHOTOS}/cover-v1-flat-zoomin.png"          # FLAT zoom-in, hồng pastel
COVER_V2 = f"{PHOTOS}/cover-v2-marble-cream.png"         # Marble 3 loại trên cream
COVER_V3 = f"{PHOTOS}/cover-v3-flat-full.png"            # FLAT full pastel
COVER_V4 = f"{PHOTOS}/cover-v4-marble-flip-peach.png"    # Marble flip, peach bg
COVER_V5 = f"{PHOTOS}/cover-v5-flat-flip-zoom.png"       # FLAT flip + zoom vừa

# Legacy asset paths (middle/end slides)
FLAT  = f"{PHOTOS}/Gemini_Generated_Image_ve9v9dve9v9dve9v.png"   # flat-lay aesthetic
BLUR  = f"{PHOTOS}/Gemini_Generated_Image_4rxlek4rxlek4rxl.png"   # bg blur (CAT12)
PACK  = f"{PHOTOS}/vn-11134207-81ztc-mlz6kwe9zmyr52.webp"         # packaging (chỉ dùng giữa)

VID_ASMR = f"{VIDEOS}/Spicy_Beef_Snack_Stick_ASMR_Video.mp4"
VID_SLOW = f"{VIDEOS}/Appetizing_Beef_Stick_Slow_Motion.mp4"
VID_DROP = f"{VIDEOS}/Video_Thịt_Bò_Cay_Rơi_Xuống_Đĩa.mp4"


# === HELPERS ===
def make_text_overlay(lines, duration):
    """Transparent PNG overlay with text + drop shadow."""
    canvas = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(canvas)
    for t in lines:
        fp = FONT_BOLD if t.get("bold", True) else FONT_REGULAR
        font = ImageFont.truetype(fp, t["size"])
        bbox = draw.textbbox((0, 0), t["text"], font=font)
        tw = bbox[2] - bbox[0]
        x = (W - tw) // 2 if t.get("center", True) else t.get("x", 60)
        # Shadow
        draw.text((x + 4, t["y"] + 4), t["text"], fill=(0, 0, 0, 220), font=font)
        # Main
        c = t["color"].lstrip("#")
        r, g, b = int(c[0:2], 16), int(c[2:4], 16), int(c[4:6], 16)
        draw.text((x, t["y"]), t["text"], fill=(r, g, b, 255), font=font)
    return canvas


def make_image_slide(image_path, text_lines, duration, bg_color="#fff5e6", style="fill", brightness=1.20):
    """Slide ảnh + text overlay với translucent white box behind text để đảm bảo đọc được trên nền ảnh lộn xộn."""
    canvas = Image.new("RGB", (W, H), bg_color)
    img = Image.open(image_path).convert("RGB")
    if brightness != 1.0:
        img = ImageEnhance.Brightness(img).enhance(brightness)
        img = ImageEnhance.Contrast(img).enhance(1.05)
    if style == "fill":
        ratio = max(W / img.width, H / img.height)
        nw, nh = int(img.width * ratio), int(img.height * ratio)
        img = img.resize((nw, nh), Image.LANCZOS)
        x_off = (nw - W) // 2
        y_off = (nh - H) // 2
        img = img.crop((x_off, y_off, x_off + W, y_off + H))
        canvas.paste(img, (0, 0))
    elif style == "zoom":
        ratio = max(W / img.width, H / img.height) * 1.15
        nw, nh = int(img.width * ratio), int(img.height * ratio)
        img = img.resize((nw, nh), Image.LANCZOS)
        x_off = (nw - W) // 2
        y_off = (nh - H) // 2
        img = img.crop((x_off, y_off, x_off + W, y_off + H))
        canvas.paste(img, (0, 0))
    elif style == "center":
        ratio = W / img.width
        nh = int(img.height * ratio)
        img = img.resize((W, nh), Image.LANCZOS)
        canvas.paste(img, (0, (H - nh) // 2))

    # 1. Tính bounding box bao tất cả text → vẽ white translucent strip phía sau
    if text_lines:
        tmp_draw = ImageDraw.Draw(canvas)
        ys = []
        for t in text_lines:
            fp = FONT_BOLD if t.get("bold", True) else FONT_REGULAR
            font = ImageFont.truetype(fp, t["size"])
            bbox = tmp_draw.textbbox((0, 0), t["text"], font=font)
            th = bbox[3] - bbox[1]
            ys.append((t["y"], t["y"] + th))
        y_min = min(y for y, _ in ys) - 20
        y_max = max(yb for _, yb in ys) + 30

        # Only add strip if text in top 40% or bottom 30% (thường là vùng hook/CTA)
        # Skip strip if text in middle (v2 answer case)
        overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        o_draw = ImageDraw.Draw(overlay)
        pad = 50
        o_draw.rounded_rectangle(
            [pad, y_min, W - pad, y_max],
            radius=28,
            fill=(255, 255, 255, 200),  # translucent white
        )
        canvas = Image.alpha_composite(canvas.convert("RGBA"), overlay).convert("RGB")

    # 2. Draw text on top with shadow
    draw = ImageDraw.Draw(canvas)
    for t in text_lines:
        fp = FONT_BOLD if t.get("bold", True) else FONT_REGULAR
        font = ImageFont.truetype(fp, t["size"])
        bbox = draw.textbbox((0, 0), t["text"], font=font)
        tw = bbox[2] - bbox[0]
        x = (W - tw) // 2
        draw.text((x + 3, t["y"] + 3), t["text"], fill=(120, 120, 120), font=font)
        draw.text((x, t["y"]), t["text"], fill=t["color"], font=font)
    return canvas


def prep_video(path, duration, crop_wm=False):
    clip = VideoFileClip(path)
    if clip.duration > duration:
        clip = clip.subclipped(0, duration)
    elif clip.duration < duration:
        # loop short clip
        clip = clip.with_duration(duration)
    cw, ch = clip.size
    target_ratio = W / H
    clip_ratio = cw / ch
    zoom = 1.1 if crop_wm else 1.0
    if clip_ratio > target_ratio:
        new_h = H
        new_w = int(cw * (new_h / ch))
    else:
        new_w = W
        new_h = int(ch * (new_w / cw))
    new_w = int(new_w * zoom)
    new_h = int(new_h * zoom)
    clip = clip.resized((new_w, new_h))
    x_off = (new_w - W) // 2
    y_off = (new_h - H) // 2
    clip = clip.cropped(x1=x_off, y1=y_off, x2=x_off + W, y2=y_off + H)
    return clip


async def gen_voice(text, path, rate="+50%"):
    com = edge_tts.Communicate(text, VOICE, rate=rate)
    await com.save(path)


# === VIDEO CONFIGS ===

# Each config: voice text, rate, segments list
# Segment: {kind: "image"|"video", path, dur, text_lines, overlay_lines, style, crop_wm, fadein, fadeout}

DAY_CTA = "Hành trình xây kênh ngày thứ 3, hãy tim, comment, follow để đồng hành cùng mình!"

CONFIGS = {
    "v1-flattery-asmr": {
        "rate": "+30%",
        "voice": (
            "Mời các nàng tinh tế xem hết video này nha. "
            "Que cay bò Hương Nhãn Long, sợi giòn rụm, vị đậm đà. "
            "Cay nồng nhưng không gắt, ăn một que là muốn ăn mười. "
            + DAY_CTA
        ),
        "segments_builder": "v1",
    },
    "v2-vua-tieng-viet": {
        "rate": "+45%",
        "voice": (
            "Đố các đỉnh cao tiếng Việt. Giòn rụm hay dòn rụm? Đáp án ở cuối video nha. "
            "Que cay bò sợi giòn, cay nồng đậm đà, không ngấy. "
            "Đáp án là... GIÒN RỤM mới đúng chính tả nha. "
            "Ai đúng comment đúng rồi, ai sai comment tao sai. "
            + DAY_CTA
        ),
        "segments_builder": "v2",
    },
    "v3-hint-nguoi-yeu": {
        "rate": "+30%",
        "voice": (
            "Anh ơi, em thèm cái này lắm. "
            "Que cay bò sợi giòn rụm, hai gói chỉ vài chục nghìn thôi. "
            "Cay nồng đậm đà mà không gắt, ăn rồi nghiện luôn. "
            "Test tình yêu, nếu mai không có gói này thì nghĩ lại nha anh. "
            + DAY_CTA
        ),
        "segments_builder": "v3",
    },
    "v4-diet-12h-dem": {
        "rate": "+50%",
        "voice": (
            "Mười hai giờ đêm thèm cay, ai cứu em với? "
            "Diet ngày thứ năm, miệng thèm cay đến phát điên. "
            "Que cay bò Hương Nhãn Long, một que thôi không sao đâu nhỉ. "
            "Calories không tính vào ban đêm, ai đồng ý giơ tay! "
            "Tag đứa bạn cùng diet mà hay cheat. "
            + DAY_CTA
        ),
        "segments_builder": "v4",
    },
    "v5-challenge-5-que": {
        "rate": "+60%",
        "voice": (
            "Thách các bạn ăn năm que liền không uống nước! "
            "Que cay bò Hương Nhãn Long, cay mức ba trên mười thôi. "
            "Sợi giòn, cay nồng, đứa nào liều thì thử đi. "
            "Tag đứa liều nhất nhóm, quay lại comment kết quả nha! "
            + DAY_CTA
        ),
        "segments_builder": "v5",
    },
}


def build_segments(version, total_dur, slides_dir):
    """Return list of clips for each version. Sum duration = total_dur."""
    clips = []

    if version == "v1":
        # 4 segments: cover(hook) → ASMR → macro+slow → cover(CTA)
        seg = [0.20, 0.30, 0.30, 0.20]  # ratios
        durs = [total_dur * r for r in seg]

        # 1: V1 cover (FLAT zoom-in, hồng pastel) — SÁNG
        s1 = make_image_slide(COVER_V1, [
            {"text": "MỜI NÀNG TINH TẾ", "size": 78, "y": 200, "color": "#FF3366", "bold": True},
            {"text": "XEM HẾT VIDEO NÀY", "size": 70, "y": 310, "color": "#3D2200", "bold": True},
        ], durs[0], style="fill", brightness=1.10)
        s1.save(f"{slides_dir}/v1-s1.png")
        c1 = ImageClip(f"{slides_dir}/v1-s1.png", duration=durs[0]).with_effects([FadeIn(0.3)])
        clips.append(c1)

        # 2: ASMR video
        c2 = prep_video(VID_ASMR, durs[1], crop_wm=True)
        c2 = c2.with_effects([FadeIn(CROSSFADE), FadeOut(CROSSFADE)])
        clips.append(c2)

        # 3: slow motion video
        c3 = prep_video(VID_SLOW, durs[2], crop_wm=True)
        c3 = c3.with_effects([FadeIn(CROSSFADE), FadeOut(CROSSFADE)])
        clips.append(c3)

        # 4: FLAT end-slide (khác s1 → không lặp cover)
        s4 = make_image_slide(FLAT, [
            {"text": "FOLLOW EM NGÀY THỨ 3", "size": 64, "y": H - 320, "color": "#FF3366", "bold": True},
            {"text": "Tim • Comment • Follow", "size": 50, "y": H - 220, "color": "#3D2200", "bold": True},
        ], durs[3], style="fill", brightness=1.18)
        s4.save(f"{slides_dir}/v1-s4.png")
        c4 = ImageClip(f"{slides_dir}/v1-s4.png", duration=durs[3]).with_effects([FadeIn(CROSSFADE)])
        clips.append(c4)

    elif version == "v2":
        # 5 segments: blur(question) → ASMR(small text) → macro+slow → blur(countdown) → blur(answer)
        seg = [0.20, 0.25, 0.25, 0.10, 0.20]
        durs = [total_dur * r for r in seg]

        # 1: V2 cover (marble cream — sáng, sharp focus) + question
        s1 = make_image_slide(COVER_V2, [
            {"text": "ĐỐ TIẾNG VIỆT", "size": 60, "y": 180, "color": "#FF3366", "bold": True},
            {"text": "GIÒN RỤM", "size": 96, "y": H - 780, "color": "#3D2200", "bold": True},
            {"text": "hay", "size": 55, "y": H - 660, "color": "#888888", "bold": False},
            {"text": "DÒN RỤM ?", "size": 96, "y": H - 570, "color": "#3D2200", "bold": True},
        ], durs[0], style="fill", brightness=1.10)
        s1.save(f"{slides_dir}/v2-s1.png")
        clips.append(ImageClip(f"{slides_dir}/v2-s1.png", duration=durs[0]).with_effects([FadeIn(0.3)]))

        # 2: ASMR with small reminder text
        c2v = prep_video(VID_ASMR, durs[1], crop_wm=True)
        ovl2 = make_text_overlay([
            {"text": "Đáp án ở cuối video", "size": 44, "y": 100, "color": "#FFFFFF", "bold": True},
        ], durs[1])
        ovl2.save(f"{slides_dir}/v2-ovl2.png")
        ovl_clip = ImageClip(f"{slides_dir}/v2-ovl2.png", duration=durs[1])
        c2 = CompositeVideoClip([c2v, ovl_clip]).with_effects([FadeIn(CROSSFADE), FadeOut(CROSSFADE)])
        clips.append(c2)

        # 3: macro close-up + slow motion combined
        c3v = prep_video(VID_SLOW, durs[2], crop_wm=True).with_effects([FadeIn(CROSSFADE), FadeOut(CROSSFADE)])
        clips.append(c3v)

        # 4: countdown on bright cover (V3 flat pastel — khác s1)
        s4 = make_image_slide(COVER_V3, [
            {"text": "Đáp án...", "size": 90, "y": 700, "color": "#FF3366", "bold": True},
        ], durs[3], style="fill", brightness=1.10)
        s4.save(f"{slides_dir}/v2-s4.png")
        clips.append(ImageClip(f"{slides_dir}/v2-s4.png", duration=durs[3]).with_effects([FadeIn(0.2)]))

        # 5: answer on V3 cover
        s5 = make_image_slide(COVER_V3, [
            {"text": "GIÒN RỤM ✓", "size": 100, "y": 380, "color": "#00AA44", "bold": True},
            {"text": "DÒN là sai chính tả!", "size": 50, "y": 540, "color": "#3D2200", "bold": True},
            {"text": "Comment đúng/sai nha", "size": 44, "y": H - 220, "color": "#FF3366", "bold": True},
        ], durs[4], style="fill", brightness=1.10)
        s5.save(f"{slides_dir}/v2-s5.png")
        clips.append(ImageClip(f"{slides_dir}/v2-s5.png", duration=durs[4]).with_effects([FadeIn(CROSSFADE)]))

    elif version == "v3":
        # 5 segments: cover(hint) → packaging → ASMR+macro → drop(test love) → cover(CTA)
        seg = [0.20, 0.20, 0.30, 0.15, 0.15]
        durs = [total_dur * r for r in seg]

        # V3 cover (FLAT full pastel — hồng nhẹ, khác V1 zoom-in)
        s1 = make_image_slide(COVER_V3, [
            {"text": "GỬI CHO NGƯỜI YÊU", "size": 70, "y": 200, "color": "#FF3366", "bold": True},
            {"text": "XEM NHA  ♡", "size": 70, "y": 310, "color": "#3D2200", "bold": True},
        ], durs[0], style="fill", brightness=1.08)
        s1.save(f"{slides_dir}/v3-s1.png")
        clips.append(ImageClip(f"{slides_dir}/v3-s1.png", duration=durs[0]).with_effects([FadeIn(0.3)]))

        s2 = make_image_slide(PACK, [
            {"text": "Que cay bò", "size": 70, "y": 110, "color": "#FFFFFF", "bold": True},
            {"text": "Hương Nhãn Long", "size": 50, "y": 220, "color": "#FFE699", "bold": True},
        ], durs[1], style="fill", bg_color="#1a1a1a")
        s2.save(f"{slides_dir}/v3-s2.png")
        clips.append(ImageClip(f"{slides_dir}/v3-s2.png", duration=durs[1]).with_effects([FadeIn(CROSSFADE), FadeOut(CROSSFADE)]))

        c3 = prep_video(VID_ASMR, durs[2], crop_wm=True).with_effects([FadeIn(CROSSFADE), FadeOut(CROSSFADE)])
        clips.append(c3)

        c4v = prep_video(VID_DROP, durs[3], crop_wm=True)
        ovl4 = make_text_overlay([
            {"text": "ANH KHÔNG MUA", "size": 56, "y": 140, "color": "#FFFFFF", "bold": True},
            {"text": "= KHÔNG THƯƠNG", "size": 60, "y": 220, "color": "#FF3366", "bold": True},
        ], durs[3])
        ovl4.save(f"{slides_dir}/v3-ovl4.png")
        c4 = CompositeVideoClip([c4v, ImageClip(f"{slides_dir}/v3-ovl4.png", duration=durs[3])])
        c4 = c4.with_effects([FadeIn(CROSSFADE), FadeOut(CROSSFADE)])
        clips.append(c4)

        # End slide — V2 marble cream (khác s1 flat → không lặp)
        s5 = make_image_slide(COVER_V2, [
            {"text": "Tim • Comment • Follow", "size": 50, "y": H - 280, "color": "#3D2200", "bold": True},
            {"text": "Ngày thứ 3 ♡", "size": 56, "y": H - 200, "color": "#FF3366", "bold": True},
        ], durs[4], style="fill", brightness=1.12)
        s5.save(f"{slides_dir}/v3-s5.png")
        clips.append(ImageClip(f"{slides_dir}/v3-s5.png", duration=durs[4]).with_effects([FadeIn(CROSSFADE)]))

    elif version == "v4":
        # 5 segments: cover(hook) → packaging(diet text) → ASMR+macro → drop(calories) → cover(CTA)
        seg = [0.18, 0.20, 0.30, 0.17, 0.15]
        durs = [total_dur * r for r in seg]

        # V4 cover (marble flip + peach bg — khác V2 + SÁNG)
        s1 = make_image_slide(COVER_V4, [
            {"text": "12H ĐÊM", "size": 100, "y": 220, "color": "#FF3366", "bold": True},
            {"text": "THÈM CAY...", "size": 80, "y": 360, "color": "#3D2200", "bold": True},
        ], durs[0], style="fill", brightness=1.10)
        s1.save(f"{slides_dir}/v4-s1.png")
        clips.append(ImageClip(f"{slides_dir}/v4-s1.png", duration=durs[0]).with_effects([FadeIn(0.3)]))

        s2 = make_image_slide(PACK, [
            {"text": "DIET NGÀY 5", "size": 70, "y": 100, "color": "#FFFFFF", "bold": True},
            {"text": "Cứu em với...", "size": 56, "y": 210, "color": "#FFE699", "bold": True},
        ], durs[1], style="fill", bg_color="#1a1a1a")
        s2.save(f"{slides_dir}/v4-s2.png")
        clips.append(ImageClip(f"{slides_dir}/v4-s2.png", duration=durs[1]).with_effects([FadeIn(CROSSFADE), FadeOut(CROSSFADE)]))

        c3 = prep_video(VID_ASMR, durs[2], crop_wm=True).with_effects([FadeIn(CROSSFADE), FadeOut(CROSSFADE)])
        clips.append(c3)

        c4v = prep_video(VID_DROP, durs[3], crop_wm=True)
        ovl4 = make_text_overlay([
            {"text": "CALORIES KHÔNG TÍNH", "size": 54, "y": 140, "color": "#FFFFFF", "bold": True},
            {"text": "VÀO BAN ĐÊM!", "size": 60, "y": 220, "color": "#FF3366", "bold": True},
        ], durs[3])
        ovl4.save(f"{slides_dir}/v4-ovl4.png")
        c4 = CompositeVideoClip([c4v, ImageClip(f"{slides_dir}/v4-ovl4.png", duration=durs[3])])
        c4 = c4.with_effects([FadeIn(CROSSFADE), FadeOut(CROSSFADE)])
        clips.append(c4)

        # End — V5 flat-flip (khác s1 marble → không lặp)
        s5 = make_image_slide(COVER_V5, [
            {"text": "Tag đứa bạn cùng diet", "size": 48, "y": H - 280, "color": "#3D2200", "bold": True},
            {"text": "Follow ngày thứ 3 ♡", "size": 50, "y": H - 200, "color": "#FF3366", "bold": True},
        ], durs[4], style="fill", brightness=1.08)
        s5.save(f"{slides_dir}/v4-s5.png")
        clips.append(ImageClip(f"{slides_dir}/v4-s5.png", duration=durs[4]).with_effects([FadeIn(CROSSFADE)]))

    elif version == "v5":
        # 5 segments: cover(challenge) → flatlay(spice level) → ASMR+slow → drop(tag) → cover(CTA)
        seg = [0.18, 0.20, 0.32, 0.15, 0.15]
        durs = [total_dur * r for r in seg]

        # V5 cover (flat flip + zoom — khác V3/V1, ÁP DỤNG MÀU VÀNG)
        s1 = make_image_slide(COVER_V5, [
            {"text": "AI DÁM ?", "size": 130, "y": 200, "color": "#FF3366", "bold": True},
            {"text": "ĂN 5 QUE LIỀN", "size": 70, "y": 380, "color": "#3D2200", "bold": True},
        ], durs[0], style="fill", brightness=1.08)
        s1.save(f"{slides_dir}/v5-s1.png")
        clips.append(ImageClip(f"{slides_dir}/v5-s1.png", duration=durs[0]).with_effects([FadeIn(0.3)]))

        s2 = make_image_slide(FLAT, [
            {"text": "ĐỘ CAY", "size": 60, "y": 90, "color": "#FFFFFF", "bold": True},
            {"text": "3 / 10", "size": 110, "y": 180, "color": "#FF3366", "bold": True},
        ], durs[1], style="fill", bg_color="#fce4ec")
        s2.save(f"{slides_dir}/v5-s2.png")
        clips.append(ImageClip(f"{slides_dir}/v5-s2.png", duration=durs[1]).with_effects([FadeIn(CROSSFADE), FadeOut(CROSSFADE)]))

        c3 = prep_video(VID_ASMR, durs[2] * 0.5, crop_wm=True).with_effects([FadeIn(CROSSFADE), FadeOut(CROSSFADE)])
        c3b = prep_video(VID_SLOW, durs[2] * 0.5, crop_wm=True).with_effects([FadeIn(CROSSFADE), FadeOut(CROSSFADE)])
        clips.append(c3)
        clips.append(c3b)

        c4v = prep_video(VID_DROP, durs[3], crop_wm=True)
        ovl4 = make_text_overlay([
            {"text": "TAG ĐỨA LIỀU", "size": 60, "y": 140, "color": "#FFFFFF", "bold": True},
            {"text": "NHẤT NHÓM!", "size": 70, "y": 230, "color": "#FF3366", "bold": True},
        ], durs[3])
        ovl4.save(f"{slides_dir}/v5-ovl4.png")
        c4 = CompositeVideoClip([c4v, ImageClip(f"{slides_dir}/v5-ovl4.png", duration=durs[3])])
        c4 = c4.with_effects([FadeIn(CROSSFADE), FadeOut(CROSSFADE)])
        clips.append(c4)

        # End — V4 marble flip peach (khác s1 flat → không lặp)
        s5 = make_image_slide(COVER_V4, [
            {"text": "Follow xem thêm", "size": 50, "y": H - 280, "color": "#3D2200", "bold": True},
            {"text": "Ngày thứ 3 — đi nào!", "size": 50, "y": H - 200, "color": "#FF3366", "bold": True},
        ], durs[4], style="fill", brightness=1.10)
        s5.save(f"{slides_dir}/v5-s5.png")
        clips.append(ImageClip(f"{slides_dir}/v5-s5.png", duration=durs[4]).with_effects([FadeIn(CROSSFADE)]))

    return clips


async def make_video(version_key, cfg):
    print(f"\n{'='*60}\n=== {version_key} ===\n{'='*60}")
    # Output structure: 3 folders per product, version distinguished by FILE PREFIX
    # (see docs/video-production-format.md — anti-pattern: NO v-new/ or v1-xxx/ subfolder)
    slides_dir = f"{OUTPUT_BASE}/slides"
    audio_dir = f"{OUTPUT_BASE}/audio"
    final_dir = f"{OUTPUT_BASE}/final"
    for d in [slides_dir, audio_dir, final_dir]:
        os.makedirs(d, exist_ok=True)

    # 1. Voice — prefix version_key to filename
    audio_path = f"{audio_dir}/{version_key}-voiceover.mp3"
    print(f"  Voice rate {cfg['rate']}: {cfg['voice'][:60]}...")
    await gen_voice(cfg["voice"], audio_path, rate=cfg["rate"])

    audio = AudioFileClip(audio_path)
    total_dur = audio.duration
    print(f"  Audio: {total_dur:.2f}s")

    # 2. Build clips
    print(f"  Building segments for {cfg['segments_builder']}...")
    clips = build_segments(cfg["segments_builder"], total_dur, slides_dir)

    # 3. Assemble
    video = concatenate_videoclips(clips, method="compose")

    # Mix audio
    orig = video.audio
    if orig is not None:
        orig = orig.with_effects([MultiplyVolume(0.25)])
        mixed = CompositeAudioClip([orig, audio])
        video = video.with_audio(mixed)
    else:
        video = video.with_audio(audio)

    # 4. Render
    out_file = f"{final_dir}/260420-que-cay-bo-{version_key}.mp4"
    print(f"  Rendering → {out_file}")
    video.write_videofile(
        out_file,
        fps=30,
        codec="libx264",
        audio_codec="aac",
        preset="medium",
        threads=4,
        logger=None,
    )
    audio.close()
    video.close()
    for c in clips:
        c.close()
    print(f"  ✓ Done: {out_file}  ({total_dur:.2f}s)")
    return out_file


async def main():
    print("\n>>> GEN 5 VIDEOS — QUE CAY BO BATCH 1 <<<\n")
    results = []
    for key, cfg in CONFIGS.items():
        try:
            f = await make_video(key, cfg)
            results.append((key, f, "OK"))
        except Exception as e:
            print(f"  ✗ FAILED {key}: {e}")
            results.append((key, None, f"FAIL: {e}"))

    print("\n\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    for key, f, status in results:
        print(f"  {status:8s} | {key:30s} | {f or '-'}")


if __name__ == "__main__":
    asyncio.run(main())
