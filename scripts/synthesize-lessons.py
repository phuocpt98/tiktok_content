"""
Dùng Gemini tổng hợp "bài học" từ data 1 kênh TikTok đối thủ:
  - summary.md (stats từ analyze-channel.py)
  - videos_products.csv (có category/brand)
  - transcripts từ scene-library (nếu đã transcribe)

Output:
  assets/analysis/tiktok/<author>/lessons.md     — bài học chi tiết per kênh
  docs/pel-pel-playbook.md                       — master playbook, append section

Usage:
  # Tổng hợp lessons cho 1 kênh
  python scripts/synthesize-lessons.py beheobu0102

  # Tập trung vào 1 category (có transcripts)
  python scripts/synthesize-lessons.py beheobu0102 --category que_cay

  # Chỉ update lessons.md, KHÔNG ghi vào playbook tổng
  python scripts/synthesize-lessons.py beheobu0102 --no-playbook

Yêu cầu:
  - .env có GEMINI_API_KEY
  - Đã chạy analyze-channel.py + extract-products.py trước đó
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import time
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")

try:
    from google import genai
except ImportError:
    raise SystemExit("Thiếu google-genai. Cài: pip install --user google-genai")

MODEL = "gemini-2.5-flash"
PLAYBOOK = ROOT / "docs" / "pel-pel-playbook.md"
ANALYSIS_DIR = ROOT / "assets" / "analysis" / "tiktok"
SCENE_LIB = ROOT / "assets" / "scene-library"


PROMPT_TEMPLATE = """Bạn là Growth Strategist của kênh TikTok "Tạp Hóa Pel Pel" (food/snack VN, giai đoạn 0→1K followers).

Nhiệm vụ: phân tích data kênh đối thủ @{author} và rút BÀI HỌC áp dụng được cho Pel Pel.

## INPUT 1: Thống kê tổng quan kênh

{summary}

## INPUT 2: Top video (CSV rút gọn)

{csv_preview}

{transcripts_block}

## YÊU CẦU OUTPUT

Viết phân tích tiếng Việt, markdown, cấu trúc như sau (giữ nguyên các heading):

### 🎯 Định vị kênh đối thủ
2-3 câu: họ là ai, bán content gì, tệp khán giả nào.

### 📊 Công thức viral của họ (từ data)
Liệt kê 5-8 pattern cụ thể. Mỗi pattern dạng bullet:
- **[Yếu tố]**: [pattern cụ thể với số liệu]. Ví dụ: `Caption ngắn <20 ký tự → 371K views avg`.

### 🧠 Bài học cho Pel Pel
5-7 bài học cụ thể, actionable. Mỗi bài học:
- **Bài học**: [tóm tắt 1 câu]
- **Cách áp dụng**: [câu cụ thể cho Pel Pel, có thể là 1 template hoặc quy tắc]
- **Dữ liệu hỗ trợ**: [reference đến số liệu trong input]

### ⚠️ Điểm yếu để TẤN CÔNG
3 điểm kênh này LÀM CHƯA TỐT → cơ hội cho Pel Pel differentiate.

### 🚀 Template action
3 template video Pel Pel nên thử NGAY trong 2 tuần tới, dựa trên pattern của họ. Format:
1. **Tên template**: [mô tả]
   - Duration, sound, caption, hashtag, posting time cụ thể
   - Lý do chọn (link đến data)

