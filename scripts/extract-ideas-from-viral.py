"""
Extract content ideas từ top-N video viral nhất của 1 kênh đối thủ.

Khác với synthesize-lessons.py:
  - KHÔNG dùng scene-library (không tách scene)
  - Transcribe TRỌN VẸN video gốc (1 transcript/video)
  - Output chỉ focus vào CONTENT IDEAS actionable, không framework tổng

Flow:
  1. Đọc videos_products.csv → filter --category (opt) + sort by views
  2. Top N video (--top)
  3. Với mỗi MP4 có sẵn trong assets/raw/tiktok/<author>/: transcribe full qua Gemini
  4. Build prompt giàu: caption + hashtag + music + voiceover text cho N video
  5. Gemini text → sinh section markdown "Ideas viral từ @<author> — <category>"
  6. Append vào `assets/content-ideas/<author>_<category>_ideas.md`

Usage:
  # Top 5 video que_cay của @beheobu0102
  python scripts/extract-ideas-from-viral.py beheobu0102 --category que_cay --top 5

  # Top 10 không filter category
  python scripts/extract-ideas-from-viral.py beheobu0102 --top 10

Yêu cầu:
  - .env có GEMINI_API_KEY
  - Đã chạy analyze-channel.py + extract-products.py
  - MP4 đã có trong assets/raw/tiktok/<author>/ (ingest-tiktok.py trước đó)
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
ANALYSIS_DIR = ROOT / "assets" / "analysis" / "tiktok"
RAW_DIR = ROOT / "assets" / "raw" / "tiktok"
IDEAS_DIR = ROOT / "assets" / "content-ideas"


TRANSCRIBE_PROMPT = """Nghe voiceover của video TikTok này. Ghi lại toàn bộ lời nói bằng tiếng Việt.

Quy tắc:
- CHỈ ghi text thoại (voiceover, lời creator). Bỏ qua tiếng nhạc nền, sound effects (xèo xèo, crunch).
- Nếu không có lời thoại nào → trả về: [NO_VOICE]
- Giữ nguyên từ ngữ gốc (teen, lóng, vùng miền, thán từ "chu choa", "má ưi", v.v.)
- Không thêm giải thích, không comment. Chỉ text."""


IDEAS_PROMPT = """Bạn là Content Strategist cho kênh TikTok "Tạp Hóa Pel Pel" (food/snack VN, giai đoạn 0→1K followers).

Nhiệm vụ: từ {n} video VIRAL của kênh đối thủ @{author} dưới đây, rút ra CONTENT IDEAS cụ thể cho Pel Pel tái sử dụng (với biến thể để khác biệt).

## Data của {n} video viral nhất (category: {category})

{videos_block}

## YÊU CẦU OUTPUT

Viết markdown tiếng Việt, cấu trúc:

### 🎬 Hook patterns (3 giây đầu)
Liệt kê 5-7 hook mở video cụ thể mà top video dùng. Mỗi hook:
- "Câu hook" — [views ref]
- Cách Pel Pel biến thể (thay từ/sản phẩm để khác biệt)

### 🗣️ Voice & delivery
- Tone: (từ data — ví dụ: nhõng nhẽo, hài, nostalgic)
- Cadence: (nhanh/chậm, dùng từ đệm nào)
- Thán từ / emoji xuất hiện nhiều

### 📝 Caption templates
5-8 caption template sẵn dùng, mỗi cái:
- Template: `"..."` — mô phỏng video [views ref]
- Khi dùng: [tình huống nào phù hợp]

### 🎯 Product angles (cách giới thiệu sản phẩm)
Từ transcript, rút ra các **góc tiếp cận** đối thủ dùng để giới thiệu sản phẩm:
- Angle 1: [tên] — ví dụ "Nhấn mạnh kích thước to dài"
  - Dùng khi: ...
  - Pel Pel template: "..."

### 🚀 3 Video ideas ĐẶC BIỆT đáng làm ngay cho Pel Pel
3 video cụ thể để gen ngay, dựa trên data:
1. **Tên**: [mô tả]
   - Hook: "..."
   - Body: [timing + action]
   - Caption: "..."
   - Hashtag: [list]
   - Lý do (link data): "..."

LƯU Ý:
- Chỉ dùng phát hiện thực từ data, KHÔNG chế
- Mỗi template PHẢI có reference views/video nguồn để tra ngược
- Ngắn gọn, actionable
- Nếu video không có voiceover (transcript [NO_VOICE]) → ghi rõ "caption/visual-only"
"""


# ── Helpers ────────────────────────────────────────────────────────────────

def get_client():
    key = os.getenv("GEMINI_API_KEY")
    if not key:
        raise SystemExit("Thiếu GEMINI_API_KEY trong .env")
    return genai.Client(api_key=key)


def transcribe_full_video(client, mp4: Path) -> str:
    """Transcribe trọn video, trả về text tiếng Việt (hoặc '[NO_VOICE]')."""
    uploaded = client.files.upload(file=str(mp4))
    # Wait ACTIVE
    for _ in range(30):
        st = client.files.get(name=uploaded.name).state
        st_name = st.name if hasattr(st, "name") else str(st)
        if st_name == "ACTIVE":
            break
        if st_name == "FAILED":
            raise RuntimeError(f"Upload failed: {mp4.name}")
        time.sleep(1)

    response = client.models.generate_content(
        model=MODEL,
        contents=[TRANSCRIBE_PROMPT, uploaded],
    )
    text = (response.text or "").strip()

    try:
        client.files.delete(name=uploaded.name)
    except Exception:
        pass

    return text or "[NO_VOICE]"


def load_top_videos(author: str, category: str | None, top_n: int) -> list[dict]:
    csv_path = ANALYSIS_DIR / author / "videos_products.csv"
    if not csv_path.exists():
        raise SystemExit(f"Thiếu: {csv_path}. Chạy analyze-channel + extract-products trước.")

    with csv_path.open(encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    if category:
        rows = [r for r in rows if r.get("category") == category]

    def to_int(x):
        try: return int(x)
        except: return 0
    rows.sort(key=lambda r: to_int(r.get("views", 0)), reverse=True)
    return rows[:top_n]


def format_video_block(idx: int, row: dict, transcript: str) -> str:
    return f"""### Video #{idx}: {row.get('views', '?')} views
