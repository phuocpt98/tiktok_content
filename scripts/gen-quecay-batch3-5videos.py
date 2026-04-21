"""
Generate Batch 3 (5 unique videos) for Que Cay Pel Pel.
- 2 Vua Tiếng Việt scripts (Fix: robust TTS and longer durations)
- 3 Review scripts
- Unique scenes for each video to avoid repetition.
- Enhanced TTS with multiple voice fallbacks and cleaning.
"""
import json
import os
import subprocess
import time
import asyncio
import edge_tts
import re
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from google import genai
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")

SCENE_LIB = ROOT / "assets" / "scene-library" / "que_cay"
OUTPUT_DIR = ROOT / "assets" / "products" / "que-cay" / "output"
FINAL_DIR = OUTPUT_DIR / "final"
LABEL_Y = 280

# TTS Settings
VOICES = ["vi-VN-NamMinhNeural", "vi-VN-HoaiMyNeural"]
TTS_RATE = "+10%"

# Gemini Client for fallback
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
gemini_client = genai.Client(api_key=GEMINI_KEY) if GEMINI_KEY else None

VIDEOS_CONFIG = [
    {
        "name": "vua_tv_sac_so",
        "caption": "SẶC SỠ hay XẶC XỠ? 🤔 Bò cay này cũng sặc sỡ mà ngon lắm nha! #vuatiengviet #quecay #anvat #pelpel #fyp",
        "label": "VUA TIẾNG VIỆT • PEL PEL",
        "segments": [
            {"text_voice": "Đố các cao thủ tiếng Việt. Đáp án đúng là gì?", "text_subtitle": "SẶC SỠ hay XẶC XỠ? 🤔", "keywords": ["quecay"], "scene_id": "beheobu0102_7487206549224459526_scene_01", "min_dur": 4.0},
            {"text_voice": "Trong lúc đợi đáp án thì xem mình review que cay vị bò này nhé.", "text_subtitle": "Đang nghĩ thì xem mình review nha!", "keywords": ["quecay"], "scene_id": "beheobu0102_7507637747360812295_scene_01"},
            {"text_voice": "Vị bò cay đậm đà, giòn sần sật, ăn một que là nghiện luôn.", "text_subtitle": "Bò cay đậm đà - Ăn là nghiện 🤤", "keywords": ["quecay"], "scene_id": "beheobu0102_7587471944946076936_scene_01"},
            {"text_voice": "Đáp án đúng chính là: SẶC SỠ!", "text_subtitle": "Đáp án: SẶC SỠ ✅", "keywords": ["quecay"], "scene_id": "beheobu0102_7591174570623782162_scene_01", "min_dur": 3.0},
            {"text_voice": "Ai đúng comment đỉnh, ai sai comment hic nha! Follow mình nhé!", "text_subtitle": "Comment 'đỉnh' nếu bạn đúng! ✌️", "keywords": ["quecay"], "scene_id": "beheobu0102_7591563909870390546_scene_01", "min_dur": 4.0},
        ]
    },
    {
        "name": "vua_tv_suyt_nua",
        "caption": "90% dùng sai từ này: SUÝT hay XUÝT? 🤔 Suýt nữa là bỏ qua cực phẩm bò cay rồi! #vuatiengviet #reviewanvat #quecay #pelpel #xuhuong",
        "label": "VUA TIẾNG VIỆT • PEL PEL",
        "segments": [
            {"text_voice": "Suýt nữa hay Xuýt nữa? Chín mươi phần trăm người dùng sai từ này!", "text_subtitle": "SUÝT NỮA hay XUÝT NỮA?", "keywords": ["quecay"], "scene_id": "beheobu0102_7592532683742399751_scene_01", "min_dur": 4.0},
            {"text_voice": "Đừng để sai chính tả như cách bạn bỏ lỡ gói bò cay này.", "text_subtitle": "Đừng bỏ lỡ gói bò cay này!", "keywords": ["quecay"], "scene_id": "beheobu0102_7592686485128613127_scene_01"},
            {"text_voice": "Cay nồng vừa phải, thơm mùi thịt bò, ăn cuốn cực kỳ luôn.", "text_subtitle": "Thơm mùi bò - Cay cuốn lưỡi", "keywords": ["quecay"], "scene_id": "beheobu0102_7593420068646571272_scene_01"},
            {"text_voice": "Đáp án là: SUÝT NỮA! Suýt chút nữa là bạn quên tim video này rồi.", "text_subtitle": "Đáp án: SUÝT NỮA ✅", "keywords": ["quecay"], "scene_id": "beheobu0102_7593817876264537352_scene_01", "min_dur": 3.0},
            {"text_voice": "Tim và follow để mình review mỗi ngày nha!", "text_subtitle": "Suýt quên tim thì làm ngay đi! ♡", "keywords": ["quecay"], "scene_id": "beheobu0102_7596391126433565970_scene_01", "min_dur": 4.0},
        ]
    },
    {
        "name": "review_van_phong",
        "caption": "3 giờ chiều là giờ của Bò Cay 🤤 Dân văn phòng không thể thiếu món này đâu nha! #danvanphong #reviewanvat #quecay #pelpel #ancungtiktok",
        "label": "BÒ CAY • PEL PEL",
        "segments": [
            {"text_voice": "Ba giờ chiều rồi, bụng biểu tình thì phải làm sao?", "text_subtitle": "3H CHIỀU - ĐÓI XỬ 🫠", "keywords": ["quecay"], "scene_id": "beheobu0102_7597119392350096648_scene_01"},
            {"text_voice": "Tèn ten! Cứu tinh đây - Que cay vị bò Pel Pel siêu gói to.", "text_subtitle": "Cứu tinh: BÒ CAY gói to!", "keywords": ["quecay"], "scene_id": "beheobu0102_7597148650015378706_scene_01"},
            {"text_voice": "Vị bò đậm đà, cay nhẹ, chia cho mấy bà đồng nghiệp là hết sảy.", "text_subtitle": "Chia nhau ăn là hết sảy luôn", "keywords": ["quecay"], "scene_id": "beheobu0102_7597596396417453319_scene_01"},
            {"text_voice": "Ăn vào là tỉnh táo làm việc tiếp luôn. Ngon xỉu mấy bà ơi!", "text_subtitle": "Tỉnh táo làm việc tiếp thôi! 🤤", "keywords": ["quecay"], "scene_id": "beheobu0102_7597872296677723400_scene_01"},
            {"text_voice": "Tag ngay đứa bạn hay đói vào đây nhé! Follow mình nha!", "text_subtitle": "Tag ngay đứa bạn hay đói! ♡", "keywords": ["quecay"], "scene_id": "beheobu0102_7598483802117393672_scene_01", "min_dur": 4.0},
        ]
    },
    {
        "name": "review_me_mang",
        "caption": "Mẹ mắng là việc của mẹ, ăn ngon là việc của mình 🤣 Bò cay này 'lạ' lắm, ăn là nghiện! #funny #quecay #reviewanvat #pelpel #xuhuong",
        "label": "BÒ CAY • PEL PEL",
        "segments": [
            {"text_voice": "Mẹ bảo suốt ngày ăn cay, nhưng mà cái vị bò này nó lạ lắm.", "text_subtitle": "MẸ: SUỐT NGÀY ĂN CAY! 😡", "keywords": ["quecay"], "scene_id": "beheobu0102_7599721210804456711_scene_01"},
            {"text_voice": "Lén lén ăn một que thôi mà nó giòn rụm, cay nồng thơm mùi bò.", "text_subtitle": "But nó ngon quá mấy vợ ơi!", "keywords": ["quecay"], "scene_id": "beheobu0102_7599828180223921415_scene_01"},
            {"text_voice": "Càng ăn càng cuốn, không gắt cổ, bảo sao cứ thèm hoài không bỏ được.", "text_subtitle": "Ăn một que là muốn ăn mười", "keywords": ["quecay"], "scene_id": "beheobu0102_7601205364905741576_scene_01"},
            {"text_voice": "Cuối cùng mẹ ăn thử xong mẹ cũng đòi mua thêm cả thùng luôn.", "text_subtitle": "Kết quả: Mẹ đòi mua cả thùng!", "keywords": ["quecay"], "scene_id": "beheobu0102_7601244453377985799_scene_01"},
            {"text_voice": "Ai giống mình thì giơ tay nhé! Tim và follow mình nha!", "text_subtitle": "Ai giống tui thì giơ tay! 🙋‍♀️", "keywords": ["quecay"], "scene_id": "beheobu0102_7602145465513053447_scene_01", "min_dur": 4.0},
        ]
    },
    {
        "name": "review_challenge",
        "caption": "Ăn 5 que không nước — Ai dám? 🔥 Tag đứa bạn hay 'gáy' ăn cay vào đây thách thức đi! #challenge #quecay #reviewanvat #pelpel #ancungtiktok",
        "label": "BÒ CAY • PEL PEL",
        "segments": [
            {"text_voice": "Thách các bạn ăn năm que bò cay liên tục mà không uống nước!", "text_subtitle": "THÁCH: ĂN 5 QUE - KO NƯỚC!", "keywords": ["quecay"], "scene_id": "beheobu0102_7606777060815670546_scene_01"},
            {"text_voice": "Bò cay Pel Pel cấp độ ba trên mười. Tưởng không cay mà cay không tưởng!", "text_subtitle": "Cấp độ 3/10 — Ko đùa được đâu!", "keywords": ["quecay"], "scene_id": "beheobu0102_7607494869052837138_scene_01"},
            {"text_voice": "Vị bò thơm nức mũi, cay tê đầu lưỡi, ai liều thì vào đây thử ngay.", "text_subtitle": "Cay tê đầu lưỡi - Thơm nức mũi", "keywords": ["quecay"], "scene_id": "beheobu0102_7608985652683705607_scene_01"},
            {"text_voice": "Mình là mình chịu thua ở que thứ ba rồi đó, còn bạn thì sao?", "text_subtitle": "Mình chịu thua rồi... Còn bạn?", "keywords": ["quecay"], "scene_id": "beheobu0102_7611607199902600456_scene_01"},
            {"text_voice": "Tag đứa bạn hay ăn cay vào thách thức đi nào! Follow mình nha!", "text_subtitle": "Tag đứa bạn 'liều' vào đây! 🔥", "keywords": ["quecay"], "scene_id": "beheobu0102_7613832315164167432_scene_01", "min_dur": 4.0},
        ]
    }
]

