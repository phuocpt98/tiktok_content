"""
Phân tích 1 kênh TikTok đối thủ — không tải video, chỉ metadata.

Export:
  - CSV: 1 dòng/video với các chỉ số engagement, timing, music, TikTokShop.
  - Summary: tổng hợp cho kênh (avg views, best videos, posting time, ...)

Usage:
  # Phân tích 50 video mới nhất (nhanh, chỉ yt-dlp)
  python scripts/analyze-channel.py https://www.tiktok.com/@beheobu0102 --limit 50

  # Phân tích toàn bộ kênh (dùng SEC_UID pagination)
  python scripts/analyze-channel.py https://www.tiktok.com/@beheobu0102 --all

  # Bao gồm dữ liệu chi tiết từ tikwm (music info, TikTokShop flag — chậm hơn)
  python scripts/analyze-channel.py <URL> --limit 20 --with-tikwm

Output:
  assets/analysis/tiktok/{author}/videos.csv
  assets/analysis/tiktok/{author}/summary.md

Cần:
  brew install yt-dlp; pip install curl_cffi (đã setup sẵn).
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import re
import shutil
import statistics
import subprocess
import sys
import time
import urllib.parse
import urllib.request
from collections import Counter
from datetime import datetime, timezone, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_OUT = ROOT / "assets" / "analysis" / "tiktok"
TIKWM_API = "https://www.tikwm.com/api/"

# +7 cho VN (GMT+7)
TZ_VN = timezone(timedelta(hours=7))

# Các field export ra CSV, theo thứ tự.
CSV_FIELDS = [
    "id", "url", "upload_date", "upload_hour_vn", "weekday_vn",
    "duration_sec",
    "views", "likes", "comments", "shares", "saves",
    "engagement_rate_pct",
    "caption", "hashtags",
    "music_title", "music_author", "is_original_sound",
    "is_tiktokshop", "is_ad",
]


# ── Helpers ────────────────────────────────────────────────────────────────

def extract_author(url: str) -> str:
    m = re.search(r"tiktok\.com/@([^/?#]+)", url)
    return m.group(1) if m else "_unknown"


def find_ytdlp() -> str:
    if env := os.environ.get("YT_DLP_BIN"):
        return env
    for c in [shutil.which("yt-dlp"), str(Path.home() / "Library/Python/3.9/bin/yt-dlp")]:
        if c and Path(c).exists():
            return c
    raise SystemExit("Không tìm thấy yt-dlp.")


def extract_sec_uid(profile_url: str) -> str | None:
    yt_dlp = find_ytdlp()
    try:
        out = subprocess.run(
            [yt_dlp, "--flat-playlist", "--playlist-end", "1",
             "--print", "%(channel_id)s", profile_url],
            capture_output=True, text=True, timeout=60,
        ).stdout
        for line in out.splitlines():
            line = line.strip()
            if line.startswith("MS4wLj"):
                return line
    except Exception:
        pass
    return None


def parse_hashtags(caption: str) -> list[str]:
    return re.findall(r"#([\wÀ-ỹ]+)", caption or "")


# ── Fetch metadata ─────────────────────────────────────────────────────────

def fetch_via_ytdlp(profile_url: str, limit: int | None) -> list[dict]:
    """Lấy metadata nhẹ từ yt-dlp --flat-playlist --dump-json. Không cần tikwm."""
    yt_dlp = find_ytdlp()

    target = profile_url
    if limit is None:
        sec = extract_sec_uid(profile_url)
        if sec:
            target = f"tiktokuser:{sec}"
            print(f"  [auto] SEC_UID={sec[:20]}...")
        else:
            print("  ⚠ SEC_UID fail, có thể chỉ ~3 video")

    cmd = [yt_dlp, "--flat-playlist", "--dump-json"]
    if limit is not None:
        cmd += ["--playlist-end", str(limit)]
    cmd.append(target)

    print(f"  Gọi: {' '.join(cmd[:3])} {'(all)' if limit is None else f'(limit {limit})'}")

    entries: list[dict] = []
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
    for line in proc.stdout or []:
        line = line.strip()
        if not line.startswith("{"):
            continue
        try:
            entries.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    proc.wait()
    return entries


def fetch_tikwm(video_url: str) -> dict | None:
    """Gọi tikwm.com cho metadata chi tiết (music_info, TikTokShop flag)."""
    params = urllib.parse.urlencode({"url": video_url, "hd": "1"})
    req = urllib.request.Request(
        f"{TIKWM_API}?{params}",
        headers={"User-Agent": "Mozilla/5.0 Safari/605.1.15"},
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            payload = json.loads(r.read())
        return payload.get("data") if payload.get("code") == 0 else None
    except Exception:
        return None


# ── Normalize to row ───────────────────────────────────────────────────────

def to_row(entry: dict, tikwm: dict | None = None) -> dict:
    """Gộp yt-dlp entry + optional tikwm vào 1 row thống nhất."""
    # yt-dlp gives: id, title/description, duration, view_count, like_count, ...
    vid_id = str(entry.get("id") or (tikwm or {}).get("video_id") or "")
    caption = entry.get("title") or entry.get("description") or (tikwm or {}).get("title") or ""
    caption = caption.strip()

    views = entry.get("view_count") or (tikwm or {}).get("play_count") or 0
    likes = entry.get("like_count") or (tikwm or {}).get("digg_count") or 0
    comments = entry.get("comment_count") or (tikwm or {}).get("comment_count") or 0
    shares = entry.get("repost_count") or (tikwm or {}).get("share_count") or 0
    saves = entry.get("save_count") or (tikwm or {}).get("collect_count") or 0

    # Engagement rate = (likes+comments+shares+saves) / views * 100
    er = 0.0
    if views:
        er = round(100 * (likes + comments + shares + saves) / views, 2)

    ts = entry.get("timestamp") or (tikwm or {}).get("create_time")
    upload_date = ""
    upload_hour = -1
    weekday = ""
    if ts:
        dt = datetime.fromtimestamp(ts, tz=TZ_VN)
        upload_date = dt.strftime("%Y-%m-%d")
        upload_hour = dt.hour
        weekday = dt.strftime("%a")

    music_info = (tikwm or {}).get("music_info") or {}
    # yt-dlp flat-playlist cũng có 'track' và 'artist'
    music_title = music_info.get("title") or entry.get("track") or ""
    music_author = music_info.get("author") or entry.get("artist") or ""
    is_original = music_info.get("original")
    if is_original is None and entry.get("track"):
        is_original = "nhạc nền -" in (entry.get("track") or "").lower()

    anchors = (tikwm or {}).get("anchors_extras") or ""
    is_shop = False
    if isinstance(anchors, str) and "is_ec_video" in anchors:
        try:
            is_shop = bool(json.loads(anchors).get("is_ec_video"))
        except Exception:
            is_shop = '"is_ec_video":1' in anchors

    return {
        "id": vid_id,
        "url": entry.get("url") or entry.get("webpage_url") or f"https://www.tiktok.com/@_/video/{vid_id}",
        "upload_date": upload_date,
        "upload_hour_vn": upload_hour if upload_hour >= 0 else "",
        "weekday_vn": weekday,
        "duration_sec": entry.get("duration") or (tikwm or {}).get("duration") or "",
        "views": views,
        "likes": likes,
        "comments": comments,
        "shares": shares,
        "saves": saves,
        "engagement_rate_pct": er,
        "caption": caption[:200],
        "hashtags": " ".join(parse_hashtags(caption)),
        "music_title": music_title,
        "music_author": music_author,
        "is_original_sound": is_original if is_original is not None else "",
        "is_tiktokshop": is_shop,
        "is_ad": (tikwm or {}).get("is_ad", "") if tikwm else "",
    }


# ── Summary ────────────────────────────────────────────────────────────────

def make_summary(author: str, rows: list[dict]) -> str:
    if not rows:
        return f"# @{author}\n\nKhông có dữ liệu.\n"

    def agg(field):
        vals = [r[field] for r in rows if isinstance(r[field], (int, float)) and r[field]]
        return vals

    views_vals = agg("views")
    likes_vals = agg("likes")
    er_vals = [r["engagement_rate_pct"] for r in rows if r["engagement_rate_pct"]]
    dur_vals = [r["duration_sec"] for r in rows if isinstance(r["duration_sec"], (int, float))]
    hours = [r["upload_hour_vn"] for r in rows if isinstance(r["upload_hour_vn"], int)]
    days = [r["weekday_vn"] for r in rows if r["weekday_vn"]]

    top_by_views = sorted(rows, key=lambda r: r["views"], reverse=True)[:10]
    top_by_er = sorted(rows, key=lambda r: r["engagement_rate_pct"], reverse=True)[:10]

    # Hashtag freq
    ht_counter: Counter = Counter()
    for r in rows:
        for ht in (r["hashtags"] or "").split():
            ht_counter[ht] += 1

    # Music freq
    music_counter: Counter = Counter()
    for r in rows:
        if r["music_title"]:
            music_counter[f"{r['music_title']} — {r['music_author']}"] += 1

    original_count = sum(1 for r in rows if r["is_original_sound"] is True)
    shop_count = sum(1 for r in rows if r["is_tiktokshop"])

    lines = []
    lines.append(f"# Phân tích kênh @{author}")
    lines.append(f"\n**Tổng số video**: {len(rows)}")
    if views_vals:
        lines.append(f"**Tổng views**: {sum(views_vals):,}")
        lines.append(f"**View/video (avg / median)**: {int(statistics.mean(views_vals)):,} / {int(statistics.median(views_vals)):,}")
    if likes_vals:
        lines.append(f"**Like/video (avg)**: {int(statistics.mean(likes_vals)):,}")
    if er_vals:
        lines.append(f"**Engagement rate (avg)**: {round(statistics.mean(er_vals), 2)}%")
    if dur_vals:
        lines.append(f"**Duration (avg / median)**: {round(statistics.mean(dur_vals), 1)}s / {int(statistics.median(dur_vals))}s")
    lines.append(f"**Original sound usage**: {original_count}/{len(rows)} ({round(100*original_count/len(rows), 1)}%)")
    lines.append(f"**TikTokShop (shoppable)**: {shop_count}/{len(rows)} ({round(100*shop_count/len(rows), 1)}%)")

    if hours:
        hour_dist = Counter(hours)
        top_hours = hour_dist.most_common(5)
        lines.append(f"\n## Giờ đăng nhiều nhất (VN timezone)")
        for h, c in top_hours:
            lines.append(f"- **{h:02d}h**: {c} video")

    if days:
        day_dist = Counter(days)
        lines.append(f"\n## Ngày đăng trong tuần")
        for d in ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]:
            if d in day_dist:
                lines.append(f"- **{d}**: {day_dist[d]} video")

    lines.append(f"\n## Top 10 video theo VIEWS")
    for r in top_by_views:
        lines.append(f"- {r['views']:>8,} views | ER {r['engagement_rate_pct']}% | {r['upload_date']} | {r['caption'][:60]}")

    lines.append(f"\n## Top 10 video theo ENGAGEMENT RATE")
    for r in top_by_er:
        lines.append(f"- ER {r['engagement_rate_pct']:>6}% | {r['views']:>8,} views | {r['upload_date']} | {r['caption'][:60]}")

    if ht_counter:
        lines.append(f"\n## Top 20 hashtag dùng nhiều nhất")
        for ht, c in ht_counter.most_common(20):
            lines.append(f"- `#{ht}` × {c}")

    if music_counter:
        lines.append(f"\n## Top 10 music/sound (lặp lại)")
        for m, c in music_counter.most_common(10):
            if c > 1:
                lines.append(f"- × {c}: {m[:100]}")

    return "\n".join(lines) + "\n"


# ── Main ───────────────────────────────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("url", help="TikTok profile URL")
    ap.add_argument("--limit", type=int, default=50,
                    help="Số video cần phân tích (default: 50, bỏ qua nếu --all)")
    ap.add_argument("--all", action="store_true",
                    help="Phân tích tất cả video (dùng SEC_UID pagination)")
    ap.add_argument("--with-tikwm", action="store_true",
                    help="Gọi thêm tikwm.com cho mỗi video để lấy music_info chi tiết, TikTokShop flag (chậm: ~1.5s/video)")
    ap.add_argument("--out", type=Path, default=None)
    args = ap.parse_args()

    author = extract_author(args.url)
    out_dir = args.out or (DEFAULT_OUT / author)
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"── Analyze channel @{author} ──────────────────")
    print(f"Out dir: {out_dir}")

    limit = None if args.all else args.limit
    entries = fetch_via_ytdlp(args.url, limit)
    print(f"✓ Thu được {len(entries)} video từ yt-dlp.")

    rows: list[dict] = []
    for i, e in enumerate(entries, 1):
        tikwm = None
        if args.with_tikwm:
            print(f"  [{i}/{len(entries)}] tikwm for {e.get('id')}", end="\r")
            tikwm = fetch_tikwm(e.get("url") or e.get("webpage_url") or "")
            time.sleep(1.5)  # rate-limit
        rows.append(to_row(e, tikwm))
    if args.with_tikwm:
        print()

    # Export CSV
    csv_path = out_dir / "videos.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    print(f"✓ CSV: {csv_path.relative_to(ROOT)}")

    # Summary
    summary = make_summary(author, rows)
    summary_path = out_dir / "summary.md"
    summary_path.write_text(summary, encoding="utf-8")
    print(f"✓ Summary: {summary_path.relative_to(ROOT)}")

    # In ra console bản tóm tắt đầu
    print("\n" + "─" * 60)
    print(summary.split("\n## Top 10 video theo VIEWS")[0])


if __name__ == "__main__":
    main()
