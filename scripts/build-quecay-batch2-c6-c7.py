"""
Build 2 concept mới cho que-cay (Concept 6 & 7).
Kế thừa quy chuẩn từ build-quecay-concepts-1-2-3.py.
Cải tiến: Multi-scene per segment & Diversity fix.
"""
from __future__ import annotations
import argparse
import json
import os
import random
import re
import subprocess
import sys
import wave
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent

# Setup Environment
_env = ROOT / ".env"
if _env.exists():
    for line in _env.read_text().splitlines():
        if "=" in line and not line.strip().startswith("#"):
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())

PRODUCT = ROOT / "assets" / "products" / "que-cay"
COMP_BEHEOBU = ROOT / "assets" / "scene-library" / "que_cay"
COMP_YEN = PRODUCT / "competitor-scenes" / "yen_doanvathot"
FINAL = PRODUCT / "output" / "final"

W, H = 1080, 1920
FPS = 30
FONT = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"

TTS_VOICE = "vi-VN-NamMinhNeural"
TTS_RATE = "+10%"

PRODUCT_LABEL = "QUE CAY - PEL PEL"
LABEL_CANVAS = (900, 140)
LABEL_COLOR = (255, 107, 0, 220)
LABEL_FONT_SIZE = 58
LABEL_Y = 280

SUBTITLE_CANVAS = (1000, 200)
SUBTITLE_BG = (0, 0, 0, 180)
SUBTITLE_FONT_SIZE = 62
SUBTITLE_Y = 1580

CONCEPTS = {
    6: {
        "slug": "nham-mat-chon-do",
        "tint": (30, 80, 200),
        "hue_shift": 15,
        "caption": "Nhắm mắt chọn đại 1 gói - Trúng gói nào ăn hết gói đó! 🔥 Thử thách cho team mê đồ cay đây cưng ơi #quecay #blindchoice #thuthachanvat #anvat #fyp #xuhuong",
        "segments": [
            {"voice": "Nhắm mắt chọn đại một gói nha, trúng gói nào ăn hết gói đó luôn!", "subtitle": "NHẮM MẮT CHỌN ĐẠI!\nTRÚNG GÓI NÀO ĂN GÓI ĐÓ", "keywords": ["que cay", "quecay"]},
            {"voice": "Gói đầu tiên... Ôi chu choa, Vương Thần Long siêu cay luôn!", "subtitle": "GÓI 1: VƯƠNG THẦN LONG\nSIÊU CAY LUÔN NÈ", "keywords": ["thần long", "thanlong"]},
            {"voice": "Gói tiếp theo... Hằng Đại huyền thoại, dẻo dẻo cay cay cuốn cực!", "subtitle": "GÓI 2: HẰNG ĐẠI\nDẺO CAY CUỐN CỰC", "keywords": ["hangdai", "hằng đại"]},
            {"voice": "Dám chơi không cưng ơi? Tag ngay đứa bạn vào thách thức nha! Follow em để xem thêm nhiều trò hay với que cay!", "subtitle": "DÁM CHƠI KHÔNG?\nTAG BẠN + FOLLOW EM NHÉ!", "keywords": ["quecay"]},
        ],
    },
    7: {
        "slug": "ban-than-an-chuc",
        "tint": (200, 30, 30),
        "hue_shift": -10,
        "caption": "Tag ngay đứa bạn chuyên 'ăn chực' que cay vào đây! 🐍 Có gói nào là hếttttt gói đó luôn á trời #quecay #banthan #meme #anvat #doanvat #fyp",
        "segments": [
            {"voice": "Trong nhóm lúc nào cũng có một đứa... chuyên gia ăn chực que cay!", "subtitle": "LUÔN CÓ 1 ĐỨA...\nCHUYÊN ĂN CHỰC QUE CAY", "keywords": ["que cay", "ăn"]},
            {"voice": "Mới xé bao bì ra chưa kịp ăn miếng nào là nó xuất hiện như một vị thần!", "subtitle": "MỚI XÉ BAO BÌ...\nNÓ ĐÃ XUẤT HIỆN!", "keywords": ["xé", "cay"]},
            {"voice": "Thôi thì mời đại hiệp, Pel Pel có đủ loại cho mấy người ăn luôn á!", "subtitle": "MỜI ĐẠI HIỆP!\nPEL PEL CÂN TẤT", "keywords": ["mlem", "quecay"]},
            {"voice": "Tag ngay đứa đó vào đây 'tế' nhẹ cái đi cưng! Đừng quên follow em để săn deal que cay giá hời nha!", "subtitle": "TAG 'ĐỨA ĐÓ' VÀO ĐÂY!\nFOLLOW EM SĂN DEAL NHÉ", "keywords": ["quecay"]},
        ],
    },
}