LƯU Ý:
- Dùng số liệu thật từ data, KHÔNG chế
- Actionable > diễn giải lý thuyết
- Nếu data không đủ để kết luận → nói rõ "chưa đủ data"
- Ngắn gọn, không lặp ý
"""


def load_summary(author: str) -> str:
    path = ANALYSIS_DIR / author / "summary.md"
    if not path.exists():
        raise SystemExit(f"Thiếu: {path}. Chạy analyze-channel.py trước.")
    return path.read_text(encoding="utf-8")


def load_csv_preview(author: str, top_n: int = 30) -> str:
    path = ANALYSIS_DIR / author / "videos_products.csv"
    if not path.exists():
        # Fallback videos.csv
        path = ANALYSIS_DIR / author / "videos.csv"
        if not path.exists():
            raise SystemExit(f"Thiếu: videos[_products].csv trong {path.parent}")

    with path.open(encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    # Sort by views desc
    def views_int(r):
        try: return int(r.get("views", 0))
        except: return 0
    rows.sort(key=views_int, reverse=True)

    # Chọn cột quan trọng, chỉ top N
    cols = ["views", "likes", "saves", "duration_sec", "upload_hour_vn", "weekday_vn",
            "is_original_sound", "music_title", "category", "subcategory", "brand", "caption"]
    # Filter cột thực sự có
    cols = [c for c in cols if c in rows[0]]

    lines = ["| " + " | ".join(cols) + " |",
             "|" + "|".join(["---"] * len(cols)) + "|"]
    for r in rows[:top_n]:
        vals = []
        for c in cols:
            v = str(r.get(c, ""))[:60]
            vals.append(v.replace("|", "/").replace("\n", " "))
        lines.append("| " + " | ".join(vals) + " |")

    return "\n".join(lines)


def load_transcripts(author: str, category: str | None) -> str:
    """Nếu có scene-library + transcripts cho kênh này (+ category) → gộp."""
    if category:
        search_dir = SCENE_LIB / category
    else:
        search_dir = SCENE_LIB

    if not search_dir.exists():
        return ""

    # Lọc file transcript thuộc kênh này (tên bắt đầu bằng <author>_)
    pattern = f"{author}_*.txt"
    txts = sorted(search_dir.rglob(pattern))
    if not txts:
        return ""

    entries = []
    for txt in txts:
        meta = txt.with_suffix(".json")
        try:
            with meta.open(encoding="utf-8") as f:
                m = json.load(f)
            cap = m.get("source_caption", "")
            views = m.get("source_views", "?")
            cat = m.get("category", "?")
        except Exception:
            cap, views, cat = "", "?", "?"

        text = txt.read_text(encoding="utf-8").strip()
        if text and text != "[NO_VOICE]":
            entries.append(f"**{txt.stem}** ({cat}, {views} views — \"{cap[:50]}\"):\n> {text}")

    if not entries:
        return ""

    header = f"## INPUT 3: Transcripts voiceover ({len(entries)} scene đã transcribe)\n\n"
    return header + "\n\n".join(entries[:30])  # max 30 để không nổ prompt


def call_gemini(prompt: str) -> str:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise SystemExit("Thiếu GEMINI_API_KEY trong .env")
    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(model=MODEL, contents=[prompt])
    return (response.text or "").strip()


def append_to_playbook(author: str, lessons_md: str, category: str | None):
    PLAYBOOK.parent.mkdir(parents=True, exist_ok=True)

    marker_start = f"<!-- BEGIN: {author}"
    if category:
        marker_start += f"/{category}"
    marker_start += " -->"
    marker_end = marker_start.replace("BEGIN", "END")

    ts = time.strftime("%Y-%m-%d")
    section = f"""
{marker_start}

## Bài học từ @{author}{f" — category `{category}`" if category else ""}

*Cập nhật: {ts}*

{lessons_md}

{marker_end}
"""

    if PLAYBOOK.exists():
        content = PLAYBOOK.read_text(encoding="utf-8")
        if marker_start in content:
            # Replace old section in-place
            pre, rest = content.split(marker_start, 1)
            _, post = rest.split(marker_end, 1)
            new = pre + section.strip() + post
        else:
            # Append
            new = content.rstrip() + "\n\n" + section.strip() + "\n"
        PLAYBOOK.write_text(new, encoding="utf-8")
    else:
        header = "# Pel Pel — Competitor Playbook\n\n"
        header += "_Gom bài học từ các kênh đối thủ đã phân tích._\n\n"
        header += "---\n"
        PLAYBOOK.write_text(header + section.strip() + "\n", encoding="utf-8")


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("author", help="Username TikTok (không @)")
    ap.add_argument("--category", default=None,
                    help="Focus vào 1 category (nếu có scene transcripts)")
    ap.add_argument("--no-playbook", action="store_true",
                    help="Chỉ ghi lessons.md, không update playbook tổng")
    args = ap.parse_args()

    author = args.author.lstrip("@")
    print(f"── Synthesize lessons: @{author} ─────────────────")

    summary = load_summary(author)
    csv_preview = load_csv_preview(author, top_n=30)
    transcripts = load_transcripts(author, args.category)

    print(f"  Summary   : {len(summary)} chars")
    print(f"  CSV       : {csv_preview.count(chr(10))} dòng")
    print(f"  Transcript: {len(transcripts)} chars")

    prompt = PROMPT_TEMPLATE.format(
        author=author,
        summary=summary,
        csv_preview=csv_preview,
        transcripts_block=transcripts or "## INPUT 3: Chưa có transcript\n",
    )

    print(f"  → Gọi Gemini ({MODEL}, prompt {len(prompt)} chars)...", flush=True)
    lessons = call_gemini(prompt)
    print(f"  ← Nhận {len(lessons)} chars response")

    # Ghi lessons.md
    out_dir = ANALYSIS_DIR / author
    out_dir.mkdir(parents=True, exist_ok=True)
    lessons_path = out_dir / "lessons.md"
    header = f"# Lessons Learned — @{author}\n\n"
    header += f"_Sinh bởi `synthesize-lessons.py` ({MODEL}) — {time.strftime('%Y-%m-%d %H:%M')}_\n\n"
    if args.category:
        header += f"Focus category: **{args.category}**\n\n"
    header += "---\n\n"
    lessons_path.write_text(header + lessons + "\n", encoding="utf-8")
    print(f"✓ Ghi: {lessons_path.relative_to(ROOT)}")

    if not args.no_playbook:
        append_to_playbook(author, lessons, args.category)
        print(f"✓ Cập nhật: {PLAYBOOK.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
