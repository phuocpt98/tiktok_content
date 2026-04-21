"""Text overlay engine - add trending text/quotes onto images for TikTok."""
import textwrap
from pathlib import Path
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
from src.config import IMAGES_DIR, VIDEO_WIDTH, VIDEO_HEIGHT


# Default font paths on Windows
WIN_FONTS = [
    "C:/Windows/Fonts/arial.ttf",
    "C:/Windows/Fonts/segoeui.ttf",
    "C:/Windows/Fonts/calibri.ttf",
]


def _get_font(size: int = 60, bold: bool = False) -> ImageFont.FreeTypeFont:
    """Get available system font."""
    for font_path in WIN_FONTS:
        if Path(font_path).exists():
            return ImageFont.truetype(font_path, size)
    return ImageFont.load_default()


def add_text_to_image(image_path: str, text: str,
                      position: str = "center",
                      font_size: int = 60,
                      text_color: str = "#FFFFFF",
                      shadow: bool = True,
                      output_name: str = None) -> str:
    """Add text overlay to an image.

    Args:
        image_path: Source image path
        text: Text to overlay
        position: center, top, bottom
        font_size: Font size in pixels
        text_color: Hex color string
        shadow: Add dark shadow for readability
        output_name: Optional output filename

    Returns: Path to new image with text overlay
    """
    img = Image.open(image_path).convert("RGBA")

    # Resize to TikTok vertical if needed
    if img.size != (VIDEO_WIDTH, VIDEO_HEIGHT):
        img = img.resize((VIDEO_WIDTH, VIDEO_HEIGHT), Image.LANCZOS)

    # Create text overlay layer
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    font = _get_font(font_size)

    # Wrap text to fit width (80% of image width)
    max_chars = int(VIDEO_WIDTH * 0.8 / (font_size * 0.55))
    wrapped = textwrap.fill(text, width=max_chars)

    # Calculate text bounding box
    bbox = draw.textbbox((0, 0), wrapped, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]

    # Position text
    x = (VIDEO_WIDTH - text_w) // 2
    if position == "top":
        y = int(VIDEO_HEIGHT * 0.15)
    elif position == "bottom":
        y = int(VIDEO_HEIGHT * 0.70)
    else:  # center
        y = (VIDEO_HEIGHT - text_h) // 2

    # Draw shadow for readability
    if shadow:
        shadow_offset = max(2, font_size // 20)
        draw.text((x + shadow_offset, y + shadow_offset), wrapped,
                  font=font, fill=(0, 0, 0, 180))

    # Draw main text
    draw.text((x, y), wrapped, font=font, fill=text_color)

    # Composite
    result = Image.alpha_composite(img, overlay).convert("RGB")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    fname = output_name or f"overlay_{timestamp}.png"
    output_path = IMAGES_DIR / fname
    result.save(str(output_path), quality=95)

    return str(output_path)


def create_text_slide(text: str, bg_color: str = "#1a1a2e",
                      text_color: str = "#FFFFFF",
                      font_size: int = 72,
                      output_name: str = None) -> str:
    """Create a pure text slide (no background image).

    Good for quote slides, intro/outro, CTA slides.
    """
    img = Image.new("RGB", (VIDEO_WIDTH, VIDEO_HEIGHT), bg_color)
    draw = ImageDraw.Draw(img)
    font = _get_font(font_size)

    # Wrap and center text
    max_chars = int(VIDEO_WIDTH * 0.75 / (font_size * 0.55))
    wrapped = textwrap.fill(text, width=max_chars)

    bbox = draw.textbbox((0, 0), wrapped, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    x = (VIDEO_WIDTH - text_w) // 2
    y = (VIDEO_HEIGHT - text_h) // 2

    draw.text((x, y), wrapped, font=font, fill=text_color, align="center")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    fname = output_name or f"textslide_{timestamp}.png"
    output_path = IMAGES_DIR / fname
    img.save(str(output_path), quality=95)

    return str(output_path)
