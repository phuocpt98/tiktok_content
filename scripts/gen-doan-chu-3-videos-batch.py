# Batch gen 3 video concept "Đuổi hình bắt chữ" + "Vua tiếng Việt"
# Products: que-cay-bo (VTV điền chữ) | keo-deo-sua-chua (đuổi hình) | keo-deku-sua (VTV sắp xếp)
# 15s mỗi video, voice HoaiMyNeural +30%, 1080x1920
# Hook hoa mỹ rotate: "nàng xinh đẹp nhất thế gian" / "người đáng yêu nhất thế giới" / "tiểu thư kiều diễm nhất hành tinh"

import asyncio
import os
import sys
import edge_tts

sys.stdout.reconfigure(encoding="utf-8")
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
from moviepy import (
    ImageClip, VideoFileClip, AudioFileClip,
    concatenate_videoclips, CompositeVideoClip,
)
from moviepy.video.fx import FadeIn, FadeOut

BASE = "D:/project/demo/content"
FONT_BOLD = "C:/Windows/Fonts/arialbd.ttf"
FONT_REG = "C:/Windows/Fonts/arial.ttf"
W, H = 1080, 1920
VOICE = "vi-VN-HoaiMyNeural"
CF = 0.3  # crossfade

# ========= CONFIGS =========
# Mỗi video có 3 câu flattery rải khắp: hook (slide 1), mid (slide 2), cta (slide 5)
# Bank 6 câu rotate để đa dạng:
#   A "công chúa xinh đẹp nhất thế gian"
#   B "nàng xinh đẹp nhất thế gian"
#   C "người đáng yêu nhất thế gian"
#   D "tiểu thư kiều diễm nhất hành tinh"
#   E "thiên thần đáng yêu nhất vũ trụ"
#   F "em bé đáng yêu nhất trái đất"

