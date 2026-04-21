# Ingest Video Guide — Runbook cho Agent

> Hướng dẫn tải video từ các nền tảng social về để làm scene library.
> Cập nhật: 2026-04-23. Script: `scripts/ingest-tiktok.py`.
> Plan gốc: `plans/260422-1805-cross-platform-clip-remix-pipeline/plan.md`.

---

## TL;DR — Lệnh thường dùng

### Tải video về (để remix / làm scene library)

```bash
# Tải 3 video mới nhất của 1 TikTok user
python3 scripts/ingest-tiktok.py "https://www.tiktok.com/@beheobu0102" --limit 3

# Tải 1 video cụ thể
python3 scripts/ingest-tiktok.py "https://www.tiktok.com/@user/video/7xxxxxxxx"

# Tải TOÀN BỘ video của kênh (có thể hàng trăm/nghìn — cẩn thận rate-limit)
python3 scripts/ingest-tiktok.py "https://www.tiktok.com/@user" --all --sleep 3

# Tuỳ chỉnh output dir
python3 scripts/ingest-tiktok.py <URL> --out assets/raw/tiktok/custom-folder
```

### Phân tích kênh đối thủ (chỉ metadata, không tải video)

```bash
# Nhanh: 50 video gần nhất
python3 scripts/analyze-channel.py "https://www.tiktok.com/@beheobu0102" --limit 50

# Toàn bộ kênh
python3 scripts/analyze-channel.py "https://www.tiktok.com/@user" --all

# Chi tiết hơn (gộp tikwm cho music + TikTokShop flag — chậm ~1.5s/video)
python3 scripts/analyze-channel.py <URL> --limit 100 --with-tikwm
```

Output:
```
assets/analysis/tiktok/{author}/
├── videos.csv       # 1 dòng/video — mở Excel/Sheets sort/filter
└── summary.md       # Tổng hợp: top videos, hashtag, music, posting time
```

Output:
```
assets/raw/tiktok/{author}/
├── {video_id}.mp4          # HD, không watermark (HEVC 720p/1080p)
├── {video_id}.info.json    # metadata đầy đủ từ tikwm
├── {video_id}.jpg          # cover thumbnail
└── _manifest.jsonl         # 1 dòng/video (audit log)
```

---

## Chiến lược kỹ thuật

### Lý do không dùng yt-dlp trực tiếp cho TikTok

yt-dlp web extractor của TikTok **thường chỉ trả audio-only** cho rất nhiều account, đặc biệt:
- Video có **TikTokShop / shoppable link** (gắn sản phẩm)
- Account nhỏ / mới
- Một số region lock

TikTok anti-bot chặn web scraping, chỉ cho mobile app xem full format.

### Stack đang dùng

```
Profile URL
    │
    ▼
yt-dlp --flat-playlist      ← chỉ lấy list URL, KHÔNG tải video
    │
    ▼  list of video URLs
    │
    ▼
tikwm.com API (per video)   ← mobile-like endpoint, bypass web limit
    │
    ▼
MP4 (hdplay) + cover + metadata JSON
    │
    ▼
assets/raw/tiktok/{author}/
```

`tikwm.com` là service cộng đồng miễn phí, reliability khá tốt (dùng nội bộ TikTok mobile API). Nếu down → xem §Troubleshooting.

---

## Setup một lần (đã làm 2026-04-23)

### 1. Dependencies

```bash
# yt-dlp + ffmpeg
brew install yt-dlp ffmpeg

# curl_cffi để yt-dlp bypass TikTok anti-bot
# Phải là 0.10.x - 0.14.x (brew yt-dlp 2026.3.17 yêu cầu)
/opt/homebrew/Cellar/yt-dlp/<version>/libexec/bin/python \
    -m pip install "curl_cffi>=0.10,<0.15"
```

Verify:
```bash
yt-dlp --list-impersonate-targets
# Phải thấy Chrome/Safari/Firefox — NOT "(unavailable)"
```

### 2. Python deps

```bash
pip3 install -r requirements.txt
```

`requirements.txt` có sẵn `yt-dlp>=2025.1.0`. Script chỉ dùng stdlib cho tikwm.

---

## Troubleshooting

### ⚠️ DNS chặn tiktok.com → 127.0.0.1

**Triệu chứng:** `dig +short tiktok.com` trả `127.0.0.1`. Curl/yt-dlp fail toàn bộ.

**Nguyên nhân:** Tailscale MagicDNS hoặc corporate VPN chặn social media.

**Fix:**
- Tắt Tailscale tạm thời: System Settings → VPN
- Hoặc đổi DNS: `sudo networksetup -setdnsservers Wi-Fi 1.1.1.1 8.8.8.8` (reset bằng `Empty`)

