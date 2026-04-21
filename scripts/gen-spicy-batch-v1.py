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
SFX_DIR = ROOT / "assets" / "audio" / "sfx"
SPEED_FACTOR = 1.75

LABEL_Y = 280

VIDEOS_DATA = [
    {
        "product": "bo-mieng-cay",
        "label": "BÒ MIẾNG CAY • PEL PEL",
        "caption": "Bò miếng mềm siêu cay, nhai cực phê ⚡️ #bomiengcay #khobo #anvat #pelpel #asmr",
        "segments": [
            {"text": "Nhìn cái miếng khô bò mềm mướt, đẫm sốt cay nồng này xem, ai mà chịu cho nổi?", "subtitle": "Khô bò mềm mướt — Cay nồng!", "kw": ["miếng", "bò"], "sfx": "clean_rustle.mp3", "vol": 0.6},
            {"text": "Cắn một miếng là vị ngọt của bò hòa quyện cùng vị cay xè lưỡi, tỉnh cả người luôn.", "subtitle": "Cắn 1 miếng — Cay xè lưỡi!", "kw": ["nhai", "ăn"], "sfx": "clean_crunch.mp3", "vol": 1.0},
            {"text": "Chốt ngay giỏ hàng Pel Pel để trải nghiệm cực phẩm này nha cưng ơi!", "subtitle": "Chốt ngay giỏ hàng nha cưng!", "kw": ["giỏ hàng", "combo"], "sfx": None, "vol": 0.5}
        ]
    },
    {
        "product": "tam-cay-den",
        "label": "TĂM CAY ĐEN • PEL PEL",
        "caption": "Tăm cay đen Bà Tuyết giòn rụm, vị lạ cực cuốn ⚡️ #tamcayden #tamcaybatuyet #pelpel #asmr #anvat",
        "segments": [
            {"text": "Tăm cay đen phiên bản mới đang hot rần rần đây. Màu đen huyền bí mà vị thì đỉnh chóp.", "subtitle": "Tăm cay đen HOT nhất lúc này!", "kw": ["đen", "tăm"], "sfx": "clean_rustle.mp3", "vol": 0.7},
            {"text": "Tiếng nhai giòn rụm rụm, vị mặn ngọt cay cay đậm đà, ăn một lần là nghiện luôn á.", "subtitle": "Nhai giòn rụm — Vị đậm đà!", "kw": ["nhai", "giòn"], "sfx": "clean_crunch.mp3", "vol": 0.9},
            {"text": "Đừng bỏ qua siêu phẩm này tại giỏ hàng Pel Pel nha mng ơi!", "subtitle": "Check ngay giỏ hàng Pel Pel nha!", "kw": ["giỏ hàng", "full"], "sfx": None, "vol": 0.5}
        ]
    },
    {
        "product": "chan-vit-cay",
        "label": "CHÂN VỊT CAY • PEL PEL",
        "caption": "Chân vịt cay Dakos dai giòn, ăn là ghiền ⚡️ #chanvitcay #dakos #anvat #pelpel #asmr",
        "segments": [
            {"text": "Team mê chân vịt cay thì tuyệt đối không được bỏ qua cực phẩm Dakos này nha.", "subtitle": "Chân vịt cay Dakos cực phẩm!", "kw": ["vịt", "chân"], "sfx": "clean_rustle.mp3", "vol": 0.6},
            {"text": "Chân vịt dai giòn sần sật, thấm đẫm sốt cay Trung Hoa, nhâm nhi lúc xem phim là hết bài.", "subtitle": "Dai giòn sần sật — Sốt cực cuốn!", "kw": ["nhai", "cận cảnh"], "sfx": "clean_crunch.mp3", "vol": 1.0},
            {"text": "Link ở giỏ hàng Pel Pel đang có đủ combo nha. Múc ngay thôi!", "subtitle": "Link giỏ hàng đủ combo nha!", "kw": ["giỏ hàng", "combo"], "sfx": None, "vol": 0.5}
        ]
    }
]

