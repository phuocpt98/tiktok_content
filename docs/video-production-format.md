# Video Production Format — Tạp Hóa Pel Pel

> **Reference implementation**: `scripts/build-quecay-concept-v4.py` (Day 1 Phonk Macro concept).
> Video mẫu "đúng format": `assets/products/que-cay/output/final/Que cay brand nào đỉnh nhất team #anvat #quecay ...mp4` (build 2026-04-23).
> Các script build mới PHẢI giữ layout overlay như script này.

---

## 🎬 Canvas & Encoding (bắt buộc)

| | Spec |
|---|---|
| Resolution | **1080×1920** (9:16 TikTok) |
| FPS | **30** |
| Video codec | **H.264** (libx264, preset fast, CRF 21) |
| Audio codec | **AAC** 192kbps |
| Pixel format | `yuv420p` |
| Flags | `-movflags +faststart` (streaming-friendly) |
| Duration | **10-18s** (sweet spot, không quá 20s cho TikTok short) |

---

## 🏷️ Label tên sản phẩm + PEL PEL (persistent, mọi frame)

```
Format text: "<TÊN SẢN PHẨM UPPERCASE> • PEL PEL"
Ví dụ: "QUE CAY - PEL PEL", "BÒ CAY - PEL PEL", "MỰC - PEL PEL"
```

### Pillow render spec

| | Value |
|---|---|
| Canvas PNG | **900×140 px** |
| Background | Pill bo tròn, radius = height/2 |
| Color | `rgba(255, 107, 0, 220)` — cam Pel Pel, alpha ~86% |
| Font | Arial Unicode MS (macOS) hoặc HelveticaNeue |
| Font size | **58 pt** |
| Font color | Trắng `#FFFFFF` |
| Stroke | 3px đen `#000000` (readability trên mọi background) |
| Text position | Center cả chiều ngang + dọc |

### Overlay ffmpeg

```python
overlay_x = "(main_w-overlay_w)/2"  # center ngang
overlay_y = 280                     # ← y=280, KHÔNG đổi
```

→ y=280 là **vị trí chuẩn** (đã tested user confirm). KHÔNG đặt y=80 (quá sát top) hoặc y=880 (giữa video — sai hôm nay 24/4 Day 9).

---

## 🏷 Series badge (CHỈ cho serial — chương 1, 2, 3...)

Khi video thuộc serial nhiều chương, thêm badge nhỏ ở **góc trái-dưới** để
viewer biết là chương mấy.

| | Value |
|---|---|
| Format text | `#1`, `#2`, `#3`, `#4`, `#5` (ngắn gọn — chỉ số chương) |
| Canvas PNG | **140×80 px** |
| Background | Pill bo tròn radius 30, `rgba(0, 0, 0, 200)` đen mờ |
| Font | Arial Unicode 56pt, trắng, stroke đen 2px |
| Overlay position | **x=20, y=1740** (góc trái-dưới, không đè watermark phải) |
| Persistent | Mọi frame của chương đó |

KHÔNG dùng cho video standalone (không phải serial).

---

## 💬 Subtitle theo segment (đồng bộ với voice)

Mỗi segment voice có 1 subtitle PNG riêng, overlay **chỉ trong duration của segment đó** (qua trim clip theo voice_dur).

### Pillow render spec

| | Value |
|---|---|
| Canvas PNG | **1000×200 px** |
| Background box | Bo tròn radius 25, `rgba(0, 0, 0, 180)` — đen mờ |
| Padding | 20px box vs edge |
| Font | Arial Unicode MS 62 pt |
| Font color | Trắng `#FFFFFF`, stroke 2px đen |
| Text color phụ (optional) | Vàng `#FFDC00` cho highlight |
| Word wrap | Auto theo max_width = 940px (50px padding 2 bên) |
| Line height | 74px |

### Overlay ffmpeg

```python
overlay_x = "(main_w-overlay_w)/2"  # center ngang
overlay_y = 1580                    # ← y=1580 (bottom area)
```

→ y=1580 là **chuẩn bottom** (1920 - 200 px height - 140 margin).

### ⚠️ Rule SUBTITLE

