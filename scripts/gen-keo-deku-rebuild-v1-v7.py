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
        "id": "v1_intro_fixed",
        "caption": "Kẹo nén sữa chua Deku - Màu pastel cưng xỉu, ăn là ghiền 🔥 #keodeku #asmr #anvat #pelpel",
        "segments": [
            {"text": "Kẹo nén sữa chua Deku đang hot rần rần đây cả nhà ơi. Nhìn cái màu pastel này có mê không chứ lị!", "subtitle": "Kẹo Deku HOT nhất lúc này!", "kw": ["đổ", "hũ", "pastel"], "sfx": "clean_rustle.mp3", "vol": 0.6},
            {"text": "Tiếng cắn giòn tan, vị chua chua ngọt ngọt béo ngậy, ăn là chỉ có nghiện thôi á.", "subtitle": "Cắn giòn tan — Vị cực cuốn!", "kw": ["nhai", "ăn", "cận cảnh"], "sfx": "clean_crunch.mp3", "vol": 0.9},
            {"text": "Hũ to oạch ăn hoài không hết luôn. Chốt ngay trong giỏ hàng Pel Pel nha!", "subtitle": "Hũ to oạch — Chốt đơn ngay!", "kw": ["giỏ hàng", "full"], "sfx": None, "vol": 0.5}
        ]
    },
    {
        "id": "v2_school_fixed",
        "caption": "Cứu tinh giờ giải lao cho team mê đồ ngọt đây rồi 🍬 #keodeku #anvatvung #funny #pelpel",
        "segments": [
            {"text": "Đi học đi làm mà có hũ kẹo nén Deku này nhâm nhi thì tỉnh cả người luôn á.", "subtitle": "Đi học đi làm nhâm nhi là nhất!", "kw": ["lớp", "ngăn bàn", "túi"], "sfx": "clean_rustle.mp3", "vol": 0.7},
            {"text": "Viên kẹo nhỏ xíu mà có võ, chua chua ngọt ngọt, ăn một viên là muốn ăn cả hũ luôn.", "subtitle": "Chua ngọt béo ngậy — Ăn là ghiền!", "kw": ["viên", "cầm"], "sfx": "clean_crunch.mp3", "vol": 0.8},
            {"text": "Tag ngay đứa bạn mê đồ ngọt vào đây bắt nó bao một hũ đi chứ đợi gì nữa!", "subtitle": "Tag ngay đứa bạn vào đòi bao đi!", "kw": ["hũ", "chia"], "sfx": None, "vol": 0.5}
        ]
    },
    {
        "id": "v3_spelling_fixed",
        "caption": "SỮA CHUA hay SỬA CHUA? 99% người vẫn sai từ đơn giản này 🧐 #keodeku #vuanhvien #chinhta #pelpel",
        "segments": [
            {"text": "SỮA CHUA hay SỬA CHUA? Từ này đơn giản vậy mà vẫn có khối người viết sai đó nha!", "subtitle": "SỮA CHUA hay SỬA CHUA?", "kw": ["cận cảnh", "viên"], "sfx": "clean_rustle.mp3", "vol": 0.5},
            {"text": "Dấu ngã mới là đúng nha các bà ơi. Sửa chua với dấu hỏi là đi sửa đồ rồi đó.", "subtitle": "Dấu NGÃ mới là đúng nha!", "kw": ["nhai", "ăn"], "sfx": "clean_crunch.mp3", "vol": 0.8},
            {"text": "Ăn kẹo Deku vị sữa chua mà viết sai tên em nó là dở rồi. Chốt ngay giỏ hàng đi!", "subtitle": "Đừng viết sai tên em nó nha!", "kw": ["giỏ hàng", "hũ"], "sfx": None, "vol": 0.5}
        ]
    },
    {
        "id": "v4_hands_fixed",
        "caption": "Tiếng 'póc' định mệnh và 10 cánh tay ập tới 💀 #keodeku #funny #schoollife #pelpel #xuhuong",
        "segments": [
            {"text": "Đừng bao giờ mở hũ kẹo Deku này khi lũ bạn đang thức. Chỉ cần một tiếng póc thôi là xong đời.", "subtitle": "Đừng mở kẹo khi lũ bạn đang thức!", "kw": ["mở", "nghe"], "sfx": "clean_rustle.mp3", "vol": 0.8},
            {"text": "Mười cánh tay sẽ ập tới từ mọi phía và hũ kẹo của bạn sẽ bốc hơi trong 3 nốt nhạc.", "subtitle": "Chỉ 1 giây là hũ kẹo bốc hơi!", "kw": ["tay", "chia", "nhiều"], "sfx": "clean_rustle.mp3", "vol": 0.6},
            {"text": "Tag ngay cái đứa hay xin ăn vào đây để cảnh cáo nó đi nào!", "subtitle": "Tag đứa hay xin ăn vào đây!", "kw": ["hũ", "full"], "sfx": "clean_crunch.mp3", "vol": 0.5}
        ]
    },
    {
        "id": "v5_poll_fixed",
        "caption": "Team Màu Hồng hay Màu Vàng? Comment màu bạn yêu nhất nào! 🍓 #keodeku #poll #strawberry #milk #pelpel",
        "segments": [
            {"text": "Đại chiến màu sắc: Team kẹo Deku Màu Hồng dâu hay Màu Vàng sữa mới là chân ái?", "subtitle": "Hồng dâu hay Vàng sữa đỉnh hơn?", "kw": ["hồng", "vàng", "đổ"], "sfx": "clean_rustle.mp3", "vol": 0.5},
            {"text": "Màu hồng thì thơm ngọt, màu vàng thì béo ngậy. Tui là tui chọn cả hai luôn cho lẹ.", "subtitle": "Hồng thơm ngọt — Vàng béo ngậy", "kw": ["nhai", "ăn"], "sfx": "clean_crunch.mp3", "vol": 0.8},
            {"text": "Comment ngay màu sắc yêu thích của bạn xuống đây nhé. Giỏ hàng đang có đủ vị nha!", "subtitle": "Comment màu bạn yêu nhất nào!", "kw": ["hũ", "mix"], "sfx": None, "vol": 0.5}
        ]
    },
    {
        "id": "v6_midnight_fixed",
        "caption": "Cơn đói đêm khuya và cứu tinh mang tên Deku 🌙 #keodeku #midnightcravings #asmr #pelpel",
        "segments": [
            {"text": "12 giờ đêm mà cái bụng cứ cồn cào thèm ngọt thì phải làm sao đây?", "subtitle": "12h đêm mà thèm ngọt thì sao?", "kw": ["tối", "lấy"], "sfx": "clean_rustle.mp3", "vol": 0.7},
            {"text": "Lôi ngay hũ Deku ra nhâm nhi. Vị chua ngọt tỉnh cả người mà lại không lo béo.", "subtitle": "Nhâm nhi Deku — Không lo béo!", "kw": ["ăn", "viên"], "sfx": "clean_crunch.mp3", "vol": 0.9},
            {"text": "Lỡ va phải video này rồi thì chốt đơn ngay một hũ cứu đói đi cưng ơi!", "subtitle": "Chốt ngay 1 hũ cứu đói đi nào!", "kw": ["hũ", "giỏ hàng"], "sfx": None, "vol": 0.5}
        ]
    },
    {
        "id": "v7_asmr_fixed",
        "caption": "ASMR Kẹo sữa chua Deku - Âm thanh gây nghiện 🤫 #keodeku #asmr #foodasmr #pelpel #relax",
        "segments": [
            {"text": "Suỵt! Nhắm mắt lại và thưởng thức âm thanh gây nghiện của kẹo sữa chua Deku nha.", "subtitle": "Cảm nhận âm thanh gây nghiện...", "kw": ["viên", "cầm"], "sfx": "clean_rustle.mp3", "vol": 0.4},
            {"text": "Tiếng cắn giòn tan hòa quyện cùng vị sữa béo ngậy. Nghe thôi đã thấy thèm rồi.", "subtitle": "Giòn tan — Béo ngậy — Thèm xỉu!", "kw": ["nhai", "ăn"], "sfx": "clean_crunch.mp3", "vol": 1.0},
            {"text": "Giỏ hàng Pel Pel đang chờ bạn đó. Trải nghiệm ngay thôi nào!", "subtitle": "Trải nghiệm ngay trong giỏ hàng nha!", "kw": ["đổ", "hũ"], "sfx": "clean_rustle.mp3", "vol": 0.3}
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

def generate_voice_gtts(text, out_path):
    tts = gTTS(text=text, lang='vi')
    tts.save(str(out_path))

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

async def build_single_video(video_meta, all_scenes_meta):
    vid_id = video_meta["id"]; tmp_dir = OUTPUT_DIR / f"_tmp_{vid_id}_rebuild"; tmp_dir.mkdir(parents=True, exist_ok=True)
    label_png = tmp_dir / "label.png"; render_png(LABEL_TEXT, label_png, True)
    local_scenes = list(all_scenes_meta); random.shuffle(local_scenes)
    video_segments, voice_segments, sfx_segments, total_time, used_ids = [], [], [], 0.0, set()
    for i, seg in enumerate(video_meta["segments"], 1):
        voice_path = tmp_dir / f"voice_{i:02d}.mp3"; generate_voice_gtts(seg["text"], voice_path)
        dur = get_dur(voice_path); render_png(seg["subtitle"], tmp_dir / f"sub_{i:02d}.png", False)
        clip_path = tmp_dir / f"clip_{i:02d}.mp4"; picked_paths = pick_suitable_scenes(local_scenes, dur, used_ids, seg["kw"])
        build_segment_video(picked_paths, dur, label_png, tmp_dir / f"sub_{i:02d}.png", clip_path, i, len(video_meta["segments"]))
        video_segments.append(clip_path); voice_segments.append((voice_path, total_time))
        if seg["sfx"]: sfx_segments.append((SFX_DIR / seg["sfx"], total_time, seg["vol"]))
        total_time += dur
    concat_voice = tmp_dir / "all_voice.mp3"
    with open(tmp_dir / "v_list.txt", "w") as f:
        for v, _ in voice_segments: f.write(f"file '{v.resolve()}'\n")
    run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(tmp_dir / "v_list.txt"), "-c:a", "libmp3lame", "-q:a", "2", str(concat_voice)])
    ambience = SFX_DIR / "clean_ambience_loop.mp3"
    f_complex = f"[0:a]volume=2.0[v];[1:a]volume=0.08[bg];"
    m_inputs = f"[v][bg]"
    s_args = []
    for i, (path, start, vol) in enumerate(sfx_segments):
        s_args.extend(["-i", str(path)])
        idx = i + 2
        f_complex += f"[{idx}:a]adelay={int(start*1000)}|{int(start*1000)},volume={vol}[s{i}];"
        m_inputs += f"[s{i}]"
    f_complex += f"{m_inputs}amix=inputs={2+len(sfx_segments)}:duration=longest[outa]"
    final_audio = tmp_dir / "final_audio.m4a"
    run(["ffmpeg", "-y", "-i", str(concat_voice), "-i", str(ambience), *s_args, "-filter_complex", f_complex, "-map", "[outa]", "-c:a", "aac", "-b:a", "192k", "-t", str(total_time), str(final_audio)])
    cl_list = tmp_dir / "cl_list.txt"
    with open(cl_list, "w") as f:
        for c in video_segments: f.write(f"file '{c.resolve()}'\n")
    all_video = tmp_dir / "all_video.mp4"
    run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(cl_list), "-c", "copy", str(all_video)])
    final_path = FINAL_DIR / f"{video_meta['caption']}.mp4"
    run(["ffmpeg", "-y", "-i", str(all_video), "-i", str(final_audio), "-c:v", "copy", "-c:a", "copy", "-t", str(total_time), "-movflags", "+faststart", str(final_path)])
    print(f"✅ Rebuilt: {final_path.name}")

async def main():
    FINAL_DIR.mkdir(parents=True, exist_ok=True); all_scenes_meta = load_all_scenes()
    for v_meta in VIDEOS_DATA: await build_single_video(v_meta, all_scenes_meta)

if __name__ == "__main__": asyncio.run(main())
