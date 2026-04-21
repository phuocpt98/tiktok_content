"""
Tải video TikTok không watermark + metadata JSON.

Chiến lược:
  1. yt-dlp --flat-playlist: extract list video URL từ profile (không tải video).
  2. tikwm.com API: với mỗi URL, tải MP4 không WM + metadata.

Lý do: yt-dlp built-in TikTok extractor thường chỉ trả audio-only cho nhiều
account (TikTok anti-bot). tikwm.com là service cộng đồng, stable hơn cho video.

Usage:
  # Tải N video mới nhất của 1 user
  python scripts/ingest-tiktok.py https://www.tiktok.com/@beheobu0102 --limit 3

  # Tải 1 video cụ thể
  python scripts/ingest-tiktok.py https://www.tiktok.com/@user/video/7xxxxxxx

  # Tuỳ chỉnh thư mục output
  python scripts/ingest-tiktok.py <URL> --out assets/raw/tiktok/beheobu0102

Output:
  assets/raw/tiktok/{author}/{video_id}.mp4          # video không watermark
  assets/raw/tiktok/{author}/{video_id}.info.json    # metadata (caption, view, like, ...)
  assets/raw/tiktok/{author}/{video_id}.jpg          # thumbnail cover
  assets/raw/tiktok/{author}/_manifest.jsonl         # 1 dòng/video đã tải (audit log)

Cần:
  brew install yt-dlp ffmpeg
  pip install --user yt-dlp       # tuỳ chọn, có sẵn trong repo requirements
"""
from __future__ import annotations

import argparse
import json
import os
import random
import re
import shutil
import subprocess
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_OUT = ROOT / "assets" / "raw" / "tiktok"
TIKWM_API = "https://www.tikwm.com/api/"


# ── Helpers ────────────────────────────────────────────────────────────────

def extract_author(url: str) -> str:
    """Lấy @handle từ URL. Fallback '_unknown' nếu không match.

    Lưu ý: yt-dlp --flat-playlist trả URL dùng SEC_UID (88-char MS4wLj...) thay vì
    @username. Ta detect pattern này và KHÔNG dùng làm author (sẽ resolve qua tikwm).
    """
    m = re.search(r"tiktok\.com/@([^/?#]+)", url)
    if not m:
        return "_unknown"
    handle = m.group(1)
    # SEC_UID: 88 chars, bắt đầu bằng MS4wLj (base64-ish)
    if len(handle) > 40 and handle.startswith("MS4wLj"):
        return "_unknown"
    return handle


def resolve_author_via_tikwm(url: str) -> str:
    """Gọi tikwm 1 lần để lấy real author.unique_id. Dùng khi URL dùng SEC_UID."""
    try:
        data = tikwm_fetch(url)
        uid = (data.get("author") or {}).get("unique_id")
        return uid or "_unknown"
    except Exception:
        return "_unknown"


def is_user_profile(url: str) -> bool:
    """Profile URL (không trỏ tới 1 video cụ thể)."""
    return "/video/" not in url and "/photo/" not in url


def find_ytdlp() -> str:
    """Tìm yt-dlp binary. Dùng để extract list URL (không tải video)."""
    if env := os.environ.get("YT_DLP_BIN"):
        return env
    for candidate in [
        shutil.which("yt-dlp"),
        str(Path.home() / "Library/Python/3.9/bin/yt-dlp"),
        str(Path.home() / ".local/bin/yt-dlp"),
    ]:
        if candidate and Path(candidate).exists():
            return candidate
    raise SystemExit("Không tìm thấy yt-dlp. Cài: brew install yt-dlp")


def extract_sec_uid(profile_url: str) -> str | None:
    """Extract SEC_UID (channel_id của TikTok) từ profile URL.

    SEC_UID là 88-char base64 trông như 'MS4wLjABAAAAdsu...'. Nếu có nó, ta
    có thể paginate toàn bộ video của user qua format 'tiktokuser:SEC_UID'.
    """
    yt_dlp = find_ytdlp()
    cmd = [
        yt_dlp, "--flat-playlist", "--playlist-end", "1",
        "--print", "%(channel_id)s", profile_url,
    ]
    try:
        out = subprocess.run(cmd, capture_output=True, text=True, timeout=60).stdout
        for line in out.splitlines():
            line = line.strip()
            if line.startswith("MS4wLj"):  # SEC_UID prefix cố định
                return line
    except Exception:
        pass
    return None