def run(cmd, check=True):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if check and r.returncode != 0:
        print("CMD FAIL:", " ".join(map(str, cmd))); print(r.stderr[-500:]); raise SystemExit(1)
    return r

def probe_dur(path: Path) -> float:
    r = run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "json", str(path)])
    return float(json.loads(r.stdout)["format"]["duration"])

def _tts_single(text: str, voice: str, rate: str | None, out_path: Path, retries: int = 3) -> bool:
    import time as _time
    for attempt in range(retries):
        cmd = [sys.executable, "-m", "edge_tts", "--voice", voice]
        if rate: cmd += ["--rate", rate]
        cmd += ["--text", text, "--write-media", str(out_path)]
        r = run(cmd, check=False)
        if r.returncode == 0 and out_path.exists() and out_path.stat().st_size > 1000: return True
        _time.sleep(1 + attempt)
    return False

def _gemini_tts(text: str, out_path: Path) -> bool:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key: return False
    try:
        from google import genai
        from google.genai import types
        client = genai.Client(api_key=api_key)
        resp = client.models.generate_content(
            model="gemini-2.5-flash-preview-tts", contents=text,
            config=types.GenerateContentConfig(
                response_modalities=["AUDIO"],
                speech_config=types.SpeechConfig(voice_config=types.VoiceConfig(prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name="Kore"))),
            ),
        )
        pcm = next((p.inline_data.data for p in resp.candidates[0].content.parts if hasattr(p, "inline_data") and p.inline_data), None)
        if not pcm: return False
        wav_tmp = out_path.with_suffix(".gemini.wav")
        with wave.open(str(wav_tmp), "wb") as wf:
            wf.setnchannels(1); wf.setsampwidth(2); wf.setframerate(24000); wf.writeframes(pcm)
        subprocess.run(["ffmpeg", "-y", "-i", str(wav_tmp), "-c:a", "libmp3lame", "-b:a", "192k", str(out_path)], capture_output=True)
        wav_tmp.unlink(missing_ok=True)
        return True
    except: return False

def gen_voice(text: str, out_path: Path):
    if _gemini_tts(text, out_path): return
    if _tts_single(text, TTS_VOICE, TTS_RATE, out_path, retries=5): return
    est_dur = max(3.0, len(text) / 10.0)
    run(["ffmpeg", "-y", "-f", "lavfi", "-i", f"anullsrc=r=44100:cl=mono", "-t", f"{est_dur:.3f}", "-c:a", "libmp3lame", "-b:a", "128k", str(out_path)])

def load_all_scenes() -> dict:
    pools = {"beheobu0102": [], "yen_doanvathot": []}
    for d in (COMP_BEHEOBU, COMP_YEN):
        if not d.exists(): continue
        for j in d.glob("*.json"):
            try:
                m = json.loads(j.read_text()); a = m.get("source_author")
                if a not in pools: continue
                mp4 = j.with_suffix(".mp4")
                if mp4.exists(): pools[a].append((m.get("source_views") or 0, m.get("duration_sec") or 0, m.get("source_video_id"), mp4, (m.get("source_caption") or "").lower()))
            except: continue
    return pools

