# TikTok Upload Automation Tools Research Report
**Date:** 2026-04-14 | **Updated:** 15:51

---

## Executive Summary

Research identified **3 production-ready TikTok upload automation tools** actively maintained in 2024-2026. None explicitly advertise Photo Mode/carousel support — all focus on video upload. **TikTok's official Content Posting API** supports photo uploads via `/v2/post/publish/content/init/` but requires developer approval. For Pel Pel channel (Creator Account, Photo Mode priority), automation via browser-based tools is the most practical short-term approach, with official API as longer-term alternative.

---

## Tools Comparison

| **Project** | **Stars** | **Last Commit** | **Language** | **Method** | **Key Strength** | **Photo Mode** | **Windows** |
|---|---|---|---|---|---|---|---|
| **tiktok-uploader** (wkaisertexas) | 710 | Dec 2024 | Python | Playwright + cookies | Stable, documented | ❌ Not mentioned | ✓ Yes |
| **TiktokAutoUploader** (makiisthenes) | 989 | Mar 2025 | Python/Node.js | Requests + undetected-chromedriver | Fastest (~3s), YouTube Shorts integration | ❌ Not mentioned | ✓ Yes |
| **TikTokAutoUploader** (haziq-exe) | 242 | Feb 2026 | Python | Phantomwright (bot evasion) | Latest update, stealth, scheduling | ❌ Not mentioned | ✓ Yes |

---

## Detailed Analysis

