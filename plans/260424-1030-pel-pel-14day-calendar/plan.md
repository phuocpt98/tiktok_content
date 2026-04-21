# Pel Pel — 14-Day Content Calendar (Gemini Pro output)

**Nguồn**: Gemini Pro (paste từ user 2026-04-24)
**Mục tiêu**: 14 concept video cho 2 tuần tới, áp dụng playbook từ `assets/analysis/tiktok/tap_hoa_pel_pel/lessons.md`

---

## Tài nguyên hiện có

- **Scene library Que Cay**: 296 scenes (@beheobu0102) + 27 scenes (@yen_doanvathot) = 323
- **Scene library Mực/Bạch Tuộc**: 38 scenes (@phuongoanh.daily + @dacsannhatrangphuonganh)
- **Scene library Yến**: ❌ CHƯA CÓ — cần ingest hoặc Pel Pel tự quay
- **Watermark Pel Pel**: `assets/brand/pelpel-watermark.png` (512px)
- **Product videos (Pel Pel có sẵn)**: 
  - `que-cay/videos/*.mp4` — 6 video AI-gen (không dùng theo feedback 2026-04-23)
  - `muc-bach-tuoc/videos/` — chưa có
  - `snack-bach-tuoc/videos/Appetizing_Octopus_Snack_Advertisement.mp4` (AI)

## Gap analysis (yêu cầu vs resource)

| Yêu cầu Gemini | Resource sẵn sàng? |
|---|---|
| **Scene que cay bóc, cắn, đổ** | ✅ 323 scene |
| **Scene mực/bạch tuộc ASMR** | ✅ 38 scene |
| **Scene yến** | ❌ Chưa ingest |
| **Scene quay Pel Pel (face)** | ❌ Đã filter face khỏi library |
| **Scene văn phòng / đóng hàng / thắt nơ** | ❌ Không có trong library |
| **Graphic/text overlay (cung hoàng đạo)** | ✅ Pillow render được |

## Phân loại 14 concept theo khả năng build

### ✅ Build được ngay (mix scene library + TTS voice)
- **Day 1** (Que Cay — Phonk trending) — 323 scene đủ pick close-up
- **Day 2** (Mực/Bạch Tuộc — ASMR) — 38 scene có scene ASMR tốt
- **Day 9** (Cung hoàng đạo) — graphic slide + text overlay, ít dựa scene
- **Day 14** (Combo 3 sản phẩm) — mix scene que cay + mực, thiếu yến thì skip phần 3 hoặc dùng stock

### 🟡 Khó / Cần adapt (thiếu face hoặc scene chuyên biệt)
- **Day 6** (Mix que cay + mì tôm) — cần quay thật hoặc tìm scene mix foods
- **Day 11** (Review ngược) — cần biểu cảm face, bị filter

### ❌ Không build được (cần Pel Pel tự quay / ingest thêm)
- **Day 3, 7, 10** (Yến) — chưa có material
- **Day 4** (Văn phòng) — không có scene office
- **Day 5** (Xếp 38 hũ mực) — cần quay sản phẩm thật
- **Day 8** (Đóng hàng) — cần quay thật
- **Day 12** (Đọc comment giả định + xé gói) — cần quay thật
- **Day 13** (Thách ăn, mồ hôi) — cần quay face

---

## 14 concept chi tiết (Gemini Pro)

### Day 1: Đánh thức vị giác (Que Cay)
- **Hook Script**: "Đừng xem nếu bạn sợ cay!" (TTS AI nữ lôi cuốn)
- **Scene Pick**: Góc quay siêu cận (Macro) xé bao bì 1 gói trong kho 296 que cay, dầu ớt tứa ra, cắn một miếng âm thanh thật giòn
- **Music Type**: Phonk giật beat/Bass boosted trending top 10
- **CTA**: "Thử thách bản thân thì nhấn vào giỏ hàng mua ngay!"
- **KPI**: Giỏ hàng TikTok Shop + Hook 3s đầu + Nhạc Trending

### Day 2: ASMR Quyến Rũ (Mực Bạch Tuộc)
- **Hook Script**: "Tìm được snack bạch tuộc NGON NHẤT Việt Nam chưa?"
- **Scene Pick**: Mở đầu bằng âm thanh GIÒN TAN cực mạnh khi nhai snack bạch tuộc (Trích từ kho 38 hũ). Không cần nói nhiều, tập trung tiếng nhai (ASMR)
- **Music Type**: Original tiếng nhai + nền Lo-fi chill trending âm lượng 10%
- **CTA**: "Tag ngay 'anh' vào đây và đòi mua ngay!"
- **KPI**: ASMR + Hook câu hỏi tò mò + CTA kêu gọi tag bạn bè