def list_video_urls(profile_url: str, limit: int | None) -> list[str]:
    """Dùng yt-dlp --flat-playlist để lấy list URL, không tải video.

    Với limit=None → lấy tất cả video của user (có thể hàng trăm/nghìn).
    Khi limit=None, tự động extract SEC_UID rồi dùng 'tiktokuser:' format
    vì profile URL thường chỉ trả ~3 video đầu.
    """
    yt_dlp = find_ytdlp()

    target_url = profile_url
    if limit is None:
        sec_uid = extract_sec_uid(profile_url)
        if sec_uid:
            target_url = f"tiktokuser:{sec_uid}"
            print(f"  [auto] SEC_UID={sec_uid[:20]}... → dùng tiktokuser: format")
        else:
            print(f"  ⚠ Không extract được SEC_UID, dùng profile URL (có thể chỉ ~3 video)")

    cmd = [yt_dlp, "--flat-playlist", "--print", "%(url)s"]
    if limit is not None:
        cmd += ["--playlist-end", str(limit)]
    cmd.append(target_url)

    out = subprocess.run(cmd, capture_output=True, text=True, check=True).stdout
    return [u.strip() for u in out.splitlines() if u.strip()]


# ── tikwm.com API ──────────────────────────────────────────────────────────

def tikwm_fetch(video_url: str, retries: int = 3) -> dict:
    """Gọi tikwm.com GET API cho 1 video URL, trả về dict data."""
    params = urllib.parse.urlencode({"url": video_url, "hd": "1"})
    api_url = f"{TIKWM_API}?{params}"

    for attempt in range(retries):
        try:
            req = urllib.request.Request(
                api_url,
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                                  "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
                },
            )
            with urllib.request.urlopen(req, timeout=30) as r:
                body = r.read().decode("utf-8")
            payload = json.loads(body)
        except Exception as e:
            if attempt == retries - 1:
                raise
            time.sleep(2 ** attempt)
            continue

        if payload.get("code") == 0:
            return payload["data"]

        # Rate-limit của tikwm (1 req/s free). Đợi rồi thử lại.
        if "limit" in str(payload.get("msg", "")).lower():
            time.sleep(2)
            continue
        raise RuntimeError(f"tikwm error: {payload}")

    raise RuntimeError(f"tikwm fetch thất bại sau {retries} lần")


def download_file(url: str, dest: Path, user_agent: str | None = None) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    headers = {
        "User-Agent": user_agent or
                      "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                      "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
    }
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=120) as r, dest.open("wb") as f:
        shutil.copyfileobj(r, f)


# ── Normalize tikwm → manifest entry ───────────────────────────────────────

def build_entry(data: dict, file_path: Path, thumb_path: Path | None) -> dict:
    """Chuẩn hoá payload tikwm thành schema manifest nhất quán."""
    author = data.get("author") or {}
    return {
        "id": str(data.get("video_id") or data.get("id") or file_path.stem),
        "platform": "tiktok",
        "url": f"https://www.tiktok.com/@{author.get('unique_id')}/video/{data.get('video_id')}",
        "author": author.get("nickname"),
        "author_id": author.get("unique_id"),
        "author_uid": author.get("id"),
        "caption": (data.get("title") or "").strip(),
        "duration_sec": data.get("duration"),
        "views": data.get("play_count"),
        "likes": data.get("digg_count"),
        "comments": data.get("comment_count"),
        "shares": data.get("share_count"),
        "downloads": data.get("download_count"),
        "upload_ts": data.get("create_time"),
        "music_title": (data.get("music_info") or {}).get("title"),
        "music_author": (data.get("music_info") or {}).get("author"),
        "is_original_sound": (data.get("music_info") or {}).get("original"),
        "region": data.get("region"),
        "file_path": str(file_path.resolve().relative_to(ROOT)) if file_path.exists() else None,
        "thumb_path": str(thumb_path.resolve().relative_to(ROOT)) if thumb_path and thumb_path.exists() else None,
        "ingested_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
    }


def append_manifest(out_dir: Path, entry: dict) -> None:
    path = out_dir / "_manifest.jsonl"
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def load_existing_ids(out_dir: Path) -> set[str]:
    path = out_dir / "_manifest.jsonl"
    if not path.exists():
        return set()
    ids = set()
    with path.open() as f:
        for line in f:
            try:
                ids.add(json.loads(line)["id"])
            except Exception:
                pass
    return ids


# ── Main pipeline ──────────────────────────────────────────────────────────

