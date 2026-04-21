#!/usr/bin/env python3
import asyncio
import json
import os
import subprocess
import time
import random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from gtts import gTTS

# --- CONFIGURATION ---
ROOT = Path(__file__).resolve().parent.parent
PRODUCT_SLUG = "keo-sua-deku"
SCENE_LIB = ROOT / "assets" / "products" / PRODUCT_SLUG / "competitor-scenes"
SFX_DIR = ROOT / "assets" / "audio" / "sfx"
OUTPUT_DIR = ROOT / "assets" / "products" / PRODUCT_SLUG / "output"
FINAL_DIR = OUTPUT_DIR / "final"

LABEL_TEXT = "KẸO DEKU • PEL PEL"
LABEL_Y = 280

VIDEOS_DATA = [
    {
        "id": "v8_mom_drama_fixed",
        "caption": "Mẹ bảo lớn rồi còn ăn kẹo, và cái kết cực sốc sau 3 giây 🍬 #keodeku #funny #momlife #pelpel #xuhuong",
        "segments": [
            {"text": "Nhìn tui ôm hũ kẹo Deku, mẹ tui mắng: Lớn tướt xác rồi mà còn ăn kẹo như con nít!", "subtitle": "Lớn rồi còn ăn kẹo sữa??", "kw": ["mắng", "mẹ", "hũ"], "sfx": "clean_rustle.mp3", "vol": 0.6},
            {"text": "Ấy thế mà mời mẹ thử một viên xong, mẹ chiếm luôn cái hũ rồi ngồi cày phim luôn mới ghê chứ.", "subtitle": "Mời mẹ thử 1 viên... và cái kết!", "kw": ["ăn", "nhai", "viên"], "sfx": "clean_crunch.mp3", "vol": 0.9},
            {"text": "Đúng là kẹo nén sữa chua Deku, sức mạnh không thể chối từ. Link ở giỏ hàng nha cả nhà!", "subtitle": "Sức mạnh không thể chối từ — Chốt đơn ngay!", "kw": ["đổ", "hũ", "nhiều"], "sfx": None, "vol": 0.5}
        ]
    },
    {
        "id": "v9_crush_bait_fixed",
        "caption": "Tuyệt chiêu 'thả thính' bằng kẹo sữa chua Deku - Đổ 100% 🍓 #keodeku #crush #trending #pelpel #valentine",
        "segments": [
            {"text": "Muốn tán đổ crush mà nhát quá không dám nói gì? Thử 'vô tình' đưa hũ kẹo Deku này ra xem.", "subtitle": "Tuyệt chiêu tán đổ crush!", "kw": ["đưa", "unbox", "hồng"], "sfx": "clean_rustle.mp3", "vol": 0.5},
            {"text": "Cái màu pastel ngọt ngào này cộng với vị béo ngậy của sữa chua thì ai mà chịu cho thấu.", "subtitle": "Màu pastel cưng xỉu — Vị cực cuốn!", "kw": ["cận cảnh", "viên"], "sfx": "clean_crunch.mp3", "vol": 0.8},
            {"text": "Tag ngay crush vào đây để 'đánh dấu chủ quyền' đi nào. Giỏ hàng Pel Pel chờ bạn nha!", "subtitle": "Tag crush vào đây ra tín hiệu đi!", "kw": ["hũ", "nhiều"], "sfx": None, "vol": 0.4}
        ]
    }
]

def run(cmd):
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def find_vi_font(size: int) -> ImageFont.FreeTypeFont:
    for p in ["/System/Library/Fonts/Supplemental/Arial Unicode.ttf", "/System/Library/Fonts/HelveticaNeue.ttc"]:
        if Path(p).exists(): return ImageFont.truetype(p, size)
    return ImageFont.load_default()

