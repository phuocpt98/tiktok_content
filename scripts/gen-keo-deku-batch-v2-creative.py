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

LABEL_TEXT = "KẸO DEKU • PEL PEL"
LABEL_Y = 280

# Danh sách giọng đọc để retry
VOICES = ["vi-VN-NamMinhNeural", "vi-VN-HoaiMyNeural"]

VIDEOS_DATA = [
    {
        "id": "v8_mom_drama",
        "caption": "Mẹ bảo lớn rồi còn ăn kẹo, và cái kết sau khi mẹ thử hũ Deku 🍬 #keodeku #funny #momlife #pelpel #xuhuong",
        "segments": [
            {"text": "Mẹ tui bảo: Lớn tướt xác rồi mà suốt ngày ôm hũ kẹo sữa như con nít vậy hả?", "subtitle": "Mẹ bảo: Lớn rồi còn ăn kẹo sữa??", "kw": ["hũ", "nhiều"], "sfx": "clean_rustle.mp3", "vol": 0.6},
            {"text": "Xong tui mời mẹ thử một viên kẹo nén Deku. Và giờ thì hũ kẹo đã nằm trên giường mẹ luôn rồi.", "subtitle": "Và cái kết... mẹ chiếm luôn hũ kẹo!", "kw": ["viên", "nhai"], "sfx": "clean_crunch.mp3", "vol": 0.9},
            {"text": "Đúng là kẹo quốc dân, từ già đến trẻ ai cũng mê. Chốt ngay trong giỏ hàng nha mng!", "subtitle": "Kẹo quốc dân ai cũng mê — Chốt đơn thôi!", "kw": ["đổ", "giỏ hàng"], "sfx": None, "vol": 0.5}
        ]
    },
    {
        "id": "v9_crush_bait",
        "caption": "Tuyệt chiêu tán đổ crush bằng kẹo sữa chua Deku 🍓 #keodeku #crush #trending #pelpel #valentine",
        "segments": [
            {"text": "Muốn bắt chuyện với crush mà chưa biết nói gì? Đưa ngay hũ kẹo Deku pastel này ra nhé.", "subtitle": "Muốn bắt chuyện với crush? Thử cách này!", "kw": ["unbox", "hồng"], "sfx": "clean_rustle.mp3", "vol": 0.5},
            {"text": "Màu thì nịnh mắt, vị thì chua ngọt béo ngậy. Đảm bảo crush sẽ đổ rầm rầm luôn cho xem.", "subtitle": "Màu pastel cưng xỉu — Vị chua ngọt đổ đứ đừ", "kw": ["cận cảnh", "viên"], "sfx": "clean_crunch.mp3", "vol": 0.8},
            {"text": "Tag ngay 'người ấy' vào đây để ngầm ra tín hiệu đi nào. Link ở giỏ hàng nha!", "subtitle": "Tag 'người ấy' vào đây ra tín hiệu đi!", "kw": ["hũ", "nhiều"], "sfx": None, "vol": 0.4}
        ]
    },
    {
        "id": "v10_math_class",
        "caption": "Cứu tinh giờ Toán là đây chứ đâu 💀 #keodeku #schoollife #math #anvatvung #pelpel",
        "segments": [
            {"text": "Đang trong giờ Toán mà cơn buồn ngủ ập tới thì chỉ có kẹo nén Deku mới cứu nổi tui thôi.", "subtitle": "Cứu tinh giờ Toán — Chống buồn ngủ cực mạnh!", "kw": ["lấy", "túi", "giấu"], "sfx": "clean_rustle.mp3", "vol": 0.7},
            {"text": "Cắn một cái giòn tan, vị sữa chua cực mạnh xộc lên đại não. Tỉnh cả người luôn các bác ạ!", "subtitle": "Cắn giòn tan — Tỉnh táo tức thì!", "kw": ["nhai", "ăn"], "sfx": "clean_crunch.mp3", "vol": 1.0},
            {"text": "Anh em đồng môn nào hay buồn ngủ trong lớp thì thủ ngay 1 hũ trong cặp đi nha!", "subtitle": "Thủ ngay 1 hũ trong cặp đi anh em ơi!", "kw": ["hũ", "full"], "sfx": "clean_rustle.mp3", "vol": 0.4}
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

async def tts_with_retry(text, out_path):
    """Gen Voice với cơ chế Retry nhiều giọng để tránh mất tiếng."""
    for voice in VOICES:
        try:
            communicate = edge_tts.Communicate(text, voice, rate="+10%")
            await communicate.save(out_path)
            # Kiểm tra xem file có thực sự có dữ liệu không
            if os.path.exists(out_path) and os.path.getsize(out_path) > 1000:
                print(f"   ✓ Voice gen success with {voice}")
                return True
        except Exception as e:
            print(f"   ⚠ {voice} failed: {e}")
        await asyncio.sleep(1)
    
    # Final fallback: Silent
    print(f"   ❌ All TTS failed for: {text[:20]}... Using silent.")
    run(["ffmpeg", "-y", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo", "-t", str(len(text)/15.0), "-c:a", "libmp3lame", str(out_path)])
    return False

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
    vf = "".join(filter_parts)
    cmd = ["ffmpeg", "-y"]
    for p in paths: cmd.extend(["-i", str(p)])
    cmd.extend(["-i", str(label_png), "-i", str(sub_png), "-t", str(dur), "-filter_complex", vf, "-map", "[vo]", "-c:v", "libx264", "-preset", "fast", "-crf", "21", "-an", str(out)])
    run(cmd)

async def build_single_video(video_meta, all_scenes_meta):
    vid_id = video_meta["id"]
    print(f"\n🚀 Dựng Video Sáng Tạo: {vid_id}")
    tmp_dir = OUTPUT_DIR / f"_tmp_{vid_id}_v2"
    tmp_dir.mkdir(parents=True, exist_ok=True)
    label_png = tmp_dir / "label.png"
    render_png(LABEL_TEXT, label_png, True)
    local_scenes = list(all_scenes_meta)
    random.shuffle(local_scenes)
    video_segments, voice_segments, sfx_segments, total_time, used_ids = [], [], [], 0.0, set()

    for i, seg in enumerate(video_meta["segments"], 1):
        voice_path = tmp_dir / f"voice_{i:02d}.mp3"
        await tts_with_retry(seg["text"], str(voice_path))
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

    # Unified Audio Timeline (Robust)
    concat_voice = tmp_dir / "all_voice.mp3"
    v_list = tmp_dir / f"v_list_{vid_id}.txt"
    with v_list.open("w") as f:
        for v, _ in voice_segments: f.write(f"file '{v.resolve()}'\n")
    run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(v_list), "-c:a", "libmp3lame", "-q:a", "2", str(concat_voice)])
    
    ambience = SFX_DIR / "clean_ambience_loop.mp3"
    f_complex = f"[0:a]volume=1.8[v];[1:a]volume=0.08[bg];"
    m_inputs = f"[v][bg]"
    s_args = []
    for i, (path, start, vol) in enumerate(sfx_segments):
        s_args.extend(["-i", str(path)])
        f_complex += f"[{i+2}:a]adelay={int(start*1000)}|{int(start*1000)},volume={vol}[s{i}];"
        m_inputs += f"[s{i}]"
    f_complex += f"{m_inputs}amix=inputs={2+len(sfx_segments)}:duration=longest[outa]"
    final_audio = tmp_dir / "final_audio.m4a"
    run(["ffmpeg", "-y", "-i", str(concat_voice), "-i", str(ambience), *s_args, "-filter_complex", f_complex, "-map", "[outa]", "-c:a", "aac", "-b:a", "192k", "-t", str(total_time), str(final_audio)])

    all_video = tmp_dir / "all_video.mp4"
    cl_list = tmp_dir / f"cl_list_{vid_id}.txt"
    with cl_list.open("w") as f:
        for c in video_segments: f.write(f"file '{c.resolve()}'\n")
    run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(cl_list), "-c", "copy", str(all_video)])

    final_path = FINAL_DIR / f"{video_meta['caption']}.mp4"
    run(["ffmpeg", "-y", "-i", str(all_video), "-i", str(final_audio), "-c:v", "copy", "-c:a", "copy", "-t", str(total_time), "-movflags", "+faststart", str(final_path)])
    print(f"✅ Thành công: {final_path.name}")

async def main():
    FINAL_DIR.mkdir(parents=True, exist_ok=True)
    all_scenes_meta = load_all_scenes()
    for v_meta in VIDEOS_DATA:
        await build_single_video(v_meta, all_scenes_meta)
        await asyncio.sleep(2) # Nghỉ giữa các video để tránh bị block TTS

if __name__ == "__main__":
    asyncio.run(main())