def run(cmd):
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def render_png(text, out, is_label=True, label_text=""):
    img = Image.new("RGBA", (900, 140) if is_label else (1000, 200), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    for p in ["/System/Library/Fonts/Supplemental/Arial Unicode.ttf", "/System/Library/Fonts/HelveticaNeue.ttc"]:
        if Path(p).exists(): font = ImageFont.truetype(p, 58 if is_label else 62); break
    else: font = ImageFont.load_default()
    if is_label:
        draw.rounded_rectangle([(0, 0), (899, 139)], radius=70, fill=(255, 107, 0, 220))
        bbox = draw.textbbox((0, 0), label_text, font=font)
        draw.text(((900-(bbox[2]-bbox[0]))//2, (140-(bbox[3]-bbox[1]))//2-bbox[1]), label_text, font=font, fill=(255, 255, 255, 255), stroke_width=3, stroke_fill=(0, 0, 0, 255))
    else:
        draw.rounded_rectangle([(20, 50), (980, 170)], radius=25, fill=(0, 0, 0, 180))
        bbox = draw.textbbox((0, 0), text, font=font)
        draw.text(((1000-(bbox[2]-bbox[0]))//2, (200-(bbox[3]-bbox[1]))//2-bbox[1]), text, font=font, fill=(255, 255, 255, 255), stroke_width=2, stroke_fill=(0, 0, 0, 255))
    img.save(out, "PNG")

def generate_voice_fast(text, out_path):
    tmp_v = out_path.with_name(f"{out_path.stem}_tmp.mp3")
    gTTS(text=text, lang='vi').save(str(tmp_v))
    run(["ffmpeg", "-y", "-i", str(tmp_v), "-filter:a", f"atempo={SPEED_FACTOR}", str(out_path)])

def get_dur(p):
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", str(p)], capture_output=True, text=True).stdout.strip() or 0)

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

async def main():
    for v_meta in VIDEOS_DATA:
        p_slug = v_meta["product"]
        print(f"\n🚀 Dựng Video: {p_slug}")
        out_dir = ROOT / "assets" / "products" / p_slug / "output"
        final_dir = out_dir / "final"; final_dir.mkdir(parents=True, exist_ok=True)
        tmp_dir = out_dir / "_tmp_fast"; tmp_dir.mkdir(parents=True, exist_ok=True)
        
        label_png = tmp_dir / "label.png"
        render_png("", label_png, True, v_meta["label"])
        
        scene_lib = ROOT / "assets" / "products" / p_slug / "competitor-scenes"
        all_scenes = []
        for jf in scene_lib.rglob("*.json"):
            try:
                with jf.open() as f: data = json.load(f)
                mp4 = jf.with_suffix(".mp4")
                if mp4.exists(): data["_mp4_path"] = mp4; all_scenes.append(data)
            except: continue
        random.shuffle(all_scenes)
        
        video_segments, voice_segments, sfx_segments, total_time, used_ids = [], [], [], 0.0, set()
        for i, seg in enumerate(v_meta["segments"], 1):
            voice_path = tmp_dir / f"voice_{i:02d}.mp3"
            generate_voice_fast(seg["text"], voice_path)
            dur = get_dur(voice_path); sub_png = tmp_dir / f"sub_{i:02d}.png"
            render_png(seg["subtitle"], sub_png, False)
            clip_path = tmp_dir / f"clip_{i:02d}.mp4"
            # Pick scenes logic
            picked = []
            cur_s_dur = 0.0
            for s in all_scenes:
                sid = f"{s.get('source_video_id')}_{s.get('scene_index')}"
                if sid not in used_ids:
                    picked.append(s["_mp4_path"]); used_ids.add(sid)
                    cur_s_dur += s.get("duration_sec", 0)
                    if cur_s_dur >= dur: break
            if not picked: picked = [all_scenes[0]["_mp4_path"]] # fallback
            
            build_segment_video(picked, dur, label_png, sub_png, clip_path, i, len(v_meta["segments"]))
            video_segments.append(clip_path); voice_segments.append((voice_path, total_time))
            if seg["sfx"]: sfx_segments.append((SFX_DIR / seg["sfx"], total_time, seg["vol"]))
            total_time += dur
            
        # Audio Mix
        v_list = tmp_dir / "v_list.txt"
        with open(v_list, "w") as f:
            for v, _ in voice_segments: f.write(f"file '{v.resolve()}'\n")
        concat_voice = tmp_dir / "all_voice.mp3"
        run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(v_list), "-c:a", "libmp3lame", "-q:a", "2", str(concat_voice)])
        
        final_audio = tmp_dir / "final_audio.m4a"; ambience = SFX_DIR / "clean_ambience_loop.mp3"
        f_complex = f"[0:a]volume=2.0[v];[1:a]volume=0.1[bg];"
        m_inputs = f"[v][bg]"
        s_args = []
        for i, (path, start, vol) in enumerate(sfx_segments):
            s_args.extend(["-i", str(path)]); f_complex += f"[{i+2}:a]adelay={int(start*1000)}|{int(start*1000)},volume={vol}[s{i}];"
            m_inputs += f"[s{i}]"
        f_complex += f"{m_inputs}amix=inputs={2+len(sfx_segments)}:duration=longest[outa]"
        run(["ffmpeg", "-y", "-i", str(concat_voice), "-i", str(ambience), *s_args, "-filter_complex", f_complex, "-map", "[outa]", "-c:a", "aac", "-b:a", "192k", "-t", str(total_time), str(final_audio)])
        
        cl_list = tmp_dir / "cl_list.txt"
        with open(cl_list, "w") as f:
            for c in video_segments: f.write(f"file '{c.resolve()}'\n")
        all_video = tmp_dir / "all_video.mp4"
        run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(cl_list), "-c", "copy", str(all_video)])
        
        final_path = final_dir / (v_meta["caption"] + ".mp4")
        run(["ffmpeg", "-y", "-i", str(all_video), "-i", str(final_audio), "-c:v", "copy", "-c:a", "copy", "-t", str(total_time), "-movflags", "+faststart", str(final_path)])
        print(f"✅ Xong: {final_path.name}")
        # Clean tmp
        run(["rm", "-rf", str(tmp_dir)])

if __name__ == "__main__": asyncio.run(main())