### Day 3: Giải Quyết Nỗi Đau (Yến)
- **Hook Script**: "Cuối tháng viêm màng túi nhưng vẫn muốn bồi bổ xịn xò?"
- **Scene Pick**: Quay cảnh bàn làm việc mệt mỏi, sau đó bật nắp 1 hũ yến (trong kho 27 hũ), khói lạnh bay ra (đá khô tạo hiệu ứng), ăn một ngụm mãn nguyện
- **Music Type**: Nhạc chữa lành (Healing/Acoustic) đang viral
- **CTA**: "Lưu ngay video này lại và chốt đơn ở góc trái nhé!"
- **KPI**: Giỏ hàng TikTok Shop + Nhạc Trending + Content mang giá trị đồng cảm

### Day 4: Thử Thách Văn Phòng (Que Cay)
- **Hook Script**: "Mang que cay lên văn phòng lén ăn và cái kết..."
- **Scene Pick**: Cầm bịch que cay đi vòng quanh công ty, lén đút cho đồng nghiệp ăn thử và quay lại phản ứng (nhăn mặt vì cay hoặc bất ngờ vì ngon)
- **Music Type**: Nhạc meme hài hước/Sound effect giật gân trending
- **CTA**: "Share cho bạn thân mê ăn vặt rủ mua chung nào!"
- **KPI**: Content giải trí + Không dùng original sound + Có giỏ hàng

### Day 5: Đánh Vào Tâm Lý Khan Hiếm (Mực Bạch Tuộc)
- **Hook Script**: "Cảnh báo: Kho nhà Pel chỉ còn đúng 38 hũ mực này thôi!"
- **Scene Pick**: Xếp chồng 38 hũ mực bạch tuộc lên bàn, hất đổ một hũ về phía camera
- **Music Type**: Nhạc kịch tính/Epic trending
- **CTA**: "Nhấn vào giỏ hàng mua ngay kẻo hết đồ nhâm nhi cuối tuần!"
- **KPI**: Giỏ hàng TikTok Shop + Hook mạnh mẽ 3s đầu

### Day 6: Mix & Match Phá Cách (Que Cay)
- **Hook Script**: "Bí mật snack gây nghiện không ai biết!"
- **Scene Pick**: Cắt nhỏ que cay trộn vào tô mì tôm nóng hổi, trộn đều lên cho sốt ớt áo đều sợi mì
- **Music Type**: Hiphop/Rap trending nhịp điệu nhanh
- **CTA**: "Comment món bạn muốn Pel Pel review kết hợp tiếp theo!"
- **KPI**: Đa dạng format (Mix & Match) + CTA tương tác bình luận

### Day 7: Trải Nghiệm Cá Nhân (Yến)
- **Hook Script**: "Đừng xem nếu bạn đang giảm cân!"
- **Scene Pick**: Pel Pel ngồi ăn yến lúc 2h sáng, quay màn hình đồng hồ, ăn ngon lành nhưng text overlay ghi "Yến mix hạt chia, siêu ít calo"
- **Music Type**: Nhạc sped-up (tua nhanh) các bài V-Pop đang lên xu hướng
- **CTA**: "Follow để không bỏ lỡ deal hot mỗi đêm nhé!"
- **KPI**: Hook đánh vào tâm lý + Nhạc trending

### Day 8: Storytelling Đằng Sau Hậu Trường (Que Cay)
- **Hook Script**: "Đây là cách tôi giải cứu 200 gói que cay..."
- **Scene Pick**: Ngồi đóng hàng mệt mỏi nhưng vui vẻ, dán băng keo rẹt rẹt, ném que cay vào thùng carton
- **Music Type**: Nhạc truyền cảm hứng/Hustle mindset trending
- **CTA**: "Ủng hộ Tạp Hóa Pel Pel 1 đơn ở giỏ hàng bên dưới nha!"
- **KPI**: Content kể chuyện thương hiệu + Gắn TikTok Shop

### Day 9: Tương Tác Cung Hoàng Đạo (Que Cay)
- **Hook Script**: "Top 3 cung hoàng đạo nghiện ăn cay nhất! Bạn có mặt không?"
- **Scene Pick**: Chỉ tay theo nhịp beat, text box hiện (Bạch Dương, Bọ Cạp, Sư Tử) + hình gói que cay bốc lửa
- **Music Type**: Nhạc trend biến hình/chỉ tay TikTok
- **CTA**: "Bạn cung gì? Comment xem có hợp cạ ăn que cay không nha!"
- **KPI**: Format "Snack cho từng cung hoàng đạo" + CTA kêu gọi bình luận

