"""
Build 3 concept Vua Tiếng Việt mới (Concept 8, 9, 10).
Quy chuẩn: Hook -> Review -> Answer -> CTA.
Cải tiến: Multi-scene, Gemini TTS Priority.
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
    8: {
        "slug": "nuoc-xot-hay-nuoc-sot",
        "tint": (200, 100, 30),
        "hue_shift": 5,
        "caption": "Review Que Cay đẫm nước xốt siêu cay tê 🌶️ Đố bạn NƯỚC XỐT hay NƯỚC SỐT mới đúng? #quecay #reviewanvat #quecayvuongthanlong #quecayhangdai #doanvat #fyp",
        "segments": [
            {"voice": "Nước xốt que cay đẫm vị, nhìn là thèm mà viết sai là quê lắm nha công chúa ơi!", "subtitle": "NƯỚC XỐT ĐẪM VỊ!\nVIẾT SAI LÀ QUÊ NHA", "keywords": ["que cay", "xốt", "sốt"]},
            {"voice": "Nhìn cái nước xốt óng ánh, cay tê đầu lưỡi này đi. Là NƯỚC XỐT hay NƯỚC SỐT mới đúng ta?", "subtitle": "NHÌN NƯỚC XỐT NÀY ĐI!\nLÀ XỐT HAY SỐT?", "keywords": ["mlem", "ăn"]},
            {"voice": "Đáp án là NƯỚC XỐT nha. Cắn một miếng que cay chuẩn vị xốt Pel Pel là bao ghiền luôn!", "subtitle": "ĐÁP ÁN: NƯỚC XỐT!\nCHUẨN VỊ LÀ BAO GHIỀN", "keywords": ["quecay"]},
            {"voice": "Đồ ngon thì phải viết đúng mới sành. Click giỏ hàng hốt ngay combo que cay đẫm xốt nè!", "subtitle": "VIẾT ĐÚNG MỚI SÀNH!\nCLICK GIỎ HÀNG NGAY NHA", "keywords": ["quecay"]},
        ],
    },
    9: {
        "slug": "gian-giua-hay-dan-dua",
        "tint": (30, 150, 50),
        "hue_shift": -8,
        "caption": "Ăn Que Cay Pel Pel cay đến mức nước mắt giàn giụa luôn á trời 😭 Đố bạn GIÀN GIỤA hay DÀN DỤA? #quecay #reviewanvat #quecayvuongthanlong #cayxe #anvat #fyp",
        "segments": [
            {"voice": "Que cay siêu cấp, ăn một miếng mà nước mắt chảy ròng ròng vì đã quá nè!", "subtitle": "QUE CAY SIÊU CẤP!\nĂN LÀ ĐÃ CÁI NƯA", "keywords": ["giòn", "cay"]},
            {"voice": "Nước mắt chảy GIÀN GIỤA hay là DÀN DỤA mới đúng đây? Cay xè mà cuốn không dừng được luôn!", "subtitle": "CHẢY GIÀN GIỤA\nHAY LÀ DÀN DỤA?", "keywords": ["giòn", "ăn"]},
            {"voice": "Chính xác là GIÀN GIỤA nha. Cay tê tái, ăn là ghiền, đúng chất que cay Pel Pel tự luyện!", "subtitle": "ĐÁP ÁN: GIÀN GIỤA!\nĂN LÀ GHIỀN LUÔN", "keywords": ["quecay"]},
            {"voice": "Thèm cái cảm giác này thì vào giỏ hàng chốt đơn liền đi cưng ơi!", "subtitle": "THÈM LÀ PHẢI CHỐT!\nVÀO GIỎ HÀNG NGAY NHA", "keywords": ["quecay"]},
        ],
    },
    10: {
        "slug": "sac-sua-hay-xac-xua",
        "tint": (180, 40, 40),
        "hue_shift": 12,
        "caption": "Mùi que cay nồng nặc SẶC SỤA là biết hàng chuẩn rồi 🌶️ Đố bạn SẶC SỤA hay XẶC XỤA? #quecay #reviewanvat #quecayhangdai #anvattuoitho #doanvat #fyp",
        "segments": [
            {"voice": "Mở túi que cay ra là mùi ớt nồng nặc bốc lên, sướng cái mũi cực kỳ luôn!", "subtitle": "MỞ TÚI LÀ THẤY SƯỚNG!\nMÙI ỚT SIÊU NỒNG NÀY", "keywords": ["cay", "quecay"]},
            {"voice": "Mùi cay nồng bốc lên SẶC SỤA hay là XẶC XỤA?", "subtitle": "LÀ SẶC SỤA\nHAY LÀ XẶC XỤA?", "keywords": ["xé", "ăn"]},
            {"voice": "Viết đúng mới là dân sành ăn que cay nha!", "subtitle": "VIẾT ĐÚNG MỚI LÀ\nDÂN SÀNH ĂN NHA", "keywords": ["quecay", "mlem"]},
            {"voice": "Đáp án là SẶC SỤA nha. Nhìn miếng que cay đỏ âu, cắn một cái là phê chữ ê kéo dài!", "subtitle": "ĐÁP ÁN: SẶC SỤA!\nCẮN MỘC CÁI LÀ PHÊ", "keywords": ["quecay"]},
            {"voice": "Hàng chuẩn là phải nồng như vầy nè. Click giỏ hàng săn deal hot ngay đi mấy bà!", "subtitle": "HÀNG CHUẨN LÀ ĐÂY!\nCLICK GIỎ HÀNG NGAY NHA", "keywords": ["quecay"]},
        ],
    },

}

def run(cmd, check=True):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if check and r.returncode != 0: print(r.stderr); raise SystemExit(1)
    return r

def probe_dur(path: Path) -> float:
    r = run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "json", str(path)])
    return float(json.loads(r.stdout)["format"]["duration"])

def _tts_single(text: str, voice: str, rate: str | None, out_path: Path, retries: int = 5) -> bool:
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
        wav_t = out_path.with_suffix(".gemini.wav")
        with wave.open(str(wav_t), "wb") as wf:
            wf.setnchannels(1); wf.setsampwidth(2); wf.setframerate(24000); wf.writeframes(pcm)
        subprocess.run(["ffmpeg", "-y", "-i", str(wav_t), "-c:a", "libmp3lame", "-b:a", "192k", str(out_path)], capture_output=True)
        wav_t.unlink(missing_ok=True)
        return True
    except: return False

def gen_voice(text: str, out_path: Path):
    """Gia cố Voice: Gemini -> Edge Nam -> Edge Nữ -> Retry."""
    print(f"    [TTS] {text[:40]}...")
    
    # 1. Gemini
    if _gemini_tts(text, out_path):
        print(f"      ✓ Gemini OK")
        return

    # 2. Edge TTS (Retry 10 lần, đổi giọng nếu fail)
    voices = ["vi-VN-NamMinhNeural", "vi-VN-HoaiMyNeural"]
    for attempt in range(10):
        v = voices[attempt % 2]
        if _tts_single(text, v, TTS_RATE, out_path, retries=1):
            print(f"      ✓ Edge TTS OK ({v}, attempt {attempt+1})")
            return
        print(f"      ! Edge TTS fail (attempt {attempt+1}), retrying...")
        import time; time.sleep(1)

    # 3. SILENT fallback (Cực chẳng đã)
    est_dur = max(3.5, len(text) / 10.0)
    print(f"      ⚠ SILENT FALLBACK ({est_dur:.1f}s)")
    run(["ffmpeg", "-y", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=mono", "-t", f"{est_dur:.3f}", "-c:a", "libmp3lame", str(out_path)])

def load_all_scenes() -> dict:
    pools = {"beheobu0102": [], "yen_doanvathot": []}
    for d in (COMP_BEHEOBU, COMP_YEN):
        if not d.exists(): continue
        for j in d.glob("*.json"):
            try:
                m = json.loads(j.read_text()); a = m.get("source_author")
                if a in pools: pools[a].append((m.get("source_views") or 0, m.get("duration_sec") or 0, m.get("source_video_id"), j.with_suffix(".mp4"), (m.get("source_caption") or "").lower()))
            except: continue
    return pools

def pick_scenes(pools: dict, keywords: list[str], used: set, dur: float, seed: int) -> list[Path]:
    rng = random.Random(seed); matches = []
    for a in pools: matches.extend([e for e in pools[a] if e[2] not in used and any(k in e[4] for k in keywords)])
    if not matches:
        for a in pools: matches.extend([e for e in pools[a] if e[2] not in used])
    rng.shuffle(matches); picked, cur = [], 0.0
    for m in matches:
        picked.append(m[3]); used.add(m[2]); cur += m[1]
        if cur >= dur and len(picked) >= (2 if dur > 3 else 1): break
    return picked if picked else [random.choice(pools["beheobu0102"])[3]]

def scene_to_v(src: Path, dur: float, out: Path, hue: int, zoom: float):
    vf = f"scale={W}:{H}:force_original_aspect_ratio=decrease,pad={W}:{H}:(ow-iw)/2:(oh-ih)/2:color=black,setsar=1,fps={FPS},hue=h={hue}"
    if zoom != 1.0: zw, zh = int(W*zoom), int(H*zoom); vf += f",scale={zw}:{zh},crop={W}:{H}:{(zw-W)//2}:{(zh-H)//2}"
    s_dur = probe_dur(src)
    if s_dur >= dur: run(["ffmpeg", "-y", "-i", str(src), "-t", f"{dur:.3f}", "-vf", vf, "-an", "-c:v", "libx264", "-preset", "veryfast", str(out)])
    else:
        lf = out.parent / f"l_{src.stem}.txt"; lf.write_text(f"file '{src.as_posix()}'\n" * (int(dur/s_dur)+1))
        tmp = out.parent / f"l_{src.stem}.mp4"
        run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(lf), "-c:v", "libx264", "-preset", "veryfast", "-an", str(tmp)])
        run(["ffmpeg", "-y", "-i", str(tmp), "-t", f"{dur:.3f}", "-vf", vf, "-an", str(out)])

def render_label(text: str, out: Path):
    img = Image.new("RGBA", LABEL_CANVAS, (0,0,0,0)); d = ImageDraw.Draw(img); f = ImageFont.truetype(FONT, LABEL_FONT_SIZE)
    d.rounded_rectangle([0,0,LABEL_CANVAS[0]-1,LABEL_CANVAS[1]-1], radius=70, fill=LABEL_COLOR)
    b = d.textbbox((0,0), text, font=f, stroke_width=3); d.text(((LABEL_CANVAS[0]-(b[2]-b[0]))//2, (LABEL_CANVAS[1]-(b[3]-b[1]))//2-4), text, font=f, fill=(255,255,255,255), stroke_width=3, stroke_fill=(0,0,0,255))
    img.save(out)

def render_sub(text: str, out: Path):
    img = Image.new("RGBA", SUBTITLE_CANVAS, (0,0,0,0)); d = ImageDraw.Draw(img); f = ImageFont.truetype(FONT, SUBTITLE_FONT_SIZE)
    d.rounded_rectangle([0,0,SUBTITLE_CANVAS[0]-1,SUBTITLE_CANVAS[1]-1], radius=25, fill=SUBTITLE_BG)
    ls = text.split("\n"); h = 74; y = (SUBTITLE_CANVAS[1]-h*len(ls))//2
    for l in ls: b = d.textbbox((0,0), l, font=f, stroke_width=2); d.text(((SUBTITLE_CANVAS[0]-(b[2]-b[0]))//2, y), l, font=f, fill=(255,255,255,255), stroke_width=2, stroke_fill=(0,0,0,255)); y += h
    img.save(out)

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--concept", type=int, choices=[8, 9, 10], required=True); args = ap.parse_args()
    cfg = CONCEPTS[args.concept]; print(f"── VTV Concept {args.concept} ──")
    tmp = PRODUCT / "output" / f"_tmp_vtv{args.concept}"; tmp.mkdir(parents=True, exist_ok=True); FINAL.mkdir(parents=True, exist_ok=True)
    pools = load_all_scenes(); used = set(); vs, vps = [], []; tail = 0.15
    for i, seg in enumerate(cfg["segments"], 1):
        vm = tmp / f"v_{i:02d}.mp3"; gen_voice(seg["voice"], vm); vd = probe_dur(vm); td = vd + tail
        vp = tmp / f"v_{i:02d}_p.m4a"; run(["ffmpeg", "-y", "-i", str(vm), "-af", f"apad=pad_dur={tail:.3f}", "-t", f"{td:.3f}", "-c:a", "aac", str(vp)]); vs.append(vp)
        scs = pick_scenes(pools, seg["keywords"], used, td, args.concept*100+i); raw = tmp / f"r_{i:02d}.mp4"
        if len(scs) == 1: scene_to_v(scs[0], td, raw, cfg["hue_shift"], 1.0+i*0.02)
        else:
            ps, dp = [], td/len(scs)
            for idx, s in enumerate(scs): p = tmp / f"p_{i:02d}_{idx}.mp4"; scene_to_v(s, dp, p, cfg["hue_shift"], 1.0+i*0.02+idx*0.01); ps.append(p)
            lf = tmp / f"vc_{i}.txt"; lf.write_text("\n".join(f"file '{f.as_posix()}'" for f in ps)); run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(lf), "-c:v", "libx264", "-an", str(raw)])
        sp = tmp / f"s_{i:02d}.png"; render_sub(seg["subtitle"], sp); vf = tmp / f"f_{i:02d}.mp4"; run(["ffmpeg", "-y", "-i", str(raw), "-i", str(sp), "-filter_complex", f"[0:v][1:v]overlay=(W-w)/2:{SUBTITLE_Y}", "-c:v", "libx264", "-an", str(vf)]); vps.append(vf)
    mv, ma = tmp / "mv.mp4", tmp / "ma.m4a"; lf = tmp / "vfinal.txt"; lf.write_text("\n".join(f"file '{f.as_posix()}'" for f in vps)); run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(lf), "-c:v", "libx264", "-an", str(mv)])
    run(["ffmpeg", "-y"] + [item for p in vs for item in ("-i", str(p))] + ["-filter_complex", f"concat=n={len(vs)}:v=0:a=1[out]", "-map", "[out]", "-c:a", "aac", str(ma)])
    lp = tmp / "lp.png"; render_label(PRODUCT_LABEL, lp); fvl = tmp / "fvl.mp4"; run(["ffmpeg", "-y", "-i", str(mv), "-i", str(lp), "-filter_complex", f"[0:v][1:v]overlay=(W-w)/2:{LABEL_Y}", "-c:v", "libx264", "-an", str(fvl)])
    fp = FINAL / f"{cfg['caption']}.mp4"; run(["ffmpeg", "-y", "-i", str(fvl), "-i", str(ma), "-c:v", "copy", "-c:a", "aac", "-shortest", str(fp)])
    print(f"✓ {fp.name}")
if __name__ == "__main__": main()
