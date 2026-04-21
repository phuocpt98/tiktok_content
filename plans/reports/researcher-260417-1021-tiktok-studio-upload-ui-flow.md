# TikTok Studio Web Upload UI Flow Research

**Date:** 2026-04-17
**Focus:** Exact UI flow, form elements, selectors, and 2025-2026 changes for automation via Playwright

---

## Executive Summary

TikTok Studio Web (`www.tiktok.com/tiktokstudio/upload`) lacks public technical documentation on form selectors and UI element structure. Open-source Playwright automation projects exist (wkaisertexas/tiktok-uploader, haziq-exe/TikTokAutoUploader) but rely on proprietary XPath/CSS mappings that are not fully exposed in READMEs. **Selector details must be reverse-engineered from live inspection or extracted from source code repos.**

---

## 1. Upload Page URL

**Primary:** `https://www.tiktok.com/tiktokstudio/upload`
**Alternative:** `https://www.tiktok.com/tiktokstudio/upload?from=webapp`
**Creator Center Variant:** `https://www.tiktok.com/tiktokstudio/upload?from=creator_center`

---

## 2. Step-by-Step UI Flow

### Known Upload Process

1. **File Input** — Select video file (MP4, WebM, MOV, etc.)
2. **Caption Field** — Enter video description/caption
3. **Hashtag Input** — Add hashtags (#tag format)
4. **Sound Selection** — Choose TikTok sound or original audio
5. **Cover Image** — Select/upload custom thumbnail
6. **Location Field** — (Optional) Add location tag
7. **Post Scheduling** — Set publish time (up to 10 days ahead)
8. **Submit/Post** — Publish to feed

### Gaps in Public Documentation

- **Exact form field ordering** on current web interface not documented
- **Suggested sounds modal** location and interaction flow unclear
- **CapCut template integration** status on web upload (appears to be mobile-first feature)
- **Audio volume controls** (original vs. added music) may not be available on web, or hidden in advanced settings

---

## 3. Form Elements (Inferred from Automation Projects)

### wkaisertexas/tiktok-uploader Project

- **Config Storage:** All XPath selectors stored in `config.toml`
- **Key Functions:**
  - `upload_videos()` — Main upload function
  - `capture_cover()` — Cover image handling
  - Upload with caption/description
  - Hashtag support
  - Cover image formats: `.png`, `.jpeg`, `.jpg`

**Status:** Last commit 6 days ago (February 2025); 673 GitHub stars; uses Playwright after Selenium deprecation.

### haziq-exe/TikTokAutoUploader Project (Feb 2026)

**Documented Parameters:**
- `sound_aud_vol` — Audio balance control: `'main'` (original), `'mix'` (blend), `'background'` (music-only)
- Sound search mode: `'search'` (by name) or `'favorites'` (from library)
- Hashtag input: Must be space-separated to appear as clickable hashtags
- Cover editor & frame slider for custom thumbnails
- Copyright checking before upload
- Post scheduling support

**Engine:** Phantomwright (Playwright wrapper with bot-detection evasion)

---

## 4. Suggested Sounds & Templates

### Sounds Feature Status
- **Web availability:** Unclear if "suggested sounds" modal is fully exposed on web version
- **Mobile reference:** iOS/Android TikTok app shows Sound Library recommendations by video type
- **Automation approach:** Haziq project uses sound search (by name) or favorites list as fallback
- **Default:** Sound mixing parameter default is `sound_aud_vol='mix'` to avoid failures

### CapCut Templates
- **Not found** in web upload flow documentation
- **Appears to be** mobile/native app feature, not integrated into TikTok Studio web
- **Alternative:** Users edit in CapCut desktop, then upload final video to TikTok Studio

---

## 5. Audio Volume Control on Web

**Finding:** Explicit audio volume slider/control **not documented** for web upload.

- **Inferred capability:** May be buried in "advanced settings" or not exposed on web
- **Automation approach:** TikTokAutoUploader handles this server-side via `sound_aud_vol` parameter
- **Limitation:** Web UI may default to automatic mixing (no manual controls)

---

## 6. CSS Selectors & Identifiers

### Available Information

**From GitHub projects:**
- `config.toml` in wkaisertexas/tiktok-uploader contains XPath selectors (not publicly exposed in detail)
- Selectors are version-fragile; TikTok UI changes break them frequently

**Reality check:**
- TikTok actively updates UI (noted in Feb 2025 "build-uv-v1.7" release: "Updates to Handle TikTok's Changing User Interface")
- No canonical selector registry published by TikTok
- All projects rely on **manual browser inspection** (DevTools F12) to reverse-engineer current selectors

### How to Find Current Selectors

```
1. Open https://www.tiktok.com/tiktokstudio/upload
2. Right-click on element → Inspect
3. Find class names, IDs, or data-testid attributes
4. Test with CSS selectors like: [data-testid="..."], .caption-input, input[type="file"]
```

---

## 7. 2025-2026 UI Changes

### Confirmed Updates

1. **Playwright Modernization** (Feb 2025) — wkaisertexas project upgraded auth flows and client APIs
2. **Smart Split Feature** — AI-powered video editing tool added to TikTok Studio
3. **Extended Video Length** — Testing 30-minute uploads (was ~10-60 min limit before)
4. **Accessibility Improvements** — New text size options
5. **AI Avatar Stickers** — Personalized avatar generation within Studio

### No Major Upload Form Overhaul

- Core flow (file → caption → post) remains stable
- Selector changes likely incremental, not wholesale layout redesign
- XPath/CSS mappings require periodic refresh (quarterly or after major rollouts)

---

## 8. Known Limitations & Risks

| Issue | Impact |
|-------|--------|
| No official TikTok automation API docs | Selectors must be reverse-engineered |
| Frequent UI updates | Selectors break every few months |
| No public "sounds" endpoint on web | Sound selection may require UI scraping |
| CapCut integration unclear | May not be available on web at all |
| Audio volume hidden | May not have manual web controls |
| Region/account-based UI variance | Selectors may differ by geography/account type |

---

## 9. Recommended Approach for Playwright Automation

### Phase 1: Reverse-Engineer Current Selectors
1. Open TikTok Studio upload page live
2. Use DevTools to inspect each form element
3. Document `[data-testid]`, CSS class names, input IDs
4. Create mapping file (e.g., `selectors.json`)

### Phase 2: Implement Stable Selectors
```python
# Example Playwright selector strategy
file_input = page.locator('input[type="file"]')
caption_field = page.locator('[data-testid="caption-input"]')  # or similar
hashtag_input = page.locator('textarea[placeholder*="hashtag"]')  # adjust as needed
publish_button = page.locator('button:has-text("Post")')  # or "Publish"
```

### Phase 3: Add Fallback Logic
- Use multiple selector strategies (ID > data-testid > class > XPath)
- Implement retry loops with selector validation
- Log failures with screenshot for manual inspection

### Phase 4: Monitor & Maintain
- Run selectors monthly on live page
- Add assertions to catch UI breaks early
- Document TikTok update dates and selector changes

---

## 10. Open Questions

1. **Is "suggested sounds" a dedicated modal on web, or embedded inline?** → Need live inspection
2. **Does web upload support CapCut template integration?** → Appears NO, but verify
3. **What are exact HTML class names for caption and hashtag inputs?** → Varies; must inspect live
4. **Can audio volume be controlled via web form, or server-side only?** → Automation projects handle server-side; web UI control unclear
5. **Is there a region-specific UI variant (US vs. other markets)?** → Likely yes; test with target account
6. **How often does TikTok update upload form selectors?** → Appears monthly to quarterly; requires monitoring

---

## Sources

- [GitHub - haziq-exe/TikTokAutoUploader (Feb 2026)](https://github.com/haziq-exe/TikTokAutoUploader)
- [GitHub - wkaisertexas/tiktok-uploader](https://github.com/wkaisertexas/tiktok-uploader)
- [TikTok Studio Upload Page](https://www.tiktok.com/tiktokstudio/upload)
- [wanghaisheng/tiktoka-studio-uploader Playwright Branch](https://github.com/wanghaisheng/tiktoka-studio-uploader/blob/playwright/how-to-upload-tiktok.md)
- [2026 TikTok Updates - SocialBee](https://socialbee.com/blog/tiktok-updates/)
- [CapCut TikTok Template Guide (2025-2026)](https://www.capcut.com/resource/tiktok-template)
- [Python Library: TikTokAutoUploader - DEV Community](https://dev.to/haziq_exe/python-library-that-auto-solves-tiktoks-captchas-and-lets-you-uploadschedule-videos-with-tiktok-sounds-and-hashtags-5h4f)

---

**Report Status:** Complete — Limited by lack of public selector documentation; live inspection required for production automation.
