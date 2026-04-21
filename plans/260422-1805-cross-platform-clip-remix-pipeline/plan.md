# Cross-Platform Clip Remix Pipeline

**Status:** 🔨 Đang làm — Phase A (TikTok ingest) ✅ xong 2026-04-23
**Tạo:** 2026-04-22
**Liên quan:**
- `plans/260414-0905-food-clip-remix-series/` — remix từ clip tự quay (plan này mở rộng sang clip đi mượn)
- `docs/ingest-video-guide.md` — **runbook** cho agent kế tiếp tải video

---

## 1. Mục Tiêu

Xây pipeline tự động:
1. **Tải video** từ nhiều platform (TikTok, YouTube Shorts, Instagram Reels, Facebook)
2. **Cắt thành scene nhỏ** (2-5s mỗi scene)
3. **Lưu scene library** có tag, search được
4. **Trộn ngẫu nhiên theo công thức** thành video mới
5. **Đè voice mới (tiếng Việt)** + text overlay + nhạc
6. **Output video "mới"** đăng được TikTok

Mục đích: tăng volume content cho kênh Pel Pel giai đoạn 0→1K FL mà không cần quay nhiều.

---

## 2. Cảnh Báo Rủi Ro (đọc trước khi code)

### Detection của TikTok
TikTok có 2 hệ thống phát hiện trùng lặp:

1. **Audio fingerprint** (Shazam-style) — dễ bypass: đổi voice/nhạc hoàn toàn
2. **Video fingerprint** (PDQ perceptual hash) — khó hơn, cần transform mạnh

### Bảng rủi ro

| Mức độ "trộn" | Detect? | Rủi ro |
|---|---|---|
| Re-upload nguyên, chỉ đổi voice | 🔴 ~100% dính | Giảm reach → ban kênh |
| Cắt <3s + voice mới + transform nặng | 🟡 Có thể qua | Ổn nếu khéo |
| Stock footage (Pexels/Mixkit) + voice | 🟢 An toàn | Legal 100% |
| AI-generated (Veo/Runway) + voice | 🟢 An toàn | Tốn budget |

### Legal
- **Video của mình** → thoải mái.
- **Người khác** → fair use nếu: cắt ngắn + value-add (commentary, education, curation) + transform nặng.
- Re-upload nguyên xi = vi phạm copyright + ToS → ban vĩnh viễn.

### Khuyến nghị cho Pel Pel
Tỉ lệ content nên:
- 70% ảnh thật sản phẩm + voice + Photo Mode (an toàn tuyệt đối)
- 20% stock footage + voice (an toàn, chi phí ~0)
- 10% remix clip đi mượn (dùng pipeline này, làm rất cẩn thận)

**KHÔNG làm kênh 100% remix** — Stage 1 cần build trust, không muốn ban.

---

## 3. Kiến Trúc Pipeline

```
┌─────────────────────────────────────────────────┐
│ STAGE 1: INGEST                                 │
│   yt-dlp pull từ TT/YT/IG/FB                    │
│   → assets/raw/{platform}/{id}.mp4              │
│   → metadata.json (caption, view, like, author) │
├─────────────────────────────────────────────────┤
│ STAGE 2: SCENE SPLIT                            │
│   scripts/split-video-by-scenes.py (đã có)      │
│   Dùng PySceneDetect (ContentDetector)          │
│   → assets/scenes/{source_id}_{scene_n}.mp4     │
├─────────────────────────────────────────────────┤
│ STAGE 3: AUTO-TAG                               │
│   Gemini Vision phân tích từng scene            │
│   → topic, mood, dominant_color, has_text,      │
│     has_face, action_type, aesthetic_score      │
│   → SQLite scene_library                        │
├─────────────────────────────────────────────────┤
│ STAGE 4: SCRIPT + TTS                           │
│   Claude viết script viral (hook + body + CTA)  │
│   tts-engine.py → voice.mp3                     │
├─────────────────────────────────────────────────┤
│ STAGE 5: MIX                                    │
│   Pick N scenes phù hợp topic của script        │
│   Áp transform stack (xem §5)                   │
│   Concat theo timing của voice.mp3              │
├─────────────────────────────────────────────────┤
│ STAGE 6: POST-PROCESS                           │
│   Caption burn-in, Pel Pel logo overlay         │
│   BGM (mix-down -20dB dưới voice)               │
│   Export 9:16 1080x1920 H.264                   │
└─────────────────────────────────────────────────┘
```

---

## 4. Tool Stack

### Đã có trong project
- `scripts/split-video-by-scenes.py` — cắt scene
- `src/tts-engine.py` — TTS tiếng Việt
- `src/video-assembler.py` — ghép video
- `src/gemini-client.py` — Gemini API (dùng cho vision tag)
- `src/database.py` — SQLite layer

### Cần thêm
| Tool | Mục đích | Cài |
|---|---|---|
| `yt-dlp` | Tải video đa platform | `pip install yt-dlp` |
| `ffmpeg-python` | Wrapper ffmpeg cho Python | `pip install ffmpeg-python` |
| `scenedetect` | Scene detection (nếu chưa có) | `pip install scenedetect[opencv]` |
| `imagehash` | pHash để dedup scene | `pip install ImageHash` |
| `librosa` | Detect beat / BPM cho sync | `pip install librosa` |

