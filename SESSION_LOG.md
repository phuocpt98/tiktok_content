# Session Log

> Cross-session work log. Các Claude session song song đọc file này để biết
> nhau đang làm gì, tránh conflict + share context.
>
> Format: 3 section — 🔴 Active / 📋 Planned / ✅ Recent.
> Quy tắc cập nhật ở CLAUDE.md § "Session Log Protocol".

---

## 🔴 Active (đang chạy)

*(Trống)*

---

## 📋 Planned (chuẩn bị xong, chờ trigger)

### Phân tích kênh @yen_doanvathot
- **Trigger**: user yêu cầu `/pelpel analyze @yen_doanvathot` hoặc tương tự
- **Pipeline**:
  1. `python3 scripts/analyze-channel.py https://www.tiktok.com/@yen_doanvathot --all --with-tikwm`
  2. `python3 scripts/extract-products.py assets/analysis/tiktok/yen_doanvathot/videos.csv`
  3. `python3 scripts/synthesize-lessons.py yen_doanvathot`
- **ETA**: 25-40 phút (phụ thuộc số video)
- **Writing dirs**: `assets/analysis/tiktok/yen_doanvathot/`
- **Note**: có 1 MP4 viral (589K views) đã tải từ trước trong `assets/raw/tiktok/yen_doanvathot/`

### Tải que cay từ kênh mới → resource
- **Trigger**: sau khi analyze-channel xong, user nói "tải que cay về"
- **Pipeline**: filter-videos → ingest-tiktok --from-urls → split-with-watermark
- **Writing dirs**: `assets/raw/tiktok/<author>/` + `assets/scene-library/que_cay/`
- **Note**: scene-library/que_cay/ là shared across channels. Tên file prefix author để dedup.

### Synthesize lessons cho @beheobu0102
- **Trigger**: user sẵn sàng
- **Pipeline**: `python3 scripts/synthesize-lessons.py beheobu0102 --category que_cay`
- **Writing dirs**: `assets/analysis/tiktok/beheobu0102/lessons.md` + `docs/pel-pel-playbook.md`
- **Note**: data đầy đủ (845 video), đã có 52 que_cay scenes (đang split)

---

## ✅ Recent (last 20)

### [2026-04-24 11:20] build-quecay-5-concepts-canonical-label
- **Output** (5 video trong `assets/products/que-cay/output/final/`):
  - Concept 1: `3 ông vua que cay team nào đây cưng 🔥 Comment 1, 2 hoặc 3 nha #quecay #quecayvuongthanlong #quecayhangdai #anvat #fyp #xuhuong.mp4` (24.60s, 12MB)
  - Concept 2: `Trời ơi cái này dài tới mức nào 🔥 ASMR cắn giòn tan luôn 🤤 #sonachvuongthanlong #quecayvuongthanlong #quecaydai #anvat #asmr #mlem #fyp.mp4` (19.63s, 14MB)
  - Concept 3: `Anh ơi em thèm cái này 🥺 Gửi cho người yêu - nếu anh xứng đáng ✨ #quecay #hintnguoiyeu #anvat #couplegoals #fyp #xuhuong.mp4` (19.17s, 13MB)
  - Concept 4: `XUÝT XOA hay SUÝT XOA khi cay quá - 90% người viết sai 👑 #vuativiet #chinhta #quecay #doanvat #fyp.mp4` (27.53s, 4.9MB)
  - Concept 5: `CAY XÉ hay CAY XÈ lưỡi - cả 2 đều đúng á 🌶️ #vuativiet #quecay #minigame #doanvat #fyp.mp4` (26.83s, 5.1MB)
- **Canonical spec** (tuân `docs/video-production-format.md`):
  - Label pill 900×140, cam `rgba(255,107,0,220)`, Arial 58pt trắng stroke 3px đen, overlay y=280 absolute
  - Subtitle pill 1000×200, đen `rgba(0,0,0,180)`, font 62pt, y=1580 absolute, ALL CAPS no emoji
  - Filename = caption đầy đủ (TikTok auto-fill)
- **Anti-dedup signatures per concept**:
  - Color tint: vàng / xanh lá / hồng / đỏ cam / tím
  - Hue shift: +3 / -5 / +10 / +5 / -8 độ
  - Progressive zoom per-scene
  - Scene mix 2 kênh beheobu + yen, dedup video_id, alternate author, seed khác
- **Scripts**: `scripts/build-quecay-concepts-1-2-3.py` (concept 1-3 scene-driven) + `scripts/build-quecay-vua-tieng-viet.py` (concept 4-5 CAT 12 hook-review-answer-invite)
- **TTS fallback 4-tier**: Edge direct → Edge chunking → Gemini Kore → **SILENT MP3** (lavfi anullsrc, dur ước theo len(text)/13.0) vì Edge cực unstable + Gemini 10 req/day hết quota. User add voice trên TikTok app cho segments silent.
- **Audio concat bug fix**: `concat demuxer + -c:a aac` fail khi mix codec (silent lame vs voice aac) — 24s video + chỉ 13s audio. Fix bằng `filter_complex concat=n=N:v=0:a=1[out]` re-encode cuối → reliable.
- **Memory update**: `feedback_product_label_top.md` + `feedback_video_format_canonical.md` pointers vào `docs/video-production-format.md` + reference script `build-quecay-concept-v4.py`

