#!/usr/bin/env python3
import asyncio
import edge_tts
import json
import os
import subprocess
import time
import random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

# --- CONFIGURATION ---
ROOT = Path(__file__).resolve().parent.parent
PRODUCT_SLUG = "keo-sua-deku"
SCENE_LIB = ROOT / "assets" / "products" / PRODUCT_SLUG / "competitor-scenes"
SFX_DIR = ROOT / "assets" / "audio" / "sfx"
OUTPUT_DIR = ROOT / "assets" / "products" / PRODUCT_SLUG / "output"
FINAL_DIR = OUTPUT_DIR / "final"
TMP_DIR = OUTPUT_DIR / "_tmp_v2_smooth_fixed"

LABEL_TEXT = "KẸO DEKU • PEL PEL"
LABEL_Y = 280
TTS_VOICE = "vi-VN-NamMinhNeural" 
TTS_RATE = "+10%"

CAPTION = "Cứu tinh giờ giải lao cho team mê đồ ngọt đây rồi 🍬 #keodeku #anvatvung #pelpel #funny #asmr"
FINAL_NAME = f"{CAPTION}.mp4"

SEGMENTS = [
    {
        "text": "Đi học đi làm mà có hũ kẹo nén Deku này nhâm nhi thì tỉnh cả người luôn á.",
        "subtitle": "Đi học đi làm có hũ này là tỉnh cả người!",
        "keywords": ["lớp", "ngăn bàn", "túi"], 
        "sfx": "clean_rustle.mp3",
        "sfx_vol": 0.7
    },
    {
        "text": "Viên kẹo nhỏ xíu mà có võ, chua chua ngọt ngọt, ăn một viên là muốn ăn cả hũ luôn.",
        "subtitle": "Chua chua ngọt ngọt — Ăn là ghiền!",
        "keywords": ["cận cảnh", "viên", "nhai"],
        "sfx": "clean_crunch.mp3",
        "sfx_vol": 0.8
    },
    {
        "text": "Tag ngay đứa bạn mê đồ ngọt vào đây bắt nó bao một hũ đi chứ đợi gì nữa!",
        "subtitle": "Tag ngay đứa bạn mê đồ ngọt vào đây nha!",
        "keywords": ["giỏ hàng", "chia", "hũ"],
        "sfx": "clean_rustle.mp3",
        "sfx_vol": 0.4
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
        draw.rounded_rectangle([(20, 60), (980, 160)], radius=25, fill=(0, 0, 0, 180))
        bbox = draw.textbbox((0, 0), text, font=font)
        draw.text(((1000-(bbox[2]-bbox[0]))//2, (200-(bbox[3]-bbox[1]))//2-bbox[1]), text, font=font, fill=(255, 255, 255, 255), stroke_width=2, stroke_fill=(0, 0, 0, 255))
    img.save(out, "PNG")

async def tts_async(text, out):
    try:
        await edge_tts.Communicate(text, TTS_VOICE, rate=TTS_RATE).save(out)
    except:
        run(["ffmpeg", "-y", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo", "-t", str(len(text)/15.0), "-c:a", "libmp3lame", str(out)])

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
    random.shuffle(scenes) 
    return scenes

def pick_suitable_scenes(all_scenes, required_dur, used_ids, keywords):
    candidates = []
    for s in all_scenes:
        sid = f"{s.get('source_video_id')}_{s.get('scene_index')}"
        if sid in used_ids: continue
        caption = (s.get("source_caption") or "").lower()
        score = sum(1 for k in keywords if k in caption)
        if score > 0: candidates.append((score, s))
    candidates.sort(key=lambda x: x[0], reverse=True)
    picked = []
    current_dur = 0.0
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
    label_idx = num_paths
    sub_idx = num_paths + 1
    final_filter = f"fade=t=out:st={round(dur-0.2, 2)}:d=0.2" if i < total_segments else "null"
    filter_parts.append(f"[vcat][{label_idx}:v]overlay=(main_w-overlay_w)/2:{LABEL_Y}[v_lab];[v_lab][{sub_idx}:v]overlay=(main_w-overlay_w)/2:1580[v_sub];[v_sub]{final_filter}[vo]")
    vf = "".join(filter_parts)
    cmd = ["ffmpeg", "-y"]
    for p in paths: cmd.extend(["-i", str(p)])
    cmd.extend(["-i", str(label_png), "-i", str(sub_png), "-t", str(dur), "-filter_complex", vf, "-map", "[vo]", "-c:v", "libx264", "-preset", "fast", "-crf", "21", "-an", str(out)])
    run(cmd)

async def main():
    FINAL_DIR.mkdir(parents=True, exist_ok=True)
    TMP_DIR.mkdir(parents=True, exist_ok=True)
    label_png = TMP_DIR / "label.png"
    render_png(LABEL_TEXT, label_png, True)
    all_scenes_meta = load_all_scenes()
    video_segments, voice_segments, sfx_segments = [], [], []
    total_time, used_ids = 0.0, set()
    for i, seg in enumerate(SEGMENTS, 1):
        voice_path = TMP_DIR / f"voice_{i:02d}.mp3"
        await tts_async(seg["text"], str(voice_path))
        dur = get_dur(voice_path)
        render_png(seg["subtitle"], TMP_DIR / f"sub_{i:02d}.png", False)
        clip_path = TMP_DIR / f"clip_{i:02d}.mp4"
        picked_paths = pick_suitable_scenes(all_scenes_meta, dur, used_ids, seg["keywords"])
        print(f"Segment {i}: {dur:.2f}s, {len(picked_paths)} scenes")
        build_segment_video(picked_paths, dur, label_png, TMP_DIR / f"sub_{i:02d}.png", clip_path, i, len(SEGMENTS))
        video_segments.append(clip_path)
        voice_segments.append((voice_path, total_time))
        if seg["sfx"]: sfx_segments.append((SFX_DIR / seg["sfx"], total_time, seg["sfx_vol"]))
        total_time += dur
    concat_voice = TMP_DIR / "all_voice.mp3"
    v_list = TMP_DIR / "v_list.txt"
    with v_list.open("w") as f:
        for v, _ in voice_segments: f.write(f"file '{v.resolve()}'\n")
    run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(v_list), "-c", "copy", str(concat_voice)])
    ambience = SFX_DIR / "clean_ambience_loop.mp3"
    filter_complex = f"[0:a]volume=1.5[v];[1:a]volume=0.1[bg];"
    mix_inputs = f"[v][bg]"
    sfx_args = []
    for i, (path, start, vol) in enumerate(sfx_segments):
        sfx_args.extend(["-i", str(path)])
        filter_complex += f"[{i+2}:a]adelay={int(start*1000)}|{int(start*1000)},volume={vol}[s{i}];"
        mix_inputs += f"[s{i}]"
    filter_complex += f"{mix_inputs}amix=inputs={2+len(sfx_segments)}:duration=longest[outa]"
    final_audio = TMP_DIR / "final_audio.m4a"
    run(["ffmpeg", "-y", "-i", str(concat_voice), "-i", str(ambience), *sfx_args, "-filter_complex", filter_complex, "-map", "[outa]", "-c:a", "aac", "-b:a", "192k", "-t", str(total_time), str(final_audio)])
    v_list_f = TMP_DIR / "v_list_final.txt"
    with v_list_f.open("w") as f:
        for v in video_segments: f.write(f"file '{v.resolve()}'\n")
    all_video = TMP_DIR / "all_video.mp4"
    run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(v_list_f), "-c", "copy", str(all_video)])
    run(["ffmpeg", "-y", "-i", str(all_video), "-i", str(final_audio), "-c:v", "copy", "-c:a", "copy", "-t", str(total_time), "-movflags", "+faststart", str(FINAL_DIR / FINAL_NAME)])
    print(f"\n✅ Video Kẹo Deku Fixed: {FINAL_DIR / FINAL_NAME}")

if __name__ == "__main__":
    asyncio.run(main())