### Hệ thống
- `ffmpeg` (brew install ffmpeg) — bắt buộc
- `ffprobe` — đi kèm ffmpeg

---

## 5. Transform Stack — Anti-Detection

Áp theo thứ tự cho mỗi scene đi mượn:

```python
# Pseudocode
scene = load(clip)
scene = speed(scene, factor=random(0.93, 1.07))      # 1
scene = mirror_horizontal(scene)                      # 2
scene = zoom(scene, factor=random(1.05, 1.12))        # 3
scene = color_grade(scene, lut="warm_pelpel.cube")    # 4
scene = overlay(scene, "pelpel_watermark.png",        # 5
                position="top-right", opacity=0.3)
scene = mute_audio(scene)                             # 6 — voice mới đè 100%
scene = re_encode(scene, codec="libx264",             # 7
                  preset="medium", crf=23)
# Thêm cho scene đầu/cuối:
if first_or_last:
    scene = transition(scene, type="zoom_blur", dur=0.3)
```

**Ghi chú:**
- Không bỏ qua bước 6 (mute). Audio fingerprint là detect dễ nhất.
- CRF 23 là sweet spot — re-encode đủ để đổi bitstream nhưng không xấu quá.
- LUT màu: tạo 1 preset riêng cho Pel Pel (warm, vàng ấm) để video đồng bộ nhận diện brand.

---

## 6. Scene Library Schema (SQLite)

```sql
CREATE TABLE sources (
    id TEXT PRIMARY KEY,              -- {platform}_{video_id}
    platform TEXT,                    -- tiktok, youtube, instagram, facebook
    url TEXT,
    author TEXT,
    caption TEXT,
    views INTEGER,
    likes INTEGER,
    downloaded_at DATETIME,
    file_path TEXT
);

CREATE TABLE scenes (
    id TEXT PRIMARY KEY,              -- {source_id}_scene_{n}
    source_id TEXT REFERENCES sources(id),
    start_sec REAL,
    end_sec REAL,
    duration REAL,
    file_path TEXT,
    phash TEXT,                       -- perceptual hash, dedup
    -- Gemini auto-tag:
    topic TEXT,                       -- e.g. "mì tôm", "bánh kẹo", "đóng gói"
    mood TEXT,                        -- calm, energetic, funny, aesthetic
    dominant_color TEXT,              -- hex
    has_text BOOLEAN,
    has_face BOOLEAN,
    action_type TEXT,                 -- pouring, cutting, eating, unboxing
    aesthetic_score REAL,             -- 0-1, Gemini đánh giá
    usage_count INTEGER DEFAULT 0     -- tránh dùng lại quá nhiều
);

CREATE TABLE outputs (
    id TEXT PRIMARY KEY,
    script_text TEXT,
    voice_path TEXT,
    scene_ids TEXT,                   -- JSON array
    final_path TEXT,
    created_at DATETIME,
    tiktok_url TEXT,                  -- sau khi đăng
    views INTEGER,                    -- update định kỳ
    status TEXT                       -- draft, posted, removed, banned
);
```

Scene library sẽ dày dần theo thời gian → pick scene cho content mới càng về sau càng nhanh.

---

## 7. Script Ingest Mẫu

```python
# scripts/ingest-video.py
import yt_dlp
from pathlib import Path

def ingest(url: str, platform: str):
    out_dir = Path(f"assets/raw/{platform}")
    out_dir.mkdir(parents=True, exist_ok=True)

    opts = {
        "outtmpl": str(out_dir / "%(id)s.%(ext)s"),
        "writeinfojson": True,
        "writethumbnail": True,
        "format": "best[height<=1080]",
        "sleep_interval": 3,
        "max_sleep_interval": 7,
    }
    with yt_dlp.YoutubeDL(opts) as y:
        info = y.extract_info(url, download=True)

    # Insert vào DB
    insert_source(
        id=f"{platform}_{info['id']}",
        platform=platform,
        url=url,
        author=info.get("uploader"),
        caption=info.get("description"),
        views=info.get("view_count"),
        likes=info.get("like_count"),
        file_path=opts["outtmpl"] % info,
    )
```

Platform detect từ URL:
- `tiktok.com` → tiktok
- `youtube.com/shorts` / `youtu.be` → youtube
- `instagram.com/reel` → instagram
- `facebook.com/reel` / `fb.watch` → facebook

---

## 8. Pick Algorithm — Chọn Scene Cho Script

Input: script text + timing segments từ TTS
Output: list scene ids sắp xếp

