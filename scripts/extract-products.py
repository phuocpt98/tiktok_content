"""
Extract thông tin sản phẩm từ videos.csv (caption + hashtag) → CSV enriched.

Thêm 4 cột:
  - category         : que_cay, snack, mi, banh, thach, man, ... (rule-based từ hashtag)
  - subcategory      : chi tiết hơn (vd: "que cay vị gà", "mì Haidilao")
  - brand            : nhãn hàng được nhắc tên (Sasin, Haidilao, Minh Chau, ...) — rỗng nếu không có
  - is_branded       : True nếu caption/hashtag có tên brand

Usage:
  python scripts/extract-products.py assets/analysis/tiktok/beheobu0102/videos.csv
  # → sinh ra videos_products.csv cùng folder

  # Chỉ định output path khác
  python scripts/extract-products.py <input.csv> --out <output.csv>

  # Xem top sản phẩm (aggregation view)
  python scripts/extract-products.py <input.csv> --summary
"""
from __future__ import annotations

import argparse
import csv
import re
from collections import Counter, defaultdict
from pathlib import Path
from statistics import mean


# ── Category rules ────────────────────────────────────────────────────────
# Mapping hashtag → category. Mỗi hashtag chỉ match 1 category (first-match).
# Thứ tự quan trọng: đặc thù trước, chung sau.

CATEGORY_RULES = [
    # Banh trang (niche hit lớn) tách ra trước "banh" nói chung
    ("banh_trang", ["banhtrang", "banhtrangphoisuong", "banhtrangphomai",
                    "banhtrangcatsky", "banhtrangnuong", "banhtrangmix",
                    "banhtrangmutom", "banhtranggion", "banhtrangcom",
                    "banhtrangdeo", "banhtrangchien", "banhtrangrong",
                    "banhtrangtrungmuoi", "banhtrangvn"]),
    ("que_cay", ["quecay", "quecayhangdai", "quecayviga", "quecayvuongthanlong",
                 "quecayvu", "quecayvuong", "hangdai", "caycay",
                 "quecaythanlong", "quecayngon", "quecayhang", "quecaythan"]),
    ("mi",      ["mi", "micay", "micaysasin", "mycay", "mitrongacay", "migacayphomai",
                 "haidilao", "mihaidilao", "micayhaidilao"]),
    ("snack",   ["snack", "snackphomai", "snacktaiheo", "snackmucnuong", "snackngon",
                 "snackcay", "bimbim", "snacktamque"]),
    ("man",     ["man", "manchua", "mancom", "manhau", "manngot", "manto"]),
    ("com_chay",["comchay", "comchaychabong", "comchaymamhanh", "comchaychienmamhanh",
                 "comchaymo", "comchaydacsan"]),
    # Bánh nói chung (đặt SAU banh_trang)
    ("banh",    ["banh", "banhngot", "banhsocola", "banhcupcake", "banhchuoi",
                 "chuoiepdeo", "chuoi", "banhnhan", "banhngon"]),
    ("thach",   ["thach", "thachdua", "thachduaminhchau"]),
    ("chan_ga", ["changa", "changadaho", "changaheyyo", "changadedeo",
                 "changangam", "changaheo"]),
    ("vit",     ["vit", "vitcosaykho", "vitsaykho", "vitsay"]),
    ("nui",     ["nui", "nuichien", "nuichiengion"]),
    ("nam",     ["nam", "namsaygion", "namhuongsaygion"]),
    ("xoai",    ["xoai", "xoaisay", "xoaisaygion", "xoaisaygionlula",
                 "xoaingot", "xoaichua", "xoaicaykho"]),
    ("khoai",   ["khoai", "khoaimon", "khoaimonmamhanh", "khoaitaylacphomai"]),
    ("xuc_xich",["xucxich", "xucxichphomai"]),
    ("tokbokki",["tokbokki"]),
    ("topmo",   ["topmo", "topmorimmamtoi", "topmochuchan"]),
    ("tra_sua", ["trasua", "settrasua", "settrasuatunau"]),
    ("kem",     ["kem", "kemlanh"]),
    ("nuoc_uong",["nuocgiaikhat"]),
    ("bat_dia", ["bat", "batcute", "batancom", "batdia", "batsu"]),
]