- Subtitle **KHÔNG dùng emoji** (Pillow font Mac không render emoji → hiện ô vuông `□`). Nếu cần cảm xúc: dùng ALL CAPS hoặc chữ ký tự UTF `「」` `♡`.
- Subtitle text NGẮN, match câu thoại ≤ 40 chars mỗi segment. Nếu dài → 2 dòng max.
- Subtitle KHỚP timing voice: render mỗi segment 1 PNG riêng, overlay trong `trim(voice_dur)` của segment.

---

## 🗣️ Voice (TTS) — Priority chain

Voice-first pipeline: gen TTS TRƯỚC, đo duration THẬT, TRIM VIDEO theo voice (không ngược).

| Priority | Engine | Voice | Ghi chú |
|---|---|---|---|
| 1 | **edge-tts** | `vi-VN-NamMinhNeural` (nam) | Stable, ít bị block |
| 2 | **edge-tts** | `vi-VN-HoaiMyNeural` (nữ) | Ngọt nhưng hay bị block |
| 3 | **Gemini TTS** | `gemini-2.5-flash-preview-tts` | Fallback ổn định |

### 🛠️ Kỹ thuật xử lý Voice & Video (BẮT BUỘC)

Nhằm tránh các lỗi mất chữ đầu (ví dụ: "Đúng" đọc thành "úng") và treo hình cuối video:

1.  **Regex Clean Text:** PHẢI hỗ trợ đầy đủ ký tự tiếng Việt VIẾT HOA (Đ, À, Á...).
    ```python
    # Pattern chuẩn
    pattern = r'[^a-zA-Z0-9àáảãạâầấẩẫậăằắẳẵặèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵĐÀÁẢÃẠÂẦẤẨẪẬĂẰẮẲẴẶÈÉẺẼẸÊỀẾỂỄỆÌÍỈĨỊÒÓỎÕỌÔỒỐỔỖỘƠỜỚỞỠỢÙÚỦŨỤƯỪỨỬỮỰỲÝỶỸỴ\s,.]'
    ```
2.  **Audio Padding:** Luôn thêm **0.2s im lặng** vào ĐẦU mỗi segment audio bằng FFmpeg để tránh bị hụt chữ đầu tiên khi ghép.
3.  **Minimum Duration:** Các đoạn quan trọng (Câu hỏi Vua Tiếng Việt, CTA) phải có thời lượng tối thiểu (**3.0s - 4.5s**) để người xem kịp đọc.
4.  **Scene Looping:** Sử dụng `-stream_loop -1` trong FFmpeg. Nếu video ngắn hơn Voice, PHẢI lặp lại video thay vì để freeze frame.

### Rate / tone
- **Rate**: `+10%` đến `+15%` (nói nhanh vừa, không gấp)
- **Style**: Enthusiastic, giòn giọng, thán từ ("Ôi chu choa", "Mê rồi", "Chu choa má ơi") ưu tiên trong caption

---

## 📦 Pipeline chuẩn (voice-first)

```
1. TTS mỗi segment → .wav/.mp3 → đo duration
2. Pick scene từ library (scene-library/ hoặc competitor-scenes/)
   - Filter caption keyword-match
   - Duration ≥ voice_dur (bắt buộc)
   - Sort by source_views desc
3. Trim scene đến voice_dur, ép 9:16 1080×1920
4. Render 1 subtitle PNG / segment → overlay
5. Render 1 label PNG (persistent) → overlay
6. Concat clips → concat audio → mux
7. Output: assets/products/{slug}/output/final/<caption>.mp4
```

---

## 📁 Output file + naming (convention mới, updated 2026-04-23)

```
assets/products/{slug}/output/final/
├── <caption + hashtag>.mp4           ← TikTok upload ready
├── <caption + hashtag>.mp4.meta.json ← metadata (source scene, voice script, duration)
└── (KHÔNG còn subfolder tiktok-ready/)
```

---

## ✅ Checklist QA trước khi ship video

- [ ] Resolution 1080×1920, 30fps
- [ ] Label "TÊN SP • PEL PEL" ở **y=280** (top)
- [ ] Subtitle pill đen mờ ở **y=1580** (bottom)
- [ ] **Voice KHÔNG bị mất chữ đầu (chữ Đ, À, Á...)**
- [ ] **Audio có padding 0.2s ở đầu**
- [ ] **Video không bị treo hình ở cuối (dùng loop nếu thiếu)**
- [ ] Tên file = caption + hashtag đầy đủ
