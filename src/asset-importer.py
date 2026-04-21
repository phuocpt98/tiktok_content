"""Import manually downloaded files into the asset system."""
import shutil
from pathlib import Path
from datetime import datetime
from src.config import IMAGES_DIR, VIDEOS_DIR, AUDIO_DIR, TEXT_DIR
from src.database import add_asset

# Map file extensions to asset type and directory
EXT_MAP = {
    # Images
    ".png": ("image", IMAGES_DIR),
    ".jpg": ("image", IMAGES_DIR),
    ".jpeg": ("image", IMAGES_DIR),
    ".webp": ("image", IMAGES_DIR),
    # Videos
    ".mp4": ("video", VIDEOS_DIR),
    ".mov": ("video", VIDEOS_DIR),
    ".webm": ("video", VIDEOS_DIR),
    # Audio
    ".mp3": ("audio", AUDIO_DIR),
    ".wav": ("audio", AUDIO_DIR),
    ".m4a": ("audio", AUDIO_DIR),
    # Text
    ".txt": ("text", TEXT_DIR),
    ".json": ("text", TEXT_DIR),
}


def import_file(file_path: str, tags: list = None,
                source: str = "manual", prompt: str = "",
                project_id: int = None) -> dict:
    """Import a file into the asset system.

    Copies file to correct asset directory, registers in database.
    Returns dict with asset info.
    """
    src = Path(file_path)
    if not src.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    ext = src.suffix.lower()
    if ext not in EXT_MAP:
        raise ValueError(f"Unsupported file type: {ext}. Supported: {list(EXT_MAP.keys())}")

    asset_type, dest_dir = EXT_MAP[ext]

    # Copy with timestamp prefix to avoid name collision
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    dest_name = f"{timestamp}_{src.name}"
    dest_path = dest_dir / dest_name

    shutil.copy2(str(src), str(dest_path))

    # Register in database
    asset_id = add_asset(
        asset_type=asset_type,
        name=src.stem,
        file_path=str(dest_path),
        tags=tags or [],
        source=source,
        prompt=prompt,
        project_id=project_id,
    )

    return {
        "id": asset_id,
        "type": asset_type,
        "name": src.stem,
        "path": str(dest_path),
        "source": source,
    }


def import_folder(folder_path: str, tags: list = None,
                  source: str = "manual", project_id: int = None) -> list[dict]:
    """Import all supported files from a folder."""
    folder = Path(folder_path)
    if not folder.is_dir():
        raise NotADirectoryError(f"Not a directory: {folder_path}")

    results = []
    for f in sorted(folder.iterdir()):
        if f.suffix.lower() in EXT_MAP:
            result = import_file(str(f), tags=tags, source=source,
                                project_id=project_id)
            results.append(result)

    return results
