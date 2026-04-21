# AI Tools Reference - Tạp Hóa Pel Pel

> Danh sách AI tools dùng trong dự án, cập nhật 2026-04-13

## Chiến lược chọn tool

```
Ưu tiên 1: Free unlimited (Edge TTS, Meta AI web, Stable Diffusion local)
Ưu tiên 2: Free tier có giới hạn (Gemini API, Leonardo, Kling)
Ưu tiên 3: Gemini Web Pro (manual, $0 vì đã có gói Pro)
Ưu tiên 4: Paid API (chỉ khi scale lớn)
```

---

## Image Generation

| Tool | Free/ngày | API? | Chất lượng | Cách dùng |
|------|-----------|------|------------|-----------|
| **Gemini API** (Imagen) | ~50 ảnh (free tier) | **Có** | ⭐⭐⭐⭐ | Auto mode |
| **Gemini Web Pro** | Không giới hạn* | Không | ⭐⭐⭐⭐ | Manual mode (copy prompt) |
| **Meta AI** (meta.ai) | Không giới hạn* | **Không có API** | ⭐⭐⭐⭐ | Web only, không gọi API được |
| **Leonardo AI** | ~20-30 ảnh | **Có** | ⭐⭐⭐⭐ | Backup API |
| **Ideogram** | ~6/ngày | Không | ⭐⭐⭐⭐ | Text trong ảnh tốt nhất |
| **Stable Diffusion** | Không giới hạn | Local | ⭐⭐⭐⭐⭐ | Cần GPU, setup phức tạp |
| **Microsoft Copilot** | ~15/ngày | Không | ⭐⭐⭐ | Backup web |

> **Lưu ý Meta AI:** Chỉ dùng được trên web/app. Không có public API. Unofficial API vi phạm ToS.

---

## Video Generation

| Tool | Free/ngày | API? | Watermark? | Ghi chú |
|------|-----------|------|------------|---------|
| **Kling AI** | 2-3 video (5-10s) | Không | Có | Tốt nhất free |
| **Hailuo/MiniMax** | Có giới hạn | Không | Có | Chất lượng tốt |
| **MindVideo AI** | Vài video | Không | Có | Image-to-video |
| **Pollo AI** | Vài video | Không | Có | Image-to-video |
| **Gemini Veo** (API) | Rất ít free | Có | Không | Đắt (~$6/clip) |

> **Khuyến nghị:** Giai đoạn đầu dùng **slideshow ảnh + voice** thay vì AI video. Không watermark, chất lượng ổn định.

---

## Text-to-Speech (TTS)

| Tool | Free/ngày | Tiếng Việt? | Chất lượng | Cách dùng |
|------|-----------|-------------|------------|-----------|
| **Edge TTS** | **Không giới hạn** | **Có** | ⭐⭐⭐⭐ | Local, tích hợp code |
| **Gemini TTS** | Free tier | Có | ⭐⭐⭐⭐ | API, đã có key |
| **ElevenLabs** | ~3K chữ/ngày | Có | ⭐⭐⭐⭐⭐ | Giọng tự nhiên nhất |

> **Khuyến nghị:** Dùng **Edge TTS** làm default (free unlimited + tiếng Việt). ElevenLabs cho content quan trọng.

---

## Music Generation

| Tool | Free/ngày | Chất lượng | Ghi chú |
|------|-----------|------------|---------|
| **Suno** | ~10 bài | ⭐⭐⭐⭐ | Tốt nhất free |
| **Udio** | Có giới hạn | ⭐⭐⭐⭐⭐ | Chất lượng cao hơn |

> **Khuyến nghị:** Tạo sẵn ~20 nhạc nền, lưu assets, reuse nhiều video.

---

## Text / Script Generation

| Tool | Free/ngày | Tiếng Việt? | Ghi chú |
|------|-----------|-------------|---------|
| **Gemini API** (Flash) | Rất nhiều | **Có** | Rẻ nhất, ~$0.001/script |
| **Gemini Web Pro** | Không giới hạn | **Có** | Manual mode |

---

## Workflow Tối Ưu $0/video

```
Script:  Gemini API Flash (auto) hoặc Gemini Web (manual)
Ảnh:     Gemini Web Pro (manual, unlimited) → Meta AI web (backup)
Voice:   Edge TTS (auto, unlimited, tiếng Việt)
Nhạc:    Suno free → lưu asset reuse
Ghép:    FFmpeg local (unlimited)
```

## Workflow Có API (~$0.15/video)

```
Script:  Gemini API Flash (auto, ~$0.001)
Ảnh:     Gemini API Imagen (auto, ~$0.10-0.20)
Voice:   Edge TTS (auto, $0) hoặc Gemini TTS (~$0.01)
Nhạc:    Asset có sẵn ($0)
Ghép:    FFmpeg local ($0)
```

---

## Tích hợp trong hệ thống

Hệ thống hỗ trợ **dual-mode** cho mỗi bước:

| Bước | AUTO (API) | MANUAL (Web) |
|------|-----------|-------------|
| Script | Gemini API Flash | Gemini Web Pro |
| Ảnh | Gemini API Imagen | Gemini Web / Meta AI |
| Voice | Edge TTS / Gemini TTS | ElevenLabs web |
| Video | Gemini Veo (đắt) | Kling AI / slideshow |
| Nhạc | - | Suno web |