# ── Brand detection ────────────────────────────────────────────────────────
# Patterns case-insensitive trong caption (regex word boundary đơn giản).

BRAND_PATTERNS = [
    ("Sasin",        r"\bsasin\b"),
    ("Haidilao",     r"\bhaidilao\b"),
    ("Heyyo",        r"\bheyyo\b"),
    ("Minh Chau",    r"\bminh\s*chau\b|\bminhchau\b|minhchâu"),
    ("Vương Thần Long", r"v[uư][oơ]ng\s*th[aâ]n\s*long|vuongthanlong"),
    ("Quàng Quanh",  r"qu[aà]ng\s*quanh"),
    ("Cát Sky",      r"c[aá]t\s*sky|catsky"),
    ("Mắm Hành",     r"m[aắ]m\s*h[aà]nh|mamhanh"),
]

# ── Subcategory extraction ─────────────────────────────────────────────────
# Regex bắt cụm "que cay vị X", "mì cay X", "snack X"

SUBCAT_PATTERNS = [
    # "que cay vị gà", "que cay gói to"
    (re.compile(r"que\s*cay\s+(v[iị]\s+\w+|g[oó]i\s+to|\w+)", re.I),
     lambda m: f"que cay {m.group(1).lower()}"),
    # "mì cay X" / "mì trộn X" / "mì ... Haidilao"
    (re.compile(r"m[iì]\s+(cay\s+\w+|tr[oộ]n\s+\w+|g[aà]\s+cay)", re.I),
     lambda m: f"mì {m.group(1).lower()}"),
    # "snack X giòn" / "snack X" sau từ snack
    (re.compile(r"snack\s+(\w+\s*\w*)", re.I),
     lambda m: f"snack {m.group(1).lower()}"),
    # "mận X" (mận chua, mận hậu, mận cơm)
    (re.compile(r"m[aậ]n\s+(chua|h[aậ]u|c[oơ]m|to\s+gi[oò]n)", re.I),
     lambda m: f"mận {m.group(1).lower()}"),
    # "bánh X"
    (re.compile(r"b[aá]nh\s+(\w+(?:\s+\w+)?)", re.I),
     lambda m: f"bánh {m.group(1).lower()}"),
    # "thạch X"
    (re.compile(r"th[aạ]ch\s+(\w+)", re.I),
     lambda m: f"thạch {m.group(1).lower()}"),
    # "cơm cháy X"
    (re.compile(r"c[oơ]m\s+ch[aá]y(?:\s+(\w+\s*\w*))?", re.I),
     lambda m: f"cơm cháy{' ' + m.group(1).lower() if m.group(1) else ''}"),
]


# ── Core functions ─────────────────────────────────────────────────────────

def classify_category(hashtags: list[str]) -> str:
    """Match hashtag với rule. Nếu nhiều rule match, chọn rule có nhiều tag match nhất."""
    hashtags_lower = [h.lower() for h in hashtags]
    scores: dict[str, int] = defaultdict(int)
    for cat, keys in CATEGORY_RULES:
        for k in keys:
            if k in hashtags_lower:
                scores[cat] += 1
    if not scores:
        return "other"
    # Tie-break: ưu tiên rule có score cao nhất; nếu bằng nhau chọn rule đầu
    max_score = max(scores.values())
    for cat, _ in CATEGORY_RULES:
        if scores.get(cat, 0) == max_score:
            return cat
    return "other"


def extract_brand(caption: str, hashtags: list[str]) -> str:
    text = f"{caption} {' '.join(hashtags)}".lower()
    for name, pattern in BRAND_PATTERNS:
        if re.search(pattern, text, re.I):
            return name
    return ""


