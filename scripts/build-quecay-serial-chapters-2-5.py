"""
Build Serial chương 2-5: "Mối tình đầu — Chương N"

Reuse helpers + render functions từ build-quecay-serial-chapter-1.py.
4 chapter configs trong CHAPTERS dict, loop chạy tuần tự.

Usage:
    python3 scripts/build-quecay-serial-chapters-2-5.py
    # hoặc chạy 1 chương:
    python3 scripts/build-quecay-serial-chapters-2-5.py --chapter 3
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CH1_SCRIPT = ROOT / "scripts" / "build-quecay-serial-chapter-1.py"

# Import chapter-1 module để reuse functions (file có dấu `-` nên dùng importlib)
spec = importlib.util.spec_from_file_location("ch1", CH1_SCRIPT)
ch1 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ch1)

PRODUCT_VIDEOS = ROOT / "assets" / "products" / "que-cay" / "videos"


CHAPTERS: dict[int, dict] = {
    2: {
        "first_sentence": "Kẻ ngây ngô là vũ khí giết tình yêu lạnh lùng nhất",
        "bg_video": PRODUCT_VIDEOS / "Spicy_Beef_Snack_Stick_ASMR_Video.mp4",
        "bg_start": 1.0,
        "segments": [
            {
                "name": "story_a",
                "text_voice":    "Chúng tôi buông tay khi trái tim vẫn nguyên hình bóng nhau, vì rào cản tôn giáo sừng sững như ngọn núi.",
                "text_subtitle": "Buông tay vì rào cản tôn giáo sừng sững",
                "keywords":      ["hangdai", "hằng đại"],
                "prefer_views":  2_000_000,
            },
            {
                "name": "story_b",
                "text_voice":    "Nhưng kẻ có lỗi là chính tôi — hèn nhát cúi đầu, lờ đi mọi khúc mắc, đánh mất người tôi thương nhất.",
                "text_subtitle": "Tôi hèn nhát, đánh mất người tôi thương nhất",
                "keywords":      ["thần long", "than long", "to dài"],
                "prefer_views":  1_000_000,
            },
            {
                "name": "cta",
                "text_voice":    "Tôi đã trốn chạy thế nào? Phần 3 — Follow xem tiếp.",
                "text_subtitle": "Tôi trốn chạy thế nào? Follow xem Phần 3",
                "keywords":      ["quecay", "ngon"],
                "prefer_views":  500_000,
            },
        ],
    },

    3: {
        "first_sentence": "Khi tình khép lại, kỷ vật chỉ còn vô hồn",
        "bg_video": PRODUCT_VIDEOS / "Video_Thịt_Bò_Cay_Rơi_Xuống_Đĩa.mp4",
        "bg_start": 0.5,
        "segments": [
            {
                "name": "story_a",
                "text_voice":    "Tôi tự tay vùi lấp những sở thích từng là thế giới rực rỡ của hai đứa, để trốn chạy kỷ niệm.",
                "text_subtitle": "Tự tay vùi lấp thế giới rực rỡ của hai đứa",
                "keywords":      ["hangdai", "hằng đại"],
                "prefer_views":  2_000_000,
            },
            {
                "name": "story_b",
                "text_voice":    "Trekking, phòng gym, tất cả giờ chỉ là dĩ vãng — chỉ còn nghĩa vụ tẻ nhạt, trống rỗng niềm vui.",
                "text_subtitle": "Tất cả thành dĩ vãng, trống rỗng niềm vui",
                "keywords":      ["thần long", "than long", "to dài"],
                "prefer_views":  1_000_000,
            },
            {
                "name": "cta",
                "text_voice":    "Có một câu hỏi tôi chưa từng dám đối diện. Phần 4 — Follow xem.",
                "text_subtitle": "Câu hỏi tôi chưa từng dám đối diện — Phần 4",
                "keywords":      ["quecay", "ngon"],
                "prefer_views":  500_000,
            },
        ],
    },

    4: {
        "first_sentence": "Một câu hỏi đâm toạc lý tính của tôi",
        "bg_video": PRODUCT_VIDEOS / "Video_ASMR_đồ_ăn_sẵn_sàng.mp4",
        "bg_start": 0.5,
        "segments": [
            {
                "name": "story_a",
                "text_voice":    "Sao không đến tận nơi gặp người ta? Câu gặng nhẹ từ người ngoài cuộc khiến tôi chết lặng.",
                "text_subtitle": "Sao không đến tận nơi gặp người ta?",
                "keywords":      ["hangdai", "hằng đại"],
                "prefer_views":  2_000_000,
            },
            {
                "name": "story_b",
                "text_voice":    "Hóa ra tôi chỉ giải quyết qua tin nhắn vô cảm, quên rằng tình yêu cần hơi ấm và bản lĩnh.",
                "text_subtitle": "Tình yêu cần hơi ấm và bản lĩnh — tôi không có",
                "keywords":      ["thần long", "than long", "to dài"],
                "prefer_views":  1_000_000,
            },
            {
                "name": "cta",
                "text_voice":    "Cái giá tôi phải trả là gì? Phần 5 — Final, Follow xem cuối cùng.",
                "text_subtitle": "Cái giá là gì? Phần 5 Final — Follow",
                "keywords":      ["quecay", "ngon"],
                "prefer_views":  500_000,
            },
        ],
    },

    5: {
        "first_sentence": "Thành công nhân đôi, lòng vẫn trống không",
        "bg_video": PRODUCT_VIDEOS / "Video_Sẵn_Sàng_Radial_Bloom.mp4",
        "bg_start": 0.5,
        "segments": [
            {
                "name": "story_a",
                "text_voice":    "Khối lượng công việc tăng gấp ba, đêm dài thức trắng — sự thăng tiến đến vượt xa trước kia.",
                "text_subtitle": "Việc gấp ba, thăng tiến vượt xa trước kia",
                "keywords":      ["hangdai", "hằng đại"],
                "prefer_views":  2_000_000,
            },
            {
                "name": "story_b",
                "text_voice":    "Nhưng đó không phải tự hào — chỉ là bức tường tôi xây để giam mình, che đậy một sự thật.",
                "text_subtitle": "Bức tường tôi xây để giam chính mình",
                "keywords":      ["thần long", "than long", "to dài"],
                "prefer_views":  1_000_000,
            },
            {
                "name": "cta",
                "text_voice":    "Tôi vẫn đang thiếu vắng một người mãi không thuộc về mình. Cảm ơn đã theo dõi — Follow xem chuyện tiếp theo.",
                "text_subtitle": "Cảm ơn đã theo dõi. Follow xem chuyện tiếp",
                "keywords":      ["quecay", "ngon"],
                "prefer_views":  500_000,
            },
        ],
    },
}

CAPTION_HASHTAGS = "#tamsudemkhuya #moitinhdau #review #quecay #anvattuoitho #kechuyendem #pelpel"


def build_chapter(num: int, cfg: dict) -> Path:
    """Build 1 chương dùng helpers từ ch1 module."""
    print(f"\n{'='*60}\n── Build Serial chương {num} ──\n{'='*60}")

    first_sent = cfg["first_sentence"]
    caption = f"{first_sent} {CAPTION_HASHTAGS}"
    final_name = f"{caption}.mp4"

    tmp_dir = ROOT / "assets" / "products" / "que-cay" / "output" / f"_tmp_serial_ch{num}"
    final_dir = ROOT / "assets" / "products" / "que-cay" / "output" / "final"
    final_dir.mkdir(parents=True, exist_ok=True)
    tmp_dir.mkdir(parents=True, exist_ok=True)

    # Render label + badge
    label_png = tmp_dir / "label.png"
    badge_png = tmp_dir / "badge.png"
    ch1.render_label_png(ch1.LABEL_TEXT, label_png)
    ch1.render_series_badge_png(f"#{num}", badge_png)

    # Build segments list (thumbnail + story_a + story_b + cta)
    segments = [
        {
            "type": "thumbnail_video",
            "name": "thumbnail",
            "text_voice":    first_sent,
            "text_subtitle": None,
            "thumbnail_text": first_sent,
            "bg_video":      cfg["bg_video"],
            "bg_video_start": cfg.get("bg_start", 0.5),
            "duration":      4.0,
        },
    ] + [{**s, "type": "scene"} for s in cfg["segments"]]

    # 1. TTS per segment
    print(f"[1/4] TTS rate {ch1.TTS_RATE}...")
    silent_mode = False
    for i, seg in enumerate(segments, 1):
        voice_path = ch1.tts(seg["text_voice"], tmp_dir, i)
        if voice_path is None:
            silent_mode = True
            seg["voice_path"] = None
            seg["voice_dur"] = seg.get("duration", 4.0)
            print(f"  [{i}] silent {seg['voice_dur']}s — \"{seg['text_voice'][:50]}\"")
        else:
            seg["voice_path"] = voice_path
            seg["voice_dur"] = ch1.audio_duration(voice_path)
            print(f"  [{i}] {seg['voice_dur']:.2f}s — \"{seg['text_voice'][:50]}\"")

    # 2. Build clips
    print(f"[2/4] Build clips...")
    scenes = ch1.load_scenes()
    used_ids = set()
    clip_paths = []

    for i, seg in enumerate(segments, 1):
        stage_final = tmp_dir / f"clip_{i:02d}_final.mp4"

        if seg.get("type") == "thumbnail_video":
            bg = seg["bg_video"]
            start = seg.get("bg_video_start", 0)
            stage_bg = tmp_dir / f"clip_{i:02d}_bg.mp4"
            ch1.standardize_portrait_from(bg, start, seg["voice_dur"], stage_bg)

            text_png = tmp_dir / f"thumb_text_{i:02d}.png"
            ch1.render_thumbnail_text_overlay(seg["thumbnail_text"], text_png)

            ch1.run([
                "ffmpeg", "-y",
                "-i", str(stage_bg),
                "-i", str(label_png),
                "-i", str(text_png),
                "-i", str(badge_png),
                "-filter_complex",
                (f"[0:v][1:v]overlay=(main_w-overlay_w)/2:{ch1.LABEL_Y}[v1];"
                 f"[v1][2:v]overlay=0:0[v2];"
                 f"[v2][3:v]overlay={ch1.SERIES_BADGE_X}:{ch1.SERIES_BADGE_Y}[vo]"),
                "-map", "[vo]",
                "-c:v", "libx264", "-preset", "fast", "-crf", "21",
                "-pix_fmt", "yuv420p", "-an",
                str(stage_final),
            ])
            print(f"  [{i}] {seg['name']:10s} thumb BG={bg.name} ({seg['voice_dur']:.2f}s)")

        else:
            pick = ch1.pick_scene(scenes, seg["keywords"], seg["voice_dur"],
                                   seg["prefer_views"], used_ids)
            if not pick:
                raise SystemExit(f"Không pick được scene cho seg {i}")
            used_ids.add(pick["_id_key"])
            mp4 = pick["_mp4_path"]
            print(f"  [{i}] {seg['name']:10s} ← {mp4.name} ({pick.get('source_views'):,}v → {seg['voice_dur']:.2f}s)")

            stage1 = tmp_dir / f"clip_{i:02d}_raw.mp4"
            ch1.standardize_portrait(mp4, seg["voice_dur"], stage1)

            sub_png = tmp_dir / f"sub_{i:02d}.png"
            ch1.render_subtitle_png(seg["text_subtitle"], sub_png)
            ch1.overlay_label_subtitle_badge(stage1, label_png, sub_png, badge_png, stage_final)

            seg["picked_source"] = str(mp4.relative_to(ROOT))

        clip_paths.append(stage_final)

    # 3. Concat + audio
    print(f"[3/4] Concat...")
    concat_v = tmp_dir / "concat_video.mp4"
    listf = tmp_dir / "concat_v.txt"
    listf.write_text("\n".join(f"file '{p.resolve()}'" for p in clip_paths))
    ch1.run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(listf),
             "-c", "copy", str(concat_v)])

    final_path = final_dir / final_name
    if silent_mode:
        ch1.run(["ffmpeg", "-y", "-i", str(concat_v),
                 "-c", "copy", "-movflags", "+faststart", str(final_path)])
    else:
        concat_a = tmp_dir / "concat_audio.mp3"
        listf_a = tmp_dir / "concat_a.txt"
        listf_a.write_text("\n".join(f"file '{s['voice_path'].resolve()}'" for s in segments))
        ch1.run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(listf_a),
                 "-c:a", "libmp3lame", "-q:a", "2", str(concat_a)])
        ch1.run(["ffmpeg", "-y", "-i", str(concat_v), "-i", str(concat_a),
                 "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
                 "-movflags", "+faststart", str(final_path)])

    # Meta
    total_dur = sum(s["voice_dur"] for s in segments)
    meta = {
        "caption": caption,
        "series_name": ch1.SERIES_NAME,
        "chapter_num": num,
        "total_duration": total_dur,
        "silent_mode": silent_mode,
        "segments": [
            {"idx": i, "name": s["name"], "voice_dur": s["voice_dur"],
             "text_voice": s["text_voice"], "text_subtitle": s.get("text_subtitle"),
             "picked_scene": s.get("picked_source")}
            for i, s in enumerate(segments, 1)
        ],
    }
    (final_dir / f"{final_name}.meta.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"\n✓ Chương {num}: {total_dur:.2f}s")
    print(f"  → {final_path.relative_to(ROOT)}")
    return final_path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--chapter", type=int, choices=[2, 3, 4, 5], default=None,
                    help="Build chương cụ thể, mặc định build cả 2-5")
    args = ap.parse_args()

    chapters = [args.chapter] if args.chapter else [2, 3, 4, 5]
    results = []
    for n in chapters:
        try:
            p = build_chapter(n, CHAPTERS[n])
            results.append((n, p))
        except Exception as e:
            print(f"\n✗ Chương {n} fail: {e}")

    print(f"\n{'='*60}\n✓ Đã build {len(results)} chương:\n{'='*60}")
    for n, p in results:
        print(f"  Chương {n}: {p.name}")


if __name__ == "__main__":
    main()