### Day 10: Tặng Quà Sang Trọng (Yến)
- **Hook Script**: "Quà tặng mẹ mùng 1 sang xịn mà ví vẫn mỉm cười!"
- **Scene Pick**: Thắt nơ ruy băng cho 1 set yến, viết tấm thiệp nhỏ. Ánh sáng ấm áp
- **Music Type**: Nhạc nhẹ nhàng, tình cảm gia đình đang thịnh hành
- **CTA**: "Giỏ hàng góc trái đang có Flash Sale, chốt luôn đi các bác!"
- **KPI**: Cung cấp giải pháp/giá trị ngoài sản phẩm + Có TikTok Shop

### Day 11: Review "Ngược" Tạo Tranh Cãi (Mực Bạch Tuộc)
- **Hook Script**: "Ai bảo snack bạch tuộc này ngon? Trừ 1 điểm vì quá tốn mồi!"
- **Scene Pick**: Nhăn mặt lúc đầu, sau đó ăn liên tục không dừng lại được. Vừa nhai vừa gật gù
- **Music Type**: Hài hước/Plot twist sound trending
- **CTA**: "Không tin thì mua thử ở giỏ hàng đi rồi biết tay tôi!"
- **KPI**: Hook gây tò mò + Gắn TikTok Shop

### Day 12: Góc Giải Đáp (Que Cay)
- **Hook Script**: "Có người bảo que cay Pel Pel ăn toàn mùi bột? Thử luôn!"
- **Scene Pick**: Đọc một comment giả định, xé gói que cay, bóp cho thấy độ dai và xé sợi rành mạch
- **Music Type**: Review/Vlog nhịp điệu vừa phải trending
- **CTA**: "Bác nào ăn rồi cho xin cái review công tâm dưới phần comment nha!"
- **KPI**: CTA khuyến khích tương tác + Trực diện đập tan nghi ngờ

### Day 13: Thử Thách Extreme (Que Cay)
- **Hook Script**: "Thử thách tìm món này ở VN có vị cay hơn!"
- **Scene Pick**: Thách một người bạn ăn 3 gói que cay liên tục không uống nước, mồ hôi nhễ nhại
- **Music Type**: Nhạc game show/Tension xây dựng kịch tính trending
- **CTA**: "Thách bạn tag được đứa dám chơi trò này!"
- **KPI**: Format "Thử thách ăn cay" + Tối ưu nhạc trending

### Day 14: Tổng Hợp Value Cực Đại (Combo 3 Sản phẩm)
- **Hook Script**: "Top 3 snack cứu đói đêm không thể bỏ qua tại Tạp Hóa Pel Pel!"
- **Scene Pick**: Jump cut 3 sản phẩm: Que cay (cay xé) → Mực bạch tuộc (giòn tan) → Yến (ngọt thanh)
- **Music Type**: Mashup các bài hot nhất TikTok tuần này
- **CTA**: "Vào ngay giỏ hàng hốt trọn combo nhâm nhi nào!"
- **KPI**: 100% có CTA + Gắn TikTok Shop + Tổng hợp kết thúc tuần 2

---

## Build progress

- [ ] Day 1 (Que Cay — Phonk)
- [ ] Day 2 (Mực/Bạch Tuộc — ASMR)
- [ ] Day 3 (Yến — KHÔNG có scene)
- [ ] Day 4 (Văn phòng — KHÔNG có scene)
- [ ] Day 5 (Khan hiếm — KHÔNG có scene xếp hũ)
- [ ] Day 6 (Mix mì tôm — KHÔNG có scene)
- [ ] Day 7 (Yến — KHÔNG có scene)
- [ ] Day 8 (Đóng hàng — KHÔNG có scene)
- [ ] Day 9 (Cung hoàng đạo — graphic slide OK)
- [ ] Day 10 (Yến — KHÔNG có scene)
- [ ] Day 11 (Review ngược — cần face)
- [ ] Day 12 (Giải đáp — cần quay)
- [ ] Day 13 (Thử thách — cần quay)
- [ ] Day 14 (Combo 3 — thiếu yến)

## Notes & Decisions
- Yến là sản phẩm chưa có scene library → cần quyết: (a) ingest kênh yến reference, (b) Pel Pel tự quay
- Một số video yêu cầu face-on-camera → scene library đã filter face, cần relax filter hoặc quay thật
