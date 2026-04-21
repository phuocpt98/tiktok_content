"""
Filter video list từ videos.csv (hoặc videos_products.csv) theo tiêu chí → xuất URLs.

Usage:
  # Filter theo category, views tối thiểu, top N
  python scripts/filter-videos.py assets/analysis/tiktok/beheobu0102/videos_products.csv \\
      --category que_cay --min-views 10000 --top 20

  # Filter theo hashtag có trong caption
  python scripts/filter-videos.py <csv> --hashtag anvattuoitho --top 30

  # Filter + sort + export dạng khác nhau
  python scripts/filter-videos.py <csv> --sort views --top 10 --format urls
  #   formats: urls (1 URL/dòng), csv (subset CSV), ids (chỉ video id)

Output (stdout + file):
  --out URLs.txt (default cùng folder input, tên tự sinh từ filter)
"""
from __future__ import annotations

import argparse
import csv
from pathlib import Path


def parse_num(x, default=0):
    try:
        return float(x) if "." in str(x) else int(x)
    except (ValueError, TypeError):
        return default


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("input", type=Path, help="Path tới videos.csv hoặc videos_products.csv")
    ap.add_argument("--category", help="Chỉ lấy category này (vd que_cay, snack)")
    ap.add_argument("--hashtag", help="Chỉ lấy video có hashtag này trong caption")
    ap.add_argument("--brand", help="Chỉ lấy video có brand này")
    ap.add_argument("--min-views", type=int, default=0, help="Views tối thiểu (default: 0)")
    ap.add_argument("--max-views", type=int, default=None, help="Views tối đa (optional)")
    ap.add_argument("--min-er", type=float, default=0.0, help="Engagement rate tối thiểu %%")
    ap.add_argument("--duration-min", type=int, default=0, help="Duration tối thiểu giây")
    ap.add_argument("--duration-max", type=int, default=None, help="Duration tối đa giây")
    ap.add_argument("--original-sound", choices=["only", "exclude"],
                    help="only=chỉ original, exclude=chỉ trending")
    ap.add_argument("--sort", choices=["views", "er", "saves", "likes", "shares", "date"],
                    default="views", help="Sort field (desc)")
    ap.add_argument("--top", type=int, default=None, help="Lấy top N sau filter+sort")
    ap.add_argument("--format", choices=["urls", "csv", "ids"], default="urls")
    ap.add_argument("--out", type=Path, default=None,
                    help="Output file (default: <input_dir>/filtered_<criteria>.<ext>)")
    args = ap.parse_args()

    if not args.input.exists():
        raise SystemExit(f"Không tìm thấy: {args.input}")

    # Load
    with args.input.open(encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    print(f"  Loaded {len(rows)} row từ {args.input.name}", flush=True)

    # Filter
    def match(r):
        if args.category and r.get("category", "") != args.category:
            return False
        if args.hashtag:
            tags = r.get("hashtags", "").split()
            if args.hashtag not in tags:
                return False
        if args.brand and r.get("brand", "").lower() != args.brand.lower():
            return False

        v = parse_num(r.get("views", 0))
        if v < args.min_views:
            return False
        if args.max_views is not None and v > args.max_views:
            return False

        er = parse_num(r.get("engagement_rate_pct", 0))
        if er < args.min_er:
            return False

        d = parse_num(r.get("duration_sec", 0))
        if d < args.duration_min:
            return False
        if args.duration_max is not None and d > args.duration_max:
            return False

        if args.original_sound == "only" and r.get("is_original_sound") != "True":
            return False
        if args.original_sound == "exclude" and r.get("is_original_sound") == "True":
            return False

        return True

    filtered = [r for r in rows if match(r)]
    print(f"  After filter: {len(filtered)} row")

    # Sort
    sort_key_map = {
        "views": "views", "er": "engagement_rate_pct",
        "saves": "saves", "likes": "likes", "shares": "shares",
        "date": "upload_date",
    }
    key = sort_key_map[args.sort]
    if args.sort == "date":
        filtered.sort(key=lambda r: r.get(key, ""), reverse=True)
    else:
        filtered.sort(key=lambda r: parse_num(r.get(key, 0)), reverse=True)

    # Top N
    if args.top:
        filtered = filtered[: args.top]

    # Build output path default
    if args.out is None:
        parts = []
        if args.category: parts.append(f"cat-{args.category}")
        if args.hashtag: parts.append(f"tag-{args.hashtag}")
        if args.brand: parts.append(f"brand-{args.brand.lower()}")
        if args.min_views > 0: parts.append(f"v{args.min_views}")
        if args.top: parts.append(f"top{args.top}")
        slug = "_".join(parts) if parts else "all"
        ext = {"urls": "txt", "csv": "csv", "ids": "txt"}[args.format]
        args.out = args.input.parent / f"filtered_{slug}.{ext}"

    # Write output
    if args.format == "urls":
        with args.out.open("w", encoding="utf-8") as f:
            for r in filtered:
                f.write(r.get("url", "") + "\n")
    elif args.format == "ids":
        with args.out.open("w", encoding="utf-8") as f:
            for r in filtered:
                f.write(r.get("id", "") + "\n")
    elif args.format == "csv":
        if filtered:
            fieldnames = list(filtered[0].keys())
            with args.out.open("w", newline="", encoding="utf-8") as f:
                w = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
                w.writeheader()
                w.writerows(filtered)

    try:
        rel = args.out.resolve().relative_to(Path.cwd())
        print(f"✓ Wrote {len(filtered)} entries → {rel}")
    except ValueError:
        print(f"✓ Wrote {len(filtered)} entries → {args.out}")

    # Preview top 5 trên stdout
    print(f"\nPreview top 5:")
    for r in filtered[:5]:
        views = r.get("views", "?")
        cap = r.get("caption", "")[:60]
        print(f"  {views:>9} | {cap}")


if __name__ == "__main__":
    main()
