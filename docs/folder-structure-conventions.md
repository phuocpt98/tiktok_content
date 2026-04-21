# Folder Structure Conventions

> **Luật vàng**: Khi phát triển tính năng mới hoặc thêm một "đối tượng" mới
> (sản phẩm / kênh / plan / loại asset), **PHẢI dùng lại cấu trúc đã có**.
> Không tự sáng tạo layout riêng cho 1 case — thà extend convention hiện tại
> hơn là tạo variant mới.
>
> Trước khi tạo folder mới: **đọc file này + `ls` folder anh/em cùng loại**
> để copy đúng pattern. Nếu không có pattern phù hợp → bổ sung section mới
> vào file này TRƯỚC khi tạo folder, đảm bảo tương lai follow được.

---

## Nguyên tắc

1. **1 đối tượng = 1 folder riêng**, tên folder = slug không dấu, dùng dash
   (`banh-quy-lss`, không `banh_quy_lss` hay `BanhQuyLSS`).
2. **Tên file nhất quán** bên trong folder: `product.md`, `summary.md`,
   `plan.md` — không đổi tên tuỳ hứng.
3. **Timestamp prefix** cho file output/plan: `YYMMDD-HHMM-<slug>` hoặc
   `YYMMDD-<slug>-<variant>` tuỳ loại.
4. **Output ≠ Source**: không lẫn file gen vào folder input. Output luôn
   trong subfolder `output/` hoặc folder riêng như `assets/analysis/`.
5. **Khi muốn tạo cấu trúc mới** → update file này TRƯỚC, commit doc, rồi mới
   tạo folder thật.

---

## Template cho từng loại đối tượng

### 1. Sản phẩm bán (`assets/products/{slug}/`)

```
assets/products/{slug}/                  # slug: banh-quy-lss, que-cay-bo...
├── info/
│   └── product.md                       # info, selling points, content ideas
├── photos/                              # ảnh nguồn (Shopee/TikTok Shop/AI gen)
├── videos/                              # video nguồn (raw, scenes cắt ra để cạnh đây)
├── asset-library.md                     # (tùy chọn) mô tả từng file asset
└── output/                              # CHỈ CÓ khi đã gen video
    ├── slides/                          # ảnh slide đã xử lý
    ├── audio/                           # voiceover .m4a
    ├── final/                           # video MP4 sẵn-sàng-upload-TikTok
    │   ├── {caption + hashtag}.mp4      # tên = caption đầy đủ, khi upload
    │   │                                # TikTok auto-fill caption từ filename
    │   └── {caption + hashtag}.meta.json
    └── _tmp_v{N}/                       # intermediates (không commit, có thể xóa)
```

**Tạo mới**: `bash scripts/add-product.sh <slug> "Tên Sản Phẩm"` — clone từ
`_template/`.

### 2. Phân tích kênh (`assets/analysis/tiktok/{author}/`)

```
assets/analysis/tiktok/{author}/          # author: beheobu0102, yen_doanvathot
├── videos.csv                           # 1 dòng/video, có CSV_FIELDS chuẩn
├── summary.md                           # tổng hợp: avg views, top, timing, shop%
├── videos_products.csv                  # (tùy) extract-products.py output
├── filtered_cat-{category}.txt          # (tùy) output của filter-videos.py
└── lessons.md                           # (tùy) synthesize-lessons.py output
```

Pipeline: `analyze-channel.py → extract-products.py → filter-videos.py
→ synthesize-lessons.py`.

### 3. Raw ingest (`assets/raw/tiktok/{author}/`)

```
assets/raw/tiktok/{author}/
├── {video_id}.mp4                       # video gốc tải về
├── {video_id}.info.json                 # metadata yt-dlp
├── {video_id}.jpg                       # thumbnail
├── {video_id}.voiceover.txt             # (tùy) transcript đã gen
└── _manifest.jsonl                      # log ingest chung (1 dòng/video)
```

Tạo bằng `scripts/ingest-tiktok.py`.

### 4. Scene library dùng chung (`assets/scene-library/{category}/`)

```
assets/scene-library/{category}/          # category: que_cay, banh_trang_pho_mai
├── {author}_{video_id}_scene-{NN}.mp4    # scene đã cắt + watermark Pel Pel
└── {author}_{video_id}_scene-{NN}.json   # metadata: source, views, caption, ts
```

**Prefix `{author}_` bắt buộc** để dedup khi merge từ nhiều kênh. Tạo bằng
`scripts/split-with-watermark.py --ids-from ...`.

### 5. Plan / phase document (`plans/YYMMDD-HHMM-{slug}/`)

```
plans/YYMMDD-HHMM-{slug}/                 # 260422-1805-cross-platform-...
├── plan.md                              # overview, goals, deliverables
├── phase-01-{name}.md                   # (tùy) break thành phase
├── phase-02-{name}.md
└── ...

plans/reports/                           # research/analysis outputs
├── researcher-YYMMDD-HHMM-{topic}.md
├── trend-YYMMDD-HHMM-{topic}.md
└── planner-YYMMDD-HHMM-{topic}.md
```

Timestamp = lúc bắt đầu plan. Slug mô tả ngắn (≤5 từ, dash).

### 6. Content ideas (`assets/content-ideas/`)

```
assets/content-ideas/
├── viral-share-scripts.md               # kho CATEGORY 1-N, format cố định
├── {author}_{category}_ideas.md         # output extract-ideas-from-viral.py
└── {topic}.md                           # ideas theo chủ đề tự do
```

Rule: content-ideas file **chỉ chứa ideas/scripts**, không code, không data.

### 7. Scripts (`scripts/`)