CONFIGS = {
    "snack-bach-tuoc": {
        # Flat A, D, E
        "flat1_line1": "MỜI CÔNG CHÚA",
        "flat1_line2": "XINH ĐẸP NHẤT THẾ GIAN",
        "mid_flat": "MỜI TIỂU THƯ KIỀU DIỄM XEM HẾT  ♡",
        "cta_line1": "MỜI THIÊN THẦN ĐÁNG YÊU",
        "cta_line2": "FOLLOW ĐOÁN MÓN MỚI MỖI NGÀY",
        "puzzle_label": "ĐỐ BẠN MÓN GÌ?",
        "puzzle_sub": "GỢI Ý 1",
        "puzzle_display": "3 TỪ • HẢI SẢN 8 CHÂN",
        "clue_hint": "GỢI Ý 2: BẮT ĐẦU  S",
        "answer": "SNACK BẠCH TUỘC!",
        "answer_sub": "Giòn rụm • cay nồng",
        "voice": (
            "Mời công chúa xinh đẹp nhất thế gian đoán món này nào. "
            "Gợi ý, ba từ, hải sản tám chân. "
            "Mời tiểu thư kiều diễm xem hết video nhé, "
            "gợi ý hai, bắt đầu bằng chữ ét-xì. Đoán ra chưa? "
            "Chính xác, snack bạch tuộc! Giòn rụm, cay nồng. "
            "Mời thiên thần đáng yêu follow em đoán món mới mỗi ngày!"
        ),
        "hook_photo": "Untitled10.png",
        "puzzle_bg": "Untitled9.png",
        "clue_video": "ASMR_Bóp_Vỡ_Snack_Bạch_Tuộc.mp4",
        "reveal_photo": "Untitled7.png",
        "cta_photo": "Untitled.png",
        "hook_zoom": 1.8,
    },
    "que-cay-bo": {
        # Flat B, E, A
        "flat1_line1": "MỜI NÀNG XINH ĐẸP",
        "flat1_line2": "NHẤT THẾ GIAN",
        "mid_flat": "MỜI THIÊN THẦN XEM HẾT VIDEO  ♡",
        "cta_line1": "MỜI CÔNG CHÚA XINH ĐẸP",
        "cta_line2": "FOLLOW ĐOÁN MÓN MỚI MỖI NGÀY",
        "puzzle_label": "VUA TIẾNG VIỆT",
        "puzzle_sub": "ĐIỀN CHỮ CÒN THIẾU",
        "puzzle_display": "Q _ E    C _ Y    B _",
        "clue_hint": "GỢI Ý: 3 TỪ • CAY NỒNG",
        "answer": "QUE CAY BÒ!",
        "answer_sub": "Cay đậm đà • giòn rụm",
        "voice": (
            "Mời nàng xinh đẹp nhất thế gian chơi vua tiếng Việt nào. "
            "Hãy điền chữ còn thiếu vào ô trống. "
            "Mời thiên thần đáng yêu xem hết video nhé, "
            "gợi ý ba từ đặc sản cay nồng. Đoán ra chưa? "
            "Chính xác, que cay bò! Cay đậm đà, giòn rụm. "
            "Mời công chúa xinh đẹp follow em đoán món mới mỗi ngày!"
        ),
        "hook_photo": "cover-v1-flat-zoomin.png",
        "puzzle_bg": "cover-v2-marble-cream.png",
        "clue_video": "Spicy_Beef_Snack_Stick_ASMR_Video.mp4",
        "reveal_photo": "cover-v3-flat-full.png",
        "cta_photo": "cover-v5-flat-flip-zoom.png",
        "hook_zoom": 1.8,
    },
    "keo-deo-sua-chua-hoa-qua": {
        # Flat C, F, D
        "flat1_line1": "MỜI NGƯỜI ĐÁNG YÊU",
        "flat1_line2": "NHẤT THẾ GIAN",
        "mid_flat": "MỜI EM BÉ ĐÁNG YÊU XEM HẾT  ♡",
        "cta_line1": "MỜI TIỂU THƯ KIỀU DIỄM",
        "cta_line2": "FOLLOW ĐOÁN MÓN MỚI MỖI NGÀY",
        "puzzle_label": "ĐỐ BẠN MÓN GÌ?",
        "puzzle_sub": "GỢI Ý 1",
        "puzzle_display": "4 TỪ • BẮT ĐẦU: K",
        "clue_hint": "VỊ CHUA NGỌT • MỀM DẺO",
        "answer": "KẸO DẺO SỮA CHUA!",
        "answer_sub": "Hoa quả thơm • tan miệng",
        "voice": (
            "Mời người đáng yêu nhất thế gian đoán món này nào. "
            "Gợi ý, bốn từ, bắt đầu bằng chữ Ka. "
            "Mời em bé đáng yêu xem hết video nhé, "
            "một gợi ý nữa, vị chua ngọt mềm dẻo. Đoán ra chưa? "
            "Chính xác, kẹo dẻo sữa chua hoa quả! "
            "Mời tiểu thư kiều diễm follow em đoán món mới mỗi ngày!"
        ),
        "hook_photo": "photo-01.jpg",
        "puzzle_bg": "photo-05.webp",
        "clue_video": "Gummy_Candy_ASMR_Visual.mp4",
        "reveal_photo": "photo-03.jpg",
        "cta_photo": "photo-07.webp",
        "hook_zoom": 1.7,
    },
    "keo-deku-sua": {
        # Flat D, A, C
        "flat1_line1": "MỜI TIỂU THƯ KIỀU DIỄM",
        "flat1_line2": "NHẤT HÀNH TINH",
        "mid_flat": "MỜI CÔNG CHÚA XEM HẾT VIDEO  ♡",
        "cta_line1": "MỜI NGƯỜI ĐÁNG YÊU",
        "cta_line2": "FOLLOW ĐOÁN MÓN MỚI MỖI NGÀY",
        "puzzle_label": "VUA TIẾNG VIỆT",
        "puzzle_sub": "SẮP XẾP LẠI CHỮ",
        "puzzle_display": "UKDE    AỮS",
        "clue_hint": "GỢI Ý: VỊ SỮA CHUA BÉO",
        "answer": "KẸO DEKU SỮA!",
        "answer_sub": "Tan miệng • béo ngậy",
        "voice": (
            "Mời tiểu thư kiều diễm nhất hành tinh chơi vua tiếng Việt nào. "
            "Hãy sắp xếp lại các chữ cái thành tên món. "
            "Mời công chúa xinh đẹp xem hết video nhé, "
            "gợi ý, vị sữa chua béo ngậy. Đoán ra chưa? "
            "Chính xác, kẹo Deku vị sữa! Tan trong miệng, béo ngậy. "
            "Mời người đáng yêu follow em đoán món mới mỗi ngày!"
        ),
        "hook_photo": "sg-11134201-22120-9oj2s2autmlv41.jpg",
        "puzzle_bg": "Gemini_Generated_Image_cj7okpcj7okpcj7o.png",
        "clue_video": "Video_Kẹo_Sữa_Dễ_Thương.mp4",
        "reveal_photo": "sg-11134201-22120-chefwhbutmlv7b.jpg",
        "cta_photo": "vn-11134207-7qukw-ley7fao3ek5m81.jpg",
        "hook_zoom": 1.6,
    },
    "hat-hon-hop-ganyuan": {
        # Flat E, B, F | clip video nằm trong photos folder
        "flat1_line1": "MỜI THIÊN THẦN ĐÁNG YÊU",
        "flat1_line2": "NHẤT VŨ TRỤ",
        "mid_flat": "MỜI NÀNG XINH ĐẸP XEM HẾT  ♡",
        "cta_line1": "MỜI EM BÉ ĐÁNG YÊU",
        "cta_line2": "FOLLOW ĐOÁN MÓN MỚI MỖI NGÀY",
        "puzzle_label": "ĐỐ BẠN MÓN GÌ?",
        "puzzle_sub": "GỢI Ý 1",
        "puzzle_display": "2 TỪ • HEALTHY",
        "clue_hint": "GỢI Ý 2: BẮT ĐẦU CHỮ  H",
        "answer": "HẠT HỖN HỢP!",
        "answer_sub": "Giòn bùi • dinh dưỡng",
        "voice": (
            "Mời thiên thần đáng yêu nhất vũ trụ đoán món healthy này nào. "
            "Gợi ý, hai từ, healthy cho bữa phụ. "
            "Mời nàng xinh đẹp xem hết video nhé, "
            "gợi ý hai, bắt đầu bằng chữ Hờ. Đoán ra chưa? "
            "Chính xác, hạt hỗn hợp! Giòn bùi, dinh dưỡng. "
            "Mời em bé đáng yêu follow em đoán món mới mỗi ngày!"
        ),
        # Video clip nằm trong photos folder (user đặt nhầm)
        "hook_photo": "cn-11134207-7ras8-mbz0tw1w8erh24.webp",
        "puzzle_bg": "cn-11134207-820l4-mlcx8tg8p72a36.webp",
        "clue_video": "Video_Hạt_Hỗn_Hợp_Rơi_Vào_Bát.mp4",
        "clue_video_from_photos": True,  # flag: clip ở photos thay vì videos
        "reveal_photo": "cn-11134207-820l4-mlcx8tgfal1r7d.webp",
        "cta_photo": "vn-11134207-7r98o-lx8dmauzx87t88.webp",
        "hook_zoom": 1.6,
    },
}

