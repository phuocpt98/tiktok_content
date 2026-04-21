---
phase: 4
title: "Video Assembly Engine"
status: pending
effort: 8h
priority: P1
depends_on: [1, 3]
---

# Phase 4: Video Assembly Engine

## Context Links
- [ffmpeg-python docs](https://github.com/kkroening/ffmpeg-python)
- [FFmpeg slideshow guide](https://shotstack.io/learn/use-ffmpeg-to-convert-images-to-video/)
- [TikTokAIVideoGenerator (reference)](https://github.com/GabrielLaxy/TikTokAIVideoGenerator)

## Overview
Combine generated assets (images, audio, video clips) into final TikTok-ready vertical videos using FFmpeg. Support multiple content types: slideshow, short video, and mixed format.

## Key Insights
- FFmpeg is the industry standard, free, handles everything we need
- `ffmpeg-python` wrapper makes it Pythonic
- Slideshow = cheapest content type (no Veo needed)
- TikTok specs: 9:16 vertical, 1080x1920, MP4 H.264, AAC audio, max 10min

## Requirements

### Functional
- Assemble slideshow videos (images + audio + optional background music)
- Assemble video clips (concatenate Veo clips + audio)
- Add text overlays (captions, product name, price)
- Add transitions between images (fade, slide)
- Add background music (from local library)
- Output: MP4, H.264, 1080x1920, 30fps

### Non-Functional
- Assembly completes in <60s for a 30s video
- Preview before final render
- Configurable templates (timing, transitions)

## Architecture

### Video Templates

#### Template 1: Slideshow (Default, Cheapest)
```
[Image 1: Hook shot]     0-3s   + voiceover hook
[Image 2: Product detail] 3-10s  + voiceover body pt1
[Image 3: Usage/benefit]  10-18s + voiceover body pt2
[Image 4: Comparison]     18-23s + voiceover body pt3
[Image 5: CTA/price]      23-28s + voiceover CTA
+ Background music (low volume, looped)
+ Text overlays (product name, price, hashtags)
```

#### Template 2: Video Mix
```
[Veo clip: product in use] 0-8s  + voiceover hook+body
[Image slideshow]          8-20s + voiceover body
[Veo clip: CTA]            20-28s + voiceover CTA
+ Background music + text overlays
```

#### Template 3: Quick Review (15s)
```
[Image 1: Product]  0-3s   + voiceover hook
[Image 2: Detail]   3-8s   + voiceover benefit
[Image 3: CTA]      8-13s  + voiceover CTA
+ Background music + text overlay
```

### FFmpeg Pipeline
```python
def assemble_slideshow(images, audio, music=None, captions=None):
    # 1. Scale all images to 1080x1920
    # 2. Create image sequence with durations
    # 3. Add fade transitions between images
    # 4. Overlay voiceover audio
    # 5. Mix background music (20% volume)
    # 6. Add text overlays (drawtext filter)
    # 7. Encode H.264 + AAC
    # 8. Output MP4
```

### Text Overlay System
- Product name: top center, white with shadow
- Price: bottom left, yellow/red highlight
- CTA text: bottom center, animated
- Font: Vietnamese-compatible (e.g., Roboto, or system font)

## Related Code Files
- **Create**: `src/video/assembler.py` -- Main assembly logic
- **Create**: `src/video/templates.py` -- Video template definitions
- **Create**: `src/video/effects.py` -- Transitions, text overlays
- **Create**: `src/video/preview.py` -- Quick preview generation

## Implementation Steps

### 1. FFmpeg helper functions (`assembler.py`)
```python
class VideoAssembler:
    def __init__(self, output_dir, temp_dir):
        ...

    def assemble(self, project: Project, template: str = "slideshow") -> str:
        """Main entry: takes a Project with linked assets, returns output path"""

    def _scale_image(self, image_path, width=1080, height=1920) -> str:
        """Scale/crop image to exact 9:16"""

    def _create_slideshow(self, images, durations) -> str:
        """Images -> video track with transitions"""

    def _add_audio(self, video_path, voiceover_path, music_path=None) -> str:
        """Mix voiceover + optional background music"""

    def _add_text_overlay(self, video_path, texts: list[TextOverlay]) -> str:
        """Add drawtext filters for captions"""

    def _encode_final(self, video_path, output_path) -> str:
        """Final encode: H.264, AAC, TikTok-compatible"""
```

### 2. Image preparation
- Resize/crop all images to exactly 1080x1920
- Use Pillow for pre-processing (pad with blur background if aspect ratio differs)
- Ken Burns effect: slight zoom/pan on still images for motion feel

### 3. Slideshow assembly
```bash
# Core FFmpeg command (simplified)
ffmpeg -loop 1 -t 5 -i img1.png \
       -loop 1 -t 5 -i img2.png \
       -filter_complex "[0:v]fade=t=out:d=0.5[v0]; \
                         [1:v]fade=t=in:d=0.5[v1]; \
                         [v0][v1]concat=n=2:v=1:a=0" \
       -c:v libx264 -pix_fmt yuv420p output.mp4
```

### 4. Audio mixing
```bash
# Mix voiceover (100%) + music (20%)
ffmpeg -i video.mp4 -i voiceover.wav -i music.mp3 \
       -filter_complex "[1:a]volume=1.0[vo]; \
                         [2:a]volume=0.2,aloop=-1:0[music]; \
                         [vo][music]amix=inputs=2[a]" \
       -map 0:v -map "[a]" -shortest output.mp4
```

### 5. Text overlays
```bash
# Vietnamese-compatible text overlay
ffmpeg -i video.mp4 \
       -vf "drawtext=text='Nuoc giat Omo 29k':fontsize=48: \
            fontcolor=white:borderw=3:bordercolor=black: \
            x=(w-text_w)/2:y=100:fontfile=Roboto.ttf" \
       output.mp4
```

### 6. Template system (`templates.py`)
- Define timing, transitions, text positions per template
- JSON/dict config so user can customize
- Presets: "slideshow_30s", "quick_review_15s", "video_mix_30s"

### 7. Preview mode (`preview.py`)
- Generate low-res (540x960) preview quickly
- Open in default video player
- User approves before final render

### 8. CLI commands
- `pel render <project_id> [--template slideshow]`
- `pel render <project_id> --preview`
- `pel render <project_id> --template quick_review`

### 9. Background music library
- Create `data/music/` folder
- Include 3-5 royalty-free background tracks
- Auto-select based on product category
- Loop and volume-adjust automatically

## Todo List
- [ ] Create VideoAssembler class structure
- [ ] Implement image scaling/cropping to 1080x1920
- [ ] Implement slideshow creation with fade transitions
- [ ] Implement audio mixing (voiceover + background music)
- [ ] Implement text overlay system (Vietnamese font support)
- [ ] Create template definitions (slideshow, quick_review, video_mix)
- [ ] Implement preview mode (low-res quick render)
- [ ] Add Ken Burns effect for still images
- [ ] Add CLI render command
- [ ] Set up background music library
- [ ] Test end-to-end: images + audio -> final MP4
- [ ] Verify TikTok compatibility (upload test video)

## Success Criteria
- `pel render 1 --template slideshow` produces valid 1080x1920 MP4
- Video plays correctly on phone (9:16 vertical)
- Vietnamese text renders correctly (no tofu/missing chars)
- Audio is clear, music at appropriate volume
- Assembly time <60s for 30s video
- Preview mode generates in <10s

## Risk Assessment
- **Vietnamese font rendering**: Mitigation -- bundle Roboto or use system Vietnamese font, test early
- **FFmpeg filter complexity**: Mitigation -- build incrementally, test each filter separately
- **Audio sync issues**: Mitigation -- use -shortest flag, test with varying audio lengths
- **Large output files**: Mitigation -- use H.264 CRF 23 (good quality, reasonable size ~10-20MB for 30s)
