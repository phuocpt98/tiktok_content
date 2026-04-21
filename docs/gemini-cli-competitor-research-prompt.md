# Prompt cho Gemini CLI — Research + Analyze competitor TikTok

Dùng khi user muốn delegate việc research kênh đối thủ cho 1 niche cho Gemini CLI (trong project Pel Pel).

---

## 📋 Prompt TEMPLATE (fill vào `{niche}` + `{keywords}`)

```
Bạn là research agent làm trong project "Tạp Hóa Pel Pel" (@tap_hoa_pel_pel —
TikTok niche đồ ăn vặt VN, giai đoạn 0→1K follower).

Working dir: /Users/ghtk/Documents/project/personal/tiktok_content

MỤC TIÊU: Tìm + phân tích kênh TikTok đối thủ về niche "{niche}",
chuẩn bị material cho Pel Pel học hỏi pattern viral.

## BƯỚC 0 — Đọc context TRƯỚC khi làm bất cứ gì

Đọc các file này để hiểu convention + pipeline có sẵn:
1. `CLAUDE.md` — role, model routing, session log protocol
2. `docs/folder-structure-conventions.md` — layout chuẩn, KHÔNG tự sáng tạo
3. `docs/ingest-video-guide.md` — pipeline ingest + analyze
4. `docs/video-production-format.md` — format video gen (nếu cần build sau)
5. `SESSION_LOG.md` — check session khác đang làm gì, TRÁNH CONFLICT
6. `~/.claude/projects/.../memory/MEMORY.md` (nếu có) — rules đã đúc kết

KHÔNG skip bước này. Đọc trước, làm sau.

## BƯỚC 1 — Search kênh viral cho niche

Dùng tikwm search API (đã test work) để tìm top kênh có video viral về niche.

Keywords: {keywords}
(Ví dụ cho "kẹo dẻo": ["kẹo dẻo", "kẹo dẻo trái cây", "keo deo", "gummy candy VN"])

Python snippet mẫu (dùng trong scripts tạm hoặc inline):

```python
import urllib.parse, urllib.request, json, re

def tikwm_search(keyword, count=30):
    params = urllib.parse.urlencode({"keywords": keyword, "count": count})
    req = urllib.request.Request(
        f"https://www.tikwm.com/api/feed/search?{params}",
        headers={"User-Agent": "Mozilla/5.0 Safari/605.1.15"},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read()).get("data", {}).get("videos", [])

# Search multiple keywords, merge, filter by VN caption,
# sort by views → rank top 5-10 authors
```

Output mong đợi: list 5-10 top author với:
- unique_id
- top video views
- caption preview
- estimated relevance (keyword match trong caption VN)

## BƯỚC 2 — User review + chọn 2-3 kênh

KHÔNG auto-analyze tất cả kênh. **HỎI USER** chọn 2-3 kênh nào
để focus (tiết kiệm time + quota tikwm 1 req/s).

Lý do hỏi: Principle 1 (Karpathy) — không tự suy diễn về scope.

Output bước 2: list 2-3 kênh user confirm.

## BƯỚC 3 — Analyze mỗi kênh

Cho mỗi kênh user chọn, chạy (tuần tự, không song song):

```bash
cd /Users/ghtk/Documents/project/personal/tiktok_content

# Full analyze nếu kênh ≤500 video, hoặc --limit 100 nếu lớn
python3 scripts/analyze-channel.py "https://www.tiktok.com/@<handle>" \
    --all --with-tikwm

# Extract products (category, brand từ caption)
python3 scripts/extract-products.py \
    assets/analysis/tiktok/<handle>/videos.csv
```

⚠ ETA 20-40 phút/kênh nếu --all. Update `SESSION_LOG.md § Active` trước khi chạy.
Khi xong, move entry xuống Recent.

## BƯỚC 4 — Ingest top 5-10 video viral + split scenes

Với mỗi kênh đã analyze:

```bash
# Filter top 5-10 video viral về niche (keyword trong caption)
python3 scripts/filter-videos.py \
    assets/analysis/tiktok/<handle>/videos_products.csv \
    --hashtag <niche-hashtag> \
    --top 10 --format urls \
    --out /tmp/urls_<handle>.txt

# Hoặc nếu product category đã có:
# --category keo_deo --top 10

# Ingest MP4
python3 scripts/ingest-tiktok.py \
    --from-urls /tmp/urls_<handle>.txt --sleep 2

# Build IDs file cho split
grep -oE '[0-9]{15,}' /tmp/urls_<handle>.txt > /tmp/ids_<handle>.txt

# Split + watermark Pel Pel (filter face theo default)
python3 scripts/split-with-watermark.py \
    --ids-from /tmp/ids_<handle>.txt \
    --base-dir assets/raw/tiktok/<handle> \
    --out assets/products/<niche-slug>/competitor-scenes/<handle> \
    --category <niche-slug> \
    --min-len 1.5
```

Nếu product folder `assets/products/<niche-slug>/` chưa tồn tại, tạo theo
convention (xem `docs/folder-structure-conventions.md` §1):

```bash
cp -R assets/products/_template assets/products/<niche-slug>
mkdir -p assets/products/<niche-slug>/{photos,videos,competitor-scenes}
# Edit info/product.md với context niche
```

## BƯỚC 5 — Synthesize lessons

Cho mỗi kênh đã ingest:

```bash
# Lessons chi tiết per channel
python3 scripts/synthesize-lessons.py <handle> --category <niche-slug>