```
Với mỗi segment (khoảng 2-3s voice):
    1. Gemini extract keyword từ text segment
    2. SQL query scenes WHERE topic MATCH keyword
       AND usage_count < 3
       AND aesthetic_score > 0.6
    3. Rerank bằng embedding similarity (text segment ↔ scene tag)
    4. Pick top-1, fallback random nếu thiếu
    5. Update usage_count++

Ràng buộc:
- Không pick 2 scene liền nhau cùng source (tránh detect)
- Không pick scene >5s (phải cắt thêm nếu voice segment ngắn hơn)
- Phải có ít nhất 1 scene "aesthetic_score > 0.8" trong 3s đầu (hook)
```

---

## 9. Phases Triển Khai

### Phase A — MVP (2-3 buổi)
- [x] Viết `scripts/ingest-tiktok.py` (yt-dlp flat-playlist + tikwm.com) — 2026-04-23
- [x] Test với @beheobu0102 (3 video, video TikTokShop) + @yen_doanvathot (1 video viral) — OK
- [x] Ghi `docs/ingest-video-guide.md` cho agent kế tiếp — 2026-04-23
- [x] Thêm `--all` flag (SEC_UID pagination) — test @beheobu0102 cho 732 video — 2026-04-23
- [x] Viết `scripts/analyze-channel.py` + export CSV/summary phân tích đối thủ — 2026-04-23
- [ ] Tạo SQLite schema, migrate script
- [ ] Hook scene split + insert scenes vào DB (chưa tag)
- [ ] Mix thủ công: chọn scene ID list → ghép theo voice
- [ ] Output 1 video test end-to-end

### Phase B — Auto-tag (1-2 buổi)
- [ ] Gemini Vision tag scene (topic, mood, aesthetic)
- [ ] Dedup bằng pHash
- [ ] UI CLI để browse/filter scene library

### Phase C — Pick algorithm (2 buổi)
- [ ] Keyword extract từ script
- [ ] Query + rerank scene
- [ ] Tự động gen video từ script → output

### Phase D — Transform stack (1-2 buổi)
- [ ] Speed / mirror / zoom / color grade
- [ ] LUT Pel Pel warm
- [ ] Watermark auto
- [ ] So sánh pHash trước/sau → đảm bảo transform đủ mạnh

### Phase E — Scheduler + tracking (optional)
- [ ] Auto ingest daily từ list kênh tham khảo
- [ ] Track video đăng → view → flag content hot → tạo thêm biến thể

---

## 10. Câu Hỏi Mở (để nghiên cứu tiếp)

1. **PySceneDetect** có đủ tốt không hay cần thêm AI scene boundary detection?
2. Ngưỡng `CRF`, `speed`, `zoom` bao nhiêu là "đủ để bypass fingerprint"? → cần test thực tế, đăng 5-10 video thử.
3. Có tool open-source nào để **tự tính** pHash similarity với video TikTok đã public → dự đoán rủi ro trước khi đăng?
4. Gemini Vision có tag nhất quán không? Hay nên dùng CLIP embedding local cho rẻ?
5. Tỉ lệ scene/giây lý tưởng cho TikTok food content (hook-keep-retain)? → xem 260414-0905 plan đã có data.
6. TikTok có policy mới nào về "AI-generated" hoặc "repurposed content" không? → check định kỳ.
7. Khi nào nên chuyển từ "70% photo / 20% stock / 10% remix" sang "50/30/20"? → phụ thuộc FL count.

---

## 11. Alternative Path — Nếu Sau Nghiên Cứu Thấy Quá Rủi Ro

**Plan B: Stock-only pipeline**
- Thay yt-dlp bằng Pexels API / Pixabay API / Mixkit scraper
- Stock footage có license CC0 / commercial-use-OK
- Skip toàn bộ phần transform stack (không cần)
- Chỉ giữ: script → TTS → pick stock → mix → post

→ An toàn tuyệt đối, chi phí ~0, nhưng stock footage food/tạp hóa VN ít.

**Plan C: AI-gen pipeline**
- Gemini Veo / Runway Gen-3 / Kling → gen video 5-8s từ prompt
- Prompt theo script scene
- 100% legal, không ai đòi copyright
- Chi phí: ~$0.5-2 / video 30s → chấp nhận được nếu kênh có revenue

---

## 12. Liên Kết

- CLAUDE.md → Stage 1 chiến lược: chỉ viral content, chưa bán
- `plans/260414-0905-food-clip-remix-series/` → remix từ clip tự quay
- `plans/260417-1057-pel-pel-channel-strategy/` → chiến lược kênh tổng
- `docs/video-production-format.md` → format kỹ thuật video
- `docs/ai-tools-reference.md` → tool AI đang dùng
- `src/video-assembler.py` → module ghép video sẵn có
- `scripts/split-video-by-scenes.py` → scene split sẵn có

---

## 13. Notes Cho Lần Nghiên Cứu Tiếp

- Thử nghiệm nhỏ trước: ingest 10 video, cắt scene, mix 1 video output, đăng test với account phụ.
- Đo thực tế: view count, completion rate, có bị reduce reach không.
- So sánh với Photo Mode cùng chủ đề → format nào ROI cao hơn cho Pel Pel Stage 1.
- Nếu Photo Mode đủ viral rồi, **có thể skip luôn plan này**, dành effort khác.
