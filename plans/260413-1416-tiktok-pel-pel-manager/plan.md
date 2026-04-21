---
title: "Tạp Hóa Pel Pel - TikTok Content System"
description: "AI content production system - Claude operates pipeline, user reviews"
status: in-progress
priority: P1
tags: [tiktok, affiliate, ai-content, python, gemini, vietnam]
created: 2026-04-13
updated: 2026-04-13
---

# Tạp Hóa Pel Pel - TikTok Content System

## Operating Model
```
User (Creative Director)  →  Claude (Production Team)  →  Output
    đưa ý tưởng               vận hành pipeline           user duyệt
    duyệt kết quả             gọi API, tạo content        đăng TikTok
    ra quyết định              báo cáo, gợi ý
```

## Skill: `/pelpel`
| Command | Mô tả |
|---------|-------|
| `/pelpel <ý tưởng>` | Tạo content full pipeline |
| `/pelpel trend` | Quét trend TikTok |
| `/pelpel plan` | Lên content plan tuần |
| `/pelpel report` | Báo cáo tổng kết kênh |
| `/pelpel assets` | Xem kho tài nguyên |

## Content Formats (ưu tiên)
1. **Photo Mode slides** — 5-10 ảnh, upload TikTok Photo Mode (dễ viral nhất)
2. **Ảnh + text overlay** — nhúng chữ/quote trending lên ảnh
3. **Slideshow video** — ảnh + voiceover (Edge TTS) + nhạc
4. **Video ngắn** — AI-generated (sau)

## Modules Built

| Module | File | Status |
|--------|------|--------|
| Config | `src/config.py` | ✅ |
| Database | `src/database.py` | ✅ |
| Gemini Client | `src/gemini-client.py` | ✅ |
| TTS Engine | `src/tts-engine.py` | ✅ |
| Video Assembler | `src/video-assembler.py` | ✅ |
| Asset Importer | `src/asset-importer.py` | ✅ |
| Text Overlay | `src/text-overlay.py` | ✅ |
| Trend Tracker | `src/trend-tracker.py` | ✅ |
| CLI | `src/cli.py` | ✅ |

## Strategy
```
STAGE 1 (now): Cày Followers 0→1K | 100% viral content | NO selling
STAGE 2 (1K+): Affiliate | 70% value + 30% product links
```

## Key Decisions
- **Claude = operator** — user không chạy CLI, Claude gọi tools
- **Dual-mode** — API auto + Gemini Web manual, per-step
- **Photo Mode first** — dễ hơn video, viral hơn
- **Trend-driven** — quét trend → tạo content theo trend
- **Asset reuse** — lưu mọi asset, remix tiết kiệm API
- **Memory** — lưu context kênh xuyên sessions
