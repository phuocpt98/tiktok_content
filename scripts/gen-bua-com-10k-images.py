"""Generate 5 preview images for 'Bữa cơm 10K từ đồ tạp hóa' video concept."""
import sys
sys.stdout.reconfigure(encoding="utf-8")

from src.config import GEMINI_API_KEYS, IMAGES_DIR
print(f"API keys: {len(GEMINI_API_KEYS)}")

from src.config import IMAGES_DIR
from pathlib import Path

# Image prompts - food photography style, vertical 9:16
prompts = [
    # Slide 1: Hook visual
    "A Vietnamese hand holding a 10,000 VND banknote in front of a small traditional grocery store (tạp hóa) in Vietnam. "
    "Bright, warm lighting. Close-up shot. Vertical 9:16 ratio. Clean background. "
    "Text-free image, photorealistic food photography style.",

    # Slide 2: Ingredients on shelf
    "Top-down flat lay of cheap Vietnamese grocery items on a wooden table: "
    "one pack of instant noodles (mì gói Hảo Hảo), two eggs, a bundle of morning glory (rau muống), "
    "and small packets of chili sauce and soy sauce. Price tags showing very low prices. "
    "Bright, appetizing food photography. Vertical 9:16. Photorealistic.",

    # Slide 3: Cooking action
    "Close-up of a sizzling wok with stir-fried instant noodles, scrambled eggs, and green vegetables. "
    "Steam rising, golden color, Vietnamese kitchen setting. "
    "Dramatic food photography lighting. Vertical 9:16. Photorealistic, appetizing.",

    # Slide 4: Final dish - food porn
    "A beautiful Vietnamese budget meal on a simple ceramic plate: stir-fried instant noodles with egg and vegetables, "
    "garnished with fresh chili and lime wedge. Shot from 45-degree angle. "
    "Professional food photography, warm lighting, shallow depth of field. "
    "Looks expensive but made from cheap ingredients. Vertical 9:16. Photorealistic.",

    # Slide 5: Reveal / reaction
    "A young Vietnamese woman looking surprised and delighted while eating from a bowl of stir-fried noodles. "
    "Casual setting, Vietnamese grocery store background slightly blurred. "
    "Natural expression, warm lighting. Vertical 9:16. Photorealistic.",
]

import importlib
gc = importlib.import_module("src.gemini-client")

output_dir = IMAGES_DIR / "bua-com-10k"
output_dir.mkdir(exist_ok=True)

for i, prompt in enumerate(prompts):
    print(f"\n--- Generating image {i+1}/{len(prompts)} ---")
    try:
        path = gc.generate_image(
            prompt,
            filename=f"bua-com-10k/slide-{i+1:02d}.png"
        )
        print(f"OK: {path}")
    except Exception as e:
        print(f"FAILED: {e}")

print("\nDone! Check assets/images/bua-com-10k/")
