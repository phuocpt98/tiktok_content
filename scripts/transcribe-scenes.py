"""
Transcribe voiceover trong scene MP4 thành text tiếng Việt, dùng Gemini.

Usage:
  # 1 file
  python scripts/transcribe-scenes.py assets/scene-library/que_cay/beheobu0102_xxx_scene_01.mp4

  # Cả folder
  python scripts/transcribe-scenes.py assets/scene-library/que_cay/

  # Force re-transcribe (bỏ skip)
  python scripts/transcribe-scenes.py <path> --force

Output:
  Bên cạnh mỗi .mp4 sinh ra:
    <name>.txt            transcript tiếng Việt
    <name>.transcript.json  {text, model, timestamp, ...}

  Cập nhật <name>.json (scene metadata): thêm key "transcript_preview".

Yêu cầu:
  - .env có GEMINI_API_KEY
  - pip install google-genai python-dotenv
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")

try:
    from google import genai
    from google.genai import types
except ImportError:
    raise SystemExit("Thiếu google-genai. Cài: pip install --user google-genai")

MODEL = "gemini-2.5-flash"  # support audio/video, free tier tốt

PROMPT = """Bạn là tool transcribe voiceover trong video TikTok tiếng Việt.

Nhiệm vụ:
1. Nghe audio của video này
2. Ghi lại CHÍNH XÁC lời thoại (voiceover, narration, hát) bằng tiếng Việt
3. Bỏ qua: nhạc nền không lời, tiếng động tự nhiên (xèo xèo, crunch...), tiếng ASMR không có từ

Định dạng output:
- Chỉ ghi text thoại, KHÔNG giải thích, KHÔNG comment
- Nếu không có lời thoại nào → trả về chính xác chuỗi: [NO_VOICE]
- Nếu chỉ có vài từ rời rạc → ghi lại nguyên văn các từ đó
- Giữ nguyên phong cách nói (teen, lóng, emoji được đọc lên)"""


def get_client(key_index: int = 0):
    keys = [os.getenv("GEMINI_API_KEY"), os.getenv("GEMINI_API_KEY_2")]
    keys = [k for k in keys if k]
    if not keys:
        raise SystemExit("Không tìm thấy GEMINI_API_KEY trong .env")
    if key_index >= len(keys):
        raise SystemExit("Hết key để retry")
    return genai.Client(api_key=keys[key_index])


def transcribe_one(mp4: Path, force: bool = False) -> str | None:
    """Trả transcript, hoặc None nếu skip."""
    mp4 = mp4.resolve()
    txt_path = mp4.with_suffix(".txt")
    jsonlog = mp4.with_suffix(".transcript.json")

    if txt_path.exists() and not force:
        print(f"  ⊙ {mp4.name} — skip (đã có .txt)")
        return None

    # Thử key #1, nếu rate-limit chuyển key #2
    last_err = None
    for key_idx in range(2):
        try:
            client = get_client(key_idx)
            uploaded = client.files.upload(file=str(mp4))

            # Đợi file ready (Gemini sometimes needs PROCESSING → ACTIVE)
            for _ in range(30):
                state = client.files.get(name=uploaded.name).state
                state_name = state.name if hasattr(state, "name") else str(state)
                if state_name == "ACTIVE":
                    break
                if state_name == "FAILED":
                    raise RuntimeError(f"File upload failed: {mp4.name}")
                time.sleep(1)

            response = client.models.generate_content(
                model=MODEL,
                contents=[PROMPT, uploaded],
            )
            text = (response.text or "").strip()

            # Dọn file đã upload (có hạn 48h tự xoá, nhưng dọn sớm cho sạch)
            try:
                client.files.delete(name=uploaded.name)
            except Exception:
                pass

            # Save outputs
            txt_path.write_text(text, encoding="utf-8")
            log = {
                "file": str(mp4.relative_to(ROOT)),
                "model": MODEL,
                "key_index": key_idx,
                "transcribed_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
                "length_chars": len(text),
                "text": text,
            }
            jsonlog.write_text(json.dumps(log, ensure_ascii=False, indent=2), encoding="utf-8")

            # Cập nhật metadata scene nếu có
            meta_path = mp4.with_suffix(".json")
            if meta_path.exists():
                try:
                    with meta_path.open(encoding="utf-8") as f:
                        meta = json.load(f)
                    meta["transcript_preview"] = text[:200]
                    meta["has_voice"] = text != "[NO_VOICE]" and bool(text)
                    with meta_path.open("w", encoding="utf-8") as f:
                        json.dump(meta, f, ensure_ascii=False, indent=2)
                except Exception:
                    pass

            return text

        except Exception as e:
            last_err = e
            err_str = str(e).lower()
            if "rate" in err_str or "quota" in err_str or "429" in err_str:
                print(f"  ⚠ key #{key_idx}: rate-limit, chuyển key khác")
                continue
            raise

    raise RuntimeError(f"Transcribe fail sau khi thử hết key: {last_err}")


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("input", type=Path, help="File .mp4 hoặc folder chứa .mp4")
    ap.add_argument("--force", action="store_true", help="Re-transcribe ngay cả nếu đã có .txt")
    ap.add_argument("--sleep", type=float, default=1.0,
                    help="Delay giữa 2 request (default 1s, tránh rate-limit)")
    args = ap.parse_args()

    if args.input.is_file():
        files = [args.input]
    elif args.input.is_dir():
        files = sorted(args.input.glob("*.mp4"))
    else:
        raise SystemExit(f"Input không hợp lệ: {args.input}")

    if not files:
        raise SystemExit("Không tìm thấy .mp4")

    print(f"── Transcribe scenes với Gemini ─────────────────")
    print(f"Files   : {len(files)}")
    print(f"Model   : {MODEL}")
    print(f"──────────────────────────────────────────────────")

    ok, skipped, failed = 0, 0, 0
    for i, mp4 in enumerate(files, 1):
        print(f"[{i}/{len(files)}] {mp4.name}", flush=True)
        try:
            text = transcribe_one(mp4, args.force)
            if text is None:
                skipped += 1
            else:
                preview = text[:80].replace("\n", " ")
                print(f"  ✓ {len(text)} chars | {preview}")
                ok += 1
                if i < len(files):
                    time.sleep(args.sleep)
        except Exception as e:
            print(f"  ✗ {e}")
            failed += 1

    print(f"\n✓ OK {ok} | ⊙ Skip {skipped} | ✗ Fail {failed}")


if __name__ == "__main__":
    main()
