# Series: Food Clip Remix — Video Ngắn Đồ Ăn

## Concept

Quay **clip nguồn** (source clips) 5-8 giây, mỗi clip là 1 cảnh đồ ăn hấp dẫn. Sau đó **remix/ghép** các clip thành nhiều video 10-30s khác nhau để đăng TikTok.

**1 lần quay → nhiều video output** = tiết kiệm công sức, đăng nhiều, tăng cơ hội viral.

## Nguyên Lý

```
Clip nguồn:  A  B  C  D  E  F  G  H  ...
              ↓
Video 1:     A → B → C          (15s)
Video 2:     A → C → D          (18s)
Video 3:     B → D → E → F      (25s)
Video 4:     C → A → C          (18s, lặp)
Video 5:     D → E → D          (18s, lặp)
Video 6:     A → B → C → D → E  (30s, full)
...
```

Mỗi combo khác nhau = video mới trên TikTok, algorithm xem là content riêng biệt.

---

## Phase 1: Quay Clip Nguồn

### Danh Sách Clip Nguồn Cần Quay (mỗi clip 5-8s)

| ID | Cảnh | Mô tả | Tips quay |
|----|-------|--------|-----------|
| A | **Mì tôm sôi** | Nồi mì đang sôi, bỏ rau vào | Close-up, hơi nước bốc |
| B | **Xúc xích nướng** | Xúc xích trên chảo, dầu xèo xèo | Slow-mo nếu được |
| C | **Trứng chiên** | Đập trứng vào chảo, lòng đỏ còn nguyên | Góc trên xuống |
| D | **Snack bóc** | Mở gói snack, đổ ra đĩa | ASMR sound, close-up |
| E | **Cơm trộn** | Trộn cơm với đồ ăn, xúc 1 muỗng | Đầy đặn, hấp dẫn |
| F | **Nước ngọt rót** | Rót nước ngọt vào ly đá, bọt gas | Slow-mo, close-up |
| G | **Bánh tráng nướng** | Nướng bánh tráng, phết mỡ hành | Street food vibe |
| H | **Bóc hộp** | Unbox đồ ăn giao/mua từ tạp hóa | Reveal moment |
| I | **Bàn ăn full** | Bàn đầy đồ ăn, góc wide | Establishing shot |
| J | **Cắn miếng đầu** | Cắn miếng đầu tiên, reaction | Biểu cảm thích thú |

**Tối thiểu quay:** 6-8 clip nguồn = đủ tạo 15-20 video remix

### Yêu Cầu Kỹ Thuật
- **Format:** 9:16 dọc (1080x1920)
- **Thời lượng:** 5-8 giây mỗi clip
- **Chất lượng:** 1080p trở lên
- **Ánh sáng:** Sáng tự nhiên hoặc đèn ấm (warm tone)
- **Âm thanh:** Thu tiếng thật (xèo xèo, giòn rụm, nước sôi)
- **Góc quay:** Close-up là chính, 1-2 góc wide

---

## Phase 2: Công Thức Remix

### Bảng Combo Video

Ký hiệu: `ID clip (thời lượng)` → tổng ~10-30s

#### Combo ngắn (10-15s) — dễ viral, loop tốt
| # | Combo | Mô tả | Tổng |
|---|-------|--------|------|
| 1 | A → B | Mì sôi → xúc xích | ~12s |
| 2 | C → E | Trứng chiên → cơm trộn | ~12s |
| 3 | D → F | Bóc snack → rót nước | ~12s |
| 4 | G → J | Bánh tráng nướng → cắn | ~12s |
| 5 | A → A (lặp) | Mì sôi loop | ~12s |
| 6 | B → J | Xúc xích → cắn miếng | ~12s |

#### Combo vừa (15-20s) — kể chuyện mini
| # | Combo | Mô tả | Tổng |
|---|-------|--------|------|
| 7 | H → D → J | Bóc hộp → bóc snack → ăn | ~18s |
| 8 | A → C → E | Nấu mì → chiên trứng → trộn cơm | ~20s |
| 9 | I → B → G | Bàn full → nướng xúc xích → bánh tráng | ~18s |
| 10 | D → F → D | Bóc snack → rót nước → bóc thêm | ~20s |

#### Combo dài (20-30s) — story arc
| # | Combo | Mô tả | Tổng |
|---|-------|--------|------|
| 11 | H → A → C → E → J | Unbox → nấu → chiên → trộn → ăn | ~30s |
| 12 | I → B → G → D → F | Bàn ăn → nướng → bánh tráng → snack → nước | ~30s |
| 13 | D → D → D → J | 3 loại snack → reaction | ~25s |
| 14 | A → B → C → J | 3 món nấu → cắn miếng | ~25s |

#### Combo lặp (loop bait) — tăng watch time
| # | Combo | Mô tả | Tổng |
|---|-------|--------|------|
| 15 | B → J → B | Nướng → ăn → nướng lại | ~18s |
| 16 | A → E → A | Nấu → ăn → nấu lại | ~18s |
| 17 | D → F → D → F | Snack → nước → snack → nước | ~24s |