### [2026-04-24 10:51] rebuild-quecay-vtv-concept-4-5-variety-fix+label
- **Output final** (overwrite bản 10:22):
  - `XUÝT XOA hay SUÝT XOA khi cay quá - 90% người viết sai 👑 #vuativiet #chinhta #quecay #doanvat #fyp.mp4` (27.53s, 5.2MB)
  - `CAY XÉ hay CAY XÈ lưỡi - cả 2 đều đúng á 🌶️ #vuativiet #quecay #minigame #doanvat #fyp.mp4` (28.13s, 5.4MB)
- **Fix variety** (user complaint "2 video nền giống hệt"):
  - Background slides: 3 photos khác nhau × 2 concept = 6 photo unique (`_BG_USED_IN_SESSION` track, seeds 4001/4002/4003 và 5101/5202/5303)
  - Color tint per concept: đỏ cam `(180,40,30)` vs tím `(90,30,130)` 12%
  - Hue shift scenes: +5° vs -8°
  - Review scenes: từ 3 → **5 scenes min** (3 beheobu + 2 yen mix), alternate + dedup video_id
  - Progressive zoom per scene (concept 4 step 2%, concept 5 step 2.5%)
- **Thêm PRODUCT LABEL pill** `QUE CAY - PEL PEL` persistent top (y=9%, Arial Bold 56, pill đen bo tròn), overlay trên TOÀN video. Pattern từ v4 hôm qua, user confirm dùng dấu `-` thay `•`.
- **Memory feedback mới**: `feedback_product_label_top.md` — bắt buộc cho mọi script gen video về sau

### [2026-04-24 10:22] build-quecay-vua-tieng-viet-concept-4-and-5
- **Output**:
  - `XUÝT XOA hay SUÝT XOA khi cay quá - 90% người viết sai 👑 #vuativiet #chinhta #quecay #doanvat #fyp.mp4` (27.53s, 5.6MB)
  - `CAY XÉ hay CAY XÈ lưỡi - cả 2 đều đúng á 🌶️ #vuativiet #quecay #minigame #doanvat #fyp.mp4` (27.02s, 5.0MB)
- **Convention CAT 12** (hook slide → review → answer → invite), cả 2 concept **mix 2 beheobu + 1 yen scenes**, dedup video_id + alternate author + seed khác (chống pHash match)
- **Voice**: NamMinh (HoaiMy bị block), rate +10%
- **Bug nổi cộm**: Edge TTS service **cực unstable** hôm nay — fail random text/length/voice. Phải build 3-tier fallback:
  1. Edge TTS direct
  2. Edge TTS chunking theo `. ! ? —` (câu ngắn hơn pass rate cao hơn)
  3. **Gemini TTS** (model `gemini-2.5-flash-preview-tts`, voice Kore, 10 req/day) — không cần chạy cuối cùng, chunking đã đủ
- Script mới: `scripts/build-quecay-vua-tieng-viet.py` (config-driven cho 2 concept, `--concept 4|5`)
- **Why dài 27s** (target CAT 12 là 15-18s): Edge TTS default speed + voice nam nói chậm → voice 5-8s/segment × 4 = ~25-30s. Acceptable cho niche food TikTok.
- User insights: peak viewer 12am-7am → **đăng 3:30-4:30 AM** để warm up đúng peak 6-7am

### [2026-04-24 09:35] split-yen_doanvathot-que_cay-with-face-filter
- **Output**: `assets/products/que-cay/competitor-scenes/yen_doanvathot/` — **27 scenes** (162MB), mỗi scene kèm JSON metadata
- **Drop do có mặt mẫu**: 53/80 scenes (66%). **36/50 video bị drop 100%** (POV selfie nguyên video)
- Top 3 viral (3.27M, 799K, 792K views) drop hết vì content selfie reaction
- Scenes giữ lại chủ yếu từ video tầm trung: 707K "Sổ nách vương thần long" (3 scenes), 595K "Má ơi mê mê mê" (2), 192K "Sổ néch VTL" (3)
- **Script updates** `scripts/split-with-watermark.py`:
  - Thêm `--out` flag, `--keep-face` flag (default: drop face)
  - Thêm `scene_has_face()` dùng OpenCV Haar cascade frontal (6-frame sample, 2+ hits, minSize 90px)
  - Bỏ append `category` vào path (category giờ là metadata trong JSON)
  - Default out: `assets/products/que-cay/competitor-scenes/`
- **Insight**: Yến content heavy POV face → muốn pool scene lớn hơn cần @beheobu0102 (296 scenes đã có từ 23/4 15:45) hoặc relax face filter
- Watermark Pel Pel 22% width góc phải-dưới, LUÔN add (video tikwm đã strip channel branding)