Prefix theo loại việc — **1 file = 1 mục đích**:

| Prefix | Mục đích | Ví dụ |
|---|---|---|
| `add-` | Khởi tạo đối tượng mới | `add-product.sh` |
| `ingest-` | Tải data về | `ingest-tiktok.py` |
| `analyze-` | Phân tích, không tạo asset | `analyze-channel.py` |
| `extract-` | Rút info từ data thô | `extract-products.py`, `extract-ideas-from-viral.py` |
| `filter-` | Lọc dataset | `filter-videos.py` |
| `transcribe-` | Speech-to-text | `transcribe-scenes.py` |
| `synthesize-` | Kết hợp nhiều source → insight | `synthesize-lessons.py` |
| `split-` | Cắt video/data thành chunks | `split-video-by-scenes.py`, `split-with-watermark.py` |
| `gen-` | Sinh asset mới (video/image/audio) | `gen-banh-quy-lss-v4.py` |

**Gen script cho product cụ thể**: `gen-{product-slug}-v{N}.py` hoặc
`gen-{product-slug}-{variant}.py`.

### 8. Docs (`docs/`)

```
docs/
├── ai-tools-reference.md                # cheatsheet tools + cost
├── flow-library.md                      # các flow chính
├── folder-structure-conventions.md      # file này
├── ingest-video-guide.md                # how-to runbook
├── video-production-format.md           # spec video TikTok
└── video-publish-log.md                 # lịch sử đăng + KPI
```

Rule: docs **không** chứa state/data (KPI number hay dynamic content OK nếu
là log), chỉ convention + how-to + insight lâu dài.

### 9. Memory (`~/.claude/projects/.../memory/`)

```
memory/
├── MEMORY.md                            # index — 1 dòng/entry
├── feedback_{topic}.md                  # rules, preferences, corrections
├── project_{topic}.md                   # facts về initiatives đang chạy
├── reference_{topic}.md                 # pointers đến resources bên ngoài
└── user_{topic}.md                      # user role, skills
```

Xem `CLAUDE.md § auto memory` để biết khi nào save gì.

---

## Naming conventions

| Loại | Format | Ví dụ |
|---|---|---|
| Slug folder | kebab-case, không dấu | `banh-quy-lss` |
| **Video output final (TikTok)** | `{caption + hashtag}.mp4` | `Que cay brand nào đỉnh nhất team #anvat #quecay.mp4` |
| File output nội bộ có date | `YYMMDD-{slug}-v{N}-{variant}.ext` | `260422-banh-quy-lss-v4-fast-16s.m4a` |
| File output không date | `v{N}-{role}.ext` | `v1-voiceover.m4a`, `v2-s1.png` |
| Timestamp plan/report | `YYMMDD-HHMM-{slug}` | `260422-1805-cross-platform-clip-remix-pipeline` |
| Python script | `{verb-prefix}-{object}.py` | `analyze-channel.py` |
| Script cho product cụ thể | `gen-{product-slug}-v{N}.py` hoặc `build-{product-slug}-concept-v{N}.py` | `build-quecay-concept-v4.py` |

**Quy tắc đặt tên video final** (cho TikTok upload auto-fill caption):
- File name = caption đầy đủ + hashtag, có dấu tiếng Việt, có space, có `#`, có emoji
- Chiều dài ≤ 200 ký tự (filesystem limit ~255 bytes, chừa dư)
- Ghi đè nếu build lại (idempotent) — version info nằm trong `.meta.json` cùng tên
- CHỈ video final trong `output/final/` dùng convention này. File nội bộ (audio, slides, tmp) vẫn dùng date-slug.

**Cấm**: file intermediate không có prefix (`script.py`), slug folder có dấu tiếng Việt,
version kiểu `new`/`new2`/`final`/`final_v2` cho file nội bộ.

---

## Khi thêm đối tượng mới — checklist

1. **Đọc file này** → xem loại đối tượng đã có template chưa.
2. **Nếu có** → `ls` 1 folder anh/em gần giống để copy đúng cấu trúc.
3. **Nếu KHÔNG có** → update section mới trong file này trước, commit, RỒI
   mới tạo folder thật.
4. **Script hỗ trợ**: ưu tiên dùng/mở rộng `scripts/add-*.sh` thay vì
   `mkdir` thủ công, để cấu trúc được generate nhất quán.
5. **Cập nhật SESSION_LOG** nếu là task dài (>2 phút).

---

## Khi nghiên cứu/phát triển tính năng MỚI

> Áp dụng khi: ingest nguồn data mới, thêm loại output mới, thêm niche mới,
> kết nối platform mới, v.v.

1. **Research phase** → lưu output trong `plans/YYMMDD-HHMM-{slug}/` hoặc
   `plans/reports/researcher-YYMMDD-HHMM-{topic}.md`. Không đổ vào
   `assets/` hay root.
2. **Design cấu trúc folder** → bổ sung template mới vào file này TRƯỚC khi
   code. Review: có dùng lại pattern hiện có được không? Nếu có, đừng tạo
   kiểu mới.
3. **Prototype** → viết script với prefix đúng (xem bảng `scripts/` ở trên).
4. **Docs** → nếu pipeline phức tạp, viết runbook vào `docs/{feature}-guide.md`.
5. **Update SESSION_LOG** — mỗi milestone.
6. **Memory** — nếu learn được rule/preference nào, lưu vào `memory/feedback_*`.

**KHÔNG** được bỏ qua bước 2. Một lần tạo layout sai → 10 lần sau sẽ copy
cái sai. Fix sớm rẻ, fix muộn rất đắt.
