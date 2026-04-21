# Re-render V1 với 3 hook variations (A/B test) — thay "nàng tinh tế" sượng
# v1a: "người xinh đẹp nhất thế gian"
# v1b: "công chúa xinh đẹp nhất thế gian"
# v1c: "người đáng yêu nhất thế giới"

import sys
import asyncio
import importlib.util
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
sys.stdout.reconfigure(encoding="utf-8")

# Load existing render module
_spec = importlib.util.spec_from_file_location(
    "batch1",
    Path(__file__).parent / "gen-que-cay-5-videos-batch1.py",
)
batch1 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(batch1)

# Override CONFIGS with only 3 V1 variations
DAY_CTA = batch1.DAY_CTA

VARIATIONS = {
    "v1a-xinh-dep-the-gian": {
        "hook_slide": ("NGƯỜI XINH ĐẸP NHẤT", "XEM HẾT NHÉ  ♡"),
        "voice": (
            "Mời người xinh đẹp nhất thế gian xem hết video này nha. "
            "Que cay bò Hương Nhãn Long, sợi giòn rụm, vị đậm đà. "
            "Cay nồng nhưng không gắt, ăn một que là muốn ăn mười. "
            + DAY_CTA
        ),
    },
    "v1b-cong-chua-xinh-dep": {
        "hook_slide": ("CÔNG CHÚA XINH ĐẸP", "XEM HẾT VIDEO  ♡"),
        "voice": (
            "Mời công chúa xinh đẹp nhất thế gian xem hết video này nha. "
            "Que cay bò Hương Nhãn Long, sợi giòn rụm, vị đậm đà. "
            "Cay nồng nhưng không gắt, ăn một que là muốn ăn mười. "
            + DAY_CTA
        ),
    },
    "v1c-dang-yeu-the-gioi": {
        "hook_slide": ("NGƯỜI ĐÁNG YÊU NHẤT", "XEM HẾT VIDEO  ♡"),
        "voice": (
            "Mời người đáng yêu nhất thế giới xem hết video này nha. "
            "Que cay bò Hương Nhãn Long, sợi giòn rụm, vị đậm đà. "
            "Cay nồng nhưng không gắt, ăn một que là muốn ăn mười. "
            + DAY_CTA
        ),
    },
}


# Patch build_segments to read hook_slide from per-variation map
_orig_build = batch1.build_segments


def build_v1_with_hook(hook_line1: str, hook_line2: str):
    """Return a custom build_segments closure for a specific v1 hook."""
    from moviepy import ImageClip, CompositeVideoClip
    from moviepy.video.fx import FadeIn, FadeOut

    W, H = batch1.W, batch1.H
    CROSSFADE = batch1.CROSSFADE

    def _build(version, total_dur, slides_dir):
        # Only v1 override — other versions fall through
        if version != "v1":
            return _orig_build(version, total_dur, slides_dir)

        seg = [0.20, 0.30, 0.30, 0.20]
        durs = [total_dur * r for r in seg]
        clips = []

        # 1: V1 cover với hook text tuỳ biến
        s1 = batch1.make_image_slide(batch1.COVER_V1, [
            {"text": hook_line1, "size": 72, "y": 200, "color": "#FF3366", "bold": True},
            {"text": hook_line2, "size": 60, "y": 310, "color": "#3D2200", "bold": True},
        ], durs[0], style="fill", brightness=1.10)
        s1.save(f"{slides_dir}/v1-s1.png")
        c1 = ImageClip(f"{slides_dir}/v1-s1.png", duration=durs[0]).with_effects([FadeIn(0.3)])
        clips.append(c1)

        c2 = batch1.prep_video(batch1.VID_ASMR, durs[1], crop_wm=True).with_effects([FadeIn(CROSSFADE), FadeOut(CROSSFADE)])
        clips.append(c2)

        c3 = batch1.prep_video(batch1.VID_SLOW, durs[2], crop_wm=True).with_effects([FadeIn(CROSSFADE), FadeOut(CROSSFADE)])
        clips.append(c3)

        s4 = batch1.make_image_slide(batch1.FLAT, [
            {"text": "FOLLOW EM NGÀY THỨ 3", "size": 64, "y": H - 320, "color": "#FF3366", "bold": True},
            {"text": "Tim • Comment • Follow", "size": 50, "y": H - 220, "color": "#3D2200", "bold": True},
        ], durs[3], style="fill", brightness=1.18)
        s4.save(f"{slides_dir}/v1-s4.png")
        clips.append(ImageClip(f"{slides_dir}/v1-s4.png", duration=durs[3]).with_effects([FadeIn(CROSSFADE)]))

        return clips

    return _build


async def main():
    print("\n>>> RE-RENDER V1 — 3 HOOK VARIATIONS <<<\n")
    results = []
    for vkey, v in VARIATIONS.items():
        print(f"\n{'=' * 60}\n=== {vkey} ===\n{'=' * 60}")
        h1, h2 = v["hook_slide"]
        # Monkey-patch build_segments for this variation
        batch1.build_segments = build_v1_with_hook(h1, h2)

        # Craft config mimicking batch1 format, reuse make_video
        cfg = {
            "rate": "+30%",
            "voice": v["voice"],
            "segments_builder": "v1",
        }
        try:
            out = await batch1.make_video(vkey, cfg)
            results.append((vkey, out, "OK"))
        except Exception as e:
            print(f"  FAIL {vkey}: {e}")
            results.append((vkey, None, f"FAIL: {e}"))

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    for k, f, s in results:
        print(f"  {s:8s} | {k:32s} | {f or '-'}")


if __name__ == "__main__":
    asyncio.run(main())