def extract_subcategory(caption: str) -> str:
    """Bắt cụm sản phẩm cụ thể trong caption. Trả chuỗi rỗng nếu không match."""
    # Bỏ hashtag khỏi caption trước khi match (hashtag đã dùng classify category rồi)
    clean = re.sub(r"#\S+", "", caption).strip()
    for pattern, fn in SUBCAT_PATTERNS:
        m = pattern.search(clean)
        if m:
            return fn(m).strip()
    return ""


def enrich_row(row: dict) -> dict:
    hashtags = row.get("hashtags", "").split()
    caption = row.get("caption", "")

    row["category"] = classify_category(hashtags)
    row["subcategory"] = extract_subcategory(caption)
    row["brand"] = extract_brand(caption, hashtags)
    row["is_branded"] = bool(row["brand"])
    return row


# ── Summary ────────────────────────────────────────────────────────────────

def print_summary(rows: list[dict]) -> None:
    print(f"\n=== TỔNG QUAN {len(rows)} VIDEO ===\n")

    # Category breakdown
    cat_stats: dict[str, list[int]] = defaultdict(list)
    for r in rows:
        try: v = int(r.get("views", 0))
        except: v = 0
        cat_stats[r["category"]].append(v)

    print("◆ CATEGORY")
    print(f"  {'Category':15s} | {'n':>3} | {'total':>12} | {'avg':>10} | {'best':>10}")
    print("  " + "-" * 66)
    for cat, views in sorted(cat_stats.items(), key=lambda x: -sum(x[1])):
        tv = sum(views)
        avg = int(mean(views)) if views else 0
        best = max(views) if views else 0
        print(f"  {cat:15s} | {len(views):>3d} | {tv:>12,} | {avg:>10,} | {best:>10,}")

    # Top subcategory
    sub_stats: dict[str, list[int]] = defaultdict(list)
    for r in rows:
        if r["subcategory"]:
            try: v = int(r.get("views", 0))
            except: v = 0
            sub_stats[r["subcategory"]].append(v)

    if sub_stats:
        print("\n◆ TOP SUBCATEGORY (có trong caption)")
        ranked = sorted(sub_stats.items(), key=lambda x: -sum(x[1]))[:15]
        for sub, views in ranked:
            print(f"  × {len(views):2d} | tổng {sum(views):>10,} | avg {int(mean(views)):>8,} | {sub}")

    # Brand breakdown
    brand_stats: dict[str, list[int]] = defaultdict(list)
    for r in rows:
        if r["brand"]:
            try: v = int(r.get("views", 0))
            except: v = 0
            brand_stats[r["brand"]].append(v)

    if brand_stats:
        print("\n◆ BRAND (nhắc tên trong caption/hashtag)")
        for brand, views in sorted(brand_stats.items(), key=lambda x: -sum(x[1])):
            print(f"  × {len(views):2d} | tổng {sum(views):>10,} | avg {int(mean(views)):>8,} | {brand}")

    branded = sum(1 for r in rows if r["is_branded"])
    print(f"\n  Tỉ lệ video có brand name: {branded}/{len(rows)} ({100*branded/len(rows):.1f}%)")


# ── Main ───────────────────────────────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("input", type=Path, help="Path tới videos.csv")
    ap.add_argument("--out", type=Path, default=None,
                    help="Output CSV (default: <input>_products.csv cùng folder)")
    ap.add_argument("--summary", action="store_true",
                    help="In aggregation view (không ghi file output)")
    args = ap.parse_args()

    if not args.input.exists():
        raise SystemExit(f"Không tìm thấy file: {args.input}")

    rows = []
    with args.input.open(encoding="utf-8") as f:
        rows = [enrich_row(r) for r in csv.DictReader(f)]

    print(f"✓ Đọc {len(rows)} row từ {args.input}")

    if args.summary:
        print_summary(rows)
        return

    out_path = args.out or args.input.with_name(args.input.stem + "_products.csv")
    fieldnames = list(rows[0].keys()) if rows else []
    with out_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)

    print(f"✓ Ghi {out_path}")
    print_summary(rows)


if __name__ == "__main__":
    main()
