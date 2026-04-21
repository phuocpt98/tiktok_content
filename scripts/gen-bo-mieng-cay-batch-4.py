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
PRODUCT_SLUG = "bo-mieng-cay"
SCENE_LIB = ROOT / "assets" / "products" / PRODUCT_SLUG / "competitor-scenes"
SFX_DIR = ROOT / "assets" / "audio" / "sfx"
OUTPUT_DIR = ROOT / "assets" / "products" / PRODUCT_SLUG / "output"
FINAL_DIR = OUTPUT_DIR / "final"

LABEL_TEXT = "BÒ MIẾNG CAY • PEL PEL"
LABEL_Y = 280
SPEED_FACTOR = 1.75 

VIDEOS_DATA = [
    {
        "id": "bm1_visual",
        "caption": "Bò miếng mềm đẫm sốt, nhìn thôi đã thấy thèm tê tái 🤤 #bomiengcay #khobo #anvat #pelpel #asmr",
        "segments": [
            {"text": "Nhìn cái miếng khô bò mềm mướt, thấm đẫm nước sốt cay nồng này xem, có ai mà chịu cho nổi không?", "subtitle": "Khô bò mềm mướt — Thấm đẫm sốt!", "kw": ["miếng", "cận cảnh"], "sfx": "clean_rustle.mp3", "vol": 0.6},
            {"text": "Cắn một miếng là vị ngọt của thịt bò hòa quyện cùng vị cay xè lưỡi, nhai tới đâu phê tới đó luôn.", "subtitle": "Cắn 1 miếng — Cay xè phê pha!", "kw": ["nhai", "ăn"], "sfx": "clean_crunch.mp3", "vol": 1.0},
            {"text": "Đúng là cực phẩm nhà Pel Pel, không thử là tiếc hùi hụi đó nha. Chốt đơn ngay nào!", "subtitle": "Cực phẩm Pel Pel — Chốt đơn ngay!", "kw": ["hũ", "giỏ hàng"], "sfx": None, "vol": 0.5}
        ]
    },
    {
        "id": "bm2_midnight",
        "caption": "Cơn đói đêm khuya và tiếng gọi của Bò Miếng Cay 🌙 #midnightcravings #khobo #bomiengcay #asmr #pelpel",
        "segments": [
            {"text": "3 giờ sáng rồi mà cái bụng cứ gào thét đòi ăn bò miếng cay thì phải làm sao đây các bác?", "subtitle": "3h sáng và tiếng gọi của BÒ CAY!", "kw": ["tối", "lấy", "mở"], "sfx": "clean_rustle.mp3", "vol": 0.7},
            {"text": "Phải lôi ngay một hũ ra nhâm nhi thôi. Vị cay tê tái giúp tỉnh táo hẳn luôn, cày phim là hết bài.", "subtitle": "Nhâm nhi bò cay — Cày phim hết bài!", "kw": ["ăn", "cận cảnh"], "sfx": "clean_crunch.mp3", "vol": 0.9},
            {"text": "Anh em nào hay thức khuya thì thủ ngay 1 hũ cứu đói đi nha. Link ở giỏ hàng đó!", "subtitle": "Thủ ngay 1 hũ cứu đói đi anh em!", "kw": ["giỏ hàng", "nhiều"], "sfx": None, "vol": 0.5}
        ]
    },
    {
        "id": "bm3_poll",
        "caption": "Bò miếng mềm hay Bò xé sợi? Team nào đông dân hơn đây? 🧐 #khobo #poll #bomiengcay #anvat #pelpel",
        "segments": [
            {"text": "Tranh cãi nảy lửa: Các bà thuộc team thích ăn bò miếng MỀM ướt hay bò xé sợi DAI giòn?", "subtitle": "Bò miếng MỀM hay Bò xé DAI?", "kw": ["xé", "miếng", "bò"], "sfx": "clean_rustle.mp3", "vol": 0.5},
            {"text": "Tui là tui mê cái kiểu bò miếng đẫm sốt như này này, nhai sướng cái nư mà cực kỳ đậm đà.", "subtitle": "Mê bò miếng đẫm sốt — Đậm đà!", "kw": ["nhai", "ăn"], "sfx": "clean_crunch.mp3", "vol": 0.8},
            {"text": "Comment ngay team của bạn xuống đây nhé. Giỏ hàng Pel Pel đang có đủ cả hai luôn nha!", "subtitle": "Comment team bạn chọn đi nào!", "kw": ["giỏ hàng", "combo"], "sfx": None, "vol": 0.5}
        ]
    },
    {
        "id": "bm4_energy",
        "caption": "Cứu tinh cho những giờ làm việc mệt mỏi là đây! ⚡️ #worklife #khobo #bomiengcay #pelpel #trending",
        "segments": [
            {"text": "Đang chạy deadline mà đầu óc cứ trên mây thì chỉ có miếng bò cay này mới cứu nổi tui thôi.", "subtitle": "Đang chạy deadline mà thèm bò cay!", "kw": ["lớp", "ngăn bàn", "túi"], "sfx": "clean_rustle.mp3", "vol": 0.7},
            {"text": "Vị cay xộc lên não giúp tỉnh táo tức thì, càng nhai càng cuốn, đảm bảo năng lượng tràn trề luôn.", "subtitle": "Vị cay tỉnh táo — Càng nhai càng cuốn!", "kw": ["nhai", "ăn"], "sfx": "clean_crunch.mp3", "vol": 1.0},
            {"text": "Tag ngay đứa đồng nghiệp hay buồn ngủ vào đây để cứu giá nó đi nào!", "subtitle": "Tag đồng nghiệp vào cứu giá đi!", "kw": ["giỏ hàng", "hũ"], "sfx": "clean_rustle.mp3", "vol": 0.4}
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
    tmp_v = out_path.with_name(f"{out_path.stem}_orig.mp3")
    gTTS(text=text, lang='vi').save(str(tmp_v))
    run(["ffmpeg", "-y", "-i", str(tmp_v), "-filter:a", f"atempo={SPEED_FACTOR}", str(out_path)])

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
        dur = get_dur(voice_path); sub_png = tmp_dir / f"sub_{i:02d}.png"
        render_png(seg["subtitle"], sub_png, False)
        clip_path = tmp_dir / f"clip_{i:02d}.mp4"
        picked_paths = pick_suitable_scenes(local_scenes, dur, used_ids, seg["kw"])
        build_segment_video(picked_paths, dur, label_png, sub_png, clip_path, i, len(video_meta["segments"]))
        video_segments.append(clip_path); voice_segments.append((voice_path, total_time))
        if seg["sfx"]: sfx_segments.append((SFX_DIR / seg["sfx"], total_time, seg["vol"]))
        total_time += dur
        
    v_list = tmp_dir / "v_list.txt"
    with open(v_list, "w") as f:
        for v, _ in voice_segments: f.write(f"file '{v.resolve()}'\n")
    concat_voice = tmp_dir / "all_voice.mp3"
    run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(v_list), "-c:a", "libmp3lame", "-q:a", "2", str(concat_voice)])
    
    ambience = SFX_DIR / "clean_ambience_loop.mp3"
    f_complex = f"[0:a]volume=2.0[v];[1:a]volume=0.1[bg];"
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
    print(f"✅ Bò Miếng Fast x1.75 Ready: {final_path.name}")
    run(["rm", "-rf", str(tmp_dir)])

async def main():
    FINAL_DIR.mkdir(parents=True, exist_ok=True); all_scenes_meta = load_all_scenes()
    for v_meta in VIDEOS_DATA: await build_single_video_fast(v_meta, all_scenes_meta)

if __name__ == "__main__": asyncio.run(main())