- **Duration**: {row.get('duration_sec', '?')}s
- **ER**: {row.get('engagement_rate_pct', '?')}%
- **Music**: {row.get('music_title', '?')} (original={row.get('is_original_sound', '?')})
- **Hour / Day**: {row.get('upload_hour_vn', '?')}h / {row.get('weekday_vn', '?')}
- **Category/Subcategory**: {row.get('category', '?')} / {row.get('subcategory', '')}
- **Brand**: {row.get('brand', '(không có)')}
- **Caption**: {row.get('caption', '')}
- **Hashtags**: {row.get('hashtags', '')}
- **Voiceover transcript**:
  > {transcript}
"""


def save_transcript(mp4: Path, text: str) -> None:
    """Lưu transcript cạnh MP4 để reuse lần sau."""
    mp4.with_suffix(".voiceover.txt").write_text(text, encoding="utf-8")


def load_cached_transcript(mp4: Path) -> str | None:
    cache = mp4.with_suffix(".voiceover.txt")
    if cache.exists():
        return cache.read_text(encoding="utf-8").strip()
    return None


# ── Main ───────────────────────────────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("author", help="Username TikTok (không @)")
    ap.add_argument("--category", default=None, help="Filter category (que_cay, snack, ...)")
    ap.add_argument("--top", type=int, default=5, help="Số video viral cần phân tích (default 5)")
    ap.add_argument("--out", type=Path, default=None,
                    help="File output .md (default: assets/content-ideas/<author>_<cat>_ideas.md)")
    ap.add_argument("--force-transcribe", action="store_true",
                    help="Bỏ qua cache transcript, transcribe lại")
    args = ap.parse_args()

    author = args.author.lstrip("@")
    raw_dir = RAW_DIR / author
    if not raw_dir.exists():
        raise SystemExit(f"Thiếu folder raw: {raw_dir}. Ingest MP4 trước.")

    print(f"── Extract ideas từ top {args.top} viral @{author} ────")
    if args.category:
        print(f"Category filter: {args.category}")

    top_rows = load_top_videos(author, args.category, args.top)
    print(f"Loaded {len(top_rows)} top video:")
    for i, r in enumerate(top_rows, 1):
        v = r.get("views", "?")
        cap = r.get("caption", "")[:60]
        print(f"  {i}. {v:>9}v — {cap}")

    # Transcribe each
    client = get_client()
    video_blocks = []
    missing_mp4 = []

    for i, row in enumerate(top_rows, 1):
        vid_id = row.get("id")
        mp4 = raw_dir / f"{vid_id}.mp4"
        if not mp4.exists():
            missing_mp4.append(vid_id)
            print(f"  [{i}/{len(top_rows)}] ⚠ {vid_id}.mp4 MISSING — skip")
            continue

        cached = None if args.force_transcribe else load_cached_transcript(mp4)
        if cached is not None:
            text = cached
            print(f"  [{i}/{len(top_rows)}] ⊙ {vid_id} — cached transcript ({len(text)} chars)")
        else:
            print(f"  [{i}/{len(top_rows)}] → {vid_id} — transcribing...", flush=True)
            try:
                text = transcribe_full_video(client, mp4)
                save_transcript(mp4, text)
                time.sleep(1)
            except Exception as e:
                print(f"    ✗ fail: {e}")
                text = "[TRANSCRIBE_FAILED]"

        video_blocks.append(format_video_block(i, row, text))

    if not video_blocks:
        raise SystemExit("Không có video nào xử lý được.")

    # Synthesize ideas
    print(f"\n→ Gemini synthesize ideas từ {len(video_blocks)} video...", flush=True)
    prompt = IDEAS_PROMPT.format(
        n=len(video_blocks),
        author=author,
        category=args.category or "mixed",
        videos_block="\n\n".join(video_blocks),
    )
    response = client.models.generate_content(model=MODEL, contents=[prompt])
    ideas_md = (response.text or "").strip()
    print(f"← Received {len(ideas_md)} chars")

    # Write output
    IDEAS_DIR.mkdir(parents=True, exist_ok=True)
    out_path = args.out or (IDEAS_DIR / f"{author}_{args.category or 'all'}_ideas.md")
    header = f"# Ideas viral từ @{author}"
    if args.category:
        header += f" — category `{args.category}`"
    header += f"\n\n_Sinh từ top {len(video_blocks)} video (sắp theo views) — {MODEL} — {time.strftime('%Y-%m-%d %H:%M')}_\n\n"
    header += "_Nguồn data: `assets/analysis/tiktok/{}/videos_products.csv`_\n\n---\n\n".format(author)
    out_path.write_text(header + ideas_md + "\n", encoding="utf-8")

    print(f"\n✓ Ghi: {out_path.relative_to(ROOT)}")
    if missing_mp4:
        print(f"⚠ {len(missing_mp4)} video thiếu MP4 (skipped): {missing_mp4[:5]}...")


if __name__ == "__main__":
    main()