# Và/hoặc: extract ideas từ top viral (cần transcribe)
# python3 scripts/extract-ideas-from-viral.py <handle> --category <niche-slug> --top 5
```

Output: `assets/analysis/tiktok/<handle>/lessons.md` + append
`docs/pel-pel-playbook.md`.

## BƯỚC 6 — Report user

Tóm tắt ngắn gọn (≤300 từ):
- Số kênh analyzed
- Top 3 insight từ data (viral formula, duration, music, hashtag)
- Số MP4 ingested, số scenes sinh ra
- File output quan trọng (path)
- Gap vs Pel Pel hiện tại (mỗi kênh avg views vs Pel Pel 208v)
- Next step đề xuất

## RULES BẤT KHẢ XÂM PHẠM

1. **Đọc convention doc trước** khi tạo folder/file mới (không sáng tạo layout).
2. **Update SESSION_LOG.md** trước/sau mỗi task >2 phút.
3. **KHÔNG đụng** folder của session khác đang active (check SESSION_LOG).
4. **HỎI USER** khi mơ hồ — không tự quyết scope lớn.
5. **Ưu tiên script có sẵn** trong `scripts/` — không tự viết mới trừ khi thiếu.
6. **Tôn trọng rate-limit** tikwm 1.5s/request, yt-dlp 2s/request.
7. Quota Gemini (nếu dùng TTS): 10/day free tier. Cache output vào `_tmp_*/`.
8. **KHÔNG push git** trừ khi user explicit yêu cầu.

## Known hazards

- DNS block `tiktok.com` (Tailscale filter) → user phải tắt VPN trước khi chạy
- yt-dlp cần `curl_cffi` 0.10-0.14 cho impersonation (đã setup trong brew yt-dlp)
- Edge-tts voice `vi-VN-HoaiMyNeural` thỉnh thoảng Microsoft block, fallback `vi-VN-NamMinhNeural`
- tikwm `/api/user/posts` endpoint bị Cloudflare challenge — dùng `/api/feed/search` hoặc yt-dlp --flat-playlist thay

---

## Prompt SẴN-DÙNG cho 2 niche user hỏi

### Version A — Snack Bạch Tuộc

```
[paste toàn bộ template TRÊN, fill:]
{niche} = "snack bạch tuộc / snack mực"
{keywords} = ["snack bạch tuộc", "snack mực", "mực cán tẩm", "mực sấy", "octopus snack VN"]
{niche-slug} = "muc-bach-tuoc"
{niche-hashtag} = "snackbachtuoc" hoặc "snackmucnuong"

Ghi chú đặc biệt:
- Niche này Pel Pel đã có 38 scenes từ @phuongoanh.daily + @dacsannhatrangphuonganh
  (2026-04-24). Mục tiêu: mở rộng với kênh mới bổ sung.
- Product folder `assets/products/muc-bach-tuoc/` đã có sẵn, chỉ cần thêm
  subfolder `competitor-scenes/<handle>/` cho kênh mới.
- Kênh đã có data tham chiếu:
  - @tidusfood.vn — 6.78M views (bạch tuộc takoyaki)
  - @chunamsansale — 2 video 397K/88K (snack mực)
  - @volinhfc — 826K (mực cán tẩm)
  Có thể analyze thêm @tidusfood.vn nếu chưa có kênh mới.
```

### Version B — Kẹo Dẻo (niche MỚI)

```
[paste toàn bộ template TRÊN, fill:]
{niche} = "kẹo dẻo / gummy candy"
{keywords} = ["kẹo dẻo", "kẹo dẻo trái cây", "kẹo dẻo sữa chua", "keo deo",
              "gummy candy VN", "kẹo mềm"]
{niche-slug} = "keo-deo"
{niche-hashtag} = "keodeo" hoặc "keodeotraicay"

Ghi chú đặc biệt:
- Niche MỚI chưa có data. Research sẽ build scene library từ 0.
- Product folder `assets/products/keo-deo-sua-chua-hoa-qua/` đã tồn tại
  (Pel Pel có sẵn 1 product kẹo dẻo). Có thể:
    (a) Dùng luôn folder đó, thêm `competitor-scenes/<handle>/`
    (b) Tạo folder mới `assets/products/keo-deo/` generic hơn
  → HỎI USER chọn (a) hay (b).
- Thương hiệu lớn VN: Yuyu, Que, Haribo VN, Meiji, Konnyaku
  (có thể search thêm)
```

---

## Tips vận hành

- Gemini CLI có thể chạy batch (background) qua `&` hoặc `nohup`, tương tự Claude Code
- Output của Gemini thường dài hơn Claude — lưu ý truncate khi báo cáo user
- Gemini Pro reasoning chặt hơn Flash (dùng cho synthesize step 5). Flash OK cho search + execute step 1-4.
- Nếu Gemini CLI không support MCP tool (chưa chắc), cần provide script có sẵn
  thay vì gọi API Gemini inline từ prompt
