---
phase: 3
title: "Content Generation Pipeline"
status: pending
effort: 10h
priority: P1
depends_on: [1, 2]
---

# Phase 3: Content Generation Pipeline

## Context Links
- [Gemini API docs](https://ai.google.dev/gemini-api/docs)
- [Gemini Image Generation](https://ai.google.dev/gemini-api/docs/image-generation)
- [Gemini TTS](https://ai.google.dev/gemini-api/docs/speech-generation)
- [Gemini Video (Veo)](https://ai.google.dev/gemini-api/docs/video)
- [Pricing](https://ai.google.dev/gemini-api/docs/pricing)

## Overview
The core pipeline: user provides a product idea, system generates script, images, voiceover, and optionally video clips. Always checks asset DB before calling APIs.

## Key Insights from Research

### Gemini API Models & Pricing (April 2026)
| Task | Model | Cost |
|------|-------|------|
| Script/text | gemini-2.5-flash | ~$0.001/call |
| Images | gemini-2.5-flash (native) or Imagen 4 | $0.02-0.04/image |
| TTS | gemini-2.5-flash-tts | ~$0.01/30s |
| Video | veo-3.0/3.1 | $0.75/sec (~$6/8s clip) |

### Cost Optimization Strategy
- **Default to slideshow** (images + TTS): ~$0.15-0.25/video
- **Video clips (Veo) only for hero content**: ~$6+/video
- **Reuse assets aggressively**: same product images across multiple videos
- **Batch generation**: generate 5 images at once, pick best

### Vietnamese Content Notes
- Gemini supports Vietnamese text generation well
- TTS Vietnamese voice quality varies -- test voices: "Leda", "Kore"
- Product names should be in Vietnamese for authenticity

## Requirements

### Functional
- Accept product idea as input (CLI)
- Generate video script with hook, body, CTA structure
- Generate product images (5 per product)
- Generate voiceover from script (Vietnamese)
- Optionally generate video clips (Veo -- expensive)
- Save ALL generated content as reusable assets
- Check asset DB before every API call

### Non-Functional
- Retry on API failures (max 3 attempts)
- Log all API calls with cost
- Support cancellation mid-pipeline
- Graceful handling of rate limits

## Architecture

### Pipeline Flow
```
User Input: "Nuoc giat Omo gia re, thom lau"
    |
    v
[1. Idea Refiner]
    - Input: raw idea text
    - Output: structured brief (product, key benefits, target audience)
    - Model: gemini-2.5-flash
    - Cost: ~$0.001
    |
    v
[2. Script Generator]
    - Input: structured brief
    - Output: script with sections (hook 3s, body 20s, CTA 5s)
    - Model: gemini-2.5-flash
    - Cost: ~$0.001
    |
    v
[3. Asset Check] <-- CRITICAL COST GATE
    - Search DB for existing assets matching product/tags
    - Skip generation for any found assets
    - Only generate what's missing
    |
    v
[4a. Image Generator]          [4b. TTS Generator]
    - Product photos              - Vietnamese voiceover
    - Gemini/Imagen               - gemini-2.5-flash-tts
    - 1080x1920 vertical          - WAV output
    - 5 images per product        - ~30s duration
    - Cost: $0.10-0.20            - Cost: ~$0.01
    |                              |
    v                              v
[5. Save to Asset DB]
    - All outputs saved with tags, cost, prompt
    - Ready for video assembly (Phase 4)
```

### Prompt Templates (Vietnamese context)

#### Idea Refiner Prompt
```
Ban la mot chuyen gia marketing TikTok tai Viet Nam.
Phan tich y tuong san pham sau va tra ve:
1. Ten san pham chinh xac
2. 3-5 diem noi bat (USP)
3. Doi tuong muc tieu
4. Hashtag goi y (5-10 hashtags)
5. Goc quay/phong cach video goi y

Y tuong: {user_input}
```

#### Script Generator Prompt
```
Viet kich ban video TikTok 30 giay cho san pham: {product_name}
Diem noi bat: {usps}

Cau truc:
- HOOK (3 giay): Cau noi gay soc/to mo, VD: "Cai nay ma 29k thoi a?"
- THAN BAI (20 giay): Gioi thieu 2-3 uu diem chinh, trai nghiem thuc te
- CTA (5 giay): Keu goi mua hang, "Link san pham o bio nhe!"

Yeu cau: Ngon ngu tu nhien, than thien, dung tu phia Bac hoac Nam tuy san pham.
Tra ve dang JSON voi cac truong: hook, body, cta, full_script
```

#### Image Generation Prompt
```
Product photography of {product_name}, Vietnamese style,
clean white/light background, studio lighting,
vertical composition 9:16, high quality,
{additional_context}
```

## Related Code Files
- **Create**: `src/content/idea_refiner.py` -- Parse idea into structured brief
- **Create**: `src/content/script_gen.py` -- Generate TikTok script
- **Create**: `src/content/image_gen.py` -- Generate product images via Gemini
- **Create**: `src/content/tts_gen.py` -- Generate Vietnamese voiceover
- **Create**: `src/content/video_gen.py` -- Generate video clips via Veo (optional)
- **Create**: `src/content/pipeline.py` -- Orchestrate full pipeline

## Implementation Steps

### 1. Gemini API wrapper (`src/content/gemini_client.py`)
- Singleton client with API key from config
- Methods: `generate_text()`, `generate_image()`, `generate_tts()`, `generate_video()`
- Built-in retry logic (exponential backoff)
- Cost calculation per call
- Rate limit handling

### 2. Idea Refiner (`idea_refiner.py`)
- Accept raw text input
- Call Gemini Flash with Vietnamese prompt
- Parse structured response (JSON)
- Return: product name, USPs, target audience, hashtags

### 3. Script Generator (`script_gen.py`)
- Accept refined idea
- Generate 30s TikTok script in Vietnamese
- Structure: hook (3s) + body (20s) + CTA (5s)
- Return JSON with sections and full_script
- Save script as text asset

### 4. Image Generator (`image_gen.py`)
- **First**: check AssetManager for existing product images
- If found: return existing, log "reused asset"
- If not found: generate via Gemini
- Generate 5 images per product (pick best later)
- Save as assets with product tag
- Resolution: 1080x1920 (vertical)

### 5. TTS Generator (`tts_gen.py`)
- **First**: check AssetManager for existing voiceover of same script
- Generate Vietnamese voiceover from script text
- Model: gemini-2.5-flash-tts
- Output: WAV file (24kHz, 16-bit PCM)
- Save as asset with script hash tag

### 6. Video Generator (`video_gen.py`) -- OPTIONAL/EXPENSIVE
- Only triggered by explicit user flag `--use-veo`
- Generate 8s video clip via Veo 3.x
- Poll for completion (async operation)
- Save as asset
- DEFAULT: skip this, use slideshow instead

### 7. Pipeline Orchestrator (`pipeline.py`)
- `run_pipeline(idea: str, use_veo: bool = False) -> Project`
- Step through: refine -> script -> assets check -> generate -> save
- Create Project record linking all assets
- Print cost summary after completion
- Support `--dry-run` to show what would be generated without API calls

### 8. CLI integration
- `pel create <idea>` -- full pipeline
- `pel create <idea> --dry-run` -- preview only
- `pel create <idea> --use-veo` -- include video generation
- `pel create <idea> --reuse-only` -- only use existing assets

## Todo List
- [ ] Create Gemini client wrapper with retry + cost tracking
- [ ] Implement Idea Refiner with Vietnamese prompts
- [ ] Implement Script Generator (hook/body/CTA structure)
- [ ] Implement Image Generator with asset-first check
- [ ] Implement TTS Generator with asset-first check
- [ ] Implement Video Generator (Veo, optional)
- [ ] Create Pipeline Orchestrator
- [ ] Add CLI commands
- [ ] Test full pipeline with a real product
- [ ] Tune Vietnamese prompts based on output quality
- [ ] Add --dry-run support

## Success Criteria
- `pel create "Nuoc giat Omo 29k"` produces: script + 5 images + voiceover
- All generated content saved as assets in DB
- Second run for same product reuses assets (no API calls)
- Cost summary printed after each run
- Vietnamese script reads naturally

## Risk Assessment
- **Gemini Vietnamese quality**: May need prompt iteration; mitigation: save best prompts as templates
- **TTS Vietnamese accent**: Test multiple voices; user can pick preferred voice in config
- **Veo cost ($6/clip)**: Default OFF; only for special content
- **Rate limits**: Exponential backoff + daily cost cap in config
- **Image quality**: Generate 5, let user pick; or auto-select best via Gemini scoring

## Security Considerations
- API key in .env only, never in code
- .env in .gitignore
- Daily cost cap configurable (default: $5/day)
- User confirmation before expensive operations (Veo)
