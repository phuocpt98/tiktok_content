# TikTok Content Production System: Open-Source Tools Research

**Date:** 2026-04-13
**Researcher:** researcher agent
**Focus:** Open-source GitHub projects for TikTok posting, scraping, analytics, video generation, and content automation

---

## Executive Summary

Found **12 high-value open-source projects** across 6 categories. Primary recommendations:
- **Upload/Posting:** haziq-exe/TikTokAutoUploader (Feb 2026 update), MiniGlome/Tiktok-uploader
- **Scraping/Data:** drawrowfly/tiktok-scraper (4.6k★), davidteather/TikTok-Api (6.1k★)
- **Video Gen:** Zulko/moviepy (Python FFMPEG wrapper, widely adopted)
- **Content Pipeline:** Apache Airflow, Prefect, Windmill (workflow orchestration)

---

## 1. TikTok Posting/Upload Automation

### haziq-exe/TikTokAutoUploader
**Status:** ACTIVE (Updated Feb 2026)
**Python:** ✅ Yes
**URL:** https://github.com/haziq-exe/TikTokAutoUploader
**Stars:** ~2.8k

**What it does:**
- Programmatic TikTok video upload & scheduling (up to 10 days ahead)
- Search & use favorited sounds, custom hashtags
- VPN support, Telegram integration, session-based auth

**Integration potential:**
- Direct drop-in for automated posting pipeline
- Supports bulk uploads with scheduling
- Good for content calendar workflows

**Recent activity:** MAINTAINED - latest commit Feb 2026

---

### MiniGlome/Tiktok-uploader
**Status:** ACTIVE
**Python:** ✅ Yes
**URL:** https://github.com/MiniGlome/Tiktok-uploader
**Stars:** ~2.2k

**What it does:**
- Upload & schedule videos to TikTok via sessionId auth
- Batch upload support
- Simple Python API + CLI

**Integration potential:**
- Lightweight alternative to haziq-exe version
- Good for MVP/POC
- Easy to wrap in content pipeline

---

### wkaisertexas/tiktok-uploader
**Status:** ACTIVE
**Python:** ✅ Yes
**URL:** https://github.com/wkaisertexas/tiktok-uploader
**Stars:** ~1.8k

**What it does:**
- Playwright-based automated uploader
- Single/batch video upload with metadata
- Product ID support

**Integration potential:**
- Browser automation approach (more stable vs requests)
- Good for complex upload scenarios

---

### makiisthenes/TiktokAutoUploader
**Status:** ACTIVE
**Python:** ✅ Yes
**URL:** https://github.com/makiisthenes/TiktokAutoUploader
**Stars:** ~500

**What it does:**
- Claims to be "fastest" TikTok uploader (uses requests, not Selenium)
- Automated video editing integration
- CLI tool

**Integration potential:**
- Lightweight, fast approach
- Less battle-tested than alternatives

---

## 2. TikTok Scraping & Analytics

### drawrowfly/tiktok-scraper
**Status:** ACTIVE
**Python:** ❌ No (TypeScript/Node.js)
**URL:** https://github.com/drawrowfly/tiktok-scraper
**Stars:** 4.6k

**What it does:**
- Scrape trending, hashtags, music feed metadata
- Download video posts with metadata
- Web API-based (no browser needed)
- CLI + library module support

**Integration potential:**
- Best for data collection (trending hashtags, sounds, analytics)
- Can be called via child process from Python
- Comprehensive metadata extraction

---

### davidteather/TikTok-Api
**Status:** ACTIVE
**Python:** ✅ Yes
**URL:** https://github.com/davidteather/TikTok-Api
**Stars:** 6.1k

**What it does:**
- Unofficial API wrapper for TikTok.com
- Fetch trending videos, user info, hashtag data
- Read-only (cannot post/upload)
- Playwright-based browser automation

**Integration potential:**
- Research phase: trending data, hashtag validation
- Analytics: user engagement metrics
- Limitations: No posting capability, TikTok actively blocks

**Note:** Used by 250+ companies; TikTok continuously updates blocking measures

---

### networkdynamics/pytok
**Status:** ACTIVE
**Python:** ✅ Yes
**URL:** https://github.com/networkdynamics/pytok
**Stars:** ~1.2k

**What it does:**
- Playwright-based TikTok web scraper
- Auto captcha solving
- Extracts video, text, metadata

**Integration potential:**
- Lightweight scraper alternative
- Good for bulk content research

---

### dfreelon/pyktok
**Status:** ACTIVE
**Python:** ✅ Yes
**URL:** https://github.com/dfreelon/pyktok
**Stars:** ~0.8k

**What it does:**
- Simple module for video, text, metadata collection
- Pulls from JSON in TikTok pages (no browser needed)
- Minimal dependencies

**Integration potential:**
- Lightweight data extraction
- Good for quick scripts

---

## 3. Social Media Scheduling & Automation