def clean_text(text: str) -> str:
    # Bỏ các ký tự gây lỗi TTS
    return re.sub(r'[^a-zA-Z0-9àáảãạâầấẩẫậăằắẳẵặèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵ\s,.]', '', text)

def find_vi_font(size: int) -> ImageFont.FreeTypeFont:
    for p in [
        "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
        "/System/Library/Fonts/HelveticaNeue.ttc",
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
    ]:
        if Path(p).exists():
            try: return ImageFont.truetype(p, size)
            except Exception: continue
    return ImageFont.load_default()

def render_label_png(text: str, out: Path, width: int = 900, height: int = 140) -> None:
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.rounded_rectangle([(0, 0), (width - 1, height - 1)], radius=height//2, fill=(255, 107, 0, 220))
    font = find_vi_font(58)
    bbox = draw.textbbox((0, 0), text, font=font)
    tx = (width - (bbox[2] - bbox[0])) // 2
    ty = (height - (bbox[3] - bbox[1])) // 2 - bbox[1]
    draw.text((tx, ty), text, font=font, fill=(255, 255, 255, 255), stroke_width=3, stroke_fill=(0, 0, 0, 255))
    img.save(out, "PNG")

def render_subtitle_png(text: str, out: Path, width: int = 1000, height: int = 200) -> None:
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    font = find_vi_font(62)
    words = text.split()
    lines, cur = [], ""
    for w in words:
        test = (cur + " " + w).strip()
        if draw.textlength(test, font=font) <= width - 60: cur = test
        else:
            if cur: lines.append(cur)
            cur = w
    if cur: lines.append(cur)
    line_h = 74
    total_h = line_h * len(lines) + 20
    box_top = (height - total_h) // 2
    draw.rounded_rectangle([(20, box_top - 20), (width - 20, box_top + total_h)], radius=25, fill=(0, 0, 0, 180))
    for i, line in enumerate(lines):
        bbox = draw.textbbox((0, 0), line, font=font)
        tx = (width - (bbox[2] - bbox[0])) // 2
        ty = box_top + i * line_h
        draw.text((tx, ty), line, font=font, fill=(255, 255, 255, 255), stroke_width=2, stroke_fill=(0, 0, 0, 255))
    img.save(out, "PNG")

async def tts_edge(text: str, out_mp3: Path):
    text = clean_text(text)
    for voice in VOICES:
        try:
            c = edge_tts.Communicate(text, voice, rate=TTS_RATE)
            await c.save(str(out_mp3))
            if out_mp3.exists() and out_mp3.stat().st_size > 500:
                print(f"  ✓ Edge TTS ({voice}) Success")
                return True
        except Exception as e:
            print(f"  ! Edge TTS ({voice}) Fail: {e}")
    return False

async def tts_gemini(text: str, out_mp3: Path):
    if not gemini_client:
        return False
    try:
        response = gemini_client.models.generate_content(
            model="gemini-2.0-flash",
            contents=f"Đọc đoạn văn sau: {text}",
            config={"speech_config": {"voice_config": {"prebuilt_voice_config": {"voice_name": "Kore"}}}}
        )
        if response.audio:
            out_mp3.write_bytes(response.audio)
            print(f"  ✓ Gemini TTS Success")
            return True
    except Exception as e:
        print(f"  ! Gemini TTS Fail: {e}")
    return False

async def tts_robust(text: str, out_mp3: Path):
    if await tts_edge(text, out_mp3):
        return
    if await tts_gemini(text, out_mp3):
        return
    print(f"  !! SILENCE fallback for: {text[:20]}...")
    subprocess.run(["ffmpeg", "-y", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=mono", "-t", "0.5", str(out_mp3)], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def audio_duration(path: Path) -> float:
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", str(path)], capture_output=True, text=True).stdout.strip()
    return float(out) if out else 0.5

def run_ffmpeg(cmd: list):
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

async def build_video(config: dict):
    v_name = config["name"]
    tmp = OUTPUT_DIR / f"_tmp_batch3_{v_name}"
    tmp.mkdir(parents=True, exist_ok=True)
    
    label_png = tmp / "label.png"
    render_label_png(config["label"], label_png)
    
    clip_paths = []
    audio_paths = []
    
    for i, seg in enumerate(config["segments"], 1):
        voice_mp3 = tmp / f"voice_{i:02d}.mp3"
        # Always try to gen TTS, overwrite to ensure new clean text
        await tts_robust(seg["text_voice"], voice_mp3)
        dur = audio_duration(voice_mp3)
        
        min_dur = seg.get("min_dur", 2.5)
        render_dur = max(dur, min_dur)
        
        scene_mp4 = SCENE_LIB / f"{seg['scene_id']}.mp4"
        stage1 = tmp / f"clip_{i:02d}_raw.mp4"
        vf = "scale=-1:1920:force_original_aspect_ratio=increase,crop=1080:1920:(iw-1080)/2:0,setsar=1,fps=30"
        
        scene_dur = audio_duration(scene_mp4)
        if scene_dur < render_dur:
            cmd = ["ffmpeg", "-y", "-stream_loop", "-1", "-i", str(scene_mp4), "-t", str(render_dur), "-vf", vf, "-an", "-c:v", "libx264", "-crf", "21", "-pix_fmt", "yuv420p", str(stage1)]
        else:
            cmd = ["ffmpeg", "-y", "-i", str(scene_mp4), "-t", str(render_dur), "-vf", vf, "-an", "-c:v", "libx264", "-crf", "21", "-pix_fmt", "yuv420p", str(stage1)]
        run_ffmpeg(cmd)
        
        if dur < render_dur:
            ext_audio = tmp / f"voice_{i:02d}_ext.mp3"
            run_ffmpeg(["ffmpeg", "-y", "-i", str(voice_mp3), "-f", "lavfi", "-i", f"anullsrc=r=44100:cl=mono", "-filter_complex", f"[0:a][1:a]concat=n=2:v=0:a=1", "-t", str(render_dur), str(ext_audio)])
            voice_mp3 = ext_audio
        
        sub_png = tmp / f"sub_{i:02d}.png"
        render_subtitle_png(seg["text_subtitle"], sub_png)
        
        stage2 = tmp / f"clip_{i:02d}_final.mp4"
        run_ffmpeg(["ffmpeg", "-y", "-i", str(stage1), "-i", str(label_png), "-i", str(sub_png), "-filter_complex", f"[0:v][1:v]overlay=(main_w-overlay_w)/2:{LABEL_Y}[v1];[v1][2:v]overlay=(main_w-overlay_w)/2:1580[vo]", "-map", "[vo]", "-c:v", "libx264", "-crf", "21", "-pix_fmt", "yuv420p", "-an", str(stage2)])
        
        clip_paths.append(stage2)
        audio_paths.append(voice_mp3)

    concat_v = tmp / "concat_v.mp4"
    list_v = tmp / "list_v.txt"
    with list_v.open("w") as f:
        for p in clip_paths: f.write(f"file '{p.resolve()}'\n")
    run_ffmpeg(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(list_v), "-c", "copy", str(concat_v)])
    
    concat_a = tmp / "concat_a.mp3"
    list_a = tmp / "list_a.txt"
    with list_a.open("w") as f:
        for p in audio_paths: f.write(f"file '{p.resolve()}'\n")
    run_ffmpeg(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(list_a), "-c:a", "libmp3lame", "-q:a", "2", str(concat_a)])
    
    final_path = FINAL_DIR / f"{config['caption']}.mp4"
    run_ffmpeg(["ffmpeg", "-y", "-i", str(concat_v), "-i", str(concat_a), "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", str(final_path)])
    print(f"DONE: {final_path.name}")

async def main():
    FINAL_DIR.mkdir(parents=True, exist_ok=True)
    for cfg in VIDEOS_CONFIG:
        print(f"Building {cfg['name']}...")
        await build_video(cfg)

if __name__ == "__main__":
    asyncio.run(main())
