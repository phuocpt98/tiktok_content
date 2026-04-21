# Fallback: Gen 5 distinct cover variants from 2 bright source images via Pillow
# Reason: Gemini API free quota exhausted (both keys). Manual gen via Web Pro is alternative.
# Input: FLAT (pastel star pattern 9:16) + COVER (marble flat-lay horizontal)
# Output: 5 composition variants, all bright, all distinct

import sys
from pathlib import Path
from PIL import Image, ImageEnhance, ImageFilter, ImageDraw

sys.path.insert(0, str(Path(__file__).parent.parent))
sys.stdout.reconfigure(encoding="utf-8")

PHOTOS = Path("D:/project/demo/content/assets/products/que-cay-bo/photos")
W, H = 1080, 1920

FLAT = PHOTOS / "Gemini_Generated_Image_ve9v9dve9v9dve9v.png"  # pastel pink star, 9:16
COVER = PHOTOS / "Gemini_Generated_Image_za6dpoza6dpoza6d.png"  # marble slab, horizontal


def fit_fill(img: Image.Image, w: int, h: int, zoom: float = 1.0) -> Image.Image:
    """Resize + center-crop to (w,h), optional zoom factor."""
    ratio = max(w / img.width, h / img.height) * zoom
    nw, nh = int(img.width * ratio), int(img.height * ratio)
    img = img.resize((nw, nh), Image.LANCZOS)
    x = (nw - w) // 2
    y = (nh - h) // 2
    return img.crop((x, y, x + w, y + h))


def fit_pad(img: Image.Image, w: int, h: int, bg: tuple) -> Image.Image:
    """Fit inside (w,h) keeping aspect, pad with bg color. For horizontal → vertical."""
    ratio = min(w / img.width, h / img.height)
    nw, nh = int(img.width * ratio), int(img.height * ratio)
    img = img.resize((nw, nh), Image.LANCZOS)
    canvas = Image.new("RGB", (w, h), bg)
    canvas.paste(img, ((w - nw) // 2, (h - nh) // 2))
    return canvas


def brighten(img: Image.Image, b: float = 1.22, c: float = 1.05, s: float = 1.10) -> Image.Image:
    """Boost brightness/contrast/saturation."""
    img = ImageEnhance.Brightness(img).enhance(b)
    img = ImageEnhance.Contrast(img).enhance(c)
    img = ImageEnhance.Color(img).enhance(s)
    return img


def gradient_bg(w: int, h: int, c_top: tuple, c_bot: tuple) -> Image.Image:
    """Vertical gradient background."""
    canvas = Image.new("RGB", (w, h), c_top)
    draw = ImageDraw.Draw(canvas)
    for y in range(h):
        t = y / h
        r = int(c_top[0] * (1 - t) + c_bot[0] * t)
        g = int(c_top[1] * (1 - t) + c_bot[1] * t)
        b = int(c_top[2] * (1 - t) + c_bot[2] * t)
        draw.line([(0, y), (w, y)], fill=(r, g, b))
    return canvas


def compose_over_gradient(product: Image.Image, bg: Image.Image, scale: float = 0.85, y_off: int = 0) -> Image.Image:
    """Paste product (with transparent-ish padding) centered over gradient bg."""
    pw = int(W * scale)
    ph = int(product.height * (pw / product.width))
    product = product.resize((pw, ph), Image.LANCZOS)
    canvas = bg.copy()
    x = (W - pw) // 2
    y = (H - ph) // 2 + y_off
    canvas.paste(product, (x, y))
    return canvas


def main():
    PHOTOS.mkdir(parents=True, exist_ok=True)
    if not FLAT.exists() or not COVER.exists():
        print(f"[ERR] Source missing. FLAT={FLAT.exists()} COVER={COVER.exists()}")
        sys.exit(1)

    flat = Image.open(FLAT).convert("RGB")
    cover = Image.open(COVER).convert("RGB")
    print(f"[INFO] FLAT={flat.size}  COVER={cover.size}")

    # V1 — macro-bright:    FLAT zoom-in center (que cay ở giữa nổi bật)
    v1 = fit_fill(flat, W, H, zoom=1.8)
    v1 = brighten(v1, b=1.22, c=1.06, s=1.10)
    out1 = PHOTOS / "cover-v1-flat-zoomin.png"
    v1.save(out1); print(f"  OK {out1.name}")

    # V2 — flatlay-wood:    COVER (marble flat-lay) padded over CREAM gradient
    bg2 = gradient_bg(W, H, (255, 246, 224), (252, 225, 191))  # kem-vàng nhạt
    v2 = fit_pad(cover, int(W * 0.95), int(H * 0.55), (255, 246, 224))
    v2 = brighten(v2, b=1.18, c=1.05, s=1.08)
    # composite: gradient bg + cover cropped to middle band
    cover_fit = fit_fill(cover, int(W * 0.95), int(H * 0.55), zoom=1.0)
    cover_fit = brighten(cover_fit, b=1.18, c=1.05, s=1.08)
    v2_final = bg2.copy()
    x = (W - cover_fit.width) // 2
    y = (H - cover_fit.height) // 2
    v2_final.paste(cover_fit, (x, y))
    out2 = PHOTOS / "cover-v2-marble-cream.png"
    v2_final.save(out2); print(f"  OK {out2.name}")

    # V3 — heart-pastel:    FLAT gốc (9:16) + nhạt hồng hơn, zoom vừa
    v3 = fit_fill(flat, W, H, zoom=1.0)
    v3 = brighten(v3, b=1.18, c=1.04, s=1.05)
    out3 = PHOTOS / "cover-v3-flat-full.png"
    v3.save(out3); print(f"  OK {out3.name}")

    # V4 — falling-plate:   COVER rotate + FLIP + pastel gradient BG
    cover_flip = cover.transpose(Image.FLIP_LEFT_RIGHT)
    bg4 = gradient_bg(W, H, (255, 236, 230), (255, 220, 210))  # hồng đào nhạt
    cover_fit4 = fit_fill(cover_flip, int(W * 0.98), int(H * 0.60), zoom=1.05)
    cover_fit4 = brighten(cover_fit4, b=1.20, c=1.06, s=1.12)
    v4 = bg4.copy()
    y_off = int(H * 0.08)  # lệch xuống dưới
    x = (W - cover_fit4.width) // 2
    y = (H - cover_fit4.height) // 2 + y_off
    v4.paste(cover_fit4, (x, y))
    out4 = PHOTOS / "cover-v4-marble-flip-peach.png"
    v4.save(out4); print(f"  OK {out4.name}")

    # V5 — challenge-stand: FLAT flip + zoom khác + tint vàng nhẹ
    flat_flip = flat.transpose(Image.FLIP_LEFT_RIGHT)
    v5 = fit_fill(flat_flip, W, H, zoom=1.3)
    v5 = brighten(v5, b=1.24, c=1.07, s=1.12)
    out5 = PHOTOS / "cover-v5-flat-flip-zoom.png"
    v5.save(out5); print(f"  OK {out5.name}")

    print("\n[DONE] 5 covers saved.")


if __name__ == "__main__":
    main()
