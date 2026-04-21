# TikTok Algorithm Deep Dive 2025-2026
**Báo cáo nghiên cứu:** Cơ chế thuật toán TikTok cho Kênh Tạp Hóa Pel Pel

---

## 1. Interest Graph Algorithm & FYP Ranking

**TikTok không dùng social graph (hiển thị bạn bè), mà dùng interest graph** — thuật toán dự đoán content người dùng sẽ yêu thích dù không follow creator.

### Ranking Factors (ưu tiên giảm dần):
1. **Watch time + Completion rate (~40-50%)** — thứ tự ưu tiên #1, tăng từ 2024
   - Cũ: 3s retention đủ rồi
   - Mới (2026): watch time toàn bộ + completion rate ≥60% = tốt; ≥80% = viral
2. **Shares & Saves (15-25%)** — trọng số tăng mạnh 2025, quan trọng hơn likes
3. **Comments (10-15%)** — engagement sâu hơn likes
4. **Likes (≤10%)** — engagement sơ sài nhất
5. **Captions, hashtags, sounds** — metadata phân loại content

### Content Classification:
TikTok phân tích captions, sounds, hashtags để hiểu nội dung video, sau đó match với audience interest.

---

## 2. Content Distribution Flow

### Batch Testing Multi-Stage (Không phải random):
```
Stage 1: 200-500 user (follower test)
   ↓ Đạt threshold →
Stage 2: 1,000-10,000 user
   ↓ Đạt threshold →
Stage 3: 10,000-100,000 user (wide distribution)
   ↓ Đạt threshold →
Stage 4: 100,000+ user (viral tier)
```

**Mỗi stage không random:** TikTok show video cho user có watch history liên quan topic video, targeting càng chính xác dù mới ngắn.

### Granular Watch Checkpoints:
- 3s, 15s, 30s, 60s — phân tích granular watch time tại từng checkpoint
- **Replays = top quality indicator** cho distribution

### "Follower-First Testing" (Mới 2025):
Video mới → follower cũ trước → rồi mới wider audience. Follower engagement quyết định tier nhảy tiếp.

---

## 3. Ranking Signals Priority (Có thứ tự)

| Thứ tự | Signal | Trọng số | Ghi chú |
|--------|--------|---------|---------|
| 1 | Watch time + Completion rate | 40-50% | Toàn bộ video, không 3s rule |
| 2 | Shares | 15-20% | Lớn hơn saves từ 2025 |
| 3 | Saves | 10-15% | Signal "usefulness" |
| 4 | Comments | 10-15% | Deep engagement |
| 5 | Likes | <10% | Shallow engagement |
| 6 | View velocity (2h đầu) | Support | Tốc độ accumulate views |

**Mindset 2025:** Meaningful actions > quantity. 10K views + 100 sales > 1M views + 10 sales (TikTok Shop context).

---

## 4. Niche Identification Timeline

### Bao lâu TikTok xác định niche?
**Không có con số cụ thể**, nhưng:
- **30 ngày đầu:** Platform cần data để train algorithm niche của channel
- **Mục tiêu posting:** 5-7 video/tuần × 30 ngày để accumulate signal
- **Key signal:** Captions + sounds + hashtags + watch behavior từ mỗi video
- **NLP detect:** TikTok dùng NLP trên captions + metadata + user watch pattern

### Niche Authority (Mới 2025):
- Niche micro-specialization outperform broad appeal **300%** (e.g., "snack nạp năng lượng cho study burnout" > "snack bất kỳ")
- **Niche velocity:** TikTok measure tốc độ traction trong micro-community, không chỉ raw views
- Creators tập trung 1 niche → 3-5x faster growth vs general content

### Threshold Detection:
Researchers TikTok monitoring hàng ngàn video daily, tracking:
- Total views, engagement rate, content volume, creator activity
- AI content detection (Nov 2025): auto-detect output từ 47 AI platforms, label 1.3B videos

---

## 5. Shadow Ban / Reach Suppression

