"""Export content package ready for TikTok upload."""
import shutil
import json
import logging
from pathlib import Path
from datetime import datetime
from src.config import OUTPUT_DIR
from src.database import get_project, search_assets

log = logging.getLogger(__name__)


def export_project(project_id: int) -> str:
    """Export a project as upload-ready package.

    Creates folder structure:
        output/{date}-{slug}/
        ├── caption.txt         (title + caption + hashtags, copy-paste ready)
        ├── video.mp4           (if slideshow video exists)
        ├── thumbnail.png       (first image as thumbnail)
        └── slides/             (all images for Photo Mode upload)

    Returns: path to export folder
    """
    project = get_project(project_id)
    if not project:
        raise ValueError(f"Project #{project_id} not found")

    # Create export folder with date-slug naming
    slug = _slugify(project["title"])
    timestamp = datetime.now().strftime("%Y%m%d")
    folder_name = f"{timestamp}-{slug}"
    export_dir = OUTPUT_DIR / folder_name
    export_dir.mkdir(parents=True, exist_ok=True)
    slides_dir = export_dir / "slides"
    slides_dir.mkdir(exist_ok=True)

    # Parse script data
    script_data = {}
    if project.get("script"):
        try:
            script_data = json.loads(project["script"])
        except json.JSONDecodeError:
            script_data = {"script": project["script"]}

    # Generate caption.txt (copy-paste ready)
    caption_parts = []
    if script_data.get("title"):
        caption_parts.append(script_data["title"])
    if script_data.get("caption"):
        caption_parts.append(script_data["caption"])
    elif script_data.get("hook"):
        caption_parts.append(script_data["hook"])

    # Add hashtags
    hashtags = script_data.get("hashtags", [])
    if hashtags:
        caption_parts.append("\n" + " ".join(hashtags))

    caption_text = "\n\n".join(caption_parts)
    (export_dir / "caption.txt").write_text(caption_text, encoding="utf-8")

    # Copy images to slides/
    images = search_assets(asset_type="image", project_id=project_id)
    for i, img in enumerate(images):
        src_path = Path(img["file_path"])
        if src_path.exists():
            dest = slides_dir / f"slide_{i+1:02d}{src_path.suffix}"
            shutil.copy2(str(src_path), str(dest))
            # First image as thumbnail
            if i == 0:
                shutil.copy2(str(src_path), str(export_dir / f"thumbnail{src_path.suffix}"))

    # Copy video if exists
    videos = search_assets(asset_type="video", project_id=project_id)
    for vid in videos:
        src_path = Path(vid["file_path"])
        if src_path.exists():
            shutil.copy2(str(src_path), str(export_dir / "video.mp4"))
            break

    # Copy audio if exists
    audio = search_assets(asset_type="audio", project_id=project_id)
    for aud in audio:
        src_path = Path(aud["file_path"])
        if src_path.exists():
            shutil.copy2(str(src_path), str(export_dir / f"voiceover{src_path.suffix}"))
            break

    # Save script for reference
    if script_data:
        (export_dir / "script.json").write_text(
            json.dumps(script_data, ensure_ascii=False, indent=2), encoding="utf-8"
        )

    # Generate posting guide
    guide = _generate_posting_guide(project, script_data, len(images), bool(videos))
    (export_dir / "posting-guide.txt").write_text(guide, encoding="utf-8")

    log.info(f"Exported project #{project_id} to {export_dir}")
    return str(export_dir)


def _generate_posting_guide(project: dict, script: dict,
                            image_count: int, has_video: bool) -> str:
    """Generate step-by-step posting guide."""
    lines = [
        f"=== POSTING GUIDE: {project['title']} ===",
        f"Mode: {project['mode']}",
        f"Created: {project['created_at'][:16]}",
        "",
        "--- CÁCH ĐĂNG ---",
        "",
    ]

    if has_video:
        lines.extend([
            "OPTION 1: Upload Video",
            "1. Mở TikTok → nhấn + → Upload",
            "2. Chọn file video.mp4",
            "3. Thêm trending sound (nếu muốn thay nhạc nền)",
            "4. Copy nội dung từ caption.txt → paste vào Caption",
            "5. Nhấn Post",
            "",
        ])

    if image_count > 0:
        lines.extend([
            "OPTION 2: Photo Mode (KHUYÊN DÙNG)",
            "1. Mở TikTok → nhấn + → chọn Photo Mode",
            f"2. Chọn {image_count} ảnh từ folder slides/",
            "3. Chọn trending sound (quan trọng cho reach!)",
            "4. Copy nội dung từ caption.txt → paste vào Caption",
            "5. Nhấn Post",
            "",
        ])

    lines.extend([
        "--- TIPS ---",
        "- Đăng vào 11h-13h hoặc 19h-22h (giờ cao điểm VN)",
        "- Dùng trending sound để tăng reach",
        "- Reply comment trong 1h đầu để boost engagement",
        "- Pin comment hay nhất",
    ])

    return "\n".join(lines)


def _slugify(text: str, max_len: int = 30) -> str:
    """Convert text to URL-friendly slug."""
    import re
    # Remove Vietnamese diacritics (simplified)
    replacements = {
        "à": "a", "á": "a", "ả": "a", "ã": "a", "ạ": "a",
        "ă": "a", "ắ": "a", "ằ": "a", "ẳ": "a", "ẵ": "a", "ặ": "a",
        "â": "a", "ấ": "a", "ầ": "a", "ẩ": "a", "ẫ": "a", "ậ": "a",
        "đ": "d", "è": "e", "é": "e", "ẻ": "e", "ẽ": "e", "ẹ": "e",
        "ê": "e", "ế": "e", "ề": "e", "ể": "e", "ễ": "e", "ệ": "e",
        "ì": "i", "í": "i", "ỉ": "i", "ĩ": "i", "ị": "i",
        "ò": "o", "ó": "o", "ỏ": "o", "õ": "o", "ọ": "o",
        "ô": "o", "ố": "o", "ồ": "o", "ổ": "o", "ỗ": "o", "ộ": "o",
        "ơ": "o", "ớ": "o", "ờ": "o", "ở": "o", "ỡ": "o", "ợ": "o",
        "ù": "u", "ú": "u", "ủ": "u", "ũ": "u", "ụ": "u",
        "ư": "u", "ứ": "u", "ừ": "u", "ử": "u", "ữ": "u", "ự": "u",
        "ỳ": "y", "ý": "y", "ỷ": "y", "ỹ": "y", "ỵ": "y",
    }
    slug = text.lower()
    for vn, ascii_char in replacements.items():
        slug = slug.replace(vn, ascii_char)
    slug = re.sub(r"[^a-z0-9]+", "-", slug).strip("-")
    return slug[:max_len]