def render_png(text, out, is_label=True):
    if is_label:
        img = Image.new("RGBA", (900, 140), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        draw.rounded_rectangle([(0, 0), (899, 139)], radius=70, fill=(255, 107, 0, 220))
        font = find_vi_font(58)
        bbox = draw.textbbox((0, 0), text, font=font)
        draw.text(((900-(bbox[2]-bbox[0]))//2, (140-(bbox[3]-bbox[1]))//2-bbox[1]), text, font=font, fill=(255, 255, 255, 255), stroke_width=3, stroke_fill=(0, 0, 0, 255))
    else:
        img = Image.new("RGBA", (1000, 200), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        font = find_vi_font(62)
        draw.rounded_rectangle([(20, 50), (980, 170)], radius=25, fill=(0, 0, 0, 180))
        bbox = draw.textbbox((0, 0), text, font=font)
        draw.text(((1000-(bbox[2]-bbox[0]))//2, (200-(bbox[3]-bbox[1]))//2-bbox[1]), text, font=font, fill=(255, 255, 255, 255), stroke_width=2, stroke_fill=(0, 0, 0, 255))
    img.save(out, "PNG")

def generate_voice_gtts(text, out_path):
    """Sử dụng Google TTS cực kỳ ổn định."""
    print(f"   🎙 Gen Voice (gTTS): {text[:30]}...")
    tts = gTTS(text=text, lang='vi')
    tts.save(str(out_path))
    if not out_path.exists() or out_path.stat().st_size < 1000:
        raise RuntimeError("Google TTS failed to produce audio content.")

def get_dur(p):
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", str(p)], capture_output=True, text=True).stdout.strip() or 0)

def load_all_scenes():
    scenes = []
    for jf in sorted(SCENE_LIB.rglob("*.json")):
        try:
            with jf.open() as f: data = json.load(f)
            mp4 = jf.with_suffix(".mp4")
            if mp4.exists():
                data["_mp4_path"] = mp4
                scenes.append(data)
        except: continue
    return scenes

def pick_suitable_scenes(all_scenes, required_dur, used_ids, keywords):
    candidates = []
    for s in all_scenes:
        sid = f"{s.get('source_video_id')}_{s.get('scene_index')}"
        if sid in used_ids: continue
        caption = (s.get("source_caption") or "").lower()
        score = sum(1 for k in keywords if k.lower() in caption)
        candidates.append((score, s))
    candidates.sort(key=lambda x: x[0], reverse=True)
    picked, current_dur = [], 0.0
    source_list = [c[1] for c in candidates] if candidates else all_scenes
    for s in source_list:
        sid = f"{s.get('source_video_id')}_{s.get('scene_index')}"
        if sid in used_ids: continue
        picked.append(s["_mp4_path"])
        used_ids.add(sid)
        current_dur += s.get("duration_sec", 0)
        if current_dur >= required_dur: break
    return picked

def build_segment_video(paths, dur, label_png, sub_png, out, i, total_segments):
    num_paths = len(paths)
    filter_parts = []
    for j in range(num_paths):
        filter_parts.append(f"[{j}:v]scale=-1:1920:force_original_aspect_ratio=increase,crop=1080:1920:(iw-1080)/2:0,setsar=1,fps=30[v{j}];")
    inputs_labels = "".join(f"[v{j}]" for j in range(num_paths))
    filter_parts.append(f"{inputs_labels}concat=n={num_paths}:v=1:a=0[vcat];")
    label_idx, sub_idx = num_paths, num_paths + 1
    final_filter = f"fade=t=out:st={round(dur-0.2, 2)}:d=0.2" if i < total_segments else "null"
    filter_parts.append(f"[vcat][{label_idx}:v]overlay=(main_w-overlay_w)/2:{LABEL_Y}[v_lab];[v_lab][{sub_idx}:v]overlay=(main_w-overlay_w)/2:1580[v_sub];[v_sub]{final_filter}[vo]")
    cmd = ["ffmpeg", "-y"]
    for p in paths: cmd.extend(["-i", str(p)])
    cmd.extend(["-i", str(label_png), "-i", str(sub_png), "-t", str(dur), "-filter_complex", "".join(filter_parts), "-map", "[vo]", "-c:v", "libx264", "-preset", "fast", "-crf", "21", "-an", str(out)])
    run(cmd)

def build_single_video(video_meta, all_scenes_meta):
    vid_id = video_meta["id"]
    print(f"\n🚀 Dựng Video: {vid_id}")
    tmp_dir = OUTPUT_DIR / f"_tmp_{vid_id}_v3"
    tmp_dir.mkdir(parents=True, exist_ok=True)
    label_png = tmp_dir / "label.png"
    render_png(LABEL_TEXT, label_png, True)
    local_scenes = list(all_scenes_meta)
    random.shuffle(local_scenes)
    video_segments, voice_segments, sfx_segments, total_time, used_ids = [], [], [], 0.0, set()

    for i, seg in enumerate(video_meta["segments"], 1):
        voice_path = tmp_dir / f"voice_{i:02d}.mp3"
        generate_voice_gtts(seg["text"], voice_path)
        dur = get_dur(voice_path)
        sub_png = tmp_dir / f"sub_{i:02d}.png"
        render_png(seg["subtitle"], sub_png, False)
        clip_path = tmp_dir / f"clip_{i:02d}.mp4"
        picked_paths = pick_suitable_scenes(local_scenes, dur, used_ids, seg["kw"])
        build_segment_video(picked_paths, dur, label_png, sub_png, clip_path, i, len(video_meta["segments"]))
        video_segments.append(clip_path)
        voice_segments.append((voice_path, total_time))
        if seg["sfx"]: sfx_segments.append((SFX_DIR / seg["sfx"], total_time, seg["vol"]))
        total_time += dur

    # Robust Mixing
    v_list = tmp_dir / f"v_list_{vid_id}.txt"
    with v_list.open("w") as f:
        for v, _ in voice_segments: f.write(f"file '{v.resolve()}'\n")
    concat_voice = tmp_dir / "all_voice.mp3"
    run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(v_list), "-c:a", "libmp3lame", "-q:a", "2", str(concat_voice)])
    
    ambience = SFX_DIR / "clean_ambience_loop.mp3"
    f_complex = f"[0:a]volume=2.0[v];[1:a]volume=0.1[bg];" # Voice to 2.0x, Ambience to 0.1x
    m_inputs = f"[v][bg]"
    s_args = []
    for i, (path, start, vol) in enumerate(sfx_segments):
        s_args.extend(["-i", str(path)])
        f_complex += f"[{i+2}:a]adelay={int(start*1000)}|{int(start*1000)},volume={vol}[s{i}];"
        m_inputs += f"[s{i}]"
    f_complex += f"{m_inputs}amix=inputs={2+len(sfx_segments)}:duration=longest[outa]"
    final_audio = tmp_dir / "final_audio.m4a"
    run(["ffmpeg", "-y", "-i", str(concat_voice), "-i", str(ambience), *s_args, "-filter_complex", f_complex, "-map", "[outa]", "-c:a", "aac", "-b:a", "192k", "-t", str(total_time), str(final_audio)])

    cl_list = tmp_dir / f"cl_list_{vid_id}.txt"
    with cl_list.open("w") as f:
        for c in video_segments: f.write(f"file '{c.resolve()}'\n")
    all_video = tmp_dir / "all_video.mp4"
    run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(cl_list), "-c", "copy", str(all_video)])

    final_path = FINAL_DIR / f"{video_meta['caption']}.mp4"
    run(["ffmpeg", "-y", "-i", str(all_video), "-i", str(final_audio), "-c:v", "copy", "-c:a", "copy", "-t", str(total_time), "-movflags", "+faststart", str(final_path)])
    print(f"✅ Xong: {final_path.name}")

def main():
    FINAL_DIR.mkdir(parents=True, exist_ok=True)
    all_scenes_meta = load_all_scenes()
    for v_meta in VIDEOS_DATA:
        build_single_video(v_meta, all_scenes_meta)

if __name__ == "__main__":
    main()