# ========= HELPERS =========
def brighten(img, f=1.15):
    return ImageEnhance.Brightness(img).enhance(f)


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


def draw_text_strip(canvas, lines, y_base, strip_color=(255, 255, 255, 225), pad=28):
    draw = ImageDraw.Draw(canvas, "RGBA")
    font_cache = {}
    max_w = 0
    total_h = sum(l["size"] + 18 for l in lines) + pad * 2
    for l in lines:
        fp = FONT_BOLD if l.get("bold") else FONT_REG
        f = ImageFont.truetype(fp, l["size"])
        font_cache[id(l)] = f
        bbox = draw.textbbox((0, 0), l["text"], font=f)
        max_w = max(max_w, bbox[2] - bbox[0])
    strip_w = max_w + pad * 2
    strip_x = (W - strip_w) // 2
    draw.rounded_rectangle(
        [(strip_x, y_base - pad), (strip_x + strip_w, y_base + total_h - pad)],
        radius=32, fill=strip_color,
    )
    cy = y_base
    for l in lines:
        f = font_cache[id(l)]
        bbox = draw.textbbox((0, 0), l["text"], font=f)
        tw = bbox[2] - bbox[0]
        x = (W - tw) // 2
        c = l["color"]
        if isinstance(c, str):
            r, g, b = tuple(int(c.lstrip("#")[i:i+2], 16) for i in (0, 2, 4))
            c = (r, g, b, 255)
        draw.text((x, cy), l["text"], fill=c, font=f)
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