### ayrshare/social-post-api-python
**Status:** ACTIVE
**Python:** ✅ Yes
**URL:** https://github.com/ayrshare/social-post-api-python
**Stars:** ~0.5k

**What it does:**
- Multi-platform scheduler (TikTok, Instagram, Twitter, LinkedIn, Facebook)
- API-based scheduling across platforms
- Batch operations

**Integration potential:**
- Central hub for multi-platform posting
- Good for cross-platform content strategies
- Reduces need for platform-specific tools

---

### Built-in Python Libraries
**schedule** library
- Simple in-process scheduling
- Good for background task timing

**cron** (Linux/macOS)
- OS-level scheduling
- Reliable for server environments

---

## 4. Video Generation & Processing

### Zulko/moviepy
**Status:** ACTIVE
**Python:** ✅ Yes
**URL:** https://github.com/Zulko/moviepy
**Stars:** 13k

**What it does:**
- Python wrapper over FFMPEG + ImageMagick
- Video editing, composition, effects, transitions
- GIF support, audio processing
- Simple API for common operations

**Integration potential:**
- BEST OPTION for automated video creation
- Can generate TikTok-formatted videos (9:16 aspect ratio)
- Create intros/outros, add text overlays, combine clips
- Supports all formats TikTok accepts

**Why better than raw FFmpeg:**
- Numpy array-based pixel manipulation
- Python-native effects API
- Much simpler code for common tasks

---

### Alternative: OpenCV (cv2)
**Status:** ACTIVE
**Python:** ✅ Yes
**URL:** https://github.com/opencv/opencv
**Stars:** 38k

**What it does:**
- Computer vision + video processing
- Frame-by-frame manipulation
- More low-level than moviepy

**Integration potential:**
- For advanced video analysis
- Overkill for basic video generation
- Better for content modification tasks

---

## 5. Image Generation & Graphics

### Stable Diffusion (via diffusers library)
**Status:** ACTIVE
**Python:** ✅ Yes
**URL:** https://github.com/huggingface/diffusers
**Stars:** 26k

**What it does:**
- AI image generation from text prompts
- Generate unique social media graphics
- Customizable models

**Integration potential:**
- Auto-generate thumbnail graphics
- Create cover images for videos
- But: Requires GPU, slow inference

---

### Pillow (PIL)
**Status:** ACTIVE
**Python:** ✅ Yes
**URL:** https://github.com/python-pillow/Pillow
**Stars:** 12k

**What it does:**
- Image manipulation (text overlay, resizing, filters)
- Simple graphics creation
- Lightweight

**Integration potential:**
- ESSENTIAL for TikTok graphics pipeline
- Add captions to generated thumbnails
- Combine with moviepy for video overlays
- Create cover images

---

### Matplotlib
**Status:** ACTIVE
**Python:** ✅ Yes
**URL:** https://github.com/matplotlib/matplotlib
**Stars:** 20k

**What it does:**
- Create charts, graphs, visualizations
- Good for data-driven content

**Integration potential:**
- Generate visual data content (trending charts, stats)
- Save as images for TikTok slides

---

## 6. Content Pipeline & Workflow Orchestration

### Apache Airflow
**Status:** ACTIVE
**Python:** ✅ Yes
**URL:** https://github.com/apache/airflow
**Stars:** 38k

**What it does:**
- DAG-based workflow orchestration
- Schedule, monitor, retry complex pipelines
- Web UI dashboard
- Supports TikTok custom operators

**Integration potential:**
- BEST OPTION for enterprise content pipelines
- DAG: Scrape trending → Generate content → Edit video → Upload
- Built-in retry/error handling
- Scales to thousands of daily posts

**Example DAG tasks:**
1. Fetch trending hashtags (TikTok-Api)
2. Generate video (moviepy)
3. Add graphics (Pillow)
4. Schedule upload (TikTokAutoUploader)

---

### Prefect
**Status:** ACTIVE
**Python:** ✅ Yes
**URL:** https://github.com/PrefectHQ/prefect
**Stars:** 16k

**What it does:**
- Modern alternative to Airflow
- Task-based flows in Python code
- Better error recovery
- Cloud-native

**Integration potential:**
- Lighter weight than Airflow for smaller pipelines
- Good for serverless content generation
- Simpler learning curve

---

### Windmill
**Status:** ACTIVE
**Python:** ✅ Yes
**URL:** https://www.windmill.dev/
**Stars:** 8k

**What it does:**
- Visual DAG editor + Python scripting
- Auto-generated UI for workflows
- Multi-language support
- Self-hosted

**Integration potential:**
- No-code/low-code option for non-technical team members
- Good for content manager interfaces
- Auto-exposes workflow parameters as UI

---

### n8n
**Status:** ACTIVE
**Python:** ✅ Yes (via code nodes)
**URL:** https://github.com/n8n-io/n8n
**Stars:** 50k

**What it does:**
- Visual workflow builder
- 1000+ integrations (including social media)
- Self-hosted or cloud
- Code nodes for custom logic

