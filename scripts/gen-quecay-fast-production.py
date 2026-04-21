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
PRODUCT_SLUG = "que-cay"
SCENE_LIB = ROOT / "assets" / "scene-library" / "que_cay"
SFX_DIR = ROOT / "assets" / "audio" / "sfx"
OUTPUT_DIR = ROOT / "assets" / "products" / PRODUCT_SLUG / "output"
FINAL_DIR = OUTPUT_DIR / "final"

LABEL_TEXT = "QUE CAY • PEL PEL"
LABEL_Y = 280
SPEED_FACTOR = 1.75 

VIDEOS_DATA = [
    {
        "id": "qc1_review",
        "caption": "Review 3 loại que cay quốc dân cực phẩm cho team ăn vặt ⚡️ #quecay #anvat #pelpel #review",
        "segments": [
            {"text": "Team mê que cay mà bỏ qua 3 cực phẩm này là dở rồi nha!", "subtitle": "Team mê que cay bỏ qua là dở rồi!", "kw": ["que", "quecay"], "sfx": "clean_rustle.mp3", "vol": 0.6},
            {"text": "Đầu tiên là Vương Thần Long, dai dai cay nồng. Kế đến là Hàng Đại huyền thoại, vị mặn ngọt cực cuốn.", "subtitle": "Vương Thần Long & Hàng Đại cực phẩm", "kw": ["nhai", "ăn"], "sfx": "clean_crunch.mp3", "vol": 0.9},
            {"text": "Giỏ hàng Pel Pel đang có đủ combo nha. Chốt đơn thôi cưng ơi!", "subtitle": "Giỏ hàng đang có đủ combo nha!", "kw": ["giỏ hàng", "combo"], "sfx": None, "vol": 0.5}
        ]
    },
    {
        "id": "qc2_midnight",
        "caption": "3 giờ sáng và cơn nghiện Que Cay không lối thoát 🌙 #quecay #midnightcravings #asmr #pelpel",
        "segments": [
            {"text": "3 giờ sáng rồi mà chiếc bụng đói cứ gào thét tên... QUE CAY!", "subtitle": "3 giờ sáng và cơn nghiện QUE CAY!", "kw": ["tối", "lấy"], "sfx": "clean_rustle.mp3", "vol": 0.7},
            {"text": "Nhìn sớ thịt dai dai thấm đẫm sốt cay nồng này xem, ai mà chịu cho nổi?", "subtitle": "Sớ thịt dai dai — Thấm đẫm sốt cay", "kw": ["cận cảnh", "nhai"], "sfx": "clean_crunch.mp3", "vol": 1.0},
            {"text": "Lỡ va phải Pel Pel rồi thì chốt đơn ngay đi chứ đợi gì nữa cưng ơi!", "subtitle": "Chốt ngay đi chứ đợi gì nữa!", "kw": ["đổ", "giỏ hàng"], "sfx": None, "vol": 0.5}
        ]
    },
    {
        "id": "qc3_chinhta",
        "caption": "CHÍN MUỒI hay CHÍN MÙI? Từ này mà bạn cũng sai sao? 🧐 #quecay #chinhta #vuanhvien #pelpel",
        "segments": [
            {"text": "CHÍN MUỒI hay CHÍN MÙI? Từ này đơn giản vậy mà 90% người vẫn viết sai đó!", "subtitle": "CHÍN MUỒI hay CHÍN MÙI?", "kw": ["que", "viên"], "sfx": "clean_rustle.mp3", "vol": 0.5},
            {"text": "Dấu NGÃ mới là đúng nha. Chín muồi ý chỉ sự phát triển đã đến độ chín nhất rồi.", "subtitle": "Từ đúng phải là CHÍN MUỒI!", "kw": ["nhai", "ăn"], "sfx": "clean_crunch.mp3", "vol": 0.8},
            {"text": "Check trình ăn cay của bạn xem đã chín muồi chưa tại giỏ hàng Pel Pel nhé!", "subtitle": "Check giỏ hàng Pel Pel ngay đi!", "kw": ["hũ", "giỏ hàng"], "sfx": None, "vol": 0.5}
        ]
    },
    {
        "id": "qc4_quytac",
        "caption": "3 Quy tắc ngầm khi mở Que Cay trong lớp 💀 #quecay #funny #schoollife #pelpel #xuhuong",
        "segments": [
            {"text": "Quy tắc một: Đừng bao giờ mở bịch quá to. Tiếng sột soạt sẽ tố cáo bạn với cả lớp đó.", "subtitle": "1: Đừng mở bịch quá to!", "kw": ["lớp", "ngăn bàn"], "sfx": "clean_rustle.mp3", "vol": 0.9},
            {"text": "Quy tắc hai: Tuyệt đối không để đứa bạn thân biết. Vì nó sẽ xử đẹp cả bịch trong 1 giây.", "subtitle": "2: Đừng để đứa bạn thân biết!", "kw": ["tay", "chia"], "sfx": "clean_rustle.mp3", "vol": 0.7},
            {"text": "Quy tắc ba: Luôn thủ sẵn bịch dự phòng. Chốt ngay combo tại giỏ hàng Pel Pel nha!", "subtitle": "3: Luôn thủ sẵn bịch dự phòng!", "kw": ["giỏ hàng", "nhiều"], "sfx": "clean_crunch.mp3", "vol": 0.5}
        ]
    }
]