def make_overlay(lines, y_base, dur, out_path):
    canvas = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw_text_strip(canvas, lines, y_base)
    canvas.save(out_path, "PNG")
    return ImageClip(out_path, duration=dur, transparent=True)


async def gen_voice(text, out_path, retries=4):
    last_err = None
    for attempt in range(retries):
        try:
            comm = edge_tts.Communicate(text, VOICE, rate="+30%")
            await comm.save(out_path)
            return
        except Exception as e:
            last_err = e
            print(f"  Voice retry {attempt + 1}/{retries}: {type(e).__name__}")
            await asyncio.sleep(2 + attempt)
    raise last_err


# ========= RENDER 1 VIDEO =========
async def render_video(slug, cfg):
    print(f"\n{'=' * 60}\n=== {slug} ===\n{'=' * 60}")

    OUT_BASE = f"{BASE}/assets/products/{slug}/output"
    OUT_SLIDES = f"{OUT_BASE}/slides"
    OUT_AUDIO = f"{OUT_BASE}/audio"
    OUT_FINAL = f"{OUT_BASE}/final"
    for d in (OUT_SLIDES, OUT_AUDIO, OUT_FINAL):
        os.makedirs(d, exist_ok=True)

    PHOTOS = f"{BASE}/assets/products/{slug}/photos"
    VIDEOS = f"{BASE}/assets/products/{slug}/videos"

    # 1. Voice
    print("[Voice]")
    audio_path = f"{OUT_AUDIO}/doan-chu-voiceover.mp3"
    await gen_voice(cfg["voice"], audio_path)
    audio = AudioFileClip(audio_path)
    total = audio.duration
    print(f"  Duration: {total:.2f}s")

    # 2. Segment durations (5 cảnh)
    ratios = [0.22, 0.22, 0.18, 0.22, 0.16]
    durs = [total * r for r in ratios]
    clips = []

    # --- 1. HOOK HOA MỸ ---
    print("[1] HOOK hoa my")
    s1 = make_slide(
        f"{PHOTOS}/{cfg['hook_photo']}",
        [
            {"text": cfg["flat1_line1"], "size": 62, "color": "#FF3366", "bold": True},
            {"text": cfg["flat1_line2"], "size": 58, "color": "#3D2200", "bold": True},
            {"text": "ĐOÁN CHỮ NÀO!", "size": 76, "color": "#3D2200", "bold": True},
        ],
        y_base=H - 620, brightness=1.20, zoom=cfg["hook_zoom"],
    )
    s1_path = f"{OUT_SLIDES}/doan-chu-s1-hook.png"
    s1.save(s1_path)
    clips.append(ImageClip(s1_path, duration=durs[0]).with_effects([FadeIn(0.3)]))

    # --- 2. PUZZLE slide (VTV hoặc đuổi hình clue 1) + mid flattery ---
    print("[2] PUZZLE")
    s2 = make_slide(
        f"{PHOTOS}/{cfg['puzzle_bg']}",
        [
            {"text": cfg["mid_flat"], "size": 40, "color": "#FF3366", "bold": True},
            {"text": cfg["puzzle_label"], "size": 56, "color": "#FF3366", "bold": True},
            {"text": cfg["puzzle_sub"], "size": 42, "color": "#3D2200", "bold": True},
            {"text": cfg["puzzle_display"], "size": 72, "color": "#3D2200", "bold": True},
        ],
        y_base=H - 640, brightness=1.22, zoom=1.05,
    )
    s2_path = f"{OUT_SLIDES}/doan-chu-s2-puzzle.png"
    s2.save(s2_path)
    clips.append(ImageClip(s2_path, duration=durs[1]).with_effects([FadeIn(CF), FadeOut(CF)]))

    # --- 3. CLUE VIDEO + overlay hint ---
    print("[3] CLUE video")
    clue_folder = PHOTOS if cfg.get("clue_video_from_photos") else VIDEOS
    clue_vid = f"{clue_folder}/{cfg['clue_video']}"
    v3 = prep_video(clue_vid, durs[2], zoom_wm=1.1).with_effects([FadeIn(CF), FadeOut(CF)])
    ovl_path = f"{OUT_SLIDES}/doan-chu-s3-overlay.png"
    ovl3 = make_overlay(
        [{"text": cfg["clue_hint"], "size": 56, "color": "#FF3366", "bold": True}],
        y_base=180, dur=durs[2], out_path=ovl_path,
    )
    clips.append(CompositeVideoClip([v3, ovl3]).with_duration(durs[2]))

    # --- 4. REVEAL ---
    print("[4] REVEAL")
    s4 = make_slide(
        f"{PHOTOS}/{cfg['reveal_photo']}",
        [
            {"text": "ĐÁP ÁN:", "size": 56, "color": "#FF3366", "bold": True},
            {"text": cfg["answer"], "size": 72, "color": "#3D2200", "bold": True},
            {"text": cfg["answer_sub"], "size": 42, "color": "#3D2200", "bold": True},
        ],
        y_base=H - 520, brightness=1.22, zoom=1.0,
    )
    s4_path = f"{OUT_SLIDES}/doan-chu-s4-reveal.png"
    s4.save(s4_path)
    clips.append(ImageClip(s4_path, duration=durs[3]).with_effects([FadeIn(CF), FadeOut(CF)]))

    # --- 5. CTA (flattery + follow) ---
    print("[5] CTA")
    s5 = make_slide(
        f"{PHOTOS}/{cfg['cta_photo']}",
        [
            {"text": cfg["cta_line1"], "size": 50, "color": "#FF3366", "bold": True},
            {"text": cfg["cta_line2"], "size": 46, "color": "#3D2200", "bold": True},
            {"text": "COMMENT ĐÁP ÁN NHA  ♡", "size": 42, "color": "#3D2200", "bold": True},
        ],
        y_base=H - 520, brightness=1.22, zoom=1.0,
    )
    s5_path = f"{OUT_SLIDES}/doan-chu-s5-cta.png"
    s5.save(s5_path)
    clips.append(ImageClip(s5_path, duration=durs[4]).with_effects([FadeIn(CF)]))

    # Render
    print("[Render]")
    video = concatenate_videoclips(clips, method="chain")
    video = video.with_audio(audio).with_duration(total)
    out_path = f"{OUT_FINAL}/260421-{slug}-doan-chu.mp4"
    video.write_videofile(
        out_path, fps=30, codec="libx264", audio_codec="aac",
        preset="medium", threads=4, logger=None,
    )
    print(f"  DONE: {out_path}")
    return out_path


async def main():
    results = []
    for slug, cfg in CONFIGS.items():
        try:
            p = await render_video(slug, cfg)
            results.append((slug, p, "OK"))
        except Exception as e:
            print(f"  FAIL {slug}: {e}")
            import traceback; traceback.print_exc()
            results.append((slug, None, f"FAIL: {e}"))

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    for s, p, st in results:
        print(f"  {st:8s} | {s:32s} | {p or '-'}")


if __name__ == "__main__":
    asyncio.run(main())