Confirm đã fix: `dig +short tiktok.com` phải trả IP thật (e.g. `23.202.89.xx`).

### ⚠️ yt-dlp trả `audio only` format

**Triệu chứng:** `yt-dlp --list-formats <URL>` chỉ show `audio m4a`.

**Nguyên nhân:**
1. `curl_cffi` version sai → impersonate targets "(unavailable)"
2. Video là TikTokShop → web API bị limit
3. Dù impersonate OK, web vẫn chỉ trả audio cho nhiều account

**Fix:** Dùng script `ingest-tiktok.py` (đã route qua tikwm.com). **Không nên** chạy `yt-dlp <tiktok_url>` trực tiếp để tải video.

### ⚠️ Chrome Keychain prompt khi test

Nếu thử `yt-dlp --cookies-from-browser chrome`, macOS sẽ hỏi quyền đọc Keychain.
→ **Từ chối**. Script production không dùng flag này.

### ⚠️ tikwm.com rate-limit (code 429 / "limit")

**Triệu chứng:** Lỗi từ tikwm sau nhiều request.

**Fix:**
- Tăng `--sleep` (default 1.5s) lên 3-5s
- Retry sau vài phút
- Script đã có retry + backoff tự động

### ⚠️ tikwm.com down

**Triệu chứng:** HTTP 5xx từ `tikwm.com/api/`.

**Fallback plan** (chưa code):
1. `snaptik.app` — có API riêng
2. `ssstik.io` — scrape form submission
3. yt-dlp + `--extractor-args "tiktok:app_name=trill"` (hên xui)

### ⚠️ Video `/photo/` URLs (slideshow)

Tikwm trả `play=None` cho photo posts. Script log `"không có play URL (có thể là photo post)"` và skip.

Nếu cần hỗ trợ photo slideshow → đọc `images[]` array trong response `tikwm` → xử lý riêng (chưa code).

---

## Lấy toàn bộ video 1 kênh — cơ chế

TikTok profile URL (`@username`) qua yt-dlp thường chỉ trả ~3 video đầu.
Để paginate toàn bộ, cần **SEC_UID** — ID nội bộ 88-char dạng `MS4wLj...`.

Cách script tự xử lý (khi `--all`):
1. `yt-dlp --flat-playlist --playlist-end 1 --print "%(channel_id)s" <profile_url>`
   → lấy SEC_UID từ video đầu tiên
2. `yt-dlp --flat-playlist "tiktokuser:<SEC_UID>"` → paginate toàn bộ video
3. Với mỗi URL → tikwm.com tải MP4 + metadata

Thực tế test: @beheobu0102 có **732 video** được liệt kê. Chỉ 1 lệnh.

Tikwm có endpoint `/api/user/posts` nhưng bị Cloudflare Turnstile → không dùng được trực tiếp. Luồng "yt-dlp list + tikwm per-video" ổn định hơn.

---

## Metadata phân tích đối thủ — các trường

### Từ yt-dlp `--flat-playlist --dump-json` (nhẹ, không tải video):

| Trường | Ý nghĩa phân tích |
|---|---|
| `id`, `url` | Định danh |
| `title` / `description` | Caption + hashtag |
| `duration` | Độ dài tối ưu (phân bổ) |
| `view_count` | Reach |
| `like_count` | Đồng tình |
| `comment_count` | Tương tác sâu |
| `repost_count` | Share/spread |
| `save_count` | Intent "để xem lại" — chỉ số cực quan trọng cho TikTok algorithm |
| `timestamp` (Unix) | Thời điểm đăng → weekday + hour |
| `track` / `artist` | Music/sound dùng |
| `channel_id` | SEC_UID (88-char) để paginate |
| `uploader_id` | User ID numeric |

### Từ tikwm (chi tiết, cần gọi per-video, chậm):

| Trường | Ý nghĩa phân tích |
|---|---|
| `music_info.original` | True = original sound của chính kênh, False = dùng trending |
| `music_info.id` | ID sound — track xem sound nào viral |
| `anchors_extras.is_ec_video` | True = TikTokShop/shoppable — video affiliate |
| `is_ad` | Paid promotion |
| `commerce_info` | Thông tin sản phẩm nếu shop video |
| `region` | VN/US/... |
| `collect_count` | Save count (alias của save_count) |
| `hd_size` | Size file HD — proxy cho quality đầu tư |
| `cover` / `origin_cover` / `ai_dynamic_cover` | 3 loại thumbnail — phân tích visual strategy |

### Chỉ số script tự tính

- **`engagement_rate_pct`** = `(likes + comments + shares + saves) / views × 100`
- **`upload_hour_vn`** = giờ trong ngày theo giờ VN (GMT+7)
- **`weekday_vn`** = thứ trong tuần
- **`hashtags`** = parse từ caption (tách riêng để count)