def pick_scenes_for_dur(pools: dict, keywords: list[str], used_vids: set, target_dur: float, seed: int) -> list[Path]:
    rng = random.Random(seed)
    all_matches = []
    for a in ["beheobu0102", "yen_doanvathot"]:
        all_matches.extend([e for e in pools[a] if e[2] not in used_vids and any(k.lower() in e[4] for k in keywords)])
    if not all_matches:
        for a in ["beheobu0102", "yen_doanvathot"]: all_matches.extend([e for e in pools[a] if e[2] not in used_vids])
    
    rng.shuffle(all_matches)
    picked, cur_dur = [], 0.0
    min_sc = 2 if target_dur > 3.0 else 1
    for m in all_matches:
        picked.append(m[3]); used_vids.add(m[2]); cur_dur += m[1]
        if cur_dur >= target_dur and len(picked) >= min_sc: break
    if not picked: # Fallback
        for a in pools:
            if pools[a]: picked.append(rng.choice(pools[a])[3]); break
    return picked

def scene_to_canvas_trim(src: Path, duration: float, out: Path, hue_shift: int = 0, zoom: float = 1.0):
    src_dur = probe_dur(src)
    vf = f"scale={W}:{H}:force_original_aspect_ratio=decrease,pad={W}:{H}:(ow-iw)/2:(oh-ih)/2:color=black,setsar=1,fps={FPS}"
    if zoom != 1.0:
        zw, zh = int(W * zoom), int(H * zoom)
        vf += f",scale={zw}:{zh},crop={W}:{H}:{(zw-W)//2}:{(zh-H)//2}"
    if hue_shift: vf += f",hue=h={hue_shift}"
    if src_dur >= duration:
        run(["ffmpeg", "-y", "-i", str(src), "-t", f"{duration:.3f}", "-vf", vf, "-an", "-c:v", "libx264", "-preset", "veryfast", "-pix_fmt", "yuv420p", str(out)])
    else:
        repeat = int(duration / src_dur) + 1
        lf = out.parent / f"_l_{src.stem}.txt"; lf.write_text(f"file '{src.as_posix()}'\n" * repeat)
        tmp = out.parent / f"_l_{src.stem}.mp4"
        run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(lf), "-c:v", "libx264", "-preset", "veryfast", "-pix_fmt", "yuv420p", "-an", str(tmp)])
        run(["ffmpeg", "-y", "-i", str(tmp), "-t", f"{duration:.3f}", "-vf", vf, "-an", "-c:v", "libx264", "-preset", "veryfast", "-pix_fmt", "yuv420p", str(out)])

def overlay_subtitle(video: Path, sub_png: Path, out: Path):
    run(["ffmpeg", "-y", "-i", str(video), "-i", str(sub_png), "-filter_complex", f"[0:v][1:v]overlay=(W-w)/2:{SUBTITLE_Y}", "-c:v", "libx264", "-preset", "veryfast", "-pix_fmt", "yuv420p", "-an", str(out)])

