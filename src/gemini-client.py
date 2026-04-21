"""Gemini API client with key rotation, retry, and batch generation."""
import json
import logging
import time
from pathlib import Path
from datetime import datetime
from google import genai
from src.config import GEMINI_API_KEYS, IMAGES_DIR, TEXT_DIR

log = logging.getLogger(__name__)

# Key rotation state
_current_key_index = 0
_clients = [genai.Client(api_key=k) for k in GEMINI_API_KEYS] if GEMINI_API_KEYS else []


def _get_client() -> genai.Client:
    """Get current Gemini client, rotate on rate limit."""
    global _current_key_index
    if not _clients:
        raise ValueError("No GEMINI_API_KEY configured in .env")
    return _clients[_current_key_index]


def _rotate_key():
    """Switch to next API key."""
    global _current_key_index
    if len(_clients) > 1:
        _current_key_index = (_current_key_index + 1) % len(_clients)
        log.info(f"Rotated to API key #{_current_key_index + 1}")


def _call_with_retry(func, max_retries=3):
    """Call API function with retry and key rotation on rate limit."""
    for attempt in range(max_retries):
        try:
            return func(_get_client())
        except Exception as e:
            error_str = str(e)
            if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str:
                log.warning(f"Rate limited on key #{_current_key_index + 1}, rotating...")
                _rotate_key()
                if attempt < max_retries - 1:
                    time.sleep(2)
                    continue
            elif "400" in error_str or "INVALID" in error_str:
                log.error(f"Invalid request: {error_str[:200]}")
                raise
            else:
                log.error(f"API error (attempt {attempt + 1}): {error_str[:200]}")
                if attempt < max_retries - 1:
                    time.sleep(1)
                    continue
                raise
    raise RuntimeError("All API retries exhausted")


def _parse_json(text: str) -> dict:
    """Parse JSON from LLM response, handling markdown fences."""
    text = text.strip()
    # Strip markdown code fences
    if text.startswith("```"):
        text = text.split("\n", 1)[1].rsplit("```", 1)[0].strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # Try to find JSON object in text
        start = text.find("{")
        end = text.rfind("}") + 1
        if start >= 0 and end > start:
            return json.loads(text[start:end])
        raise


def generate_script(idea: str, mode: str = "viral") -> dict:
    """Generate TikTok script from idea. Returns {title, script, scenes, hashtags, hook, filename}."""
    if mode == "viral":
        system_prompt = (
            "Bạn là chuyên gia content TikTok Việt Nam. "
            "Tạo script video ngắn 30-60 giây, hấp dẫn, dễ viral. "
            "Chủ đề: mẹo vặt, so sánh sản phẩm, mẹo tiết kiệm cho kênh tạp hóa. "
            "KHÔNG bán hàng trực tiếp, tập trung giá trị cho người xem."
        )
    else:
        system_prompt = (
            "Bạn là chuyên gia content TikTok affiliate Việt Nam. "
            "Tạo script video review sản phẩm 30-60 giây, chân thật, hấp dẫn. "
            "Kênh: Tạp Hóa Pel Pel - bán hàng tiêu dùng."
        )

    prompt = f"""Từ ý tưởng: "{idea}"

Tạo JSON:
{{
  "title": "Tiêu đề (gây tò mò, dưới 50 ký tự)",
  "script": "Script voiceover (30-60 giây, giọng tự nhiên, hook đầu)",
  "scenes": ["Mô tả cảnh 1 cho ảnh", "Mô tả cảnh 2", ...],
  "hashtags": ["#tag1", "#tag2", ...],
  "hook": "Câu mở đầu 3 giây gây chú ý",
  "caption": "Caption cho TikTok post"
}}

Trả về JSON thuần, không markdown."""

    def _call(client):
        return client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt,
            config={"system_instruction": system_prompt}
        )

    response = _call_with_retry(_call)
    result = _parse_json(response.text)

    # Save script
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filepath = TEXT_DIR / f"script_{timestamp}.json"
    filepath.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

    result["filename"] = str(filepath)
    log.info(f"Script generated: {result.get('title', idea)}")
    return result


def generate_image(prompt: str, filename: str = None) -> str:
    """Generate image via Gemini Imagen. Returns file path."""
    def _call(client):
        return client.models.generate_images(
            model="imagen-4.0-generate-001",
            prompt=prompt,
            config={"number_of_images": 1}
        )

    response = _call_with_retry(_call)
    if not response.generated_images:
        raise RuntimeError("No image generated")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    fname = filename or f"img_{timestamp}.png"
    filepath = IMAGES_DIR / fname
    filepath.write_bytes(response.generated_images[0].image.image_bytes)

    log.info(f"Image generated: {fname}")
    return str(filepath)


def generate_images_batch(prompts: list[str]) -> list[str]:
    """Generate multiple images from a list of prompts. Returns list of file paths."""
    paths = []
    for i, prompt in enumerate(prompts):
        try:
            path = generate_image(prompt, filename=f"batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{i}.png")
            paths.append(path)
            log.info(f"Batch image {i+1}/{len(prompts)} done")
        except Exception as e:
            log.warning(f"Batch image {i+1} failed: {e}")
    return paths


def generate_prompt_for_web(idea: str, mode: str = "viral") -> dict:
    """Generate optimized prompts for manual Gemini Web usage."""
    if mode == "viral":
        context = "content viral mẹo vặt/so sánh cho kênh tạp hóa TikTok"
    else:
        context = "content review sản phẩm affiliate cho kênh Tạp Hóa Pel Pel TikTok"

    prompts = {
        "script_prompt": (
            f"Viết script video TikTok 30-60 giây về: {idea}\n"
            f"Context: {context}\n"
            "Yêu cầu:\n"
            "- Hook gây chú ý trong 3 giây đầu\n"
            "- Giọng văn tự nhiên, gần gũi\n"
            "- Có CTA cuối video\n"
            "- Gợi ý 5-7 hashtag phù hợp"
        ),
        "image_prompts": [
            f"Tạo ảnh minh họa cho video TikTok về {idea}. "
            "Phong cách: sáng, bắt mắt, nền đơn giản, "
            "tỷ lệ dọc 9:16, chất lượng cao cho social media."
        ],
        "voice_prompt": (
            "Đọc đoạn script sau bằng giọng nữ miền Nam Việt Nam, "
            "tự nhiên, hào hứng, tốc độ vừa phải, phù hợp video TikTok 30 giây."
        ),
    }

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filepath = TEXT_DIR / f"prompts_{timestamp}.json"
    filepath.write_text(json.dumps(prompts, ensure_ascii=False, indent=2), encoding="utf-8")

    prompts["filename"] = str(filepath)
    return prompts
