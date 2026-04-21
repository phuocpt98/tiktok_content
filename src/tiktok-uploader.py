"""TikTok auto-upload via tiktok-uploader (Playwright-based)."""
import logging
from pathlib import Path

log = logging.getLogger(__name__)

# Cookie file for TikTok session (created after first login)
COOKIES_DIR = Path(__file__).parent.parent / "cookies"
COOKIES_DIR.mkdir(exist_ok=True)


def upload_video(video_path: str, caption: str,
                 cookies_file: str = None,
                 schedule: str = None) -> bool:
    """Upload a video to TikTok.

    Args:
        video_path: Path to .mp4 file
        caption: Caption text with hashtags
        cookies_file: Path to TikTok cookies (default: cookies/tiktok.txt)
        schedule: Optional schedule time (format: "2026-04-14 19:00")

    Returns: True if upload successful

    First time: Run save_cookies() to login and save session.
    """
    from tiktok_uploader.upload import upload_video as _upload

    cookies = cookies_file or str(COOKIES_DIR / "tiktok.txt")
    if not Path(cookies).exists():
        log.error(f"Cookies not found: {cookies}. Run save_cookies() first.")
        return False

    try:
        _upload(
            filename=video_path,
            description=caption,
            cookies=cookies,
            headless=False,  # Show browser for debugging
        )
        log.info(f"Uploaded: {video_path}")
        return True
    except Exception as e:
        log.error(f"Upload failed: {e}")
        return False


def upload_images(image_paths: list[str], caption: str,
                  cookies_file: str = None) -> bool:
    """Upload images as Photo Mode (carousel) to TikTok.

    Args:
        image_paths: List of image file paths
        caption: Caption text with hashtags
        cookies_file: Path to TikTok cookies
    """
    from tiktok_uploader.upload import upload_video as _upload

    cookies = cookies_file or str(COOKIES_DIR / "tiktok.txt")
    if not Path(cookies).exists():
        log.error(f"Cookies not found: {cookies}. Run save_cookies() first.")
        return False

    try:
        # tiktok-uploader supports photo mode via multiple images
        _upload(
            filename=image_paths,  # Pass list for photo mode
            description=caption,
            cookies=cookies,
            headless=False,
        )
        log.info(f"Uploaded {len(image_paths)} images as Photo Mode")
        return True
    except Exception as e:
        log.error(f"Upload failed: {e}")
        return False


def save_cookies(cookies_file: str = None):
    """Open browser for manual TikTok login, then save cookies.

    Run this ONCE. Browser opens → you login → cookies saved automatically.
    """
    from tiktok_uploader.auth import AuthBackend

    cookies = cookies_file or str(COOKIES_DIR / "tiktok.txt")
    log.info("Opening browser for TikTok login...")
    log.info("Please login to TikTok in the browser window.")

    auth = AuthBackend(cookies=cookies)
    auth.authenticate()

    log.info(f"Cookies saved to: {cookies}")
    return cookies