def render_product_label(text: str, out_png: Path):
    img = Image.new("RGBA", LABEL_CANVAS, (0, 0, 0, 0)); d = ImageDraw.Draw(img); font = ImageFont.truetype(FONT, LABEL_FONT_SIZE)
    d.rounded_rectangle([0, 0, LABEL_CANVAS[0]-1, LABEL_CANVAS[1]-1], radius=LABEL_CANVAS[1]//2, fill=LABEL_COLOR)
    b = d.textbbox((0, 0), text, font=font, stroke_width=3)
    d.text(((LABEL_CANVAS[0]-(b[2]-b[0]))//2, (LABEL_CANVAS[1]-(b[3]-b[1]))//2-4), text, font=font, fill=(255,255,255,255), stroke_width=3, stroke_fill=(0,0,0,255))
    img.save(out_png)

def render_subtitle_png(text: str, out: Path):
    img = Image.new("RGBA", SUBTITLE_CANVAS, (0, 0, 0, 0)); d = ImageDraw.Draw(img); font = ImageFont.truetype(FONT, SUBTITLE_FONT_SIZE)
    d.rounded_rectangle([0, 0, SUBTITLE_CANVAS[0]-1, SUBTITLE_CANVAS[1]-1], radius=25, fill=SUBTITLE_BG)
    lines = text.split("\n"); line_h = 74; y = (SUBTITLE_CANVAS[1]-line_h*len(lines))//2
    for l in lines:
        b = d.textbbox((0, 0), l, font=font, stroke_width=2)
        d.text(((SUBTITLE_CANVAS[0]-(b[2]-b[0]))//2, y), l, font=font, fill=(255,255,255,255), stroke_width=2, stroke_fill=(0,0,0,255))
        y += line_h
    img.save(out)

def concat_videos(parts: list[Path], out: Path, tmp: Path):
    lf = tmp / f"vc_{random.randint(0,999)}.txt"; lf.write_text("\n".join(f"file '{p.as_posix()}'" for p in parts) + "\n")
    run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(lf), "-c:v", "libx264", "-preset", "veryfast", "-pix_fmt", "yuv420p", "-an", str(out)])

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--concept", type=int, choices=[6, 7], required=True); args = ap.parse_args()
    cfg = CONCEPTS[args.concept]; print(f"── Build Batch 2 Concept {args.concept} ──")
    tmp = PRODUCT / "output" / f"_tmp_c{args.concept}"; tmp.mkdir(parents=True, exist_ok=True); FINAL.mkdir(parents=True, exist_ok=True)
    pools = load_all_scenes(); used_vids = set(); voice_parts, video_parts = [], []; tail = 0.15
    for i, seg in enumerate(cfg["segments"], 1):
        v_mp3 = tmp / f"v_{i:02d}.mp3"; gen_voice(seg["voice"], v_mp3); v_dur = probe_dur(v_mp3); t_dur = v_dur + tail
        v_pad = tmp / f"v_{i:02d}_p.m4a"; run(["ffmpeg", "-y", "-i", str(v_mp3), "-af", f"apad=pad_dur={tail:.3f}", "-t", f"{t_dur:.3f}", "-c:a", "aac", "-b:a", "192k", str(v_pad)])
        voice_parts.append(v_pad); scenes = pick_scenes_for_dur(pools, seg["keywords"], used_vids, t_dur, args.concept*100+i)
        print(f"  [seg {i}] {len(scenes)} scenes"); raw_v = tmp / f"raw_{i:02d}.mp4"
        if len(scenes) == 1: scene_to_canvas_trim(scenes[0], t_dur, raw_v, hue_shift=cfg["hue_shift"], zoom=1.0+i*0.02)
        else:
            ps = []; d_p = t_dur / len(scenes)
            for idx, s in enumerate(scenes):
                p = tmp / f"p_{i:02d}_{idx}.mp4"; scene_to_canvas_trim(s, d_p, p, hue_shift=cfg["hue_shift"], zoom=1.0+i*0.02+idx*0.01); ps.append(p)
            concat_videos(ps, raw_v, tmp)
        sub_p = tmp / f"s_{i:02d}.png"; render_subtitle_png(seg["subtitle"], sub_p); v_f = tmp / f"seg_{i:02d}.mp4"; overlay_subtitle(raw_v, sub_p, v_f); video_parts.append(v_f)
    merged_v, merged_a = tmp / "m_v.mp4", tmp / "m_a.m4a"
    concat_videos(video_parts, merged_v, tmp)
    inputs = []
    for p in voice_parts: inputs += ["-i", str(p)]
    run(["ffmpeg", "-y"] + inputs + ["-filter_complex", f"concat=n={len(voice_parts)}:v=0:a=1[out]", "-map", "[out]", "-c:a", "aac", "-b:a", "192k", str(merged_a)])
    label_p = tmp / "lbl.png"; render_product_label(PRODUCT_LABEL, label_p); final_v_l = tmp / "final_v_l.mp4"
    run(["ffmpeg", "-y", "-i", str(merged_v), "-i", str(label_p), "-filter_complex", f"[0:v][1:v]overlay=(W-w)/2:{LABEL_Y}", "-c:v", "libx264", "-preset", "veryfast", "-pix_fmt", "yuv420p", "-an", str(final_v_l)])
    f_path = FINAL / f"{cfg['caption']}.mp4"
    run(["ffmpeg", "-y", "-i", str(final_v_l), "-i", str(merged_a), "-c:v", "copy", "-c:a", "aac", "-shortest", str(f_path)])
    print(f"✓ {f_path.name}")
if __name__ == "__main__": main()
