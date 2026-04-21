---
type: planner
date: 2026-04-13
slug: tiktok-pel-pel-manager
---

# Planner Report: Tap hoa Pel Pel - TikTok Affiliate Content System

## Research Summary

### TikTok Content Posting API
- Requires developer app registration + TikTok audit for public posting
- Unaudited apps restricted to PRIVATE mode only
- Supports FILE_UPLOAD and PULL_FROM_URL methods
- **Verdict**: Start manual posting, apply for API access in parallel

### Gemini API (April 2026)
- **Text**: gemini-2.5-flash -- $0.10/1M input tokens, negligible per call
- **Images**: Imagen 4 ($0.02-0.06/image) or native flash ($0.039/image)
- **TTS**: gemini-2.5-flash-tts -- $0.50 input / $10.00 output per 1M tokens (~$0.01/30s)
- **Video**: Veo 3.x -- $0.75/sec (8s = $6.00) -- EXPENSIVE, use sparingly
- **Recommendation**: Default to slideshow (images+TTS) at ~$0.15-0.25/video

### Video Assembly
- FFmpeg is standard; `ffmpeg-python` wrapper for Python
- Key commands: slideshow from images, audio mixing, text overlays
- Reference project: TikTokAIVideoGenerator on GitHub
- TikTok specs: 9:16, 1080x1920, H.264, AAC

### TikTok Shop Affiliate Vietnam
- 431K TikTok shops in Vietnam (2026)
- Creator needs 1,000+ followers for external product links
- Two collab modes: Open (public) and Target (private)
- Commission: 5-30% per sale
- Products must be listed on TikTok Shop

## Plan Created
- **Location**: `plans/260413-1416-tiktok-pel-pel-manager/`
- **6 phases**, total ~40h effort
- **Critical insight**: Slideshow mode ($0.15-0.25) vs Veo mode ($6+) -- 25x cost difference

## Key Recommendations
1. Start with slideshow-only content (cheapest, fastest)
2. Build asset reuse system early -- biggest cost lever
3. Manual TikTok posting initially, API later
4. Focus first 1000 followers milestone to unlock affiliate links
5. Vietnamese prompts need iteration -- budget time for prompt tuning

## Unresolved Questions
- Which Vietnamese TTS voice sounds most natural? (needs hands-on testing)
- Gemini image quality for Vietnamese product photography -- acceptable or need real photos?
- TikTok API audit timeline -- how long does approval take?
- Background music licensing -- what royalty-free sources work for Vietnam commercial use?
