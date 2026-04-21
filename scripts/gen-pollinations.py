"""Generate product images via Pollinations.ai FLUX (free, no auth)."""
import sys, urllib.parse, urllib.request, random, ssl, time
from pathlib import Path

def gen(prompt: str, out_path: Path, w: int = 1080, h: int = 1920, seed: int = None, ref_url: str = None):
    seed = seed or random.randint(1, 999999)
    url = (
        f"https://image.pollinations.ai/prompt/{urllib.parse.quote(prompt)}"
        f"?width={w}&height={h}&model=flux&seed={seed}&nologo=true&enhance=true"
    )
    if ref_url:
        url += f"&image={urllib.parse.quote(ref_url, safe='')}"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    ctx = ssl.create_default_context()
    for attempt in range(3):
        try:
            data = urllib.request.urlopen(req, timeout=120, context=ctx).read()
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_bytes(data)
            return len(data)
        except Exception as e:
            if attempt == 2:
                raise
            print(f"  retry {attempt+1}: {e}", file=sys.stderr)
            time.sleep(3)

if __name__ == "__main__":
    # Args: product_slug ref_url_or_NONE start_idx "prompt1" "prompt2" ...
    slug = sys.argv[1]
    ref_url = sys.argv[2] if sys.argv[2] != "NONE" else None
    start_idx = int(sys.argv[3])
    prompts = sys.argv[4:]
    out_dir = Path(f"assets/products/{slug}/photos")
    for i, p in enumerate(prompts):
        idx = start_idx + i
        name = f"poll_{slug}_{idx:02d}.jpg"
        path = out_dir / name
        print(f"[{i+1}/{len(prompts)}] {name} ...", flush=True)
        size = gen(p, path, ref_url=ref_url)
        print(f"  OK {size} bytes -> {path}", flush=True)