**Integration potential:**
- EASY INTEGRATION PATH for non-developers
- Drag-drop content pipeline builder
- Built-in TikTok node support (if available)
- Good for MVP

---

## Architecture Recommendations

### Minimal MVP (< 1000 posts/month)
```
1. haziq-exe/TikTokAutoUploader        → Upload videos
2. moviepy + Pillow                    → Generate/edit content
3. drawrowfly/tiktok-scraper           → Research trending (async)
4. APScheduler or cron                 → Simple scheduling
```

### Growth Phase (1k-10k posts/month)
```
1. Apache Airflow DAG Pipeline:
   - Task 1: Scrape trending (davidteather/TikTok-Api)
   - Task 2: Generate content (moviepy)
   - Task 3: Create graphics (Pillow)
   - Task 4: Schedule upload (haziq-exe/TikTokAutoUploader)

2. Monitoring: Airflow UI + custom alerts
3. Database: Store content metadata, performance metrics
```

### Enterprise (10k+ posts/month)
```
1. Apache Airflow (multi-instance, autoscaling)
2. S3/Cloud storage for media
3. RabbitMQ for task queue
4. Elasticsearch for analytics
5. Multi-uploader strategy (risk distribution)
```

---

## Technology Stack Summary

| Category | Recommended | Stars | Maturity | Python | Notes |
|----------|------------|-------|----------|--------|-------|
| **Upload** | haziq-exe/TikTokAutoUploader | 2.8k | ✅ Active (Feb 2026) | ✅ | Most recent; full features |
| **Scraping** | drawrowfly/tiktok-scraper | 4.6k | ✅ Active | ❌ TS | Best for trending data |
| **API Wrapper** | davidteather/TikTok-Api | 6.1k | ✅ Active | ✅ | Read-only; 250+ users |
| **Video Gen** | Zulko/moviepy | 13k | ✅ Active | ✅ | Essential for automation |
| **Graphics** | Pillow | 12k | ✅ Active | ✅ | Text overlays, basic design |
| **Orchestration** | Apache Airflow | 38k | ✅ Active | ✅ | Best for scaling |
| **Workflow Builder** | n8n | 50k | ✅ Active | ✅ | Best for MVP speed |

---

## Unresolved Questions / Risks

1. **TikTok Terms of Service:** All uploaders use unofficial APIs. TikTok actively blocks them. Recommend:
   - Monitor GitHub repos for API breakages
   - Maintain backup uploaders
   - Check TikTok's official API (limited, requires approval)

2. **Authentication Stability:** sessionId-based auth may break with TikTok updates. No official API for uploads.

3. **Rate Limits:** No clear docs on TikTok's rate limiting for programmatic uploads. Test in prod carefully.

4. **Account Risk:** Bulk automated uploads may trigger TikTok spam detection. Recommend:
   - Gradual ramp-up (not 100s/day immediately)
   - Space out uploads over time
   - Use multiple accounts if critical

5. **Scraping Legality:** Scraping TikTok may violate ToS in some jurisdictions. Verify compliance before deploying.

---

## Next Steps

1. **Week 1:** Evaluate haziq-exe/TikTokAutoUploader on staging account
2. **Week 1:** Set up moviepy + Pillow for video generation POC
3. **Week 2:** Test drawrowfly/tiktok-scraper for trending data
4. **Week 3:** Design Apache Airflow DAG for full pipeline
5. **Week 4:** Load test with 100-500 posts

---

**Sources:**
- [haziq-exe/TikTokAutoUploader](https://github.com/haziq-exe/TikTokAutoUploader)
- [MiniGlome/Tiktok-uploader](https://github.com/MiniGlome/Tiktok-uploader)
- [wkaisertexas/tiktok-uploader](https://github.com/wkaisertexas/tiktok-uploader)
- [drawrowfly/tiktok-scraper](https://github.com/drawrowfly/tiktok-scraper)
- [davidteather/TikTok-Api](https://github.com/davidteather/TikTok-Api)
- [networkdynamics/pytok](https://github.com/networkdynamics/pytok)
- [dfreelon/pyktok](https://github.com/dfreelon/pyktok)
- [ayrshare/social-post-api-python](https://github.com/ayrshare/social-post-api-python)
- [Zulko/moviepy](https://github.com/Zulko/moviepy)
- [opencv/opencv](https://github.com/opencv/opencv)
- [huggingface/diffusers](https://github.com/huggingface/diffusers)
- [python-pillow/Pillow](https://github.com/python-pillow/Pillow)
- [matplotlib/matplotlib](https://github.com/matplotlib/matplotlib)
- [apache/airflow](https://github.com/apache/airflow)
- [PrefectHQ/prefect](https://github.com/PrefectHQ/prefect)
- [Windmill](https://www.windmill.dev/)
- [n8n-io/n8n](https://github.com/n8n-io/n8n)