### Insight mẫu (từ test @beheobu0102, 50 video)

```
Tổng views: 9.8M | Avg 196K | Median 7.3K
→ Chênh lệch cực lớn: vài video viral (1 vid 5.6M), còn lại khiêm tốn

Đăng 00-02h VN (31/50 video)
→ Đối tượng "thèm ăn đêm", không phải giờ vàng 11h/19h thông thường

Saturday: 13/50 videos (26%)
→ Weekend là prime time của kênh này

Top 3 sound dùng đi dùng lại 12, 10, 9 lần
→ "Sound repurpose" — tìm được hit sound, dùng nhiều

Top hashtag: #anvat × 40/50
→ Brand hashtag cố định — có chiến lược
```

---

## Cấu trúc output

### `_manifest.jsonl`
Mỗi dòng là 1 JSON entry (append-only log):

```json
{
  "id": "7630875937734855944",
  "platform": "tiktok",
  "url": "https://www.tiktok.com/@beheobu0102/video/7630875937734855944",
  "author": "Bé heo bự🐷",
  "author_id": "beheobu0102",
  "caption": "Mì cay sasin chân ái của tui#micaysasin ...",
  "duration_sec": 32,
  "views": 1031, "likes": 10, "comments": 3, "shares": 9,
  "music_title": "Hachimi Michi ...",
  "music_author": "elionzonaz",
  "is_original_sound": false,
  "region": "VN",
  "file_path": "assets/raw/tiktok/beheobu0102/7630875937734855944.mp4",
  "thumb_path": "assets/raw/tiktok/beheobu0102/7630875937734855944.jpg",
  "ingested_at": "2026-04-23T12:19:xx"
}
```

### `{video_id}.info.json`
Raw payload từ tikwm — nhiều field hơn manifest. Dùng khi cần debug hoặc
field chưa có trong manifest schema.

### Dedup
Script tự skip video đã có trong `_manifest.jsonl`. Chạy lại lệnh cùng URL
→ bỏ qua video đã tải, chỉ bổ sung video mới.

---

## Hướng dẫn cho Agent tương lai

### Khi user yêu cầu "tải video TikTok / quét kênh / ingest content"

1. **Đọc plan** `plans/260422-1805-cross-platform-clip-remix-pipeline/plan.md` để hiểu mục tiêu lớn.
2. **Chạy script có sẵn**, KHÔNG viết lại pipeline:
   ```bash
   python3 scripts/ingest-tiktok.py <URL> --limit <N>
   ```
3. Kiểm tra trước DNS không bị chặn (§Troubleshooting).
4. Nếu user muốn tải nhiều user cùng lúc → loop bash:
   ```bash
   for user in beheobu0102 yen_doanvathot khac_nua; do
       python3 scripts/ingest-tiktok.py "https://www.tiktok.com/@$user" --limit 5
   done
   ```
5. Tôn trọng rate-limit. Không giảm `--sleep` xuống dưới 1.5s.

### Khi user yêu cầu "thêm platform mới (YouTube Shorts, IG Reels, FB Reels)"

Pattern kiến trúc tương tự:
- YT Shorts: yt-dlp hoạt động tốt, không cần third-party
- IG Reels: cần `--cookies-from-browser` hoặc `instaloader`
- FB Reels: yt-dlp tạm OK, hoặc `facebook-video-downloader`

Tạo file `scripts/ingest-{platform}.py` riêng, **KHÔNG** nhồi tất cả vào 1 script — mỗi platform có quirk khác nhau.

Output schema giữ nhất quán:
```
assets/raw/{platform}/{author}/{video_id}.mp4
                              .info.json
                              .jpg
                              _manifest.jsonl
```

### Khi user yêu cầu "phân tích trend từ video đã tải"

Sau khi có MP4 → chạy pipeline tiếp:
1. `scripts/split-video-by-scenes.py` cắt scene (đã có)
2. Gemini Vision auto-tag từng scene (chưa code — Phase B của plan)
3. Lưu vào SQLite (chưa code)

### Khi user muốn scale (hàng trăm video / ngày)

- tikwm free tier KHÔNG đủ. Cân nhắc:
  - Tikwm Pro API ($/tháng)
  - Self-host TikTokApi python lib
  - Build Chrome extension (xem §page-agent research trong plan)
- Rotate IP qua residential proxy để tránh ban
- Tách hàng đợi: Redis/SQS + worker

---

## Version Log

| Ngày | Thay đổi |
|---|---|
| 2026-04-23 | Initial. `ingest-tiktok.py`: yt-dlp flat-playlist + tikwm download. |
| 2026-04-23 | Thêm `--all` (SEC_UID pagination) + script `analyze-channel.py` export CSV/summary phân tích đối thủ. |