def ingest_one(video_url: str, out_dir: Path, existing_ids: set[str]) -> dict | None:
    # tikwm không cần biết format URL trước, chấp nhận cả /video/ và /photo/
    data = tikwm_fetch(video_url)
    vid_id = str(data.get("video_id") or data.get("id"))

    if vid_id in existing_ids:
        print(f"  ⊙ {vid_id} — đã có, skip")
        return None

    play_url = data.get("hdplay") or data.get("play")
    if not play_url:
        print(f"  ✗ {vid_id} — không có play URL (có thể là photo post)")
        return None

    mp4_path = out_dir / f"{vid_id}.mp4"
    info_path = out_dir / f"{vid_id}.info.json"
    thumb_path = out_dir / f"{vid_id}.jpg"

    print(f"  ↓ {vid_id} — tải video ({data.get('duration')}s, {data.get('play_count')} views)")
    download_file(play_url, mp4_path)

    if cover := data.get("cover") or data.get("origin_cover"):
        try:
            download_file(cover, thumb_path)
        except Exception as e:
            print(f"    ⚠ thumbnail fail: {e}")

    with info_path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    entry = build_entry(data, mp4_path, thumb_path)
    append_manifest(out_dir, entry)
    existing_ids.add(vid_id)
    return entry


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("url", nargs="?", default=None,
                    help="TikTok URL (profile hoặc video đơn). Bỏ qua nếu dùng --from-urls.")
    ap.add_argument("--from-urls", type=Path, default=None,
                    help="File .txt chứa 1 URL/dòng — tải hết list. Ưu tiên hơn arg url.")
    ap.add_argument("--limit", type=int, default=3,
                    help="Số video mới nhất cần tải nếu là profile URL (default: 3). "
                         "Bỏ qua nếu --all.")
    ap.add_argument("--all", action="store_true",
                    help="Tải TẤT CẢ video của user (dùng SEC_UID pagination). "
                         "Cẩn thận rate-limit với kênh lớn.")
    ap.add_argument("--out", type=Path, default=None,
                    help="Thư mục output (default: assets/raw/tiktok/{author}/)")
    ap.add_argument("--sleep", type=float, default=1.5,
                    help="Delay giữa 2 request tikwm (default: 1.5s — tránh rate-limit)")
    args = ap.parse_args()

    # Mode 1: --from-urls → đọc file chứa list URL, KHÔNG cần author từ URL arg
    if args.from_urls:
        if not args.from_urls.exists():
            raise SystemExit(f"Không tìm thấy: {args.from_urls}")
        urls = [u.strip() for u in args.from_urls.read_text().splitlines() if u.strip()]
        if not urls:
            raise SystemExit("File URL trống")
        # Author lấy từ URL đầu tiên. Nếu URL dùng SEC_UID → resolve qua tikwm.
        author = extract_author(urls[0])
        if author == "_unknown":
            print("  URL dùng SEC_UID, resolve @username qua tikwm...")
            author = resolve_author_via_tikwm(urls[0])
            print(f"  → @{author}")
        out_dir = args.out or (DEFAULT_OUT / author)
        out_dir.mkdir(parents=True, exist_ok=True)

        print(f"── Ingest TikTok (from urls) ─────────────────────")
        print(f"URL list: {args.from_urls} ({len(urls)} video)")
        print(f"Author  : @{author} (first URL)")
        print(f"Out dir : {out_dir}")
        print(f"──────────────────────────────────────────────────")
    else:
        # Mode 2: single URL hoặc profile
        if not args.url:
            raise SystemExit("Cần <url> hoặc --from-urls")
        author = extract_author(args.url)
        out_dir = args.out or (DEFAULT_OUT / author)
        out_dir.mkdir(parents=True, exist_ok=True)

        effective_limit = None if args.all else args.limit
        print(f"── Ingest TikTok ────────────────────────────────")
        print(f"URL     : {args.url}")
        print(f"Author  : @{author}")
        if is_user_profile(args.url):
            print(f"Limit   : {'ALL' if args.all else args.limit}")
        else:
            print(f"Limit   : (video đơn)")
        print(f"Out dir : {out_dir}")
        print(f"──────────────────────────────────────────────────")

        if is_user_profile(args.url):
            print("→ Extract list video URL từ profile...")
            urls = list_video_urls(args.url, effective_limit)
            print(f"  Được {len(urls)} URL")
        else:
            urls = [args.url]

    existing = load_existing_ids(out_dir)
    new_entries: list[dict] = []

    for i, url in enumerate(urls, 1):
        print(f"\n[{i}/{len(urls)}] {url}")
        try:
            entry = ingest_one(url, out_dir, existing)
            if entry:
                new_entries.append(entry)
        except Exception as e:
            print(f"  ✗ Lỗi: {e}")
        # Tránh rate-limit tikwm (1 req/s free).
        if i < len(urls):
            time.sleep(args.sleep + random.uniform(0, 1))

    print(f"\n✓ Tải xong {len(new_entries)} video mới.")
    for e in new_entries:
        dur = f"{e['duration_sec']}s" if e['duration_sec'] is not None else "?s"
        views = f"{e['views']:,}" if e['views'] is not None else "?"
        print(f"  • {e['id']} — {dur} — {views} views")
        print(f"    {e['caption'][:80]}")


if __name__ == "__main__":
    main()
