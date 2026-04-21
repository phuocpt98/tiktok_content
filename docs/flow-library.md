# Flow Library — Tạp Hóa Pel Pel

> **MỤC ĐÍCH:** Khi user nói gì, Claude check file này trước để tìm flow có sẵn.
> Mỗi flow có link đến tài liệu chi tiết.

---

## Mục lục Flow

| # | Khi user nói... | Flow | Chi tiết |
|---|---|---|---|
| 1 | "tạo content", "làm video", "gen video mới" | [Tạo Content Mới](#1-tạo-content-mới) | Full pipeline từ ý tưởng → output |
| 2 | "thêm sản phẩm", "sản phẩm mới" | [Thêm Sản Phẩm](#2-thêm-sản-phẩm) | Setup thư mục + asset library |
| 3 | "gen ảnh", "tạo ảnh", "prompt ảnh" | [Gen Ảnh AI](#3-gen-ảnh-ai) | Chọn tool + viết prompt |
| 4 | "gen video AI", "kling", "veo" | [Gen Video AI](#4-gen-video-ai) | Chọn tool + viết prompt video |
| 5 | "voiceover", "giọng đọc", "voice" | [Tạo Voiceover](#5-tạo-voiceover) | Edge TTS settings |
| 6 | "ghép video", "assemble", "render" | [Ghép Video FFmpeg](#6-ghép-video-ffmpeg) | Slides/clips → video final |
| 7 | "trend", "xu hướng" | [Quét Trend](#7-quét-trend) | Research TikTok trends |
| 8 | "đăng", "upload", "post" | [Đăng TikTok](#8-đăng-tiktok) | Upload + caption + hashtag |
| 9 | "báo cáo", "report", "stats" | [Báo Cáo Kênh](#9-báo-cáo-kênh) | KPIs, analytics |
| 10 | "plan tuần", "lịch đăng" | [Content Calendar](#10-content-calendar) | Lên lịch đăng bài |

---

## 1. Tạo Content Mới

**Trigger:** user muốn tạo video/slideshow từ ý tưởng

**Bước:**
1. Đọc `assets/products/{slug}/asset-library.md` → biết có gì sẵn
2. Đọc `assets/content-ideas/viral-share-scripts.md` → xem ý tưởng có sẵn
3. Lên kịch bản → map asset cụ thể vào từng cảnh
4. Note asset thiếu → gen thêm (flow #3, #4) hoặc báo user chụp
5. Tạo voiceover nếu cần (flow #5)
6. Ghép video (flow #6)
7. Output → `assets/products/{product-slug}/output/{slides,audio,final}/` (prefix tên file theo version/concept, không tạo subfolder version)

**Lưu ý:**
- **BẮT BUỘC đọc `docs/video-production-format.md`** — section "Ảnh Bìa" + "Day 3 Real Data" + "Ngưỡng flop"
- Đọc memory `feedback_video_production_lessons.md` trước
- **Thumbnail SÁNG là điều kiện SỐNG CÒN** (data Day 3: tối = 0-2 view, sáng = 283-382 view)
- Check frame 0-1s + ảnh bìa TRƯỚC khi render — tối thì gen lại ảnh sáng
- Hook nhanh 1-2s, chuyển cảnh liên tục
- Nội dung giữa frame (tránh top 15% + bottom 20%)
- Không sến, không kịch bản dài dòng

**Tài liệu liên quan:**
- `docs/ai-tools-reference.md` — tool nào dùng cho bước nào
- `assets/products/{slug}/asset-library.md` — kho tài nguyên
- `assets/content-ideas/viral-share-scripts.md` — kho ý tưởng

---

## 2. Thêm Sản Phẩm

**Trigger:** user muốn thêm sản phẩm mới vào kho

**Bước:**
1. Chạy `scripts/add-product.sh {slug}` → tạo thư mục
2. Điền `assets/products/{slug}/info/product.md` — thông tin sản phẩm
3. User chụp ảnh → copy vào `assets/products/{slug}/photos/`
4. Tạo `assets/products/{slug}/asset-library.md` — mô tả từng ảnh/video
5. Thêm content ideas vào `product.md`

**Template thư mục:**
```
assets/products/{slug}/
├── info/product.md
├── photos/
├── videos/
└── asset-library.md
```

---

## 3. Gen Ảnh AI

**Trigger:** cần ảnh mà chưa có trong kho

**Bước:**
1. Check `asset-library.md` → chắc chắn chưa có ảnh phù hợp
2. Chọn tool theo `docs/ai-tools-reference.md` (ưu tiên free)
3. Viết prompt — **BẮT BUỘC thêm:** "no text, no logo, no title, no watermark, no lettering"
4. Gen → save vào `assets/products/{slug}/photos/`
5. Update `asset-library.md` với mô tả ảnh mới

**Tool ưu tiên:** Gemini API > Gemini Web > Meta AI web

---

## 4. Gen Video AI

**Trigger:** cần clip ngắn (5-10s) cho B-roll

**Bước:**
1. Check `asset-library.md` → chắc chắn chưa có clip phù hợp
2. Chọn tool: Kling (2-3 clip/ngày free) > Veo (đắt)
3. Viết prompt — **BẮT BUỘC thêm:** "no text, no logo, no title, no watermark"
4. Upload ảnh reference nếu cần (xem mapping trong session memory)
5. Save → `assets/products/{slug}/videos/`
6. Update `asset-library.md` — ghi rõ watermark, resolution, hạn chế

**Lưu ý:** Video AI chỉ dùng B-roll, KHÔNG dùng làm cảnh chính

---

## 5. Tạo Voiceover

**Trigger:** video cần giọng đọc

**Bước:**
1. Viết script ngắn gọn, punch, không dài dòng
2. Edge TTS: `vi-VN-HoaiMyNeural`, rate +50%
3. Chạy `src/tts-engine.py` hoặc inline script
4. Save → `assets/products/{product-slug}/output/audio/{prefix-}voiceover.mp3`

**Settings đã confirm:**
- Voice: vi-VN-HoaiMyNeural (nữ miền Nam)
- Rate: +50% (nhanh, punch)
- Style: ngắn gọn, không kể dài dòng

---

## 6. Ghép Video FFmpeg

**Trigger:** có đủ slides/clips + audio, cần render final

**Bước:**
1. Chuẩn bị: slides (1080x1920) + audio + clips
2. Script: `scripts/gen-snack-video-v*.py` hoặc `src/video-assembler.py`
3. FFmpeg: zoom/pan/crossfade cho ảnh tĩnh
4. **Font tiếng Việt:** luôn dùng `fontfile='C:/Windows/Fonts/arialbd.ttf'`
5. Output → `assets/products/{product-slug}/output/final/{YYMMDD}-{slug}-{version}.mp4`

**Timing:**
- Slide đầu: 1-2s (hook nhanh)
- Các slide sau: 2-3s
- Tổng: 15-20s

---

## 7. Quét Trend

**Trigger:** user muốn biết trend hiện tại

**Bước:**
1. Research TikTok Vietnam trends (researcher agent)
2. Focus: food/snack niche, Gen Z Vietnam
3. Lưu report → `plans/reports/researcher-*-tiktok-trends.md`
4. Extract ý tưởng → `assets/content-ideas/`

---

## 8. Đăng TikTok

**Trigger:** video xong, cần đăng

**Bước:**
1. Chuẩn bị video final (1080x1920, <60s)
2. Caption: ngắn, có hook
3. Hashtag: đúng 5 tag (1 brand + 2 niche + 2 viral)
4. Upload: thủ công qua app hoặc `src/tiktok-uploader.py`
5. Update `memory/project_pelpel_channel.md` — thêm vào Content History

**Hashtag mẫu:** #taphoapelpel #reviewsnack #ancungtiktok #fyp #xuhuong

---

## 9. Báo Cáo Kênh

**Trigger:** user muốn xem stats

**Bước:**
1. Đọc `memory/project_pelpel_channel.md` → current KPIs
2. Chạy `src/dashboard.py` nếu có data trong DB
3. Báo cáo: followers, views, likes, top videos
4. Gợi ý cải thiện

---

## 10. Content Calendar

**Trigger:** user muốn lên lịch đăng tuần

**Bước:**
1. Đọc channel stage → xác định tần suất (Stage 1: 1-2 video/ngày)
2. Đọc `asset-library.md` → biết có gì sẵn để làm
3. Đọc `content-ideas/` → chọn ý tưởng
4. Lên lịch: ngày, giờ đăng, concept, format
5. Lưu → `plans/content-calendar-{week}.md`

**Giờ đăng tốt (VN):** 11h-13h, 18h-21h, 22h-00h
