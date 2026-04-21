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
TMP_DIR = OUTPUT_DIR / "_tmp_bait_chinh_ta"

LABEL_TEXT = "QUE CAY • PEL PEL"
LABEL_Y = 280
TTS_VOICE = "vi-VN-NamMinhNeural" # Giọng nam trầm, ổn định hơn
TTS_RATE = "+10%"

CAPTION = "CHÍN MUỒI hay CHÍN MÙI? 99% người vẫn sai từ này 🔥 #quecay #vuanhvien #pelpel #chinhta #xuhuong"
FINAL_NAME = f"{CAPTION}.mp4"

SEGMENTS = [
    {
        "text": "CHÍN MUỒI hay CHÍN MÙI? Từ này mà bạn cũng sai thì nên học lại tiểu học nha!",
        "subtitle": "CHÍN MUỒI hay CHÍN MÙI?",
        "keywords": ["que cay"],
        "sfx": "clean_rustle.mp3",
        "sfx_vol": 0.5
    },
    {
        "text": "Rất nhiều bạn vẫn viết là CHÍN MÙI, nhưng sự thật thì từ này KHÔNG CÓ trong từ điển đâu.",
        "subtitle": "CHÍN MÙI là từ KHÔNG CÓ TRONG TỪ ĐIỂN",
        "keywords": ["thần long"],
        "sfx": "clean_crunch.mp3",
        "sfx_vol": 0.7
    },
    {
        "text": "Từ đúng phải là CHÍN MUỒI — ý chỉ sự phát triển đã đến độ chín nhất rồi đó.",
        "subtitle": "Từ đúng phải là CHÍN MUỒI!",
        "keywords": ["hằng đại"],
        "sfx": "clean_crunch.mp3",
        "sfx_vol": 0.4
    },
    {
        "text": "Check ngay giỏ hàng Pel Pel để xem trình độ ăn cay của bạn đến đâu nhé!",
        "subtitle": "Check giỏ hàng Pel Pel ngay thôi!",
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
    try:
        # Try Edge TTS first
        await edge_tts.Communicate(text, TTS_VOICE, rate=TTS_RATE).save(out)
    except Exception as e:
        print(f"Edge TTS failed: {e}. Falling back to Gemini TTS...")
        # Fallback to Gemini TTS via src.tts_engine if possible or direct call
        try:
            from src.tts_engine import generate_voice
            generate_voice(text, out, engine="gemini")
        except:
            print("Gemini TTS fallback failed. Creating silent placeholder.")
            run(["ffmpeg", "-y", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo", "-t", str(len(text)/15.0), "-c:a", "libmp3lame", str(out)])

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
    available = [s for s in all_scenes if f"{s.get('source_video_id')}_{s.get('scene_index')}" not in used_ids]
    if not available: available = all_scenes 
    for s in available:
        if s.get("duration_sec", 0) >= required_dur:
            used_ids.add(f"{s.get('source_video_id')}_{s.get('scene_index')}")
            return [s["_mp4_path"]]
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
    if num_paths > 1:
        base_filter = f"{inputs_str}concat=n={num_paths}:v=1:a=0[vcat];[vcat]"
    else:
        base_filter = "[0:v]"
    base_filter += "scale=-1:1920:force_original_aspect_ratio=increase,crop=1080:1920:(iw-1080)/2:0,setsar=1,fps=30[vpre];"
    if i < total_segments:
        final_filter = f"fade=t=out:st={round(dur-0.2, 2)}:d=0.2"
    else:
        final_filter = "null"
    vf = (
        f"{base_filter}"
        f"[vpre][{num_paths}:v]overlay=(main_w-overlay_w)/2:{LABEL_Y}[v1];"
        f"[v1][{num_paths+1}:v]overlay=(main_w-overlay_w)/2:1580[v2];"
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
        sub_png = TMP_DIR / f"sub_{i:02d}.png"
        render_png(seg["subtitle"], sub_png, False)
        clip_path = TMP_DIR / f"clip_{i:02d}.mp4"
        picked_paths = pick_suitable_scenes(all_scenes_meta, dur, used_ids)
        build_segment_video(picked_paths, dur, label_png, sub_png, clip_path, i, len(SEGMENTS))
        video_segments.append(clip_path)
        voice_segments.append((voice_path, total_time))
        if seg["sfx"]: sfx_segments.append((SFX_DIR / seg["sfx"], total_time, seg["sfx_vol"]))
        total_time += dur

    # Build Audio
    concat_voice = TMP_DIR / "all_voice.mp3"
    v_list = TMP_DIR / "v_list.txt"
    with v_list.open("w") as f:
        for v, _ in voice_segments: f.write(f"file '{v.resolve()}'\n")
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
    all_video = TMP_DIR / "all_video.mp4"
    run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(v_list_f), "-c", "copy", str(all_video)])

    # Final Mux
    final_path = FINAL_DIR / FINAL_NAME
    run(["ffmpeg", "-y", "-i", str(all_video), "-i", str(final_audio), "-c:v", "copy", "-c:a", "copy", "-t", str(total_time), "-movflags", "+faststart", str(final_path)])
    print(f"\n✅ Video Chính tả Ready: {final_path.relative_to(ROOT)}")

if __name__ == "__main__":
    asyncio.run(main())
