# Plan: Video Đầu Tiên — "Bữa cơm 10K từ đồ tạp hóa"

## Mục tiêu
Tạo video TikTok đầu tiên cho kênh Tạp Hóa Pel Pel, tối ưu cho viral.

## Ý tưởng
**"Bữa cơm 10K từ đồ tạp hóa — Ngon bất ngờ!"**
- Format: Slideshow video 15-20s (ảnh AI + voiceover + nhạc nền)
- Hook: "10 ngàn thôi mà ăn ngon hơn cơm bụi!"
- Tone: Tự nhiên, gần gũi, hơi bất ngờ

## Lý do chọn
- Relatable: ai cũng ăn cơm, ai cũng thích tiết kiệm
- Gây tò mò: "10K mua được gì?"
- Visual food → completion rate cao (bài học từ @beheobu0102)
- Không cần quay thật — Gemini Imagen tạo ảnh minh họa

## Production Pipeline

### Phase 1: Script (Gemini)
- [x] Tạo script 15-20s bằng `generate_script()`
- Hook 3s đầu: câu hỏi gây sốc về giá
- Body: show từng món (mì gói, trứng, rau, gia vị) + giá
- Ending: reveal bữa cơm hoàn chỉnh + CTA

### Phase 2: Ảnh AI (Gemini Imagen)
- [ ] Generate 5-6 ảnh minh họa bằng `generate_images_batch()`
  1. Ảnh mở: bàn tay cầm tờ 10K (hook visual)
  2. Mì gói trên kệ tạp hóa
  3. Trứng gà + rau xanh
  4. Đang nấu (xào mì, bốc khói)
  5. Bữa cơm hoàn chỉnh (close-up, food porn style)
  6. (Optional) Text overlay "CHỈ 10K!" trên nền đồ ăn

### Phase 3: Voiceover (Edge TTS)
- [ ] Generate voiceover bằng `generate_voice()` — giọng nữ miền Nam
- Tempo: nhanh, hào hứng
- Duration target: ~15s

### Phase 4: Ghép Video (FFmpeg)
- [ ] `images_to_trend_video()` — transition mix (zoom_in + zoom_out)
- Duration/image: 3s
- Crossfade: 0.5s
- Total: ~15s

### Phase 5: Nhạc nền
- [ ] Thêm nhạc trending nếu có (optional, TikTok có thể thêm sau)

### Phase 6: Output
- [ ] Export video 1080x1920, ready to upload
- [ ] Caption + hashtags
- [ ] Upload hoặc gửi user duyệt

## Output Files
- Script: `assets/text/script_*.json`
- Ảnh: `assets/images/bua-com-10k-*.png`
- Voice: `assets/audio/bua-com-10k.mp3`
- Video: `output/bua-com-10k-final.mp4`

## Hashtags
#ancungtiktok #foodfestontiktok #taphoa #buacom10k #tiettkiem #reviewanngon #taphoapelpel #fyp #xuhuong

## Thời gian đăng tối ưu
- Tối 19:00-21:30 (khung giờ vàng)
- Hoặc trưa 11:30-13:30 (giờ nghỉ tìm đồ ăn)