### Dấu hiệu chính:
1. **Sudden engagement drop** — non-follower reach drop liền (big red flag)
2. **Hashtag invisibility** — video không show trong search hashtag
3. **FYP absence** — không show ở FYP người lạ
4. **Inconsistent analytics** — video tương tự có khi cao/thấp bất thường
5. **Follower stagnation** — không có follower mới tích lũy

### Duration & Recovery:
- **3-14 ngày** (tuỳ severity)
- TikTok không notify, creator phát hiện khi track analytics

### Nó trigger bởi:
- Spam behavior, policy violations, cross-posting heavy
- **Niche switching liên tục?** Có khả năng trigger suppression (xem #6)

---

## 6. Business Account vs Entertainment → Algorithm Treatment Khác

### TikTok Shop Algorithm (khác main feed):
- **Not optimizing for entertainment** — focus: conversions
- **Ranking signal mới:** Add-to-cart, purchases = powerful signal hơn viral views
  - 10K views + 100 sales >> 1M views + 10 sales
- **Product visibility boost:** Content dùng TikTok Shop features (product anchors) + engaging = extra boost
  - Nhưng phải authentic, không purely spammy

### Main Feed vs Shop Feed:
- **Main feed:** Entertainment-first, secondarily aware of commerce
- **Shop feed:** Commerce-first, entertainment blended in for authenticity
- **Content requirement:** Educate/inspire/entertain WHILE integrating product (không chỉ demo tĩnh)

### Business Account Penalty (June 2025):
- Nếu dùng business account tag, TikTok giảm reach tối đa **40%** nếu content không match niche cũ hoặc là explicit selling
- **Workaround:** Personal account khi chuyển niche? (Rủi ro: mất verification badge, nếu có)

---

## 7. Optimization Cho Kênh Mới (30 Ngày Đầu)

### Strategy:
1. **Posting cadence:** 5-7 video/tuần (quantity matters lúc này)
2. **Focus metric:** Watch completion rate + view velocity (2h đầu), NOT total views
3. **Content pattern:** Dùng trending sounds + hashtags bí (micro niche, not mega)
4. **Hook:** 3s grab attention đầu tiên (critical)
5. **Content-to-end completion:** Hook ≠ full watch. Content phải interesting to the end.

### Algorithm Training Goal:
Accounts identify top-performing content type trong 30d + increase production 50% → avg 3x reach improvement next 60 days.

### Batch Distribution Logic:
1. Publish video
2. Show test 500-1K user (based: captions, sounds, hashtags, account history, user interest)
3. Measure: completion rate, shares, saves, comments
4. If exceed threshold → next tier
5. Repeat tier x tier

**Niche identification:** Captions metadata cực quan trọng → viết caption rõ ràng niche

---

## 8. Account Age Factor

### Lợi thế Tài Khoản Cũ:
- **Có history:** Past watch time, follower list, engagement pattern
- **Trustworthy signal:** TikTok = tài khoản cũ = stable contributor
- **Faster reactivation:** Especially với steady post history, report faster + consistent exposure

### Nhưng không tuyệt đối:
- **Không phải age alone** — quality + consistency + history violations matter
- **Factor deciding:** Account age, post consistency, content violation history, engagement trend, feature usage
- **Advantage thường overstated** — nếu tài khoản cũ post drama 2 năm, TikTok sẽ skeptical switch niche

### Cho Pel Pel (tài khoản cũ, mới post 2 ngày):
✓ Account age = advantage (trustworthy)
✗ Post history = risk (drama niche cũ → commerce niche mới = big jump)

---

## 9. Niche Switching Impact on Reach

### TikTok 2025 Behavior:
**When content jumps between categories → algorithm becomes conservative with distribution**

### Cụ thể:
- Niche consistency > frequency
- Cross-category content = reach suppression (exact %: tùy severity, est. 20-40%)
- Algorithm confidence = "Creator makes content about X" → dùng 90-day creator equity build
- Posting consistency > high frequency (2x/week consistent > 10x/week sporadic)

### Risk for Pel Pel:
Drama content (2 ngày) + switching to business/commerce → **High risk niche confusion suppression**
- Solution: Cần ~10-15 video commerce content liên tục, clear caption niche, format consistent
- Cần 30-60 ngày "retraining" algorithm coi kênh = commerce, ko drama

---

## 10. Key Insights Cho Pel Pel

### Situation:
- Tài khoản cũ ✓
- 30 FL, 2 ngày post ✓
- Drama niche trước, muốn commerce (snack, quần áo 50-200K VND) ✗
- Muốn bán hàng (cần TikTok Shop integration)

### Challenges:
1. **Niche switching penalty** — algorithm sẽ skeptical 30 ngày đầu
2. **Account history** — drama content = noise signal, commerce signal yếu
3. **New niche training** — cần commit 30-60 ngày consistency content commerce

### Action Plan:

**Phase 1 (Tuần 1-2): Clean Slate Niche Identity**
- 5-7 video/tuần, **mỗi video rõ ràng commerce/snack angle**
- Caption = micro-niche naming: "Snack bé vào học" / "Quần áo trẻ em giá yêu thương"
- Dùng trending sound ✓ nhưng niche-relevant (food, fashion)
- Hashtag strategy: không mega (#snack = 100M), chọn micro (#snackbevaohoc, #quantroemdacdac)
- Không mix drama + commerce trong 30 ngày này

**Phase 2 (Tuần 3-4): Conversion Signal**
- Integrate TikTok Shop product links / affiliate
- Video content = educate/inspire + product, NOT demo
  - Example: "Snack năng lượng ⚡ học 12h" (educate) + product (affiliate)
  - NOT: "Mình bán snack, bấm link mua"
- Measure: completion rate ≥60%, target shares/saves > likes

**Phase 3 (Tháng 2): Niche Authority Build**
- Post consistency: 5-7x/week
- Analyze top 3 video → produce 50% more similar content
- Engage comment (response rate ↑)
- Replays = quality indicator → hook + retention optimization

**What to Avoid:**
- ✗ Cross-posting từ Instagram/YouTube (reach -40%)
- ✗ Mixing niche (comedy + snack + quần áo random) — wait 60 days
- ✗ Over-linking TikTok Shop quá sớm (lúc algorithm chưa confident)
- ✗ Hashtag spamming / caption vague

---

## Unresolved Questions

1. **Exact reach suppression % khi niche switching?** Sources estimate 20-40%, nhưng TikTok không public exact algorithm.
2. **Account age advantage = bao nhiêu %?** Qualitative advantage, không có metric định lượng.
3. **Drama content in history — bao lâu expire?** Không data chính thức, estimate: 60-90 ngày post commerce consistent sẽ override.
4. **TikTok Shop affiliate commission priority vs organic?** Algorithm treat equally (nếu content engaging), nhưng chưa có data confirm.
5. **Micro-niche velocity measurement** — TikTok không public công thức, inferred từ creator reports.

---

## Sources

- [TikTok Algorithm 2026: How the FYP Really Works (Ultimate Guide)](https://beatstorapon.com/blog/tiktok-algorithm-the-ultimate-guide/)
- [How the TikTok Algorithm Works in 2026 | PostEverywhere](https://posteverywhere.ai/blog/how-the-tiktok-algorithm-works)
- [How the TikTok Algorithm Works in 2026 | FiveBBC](https://fivebbc.com/blog/how-the-tiktok-algorithm-really-works-in-2025/)
- [How the TikTok Algorithm Works in 2026 | Sprout Social](https://sproutsocial.com/insights/tiktok-algorithm/)
- [TikTok Algorithm 2025 | Enrich Labs](https://www.enrichlabs.ai/blog/tiktok-algorithm-2025)
- [How to Go Viral on TikTok: 2025 Algorithm Secrets Revealed](https://www.clipwise.ai/blogs/how-to-go-viral-on-tiktok-2025-algorithm-secrets-revealed)
- [How does the TikTok algorithm work in 2025? Tips to boost visibility](https://blog.hootsuite.com/tiktok-algorithm/)
- [TikTok Algorithm 2025: How to Go Viral on TikTok with Proven Tips](https://recurpost.com/blog/tiktok-algorithm/)
- [Recent TikTok FYP Algorithm Changes (July 2025) – Napolify](https://napolify.com/blogs/news/fyp-algorithm-changes)
- [8 Strategies to Navigate the TikTok Algorithm Changes in 2025 Sotrender Blog](https://www.sotrender.com/blog/2025/08/tiktok-algorithm/)
- [The 2025 TikTok Algorithm: What You Need To Know - Fanpage Karma Insights](https://www.fanpagekarma.com/insights/the-2025-tiktok-algorithm-what-you-need-to-know/)
- [How the TikTok Algorithm Works [2025]](https://hashmeta.com/insights/how-tiktok-algorithm-works)
- [Buffer TikTok Algorithm Guide 2026](https://buffer.com/resources/tiktok-algorithm/)
- [TikTok Shadow Ban: Everything You Need to Know in 2025 | KOLHUB](https://kolhub.com/my/tiktok-shadow-ban-everything-you-need-to-know)
- [TikTok Shadow Ban: Signs, Causes & 3 Ways to Fix It](https://litcommerce.com/blog/tiktok-shadow-ban/)
- [Understanding TikTok's Shadow Ban: How It Works in 2025 | Brand Vision](https://www.brandvm.com/post/tiktoks-shadow-ban-how-it-works-2025)
- [How to Identify and Remove a TikTok Shadow Ban in 2026](https://multilogin.com/blog/tiktok-shadow-ban/)
- [Navigating TikTok Shop's Algorithm: Tips for Boosting Visibility](https://eva.guru/blog/navigating-tiktok-shops-algorithm/)
- [Winning TikTok Shop's Algorithm: How to Get More Visibility & Sales with Predictive Analytics](https://www.graas.ai/blog/tiktok-shop-predictive-analytics-strategy)
- [Maximizing TikTok Shop LIVE Sales - Algorithm Insights 2025](https://www.darkroomagency.com/observatory/cracking-the-algorithm-maximizing-tiktok-shop-live-sales-in-2025)
- [Maximizing TikTok Shop LIVE Sales - Algorithm Insights 2026](https://www.darkroomagency.com/observatory/cracking-the-algorithm-maximizing-tiktok-shop-live-sales-in-2026)
- [Crack the Code: Understanding How the TikTok Shop Algorithm Works](https://www.anstrex.com/blog/crack-the-code-understanding-how-the-tiktok-shop-algorithm-works)
- [How TikTok Shop recommends content](https://support.tiktok.com/en/using-tiktok/exploring-videos/how-tiktok-shop-recommends-content)
- [TikTok Algorithm 2025: Complete Marketer's Guide](https://www.dataslayer.ai/blog/tiktok-algorithm-2025-complete-guide-for-marketers)
- [TikTok Marketing 2025: Grow Your Account & Master TikTok Ads | Udemy](https://www.udemy.com/course/tiktok-marketing-grow-your-account-master-tiktok-ads/)
- [From 0 to 10K: A Data-Driven Breakdown of TikTok Growth in 30 Days](https://medium.com/@marksullivanwriter/from-0-to-10k-a-tiktok-growth-in-30-days-12de6d9f7e57)
- [The Impact of Account Age on TikTok Visibility and Trust Signals](https://www.studocu.com/en-us/document/los-angeles-city-college/fundamentals-of-advertising/the-impact-of-account-age-on-tiktok-visibility-and-trust-signals/138728378)
- [We mapped 121,000 videos to figure out how TikTok learns your interests - Washington Post](https://www.washingtonpost.com/technology/interactive/2025/tiktok-algorithm-video-map-interests/)
- [How TikTok's Algorithm Decides What You See (Reverse-Engineered) | Medium](https://medium.com/@sohail_saifi/how-tiktoks-algorithm-decides-what-you-see-reverse-engineered-19bf47e66bf4)
- [How To Dominate Your Niche With TikTok Marketing In 2025](https://inkbotdesign.com/tiktok-marketing/)
- [20 Businesses Finding Success on TikTok - Examples & Guide](https://joinbrands.com/blog/businesses-winning-big-tiktok/)
- [Did TikTok limit reach for business accounts? (June 2025) – Napolify](https://napolify.com/blogs/news/tiktok-limit-business-reach)
- [TikTok for Business: The Complete 2026 Guide for Brands | Heropost](https://heropost.io/tiktok-for-business-2026/)
