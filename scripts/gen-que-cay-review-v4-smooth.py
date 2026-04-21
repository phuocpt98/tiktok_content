#!/usr/bin/env python3
import asyncio
import edge_tts
import json
import os
import subprocess
import time
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

# --- CONFIGURATION ---
ROOT = Path(__file__).resolve().parent.parent
PRODUCT_SLUG = "que-cay"
SCENE_LIB = ROOT / "assets" / "scene-library" / "que_cay"
SFX_DIR = ROOT / "assets" / "audio" / "sfx"
OUTPUT_DIR = ROOT / "assets" / "products" / PRODUCT_SLUG / "output"
FINAL_DIR = OUTPUT_DIR / "final"
TMP_DIR = OUTPUT_DIR / "_tmp_v4_smooth"

LABEL_TEXT = "QUE CAY • PEL PEL"
LABEL_Y = 280
TTS_VOICE = "vi-VN-HoaiMyNeural"
TTS_RATE = "+15%"

CAPTION = "Cơn nghiện Que Cay 3 giờ sáng không lối thoát 🔥 #quecay #anvat #pelpel #asmr #midnightcravings"
FINAL_NAME = f"{CAPTION}.mp4"

SEGMENTS = [
    {
        "text": "3 giờ sáng rồi mà chiếc bụng đói cứ gào thét tên... QUE CAY!",
        "subtitle": "3 giờ sáng và cơn nghiện QUE CAY!",
        "keywords": ["que cay"],
        "sfx": "clean_rustle.mp3",
        "sfx_vol": 0.4
    },
    {
        "text": "Nhìn sớ thịt dai dai thấm đẫm sốt cay nồng này xem, ai mà chịu cho nổi?",
        "subtitle": "Sớ thịt dai dai — Thấm đẫm sốt cay",
        "keywords": ["thần long"],
        "sfx": "clean_crunch.mp3",
        "sfx_vol": 0.6
    },
    {
        "text": "Hàng Đại hay Vương Thần Long cũng đều là chân ái đêm khuya hết nha.",
        "subtitle": "Hàng Đại hay Vương Thần Long đều đỉnh!",
        "keywords": ["hằng đại"],
        "sfx": "clean_crunch.mp3",
        "sfx_vol": 0.3
    },
    {
        "text": "Lỡ va phải Pel Pel rồi thì chốt đơn ngay đi chứ đợi gì nữa cưng ơi!",
        "subtitle": "Va phải Pel Pel rồi — Chốt đơn ngay!",
        "keywords": ["anvat"],
        "sfx": None
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
    await edge_tts.Communicate(text, TTS_VOICE, rate=TTS_RATE).save(out)

def get_dur(p):
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", str(p)], capture_output=True, text=True).stdout.strip() or 0)

def load_scenes_metadata():
    scenes = []
    for jf in sorted(SCENE_LIB.glob("*.json")):
        try:
            with jf.open() as f: data = json.load(f)
            mp4 = SCENE_LIB / f"{jf.stem}.mp4"
            if mp4.exists():
                data["_mp4_path"] = mp4
                scenes.append(data)
        except: continue
    return scenes

def pick_suitable_scenes(all_scenes, required_dur, used_ids):
    """Chọn 1 hoặc nhiều scene để lấp đầy thời lượng yêu cầu."""
    available = [s for s in all_scenes if f"{s.get('source_video_id')}_{s.get('scene_index')}" not in used_ids]
    if not available: available = all_scenes 
    
    # Ưu tiên scene có duration >= required_dur
    for s in available:
        if s.get("duration_sec", 0) >= required_dur:
            used_ids.add(f"{s.get('source_video_id')}_{s.get('scene_index')}")
            return [s["_mp4_path"]]
            
    # Ghép nhiều scene
    sorted_avail = sorted(available, key=lambda x: x.get("duration_sec", 0), reverse=True)
    picked = []
    current_dur = 0.0
    for s in sorted_avail:
        picked.append(s["_mp4_path"])
        used_ids.add(f"{s.get('source_video_id')}_{s.get('scene_index')}")
        current_dur += s.get("duration_sec", 0)
        if current_dur >= required_dur: break
    return picked

def build_segment_video(paths, dur, label_png, sub_png, out, i, total_segments):
    num_paths = len(paths)
    inputs_str = "".join(f"[{j}:v]" for j in range(num_paths))
    
    # 1. Concat nếu nhiều path, hoặc lấy path 0
    if num_paths > 1:
        base_filter = f"{inputs_str}concat=n={num_paths}:v=1:a=0[vcat];[vcat]"
    else:
        base_filter = "[0:v]"
        
    # 2. Scale, Crop, FPS
    base_filter += "scale=-1:1920:force_original_aspect_ratio=increase,crop=1080:1920:(iw-1080)/2:0,setsar=1,fps=30[vpre];"
    
    # 3. Overlays
    label_idx = num_paths
    sub_idx = num_paths + 1
    
    if i < total_segments:
        final_filter = f"fade=t=out:st={round(dur-0.2, 2)}:d=0.2"
    else:
        final_filter = "null" # Không làm gì, chỉ pass-through pad
    
    vf = (
        f"{base_filter}"
        f"[vpre][{label_idx}:v]overlay=(main_w-overlay_w)/2:{LABEL_Y}[v1];"
        f"[v1][{sub_idx}:v]overlay=(main_w-overlay_w)/2:1580[v2];"
        f"[v2]{final_filter}[vo]"
    )
    
    cmd = ["ffmpeg", "-y"]
    for p in paths: cmd.extend(["-i", str(p)])
    cmd.extend(["-i", str(label_png), "-i", str(sub_png), "-t", str(dur), "-filter_complex", vf, "-map", "[vo]", "-c:v", "libx264", "-preset", "fast", "-crf", "21", "-an", str(out)])
    run(cmd)

async def main():
    FINAL_DIR.mkdir(parents=True, exist_ok=True)
    TMP_DIR.mkdir(parents=True, exist_ok=True)
    label_png = TMP_DIR / "label.png"
    render_png(LABEL_TEXT, label_png, True)
    
    all_scenes_meta = load_scenes_metadata()
    video_segments = []
    voice_segments = []
    sfx_segments = []
    total_time = 0.0
    used_ids = set()

    for i, seg in enumerate(SEGMENTS, 1):
        voice_path = TMP_DIR / f"voice_{i:02d}.mp3"
        await tts_async(seg["text"], str(voice_path))
        dur = get_dur(voice_path)
        render_png(seg["subtitle"], TMP_DIR / f"sub_{i:02d}.png", False)
        clip_path = TMP_DIR / f"clip_{i:02d}.mp4"
        picked_paths = pick_suitable_scenes(all_scenes_meta, dur, used_ids)
        print(f"Segment {i}: {dur:.2f}s, {len(picked_paths)} scenes")
        build_segment_video(picked_paths, dur, label_png, TMP_DIR / f"sub_{i:02d}.png", clip_path, i, len(SEGMENTS))
        video_segments.append(clip_path)
        voice_segments.append((voice_path, total_time))
        if seg["sfx"]: sfx_segments.append((SFX_DIR / seg["sfx"], total_time, seg["sfx_vol"]))
        total_time += dur

    # Build Audio
    v_list = TMP_DIR / "v_list.txt"
    with v_list.open("w") as f:
        for v, _ in voice_segments: f.write(f"file '{v.resolve()}'\n")
    concat_voice = TMP_DIR / "all_voice.mp3"
    run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(v_list), "-c", "copy", str(concat_voice)])
    
    ambience = SFX_DIR / "clean_ambience_loop.mp3"
    filter_complex = f"[0:a]volume=0.15[bg];[1:a]volume=1.4[v];"
    mix_inputs = f"[bg][v]"
    sfx_args = []
    for i, (path, start, vol) in enumerate(sfx_segments):
        sfx_args.extend(["-i", str(path)])
        filter_complex += f"[{i+2}:a]adelay={int(start*1000)}|{int(start*1000)},volume={vol}[s{i}];"
        mix_inputs += f"[s{i}]"
    filter_complex += f"{mix_inputs}amix=inputs={2+len(sfx_segments)}:duration=longest[outa]"
    final_audio = TMP_DIR / "final_audio.m4a"
    run(["ffmpeg", "-y", "-i", str(ambience), "-i", str(concat_voice), *sfx_args, "-filter_complex", filter_complex, "-map", "[outa]", "-c:a", "aac", "-b:a", "192k", "-t", str(total_time), str(final_audio)])

    # Concat Video
    v_list_f = TMP_DIR / "v_list_final.txt"
    with v_list_f.open("w") as f:
        for v in video_segments: f.write(f"file '{v.resolve()}'\n")
    run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(v_list_f), "-c", "copy", str(TMP_DIR / "all_video.mp4")])

    # Final Mux
    run(["ffmpeg", "-y", "-i", str(TMP_DIR / "all_video.mp4"), "-i", str(final_audio), "-c:v", "copy", "-c:a", "copy", "-t", str(total_time), "-movflags", "+faststart", str(FINAL_DIR / FINAL_NAME)])
    print(f"\n✅ Done: {FINAL_DIR / FINAL_NAME}")

if __name__ == "__main__":
    asyncio.run(main())