### 1. **tiktok-uploader** (wkaisertexas)
- **GitHub**: [wkaisertexas/tiktok-uploader](https://github.com/wkaisertexas/tiktok-uploader)
- **Stars/Forks**: 710 / 161
- **Last Commit**: December 12, 2024
- **Open Issues**: 12
- **Architecture**: Playwright-based browser automation using exported TikTok cookies
- **Key Features**: Batch uploads, scheduling, hashtags, custom covers, product linking, headless mode
- **Photo Support**: Not documented; assumes video-only (standard Playwright browser approach)
- **Windows Compatibility**: ✓ Full support
- **Dependencies**: Python ≥3.10, Playwright (installs Chromium/Firefox), Node.js
- **Maturity**: Stable with consistent maintenance; PyPI package available

### 2. **TiktokAutoUploader** (makiisthenes)
- **GitHub**: [makiisthenes/TiktokAutoUploader](https://github.com/makiisthenes/TiktokAutoUploader)
- **Stars/Forks**: 989 / 216
- **Last Commit**: March 9, 2025
- **Open Issues**: 42
- **Architecture**: Hybrid approach — HTTP requests + undetected-chromedriver + Playwright; uses Node.js for TikTok signature generation
- **Key Features**: Ultra-fast (~3s per video), YouTube Shorts auto-download, multi-account, scheduling 10 days ahead, robust against interface changes
- **Photo Support**: Not documented; video-focused design
- **Windows Compatibility**: ✓ Full support (CLI-first)
- **Dependencies**: Python 3, Node.js, yt-dlp (for YouTube Shorts), undetected-chromedriver
- **Maturity**: Highest star count; actively maintained; professional quality

### 3. **TikTokAutoUploader** (haziq-exe)
- **GitHub**: [haziq-exe/TikTokAutoUploader](https://github.com/haziq-exe/TikTokAutoUploader)
- **Stars/Forks**: 242 / 23
- **Last Commit**: February 2026 (most recent)
- **Open Issues**: 3
- **Architecture**: Phantomwright (patched Playwright replacement designed for bot detection evasion)
- **Key Features**: Automated CAPTCHA solving, Telegram bot integration, trending audio integration, scheduling 10 days, stealth fingerprint spoofing, multi-account
- **Photo Support**: Not documented
- **Windows Compatibility**: ✓ Full support
- **Dependencies**: Python, Phantomwright, requests, Telegram SDK
- **Maturity**: Most recent updates; fewest open issues; stealth-focused design

---

## Photo Mode / Carousel Upload Status

### Browser Automation Tools (Current)
- **Finding**: None of the three popular tools explicitly support Photo Mode carousels
- **Reason**: Photo Mode is handled differently in TikTok's DOM — it requires navigating to a separate upload path and selecting multiple images; requires separate implementation
- **Current Workaround**: All tools support uploading a **cover image** with video uploads, but not native photo carousels
- **Challenge**: TikTok's "Upload cover" UI accepts images but silently discards them server-side (haziq-exe project notes this)

### Official TikTok Content Posting API
- **Documentation**: [TikTok Content Posting API — Photo Post](https://developers.tiktok.com/doc/content-posting-api-reference-photo-post)
- **Support**: ✓ Officially supports multiple image uploads via `photo_images` parameter
- **Endpoint**: `/v2/post/publish/content/init/` for photo uploads
- **Requirements**:
  - Developer account + app approval
  - Creator Account status on TikTok
  - User must authorize `video.publish` scope
  - Rate limit: 6 requests/minute per access token
- **Advantage**: Native, reliable, no bot-detection risk
- **Disadvantage**: Requires official API approval (typically 3-7 days for Vietnamese channels)

---

## Recommendation for Pel Pel Channel

### Short-term (Next 1-2 weeks): Browser Automation
**Use**: [**TiktokAutoUploader (makiisthenes)**](https://github.com/makiisthenes/TiktokAutoUploader)
- **Why**:
  - Fastest execution (3s per upload)
  - Highest community trust (989 stars)
  - Mature, well-documented
  - Recent updates (Mar 2025)
  - Windows-native CLI (no extra setup)
- **Scope**: Video uploads + slideshow workaround (create video slideshows instead of photo carousels)
- **Setup**: ~30 min (Python, Node.js, cookie export)

### Medium-term (2-4 weeks): Official API + Photo Mode
**Path**: Apply for TikTok Content Posting API
- **Why**: Native Photo Mode support, no bot detection risk
- **Steps**:
  1. Register TikTok Developer account (free)
  2. Create app, request `video.publish` scope
  3. Submit Creator Account details (Pel Pel info)
  4. Wait for approval (~3-7 days)
  5. Implement Python wrapper around `/v2/post/publish/content/init/`
- **Advantage**: Future-proof; scales with channel growth
- **Timeline**: Can start development immediately while waiting for approval

### Hybrid Approach (Recommended)
- **Immediate**: Use makiisthenes tool for video content (can auto-generate slideshows from photo sets)
- **Parallel**: Apply for official API + start building Photo Mode integration
- **Switch**: Migrate to official API once approved (cleaner, safer for long-term growth)

---

## Technical Considerations for Windows

### Setup Requirements (All Tools)
```
✓ Python ≥3.10 (install from python.org)
✓ Playwright/Phantomwright browsers (auto-downloaded)
✓ Node.js 14+ (for signature generation in some tools)
✓ Chrome/Chromium (auto-installed by Playwright)
✓ FFmpeg (optional, for video processing)
```

### TikTok Cookie Export (Required for All Browser Tools)
1. Open TikTok in Chrome
2. Login to Pel Pel account
3. Open DevTools (F12) → Application → Cookies → tiktok.com
4. Export to `cookies.json` or copy manually
5. Pass to tool via config

### Firewall & VPN Considerations
- Tools support HTTP proxies (useful for rate limiting)
- Vietnamese channel: No special setup needed (domestic uploads)
- Recommended: Test first without VPN to avoid login issues

---

## Unresolved Questions

1. **Photo Mode DOM structure**: Has TikTok's Photo Mode upload flow changed in 2026? (Last verified search results are Feb 2026)
2. **API approval timeline**: Does TikTok prioritize Vietnamese creator accounts differently? (No data on approval SLA by region)
3. **Rate limiting**: What's the actual max upload frequency without triggering bot detection? (Tools avoid testing this)
4. **Cover image server-side handling**: Is the "server-side discard" issue in haziq-exe project still current, or has TikTok fixed it?

---

## Sources

- [wkaisertexas/tiktok-uploader](https://github.com/wkaisertexas/tiktok-uploader)
- [makiisthenes/TiktokAutoUploader](https://github.com/makiisthenes/TiktokAutoUploader)
- [haziq-exe/TikTokAutoUploader](https://github.com/haziq-exe/TikTokAutoUploader)
- [TikTok Content Posting API Overview](https://developers.tiktok.com/doc/content-posting-api-reference-photo-post)
- [TikTok Content Posting API Getting Started](https://developers.tiktok.com/doc/content-posting-api-get-started)
- [How to Post Photos and Carousels on TikTok with Photo Mode](https://www.kapwing.com/resources/how-to-post-photos-and-carousels-on-tiktok-with-photo-mode/)
- [TikTok for Developers](https://developers.tiktok.com/)
