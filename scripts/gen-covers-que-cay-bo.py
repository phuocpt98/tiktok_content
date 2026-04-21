# Gen 5 bright cover images for Que Cay Bo via Gemini Nano Banana (gemini-2.5-flash-image)
# Free tier compatible. Imagen 4 requires paid plan → not usable.
# Rule: docs/video-production-format.md + memory feedback_thumbnail_covers.md
# - SÁNG, clean background, soft natural light, vibrant colors
# - 9:16 portrait, no text/logo/watermark, no duplicate composition across 5 videos

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
sys.stdout.reconfigure(encoding="utf-8")

from src.config import GEMINI_API_KEYS
from google import genai
from google.genai import types

OUT = Path("D:/project/demo/content/assets/products/que-cay-bo/photos")
MODEL = "gemini-2.5-flash-image"
ASPECT = "9:16"

NEG = "no text, no logo, no title, no watermark, no lettering, no captions, no typography, no characters, no letters"
STYLE = (
    "bright food photography, soft natural daylight, clean studio background, "
    "vibrant warm colors, appetizing, glossy, high detail, sharp focus"
)

COVERS = {
    "cover-v1-macro-bright.png": (
        "Extreme macro close-up of ONE glossy spicy beef jerky stick with chili flakes and sesame seeds sticking to its surface, "
        "shallow depth of field, placed diagonally on a PURE WHITE marble slab background, "
        "soft morning sunlight from upper-left creating gentle highlights, "
        "a few red chili peppers blurred softly in the background. "
        f"{STYLE}. {NEG}."
    ),
    "cover-v2-flatlay-wood.png": (
        "Top-down flat lay of five spicy beef jerky sticks arranged in parallel rows on a pale wooden cutting board, "
        "scattered dried red chili peppers and star anise pods around them, tiny green parsley leaves as accents, "
        "CREAM BEIGE background with soft natural shadow, overhead daylight from a window, "
        "symmetrical minimalist composition with generous negative space. "
        f"{STYLE}. {NEG}."
    ),
    "cover-v3-heart-pastel.png": (
        "Top-down view of short spicy beef jerky sticks arranged to form a HEART SHAPE on a PASTEL PINK background, "
        "small red chili peppers scattered tenderly around the heart, star anise as accents, "
        "soft rosy daylight, playful romantic aesthetic, clean wide negative space framing the heart, "
        "food styling for Valentine mood. "
        f"{STYLE}. {NEG}."
    ),
    "cover-v4-falling-plate.png": (
        "Spicy beef jerky sticks FALLING mid-air onto a clean WHITE ceramic plate, motion caught at peak drop, "
        "WARM YELLOW CREAM background, golden hour studio lighting, tiny chili flakes and sesame seeds flying, "
        "dynamic food-photography moment, dreamy yet BRIGHT, absolutely no dark shadows, "
        "high-speed capture with crisp clarity. "
        f"{STYLE}. {NEG}."
    ),
    "cover-v5-challenge-stand.png": (
        "FIVE spicy beef jerky sticks STANDING UPRIGHT in a neat row like candles on a LIGHT YELLOW kraft paper surface, "
        "small red chili peppers scattered at the base, sprinkled chili flakes like confetti, "
        "cheerful vibrant challenge-party mood, bright soft studio light from top-front, "
        "playful energetic aesthetic with clean space above for a future title area. "
        f"{STYLE}. {NEG}."
    ),
}


def gen_one(client: genai.Client, prompt: str, out_path: Path) -> bool:
    try:
        config = types.GenerateContentConfig(
            response_modalities=['IMAGE'],
            image_config=types.ImageConfig(aspect_ratio=ASPECT),
        )
        resp = client.models.generate_content(
            model=MODEL, contents=[prompt], config=config,
        )
        if not resp.candidates:
            print(f"  [ERR] no candidates")
            return False
        for part in resp.candidates[0].content.parts:
            if part.inline_data:
                out_path.write_bytes(part.inline_data.data)
                print(f"  OK -> {out_path.name}  ({out_path.stat().st_size // 1024} KB)")
                return True
        print(f"  [ERR] no inline_data in response")
        return False
    except Exception as e:
        print(f"  [ERR] {str(e)[:200]}")
        return False


def main():
    if not GEMINI_API_KEYS:
        print("[ERROR] No GEMINI_API_KEY in .env")
        sys.exit(1)

    OUT.mkdir(parents=True, exist_ok=True)

    clients = [genai.Client(api_key=k) for k in GEMINI_API_KEYS]
    print(f"[INFO] {len(clients)} API key(s), model={MODEL}, aspect={ASPECT}\n")

    ok, fail = [], []
    key_idx = 0
    for fname, prompt in COVERS.items():
        print(f"[GEN] {fname}")
        dst = OUT / fname
        success = False
        # try up to len(clients) keys on failure
        for attempt in range(len(clients)):
            client = clients[(key_idx + attempt) % len(clients)]
            if gen_one(client, prompt, dst):
                success = True
                key_idx = (key_idx + attempt) % len(clients)
                break
            time.sleep(1)
        if success:
            ok.append(fname)
        else:
            fail.append(fname)
        time.sleep(2)  # gentle rate

    print("\n" + "=" * 60)
    print(f"SUMMARY: {len(ok)} OK / {len(fail)} FAIL")
    for n in ok:
        print(f"  OK   {n}")
    for n in fail:
        print(f"  FAIL {n}")


if __name__ == "__main__":
    main()