def run(cmd):
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def render_png(text, out, is_label=True):
    img = Image.new("RGBA", (900, 140) if is_label else (1000, 200), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    for p in ["/System/Library/Fonts/Supplemental/Arial Unicode.ttf", "/System/Library/Fonts/HelveticaNeue.ttc"]:
        if Path(p).exists(): font = ImageFont.truetype(p, 58 if is_label else 62); break
    else: font = ImageFont.load_default()
    if is_label:
        draw.rounded_rectangle([(0, 0), (899, 139)], radius=70, fill=(255, 107, 0, 220))
        bbox = draw.textbbox((0, 0), text, font=font)
        draw.text(((900-(bbox[2]-bbox[0]))//2, (140-(bbox[3]-bbox[1]))//2-bbox[1]), text, font=font, fill=(255, 255, 255, 255), stroke_width=3, stroke_fill=(0, 0, 0, 255))
    else:
        draw.rounded_rectangle([(20, 50), (980, 170)], radius=25, fill=(0, 0, 0, 180))
        bbox = draw.textbbox((0, 0), text, font=font)
        draw.text(((1000-(bbox[2]-bbox[0]))//2, (200-(bbox[3]-bbox[1]))//2-bbox[1]), text, font=font, fill=(255, 255, 255, 255), stroke_width=2, stroke_fill=(0, 0, 0, 255))
    img.save(out, "PNG")

def generate_voice_fast(text, out_path):
    tmp_voice = out_path.with_name(f"{out_path.stem}_orig.mp3")
    gTTS(text=text, lang='vi').save(str(tmp_voice))
    run(["ffmpeg", "-y", "-i", str(tmp_voice), "-filter:a", f"atempo={SPEED_FACTOR}", str(out_path)])

def get_dur(p):
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", str(p)], capture_output=True, text=True).stdout.strip() or 0)

def load_all_scenes():
    scenes = []
    for jf in sorted(SCENE_LIB.rglob("*.json")):
        try:
            with jf.open() as f: data = json.load(f)
            mp4 = jf.with_suffix(".mp4")
            if mp4.exists(): data["_mp4_path"] = mp4; scenes.append(data)
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
        picked.append(s["_mp4_path"]); used_ids.add(sid)
        current_dur += s.get("duration_sec", 0)
        if current_dur >= required_dur: break
    return picked

def build_segment_video(paths, dur, label_png, sub_png, out, i, total):
    f_parts = []
    for j, p in enumerate(paths):
        f_parts.append(f"[{j}:v]scale=-1:1920:force_original_aspect_ratio=increase,crop=1080:1920:(iw-1080)/2:0,setsar=1,fps=30[v{j}];")
    f_parts.append("".join(f"[v{j}]" for j in range(len(paths))) + f"concat=n={len(paths)}:v=1:a=0[vcat];")
    final_f = f"fade=t=out:st={round(dur-0.2, 2)}:d=0.2" if i < total else "null"
    f_parts.append(f"[vcat][{len(paths)}:v]overlay=(main_w-overlay_w)/2:{LABEL_Y}[v_lab];[v_lab][{len(paths)+1}:v]overlay=(main_w-overlay_w)/2:1580[v_sub];[v_sub]{final_f}[vo]")
    cmd = ["ffmpeg", "-y"]
    for p in paths: cmd.extend(["-i", str(p)])
    cmd.extend(["-i", str(label_png), "-i", str(sub_png), "-t", str(dur), "-filter_complex", "".join(f_parts), "-map", "[vo]", "-c:v", "libx264", "-preset", "fast", "-crf", "21", "-an", str(out)])
    run(cmd)

async def build_single_video_fast(video_meta, all_scenes_meta):
    vid_id = video_meta["id"]; tmp_dir = OUTPUT_DIR / f"_tmp_{vid_id}_fast"; tmp_dir.mkdir(parents=True, exist_ok=True)
    label_png = tmp_dir / "label.png"; render_png(LABEL_TEXT, label_png, True)
    local_scenes = list(all_scenes_meta); random.shuffle(local_scenes)
    video_segments, voice_segments, sfx_segments, total_time, used_ids = [], [], [], 0.0, set()
    
    for i, seg in enumerate(video_meta["segments"], 1):
        voice_path = tmp_dir / f"voice_{i:02d}.mp3"
        generate_voice_fast(seg["text"], voice_path)
        dur = get_dur(voice_path)
        render_png(seg["subtitle"], tmp_dir / f"sub_{i:02d}.png", False)
        clip_path = tmp_dir / f"clip_{i:02d}.mp4"
        picked_paths = pick_suitable_scenes(local_scenes, dur, used_ids, seg["kw"])
        build_segment_video(picked_paths, dur, label_png, tmp_dir / f"sub_{i:02d}.png", clip_path, i, len(video_meta["segments"]))
        video_segments.append(clip_path); voice_segments.append((voice_path, total_time))
        if seg["sfx"]: sfx_segments.append((SFX_DIR / seg["sfx"], total_time, seg["vol"]))
        total_time += dur
        
    v_list = tmp_dir / "v_list.txt"
    with open(v_list, "w") as f:
        for v, _ in voice_segments: f.write(f"file '{v.resolve()}'\n")
    concat_voice = tmp_dir / "all_voice.mp3"
    run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(v_list), "-c:a", "libmp3lame", "-q:a", "2", str(concat_voice)])
    
    ambience = SFX_DIR / "clean_ambience_loop.mp3"
    f_complex = f"[0:a]volume=2.0[v];[1:a]volume=0.08[bg];"
    m_inputs = f"[v][bg]"
    s_args = []
    for i, (path, start, vol) in enumerate(sfx_segments):
        s_args.extend(["-i", str(path)]); f_complex += f"[{i+2}:a]adelay={int(start*1000)}|{int(start*1000)},volume={vol}[s{i}];"
        m_inputs += f"[s{i}]"
    f_complex += f"{m_inputs}amix=inputs={2+len(sfx_segments)}:duration=longest[outa]"
    final_audio = tmp_dir / "final_audio.m4a"
    run(["ffmpeg", "-y", "-i", str(concat_voice), "-i", str(ambience), *s_args, "-filter_complex", f_complex, "-map", "[outa]", "-c:a", "aac", "-b:a", "192k", "-t", str(total_time), str(final_audio)])
    
    cl_list = tmp_dir / "cl_list.txt"
    with open(cl_list, "w") as f:
        for c in video_segments: f.write(f"file '{c.resolve()}'\n")
    all_video = tmp_dir / "all_video.mp4"
    run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(cl_list), "-c", "copy", str(all_video)])
    
    final_path = FINAL_DIR / (video_meta['caption'] + ".mp4")
    run(["ffmpeg", "-y", "-i", str(all_video), "-i", str(final_audio), "-c:v", "copy", "-c:a", "copy", "-t", str(total_time), "-movflags", "+faststart", str(final_path)])
    print(f"✅ Que Cay Fast x1.75 Ready: {final_path.name}")

async def main():
    FINAL_DIR.mkdir(parents=True, exist_ok=True); all_scenes_meta = load_all_scenes()
    for v_meta in VIDEOS_DATA: await build_single_video_fast(v_meta, all_scenes_meta)

if __name__ == "__main__": asyncio.run(main())