---

## Phase 3: Hậu Kỳ (Claude xử lý)

### Mỗi video cần
1. **Ghép clip** theo combo (FFmpeg)
2. **Nhạc nền** — trending sound TikTok hoặc nhạc lo-fi ăn uống
3. **Text overlay** (tùy chọn) — caption ngắn "Bữa tối 30K 🍜" hoặc "Ăn gì hôm nay?"
4. **Transition** — cut thẳng (phổ biến nhất) hoặc fade nhanh
5. **Speed** — 1x hoặc 1.2x cho nhịp nhanh hơn

### Caption Template
```
[Hook emoji] + [Mô tả ngắn]
.
.
.
#anuong #doanuongngon #taphoa #pelpel #fyp #xuhuong
#angi #reviewdoan #doanuongvn #tiktokfood
```

### Ví Dụ Caption
- "Bữa tối 30K có gì? 🍜"
- "Ăn vặt cuối tuần be like 🤤"
- "Tạp hóa có đủ hết nè 😋"
- "POV: bạn đói lúc 2h sáng 🌙"

---

## Phase 4: Lịch Đăng

### Tuần đầu (từ 10 clip nguồn → 17 videos)

| Ngày | Sáng (11h) | Chiều (17h) | Tối (21h) |
|------|------------|-------------|-----------|
| T2 | Combo 1 | Combo 7 | Combo 15 |
| T3 | Combo 2 | Combo 8 | Combo 16 |
| T4 | Combo 3 | Combo 9 | Combo 5 |
| T5 | Combo 4 | Combo 10 | Combo 17 |
| T6 | Combo 6 | Combo 11 | - |
| T7 | Combo 12 | Combo 13 | - |

**17 videos/tuần từ chỉ 10 clip nguồn!**

### Tuần sau
- Quay thêm 5-6 clip mới (K, L, M...)
- Trộn clip mới + clip cũ → 15-20 video mới nữa
- Video nào viral → tạo thêm biến thể từ cùng clip

---

## Quy Trình Tóm Tắt

```
Bạn quay 10 clip (30 phút)
    ↓
Gửi file cho Claude
    ↓
Claude ghép 17+ video (FFmpeg)
    ↓
Claude tạo caption + hashtags
    ↓
Bạn review → đăng TikTok
    ↓
Track views → clip nào hot → tạo thêm biến thể
```

---

## Liên Kết Bài Học @beheobu0102
- ✅ **Đăng nhiều** — 17 vid/tuần, 2-3/ngày
- ✅ **Food content viral** — đồ ăn hấp dẫn close-up
- ✅ **Chấp nhận flop** — volume cao, chờ viral
- ✅ **Có chiến lược** — không spam random, có combo + series
- ✅ **Tiết kiệm effort** — quay 1 lần, dùng nhiều lần

---

---

## Gemini Research Insights (2026-04-14)

### Algorithm Tối Ưu
- **Completion Rate + Share/Save** quyết định lên FYP
- Food porn "gây nghiện" → xem lặp lại → boost completion rate
- Thời lượng tối ưu: **7-15s** (visual), **30-45s** (drama)

### Hook Pattern (3s đầu)
- Âm thanh mạnh: tiếng nhai giòn, mở bao bì, xèo xèo
- Câu hỏi: "Món này 90% người ăn sai cách"
- Visual shock: close-up đồ ăn ngay frame đầu

### Thời Gian Đăng (VN)
- **Trưa 11:30-13:30** — giờ nghỉ, lướt tìm đồ ăn
- **Tối 19:00-21:30** — khung giờ VÀNG
- **Khuya 22:30-00:00** — tệp "thèm ăn đêm"

### Hashtags
Core: #ancungtiktok #foodfestontiktok #taphoa #reviewanngon
Brand: #taphoapelpel | Viral: #fyp #xuhuong

### Trending Sound (T4/2026)
- Vinahouse Remix (Chờ Anh Về, Tấm Lòng Cửu Long) — cho twist
- Lofi chill — cho slide ảnh nhẹ nhàng
- "Gwenchana" — cho tình huống hài hước

### 10 Ý Tưởng Bổ Sung (từ Gemini)
1. ASMR đóng hàng (băng keo, xếp bánh)
2. Top 5 món cay nhất + twist hài
3. Grocery Haul 50K
4. Drama "Lén ăn vụng"
5. Kỳ vọng vs Thực tế — review bánh kẹo
6. Mix đồ ăn vặt lạ (mì cay + phô mai que)
7. Remix tiếng máy quét mã vạch
8. Bữa cơm 10K từ đồ tạp hóa
9. Vlog 5h sáng tại tiệm
10. Mystery Box cho khách

---

## Status: ⏳ Chờ bạn quay clip nguồn
