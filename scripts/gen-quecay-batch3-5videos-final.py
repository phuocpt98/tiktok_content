"""
Generate Batch 3 (5 videos) with FIXED TTS (No more missing 'Đ' or starting letters).
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

VOICES = ["vi-VN-NamMinhNeural", "vi-VN-HoaiMyNeural"]
TTS_RATE = "+10%"

GEMINI_KEY = os.getenv("GEMINI_API_KEY")
gemini_client = genai.Client(api_key=GEMINI_KEY) if GEMINI_KEY else None

VIDEOS_CONFIG = [
    {
        "name": "vua_tv_sac_so",
        "caption": "SẶC SỠ hay XẶC XỠ? 🤔 Bò cay này cũng sặc sỡ mà ngon lắm nha! #vuatiengviet #quecay #anvat #pelpel #fyp",
        "label": "VUA TIẾNG VIỆT • PEL PEL",
        "segments": [
            {"text_voice": "Đố các bạn biết, trong hai từ này thì từ nào mới viết đúng chính tả đây?", "text_subtitle": "SẶC SỠ hay XẶC XỠ? 🤔", "keywords": ["quecay"], "scene_id": "beheobu0102_7487206549224459526_scene_01", "min_dur": 4.5},
            {"text_voice": "Trong lúc chờ đợi thì cùng mình xem qua gói bò cay Pel Pel này nhé.", "text_subtitle": "Đang nghĩ thì xem mình review nha!", "keywords": ["quecay"], "scene_id": "beheobu0102_7507637747360812295_scene_01"},
            {"text_voice": "Vị bò cay đậm đà, sợi dai giòn, ăn một que là mê chữ ê kéo dài luôn.", "text_subtitle": "Bò cay đậm đà - Ăn là nghiện 🤤", "keywords": ["quecay"], "scene_id": "beheobu0102_7587471944946076936_scene_01"},
            {"text_voice": "Và đáp án chính xác của chúng ta là: SẶC SỠ!", "text_subtitle": "Đáp án: SẶC SỠ ✅", "keywords": ["quecay"], "scene_id": "beheobu0102_7591174570623782162_scene_01", "min_dur": 3.0},
            {"text_voice": "Bạn nào trả lời đúng thì thả tim cho mình biết với nhé. Follow mình ngay nha!", "text_subtitle": "Comment 'đỉnh' nếu bạn đúng! ✌️", "keywords": ["quecay"], "scene_id": "beheobu0102_7591563909870390546_scene_01", "min_dur": 4.0},
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
            {"text_voice": "Ba giờ chiều rồi, bụng biểu tình thì phải làm sao?", "text_subtitle": "3H CHIỀU - ĐÓI XỈU 🫠", "keywords": ["quecay"], "scene_id": "beheobu0102_7597119392350096648_scene_01", "min_dur": 3.0},
            {"text_voice": "Tèn ten! Cứu tinh đây. Que cay vị bò Pel Pel siêu gói to.", "text_subtitle": "Cứu tinh: BÒ CAY gói to!", "keywords": ["quecay"], "scene_id": "beheobu0102_7597148650015378706_scene_01"},
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
            {"text_voice": "Mẹ bảo suốt ngày ăn cay, nhưng mà cái vị bò này nó lạ lắm.", "text_subtitle": "MẸ: SUỐT NGÀY ĂN CAY! 😡", "keywords": ["quecay"], "scene_id": "beheobu0102_7599721210804456711_scene_01", "min_dur": 4.0},
            {"text_voice": "Lén lén ăn một que thôi mà nó giòn rụm, cay nồng thơm mùi bò.", "text_subtitle": "Nhưng nó ngon quá mấy vợ ơi!", "keywords": ["quecay"], "scene_id": "beheobu0102_7599828180223921415_scene_01"},
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
            {"text_voice": "Thách các bạn ăn năm que bò cay liên tục mà không uống nước!", "text_subtitle": "THÁCH: ĂN 5 QUE - KO NƯỚC!", "keywords": ["quecay"], "scene_id": "beheobu0102_7606777060815670546_scene_01", "min_dur": 4.0},
            {"text_voice": "Bò cay Pel Pel cấp độ ba trên mười. Tưởng không cay mà cay không tưởng!", "text_subtitle": "Cấp độ 3/10 — Không đùa được đâu!", "keywords": ["quecay"], "scene_id": "beheobu0102_7607494869052837138_scene_01"},
            {"text_voice": "Vị bò thơm nức mũi, cay tê đầu lưỡi, ai liều thì vào đây thử ngay.", "text_subtitle": "Cay tê đầu lưỡi - Thơm nức mũi", "keywords": ["quecay"], "scene_id": "beheobu0102_7608985652683705607_scene_01"},
            {"text_voice": "Mình là mình chịu thua ở que thứ ba rồi đó, còn bạn thì sao?", "text_subtitle": "Mình chịu thua rồi... Còn bạn?", "keywords": ["quecay"], "scene_id": "beheobu0102_7611607199902600456_scene_01"},
            {"text_voice": "Tag đứa bạn hay ăn cay vào thách thức đi nào! Follow mình nha!", "text_subtitle": "Tag đứa bạn 'liều' vào đây! 🔥", "keywords": ["quecay"], "scene_id": "beheobu0102_7613832315164167432_scene_01", "min_dur": 4.0},
        ]
    }
]

def clean_text(text: str) -> str:
    # FIXED: Added uppercase Vietnamese characters and common symbols
    # Added: Đ À Á Ả ÃẠ Â Ầ Ấ Ẩ Ẫ Ậ Ă Ằ Ắ Ẳ Ẵ Ặ È É Ẻ Ẽ Ẹ Ê Ề Ế Ể Ễ Ệ Ì Í Ỉ Ĩ Ị Ò Ó Ỏ Õ Ọ Ô Ồ Ố Ổ Ỗ Ộ Ơ Ờ Ớ Ở Ỡ Ợ Ù Ú Ủ Ũ Ụ Ư Ừ Ứ Ử Ữ Ự Ỳ Ý Ỷ Ỹ Ỵ
    pattern = r'[^a-zA-Z0-9àáảãạâầấẩẫậăằắẳẵặèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵĐÀÁẢÃẠÂẦẤẨẪẬĂẰẮẲẴẶÈÉẺẼẸÊỀẾỂỄỆÌÍỈĨỊÒÓỎÕỌÔỒỐỔỖỘƠỜỚỞỠỢÙÚỦŨỤƯỪỨỬỮỰỲÝỶỸỴ\s,.]'
    return re.sub(pattern, '', text)

def find_vi_font(size: int) -> ImageFont.FreeTypeFont:
    for p in ["/System/Library/Fonts/Supplemental/Arial Unicode.ttf", "/System/Library/Fonts/HelveticaNeue.ttc"]:
        if Path(p).exists(): return ImageFont.truetype(p, size)
    return ImageFont.load_default()

def render_label_png(text: str, out: Path):
    img = Image.new("RGBA", (900, 140), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.rounded_rectangle([(0, 0), (899, 139)], radius=70, fill=(255, 107, 0, 220))
    font = find_vi_font(58)
    bbox = draw.textbbox((0, 0), text, font=font)
    draw.text(((900-(bbox[2]-bbox[0]))//2, (140-(bbox[3]-bbox[1]))//2-bbox[1]), text, font=font, fill=(255, 255, 255), stroke_width=3, stroke_fill=(0, 0, 0))
    img.save(out, "PNG")

def render_subtitle_png(text: str, out: Path):
    img = Image.new("RGBA", (1000, 200), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    font = find_vi_font(62)
    lines, cur = [], ""
    for w in text.split():
        if draw.textlength((cur + " " + w).strip(), font=font) <= 940: cur = (cur + " " + w).strip()
        else: lines.append(cur); cur = w
    if cur: lines.append(cur)
    h = 74 * len(lines) + 20
    draw.rounded_rectangle([(20, (200-h)//2-20), (980, (200-h)//2+h)], radius=25, fill=(0, 0, 0, 180))
    for i, line in enumerate(lines):
        bbox = draw.textbbox((0, 0), line, font=font)
        draw.text(((1000-(bbox[2]-bbox[0]))//2, (200-h)//2 + i*74), line, font=font, fill=(255, 255, 255), stroke_width=2, stroke_fill=(0, 0, 0))
    img.save(out, "PNG")

async def tts_robust(text: str, out_mp3: Path):
    cleaned = clean_text(text)
    # Try Edge TTS first
    for voice in VOICES:
        try:
            c = edge_tts.Communicate(cleaned, voice, rate=TTS_RATE)
            await c.save(str(out_mp3))
            if out_mp3.exists() and out_mp3.stat().st_size > 500: 
                # ADD 0.2s SILENCE AT START to avoid clipping
                padded = out_mp3.parent / f"padded_{out_mp3.name}"
                subprocess.run(["ffmpeg", "-y", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=mono", "-t", "0.2", "-i", str(out_mp3), "-filter_complex", "[0:a][1:a]concat=n=2:v=0:a=1", str(padded)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                if padded.exists(): os.replace(padded, out_mp3)
                return True
        except: pass
    # Try Gemini fallback
    if gemini_client:
        try:
            response = gemini_client.models.generate_content(model="gemini-2.0-flash", contents=f"Đọc chậm, rõ ràng đoạn văn sau: {cleaned}", config={"speech_config": {"voice_config": {"prebuilt_voice_config": {"voice_name": "Kore"}}}})
            if response.audio: 
                out_mp3.write_bytes(response.audio)
                return True
        except: pass
    # Silence fallback
    subprocess.run(["ffmpeg", "-y", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=mono", "-t", "0.5", str(out_mp3)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return False

async def build_video(config: dict):
    tmp = OUTPUT_DIR / f"_tmp_final_{config['name']}"
    tmp.mkdir(parents=True, exist_ok=True)
    label_png = tmp / "label.png"
    render_label_png(config["label"], label_png)
    clips, audios = [], []
    for i, seg in enumerate(config["segments"], 1):
        voice = tmp / f"v_{i}.mp3"
        await tts_robust(seg["text_voice"], voice)
        dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", str(voice)], capture_output=True, text=True).stdout.strip() or 0.5)
        render_dur = max(dur, seg.get("min_dur", 2.5))
        scene = SCENE_LIB / f"{seg['scene_id']}.mp4"
        raw = tmp / f"r_{i}.mp4"
        subprocess.run(["ffmpeg", "-y", "-stream_loop", "-1", "-i", str(scene), "-t", str(render_dur), "-vf", "scale=-1:1920:force_original_aspect_ratio=increase,crop=1080:1920:(iw-1080)/2:0,setsar=1,fps=30", "-an", "-c:v", "libx264", "-crf", "21", "-pix_fmt", "yuv420p", str(raw)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if dur < render_dur:
            ext = tmp / f"v_{i}_e.mp3"
            subprocess.run(["ffmpeg", "-y", "-i", str(voice), "-f", "lavfi", "-i", "anullsrc=r=44100:cl=mono", "-filter_complex", "[0:a][1:a]concat=n=2:v=0:a=1", "-t", str(render_dur), str(ext)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            voice = ext
        sub = tmp / f"s_{i}.png"
        render_subtitle_png(seg["text_subtitle"], sub)
        out = tmp / f"f_{i}.mp4"
        subprocess.run(["ffmpeg", "-y", "-i", str(raw), "-i", str(label_png), "-i", str(sub), "-filter_complex", f"[0:v][1:v]overlay=(main_w-overlay_w)/2:{LABEL_Y}[v1];[v1][2:v]overlay=(main_w-overlay_w)/2:1580[vo]", "-map", "[vo]", "-c:v", "libx264", "-crf", "21", "-pix_fmt", "yuv420p", "-an", str(out)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        clips.append(out); audios.append(voice)
    with (tmp/"v.txt").open("w") as f:
        for c in clips: f.write(f"file '{c.resolve()}'\n")
    with (tmp/"a.txt").open("w") as f:
        for a in audios: f.write(f"file '{a.resolve()}'\n")
    cv, ca = tmp/"cv.mp4", tmp/"ca.mp3"
    subprocess.run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(tmp/"v.txt"), "-c", "copy", str(cv)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    subprocess.run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(tmp/"a.txt"), "-c:a", "libmp3lame", "-q:a", "2", str(ca)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    final = FINAL_DIR / f"{config['caption']}.mp4"
    subprocess.run(["ffmpeg", "-y", "-i", str(cv), "-i", str(ca), "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", str(final)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print(f"DONE: {final.name}")

async def main():
    FINAL_DIR.mkdir(parents=True, exist_ok=True)
    for cfg in VIDEOS_CONFIG:
        print(f"Building {cfg['name']}...")
        await build_video(cfg)
        await asyncio.sleep(2) # Avoid rate limits

if __name__ == "__main__":
    asyncio.run(main())
