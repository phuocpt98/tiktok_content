# Tạp Hóa Pel Pel - Content Production System

## Role
Claude là **team sản xuất** cho kênh TikTok "Tạp Hóa Pel Pel". User là creative director — đưa ý tưởng, duyệt kết quả.

## Quick Commands
- `/pelpel <ý tưởng>` — Tạo content từ ý tưởng (full pipeline)
- `/pelpel trend` — Quét trend TikTok hiện tại cho niche tạp hóa
- `/pelpel plan` — Lên content plan cho tuần
- `/pelpel report` — Báo cáo tổng kết kênh
- `/pelpel assets` — Xem kho tài nguyên hiện có

## Tools
- Python venv: `.venv\Scripts\python.exe`
- Run command: `cmd.exe /c "set PYTHONIOENCODING=utf-8 & cd /d D:\project\demo\content & .venv\Scripts\python.exe -c \"<code>\""`
- Modules: `src/config.py`, `src/database.py`, `src/gemini-client.py`, `src/tts-engine.py`, `src/video-assembler.py`, `src/asset-importer.py`, `src/cli.py`
- Gemini API key in `.env.example`

## Channel Context
- Read `memory/project_pelpel_channel.md` for current stage, KPIs, content history
- Update after every content creation session
- Stage 1 (0→1K FL): viral content only, NO selling
- Stage 2 (1K+ FL): 70% value + 30% affiliate

## Content Formats
1. **Photo Mode slides** (ưu tiên) — 5-10 ảnh, upload trực tiếp TikTok Photo Mode
2. **Ảnh + text overlay** — nhúng chữ trending lên ảnh
3. **Slideshow video** — ảnh + voiceover, ghép bằng FFmpeg
4. **Video ngắn** — AI-generated (Gemini Veo, dùng ít)

## Principles (Karpathy-inspired — 2 principles hay miss)

**1. Think Before Coding** — Khi yêu cầu mơ hồ, **HỎI LẠI** trước khi làm:
- Nói rõ giả định nếu phải đoán. VD: "Anh nói X, em hiểu là Y, đúng không?"
- Nếu có 2-3 cách hiểu → liệt kê cho user chọn, không tự chọn bừa.
- Nếu cách đơn giản hơn tồn tại → propose, đừng ngại "phản biện".
- Case đã fail: "dịch xuống 1 chút" vs "dịch xuống thôi ko nhỏ hơn" — hỏi trước để khỏi làm lại.

**4. Goal-Driven Execution** — Task phải có tiêu chí verify cụ thể:
- "Fix video cụt" → "Voice không cắt giữa câu, verify bằng `ffprobe duration` khớp tổng voice segments"
- "Thêm label" → "Frame đầu + frame cuối đều thấy label — check PNG preview"
- "Chạy pipeline" → list output path + file size min expected
- Mỗi dòng thay đổi phải trace được về yêu cầu user. Không trace được → chưa làm.

## Model Routing (tiết kiệm token)

Project dùng 2 tier model:

| Tier | Model | Khi dùng |
|---|---|---|
| **Main session** | Opus 4.7 (default via settings) | Suy luận, sáng tạo, phân tích rút insight, viết kịch bản/caption, thiết kế concept, debug architecture, refactor convention |
| **Batch subagent** | Haiku (via `.claude/agents/batch-runner.md`) | Chạy script có sẵn, ingest/download hàng loạt, split scene, transcribe, build video với SEGMENTS đã chốt, copy/rename theo convention |

**Khi nào Opus delegate sang batch-runner**:

- User nói: "tải xuống toàn bộ", "split hết scenes", "chạy lại cho tất cả kênh", "re-run pipeline" → dùng Agent tool với `subagent_type: "batch-runner"`
- User yêu cầu thực thi script mà Opus đã chuẩn bị xong args (không cần thêm creative thinking)
- Task >2 phút, pipeline rõ ràng, không cần suy luận giữa chừng

**Khi KHÔNG delegate** (giữ trong Opus):

- User hỏi "nghĩ hộ concept", "rút bài học từ data", "viết caption", "phân tích đối thủ", "thiết kế flow mới"
- Debug lỗi mới chưa có pattern, research tool, review kiến trúc

**Cách gọi batch-runner**:

```
Agent tool:
  subagent_type: "batch-runner"
  prompt: "Chạy script X với args Y. Output vào Z. Theo quy trình trong docs/..."
```

Haiku nhận prompt, chạy, báo lại ngắn gọn. Opus tổng hợp kết quả + quyết định next step.

## Session Log Protocol

File `SESSION_LOG.md` ở root project track công việc cross-session. Khi user
mở nhiều Claude session song song, các session phải đọc + update file này để
không dẫm chân lên nhau.

**Quy tắc cho Claude**:

1. **Session start** (bắt đầu conversation với task không rõ ràng):
   → Đọc `SESSION_LOG.md` section `🔴 Active` xem session khác đang làm gì.
   → Nếu user yêu cầu task trùng với `Active` → hỏi lại hoặc chọn task khác.

2. **Trước khi launch task dài** (>2 phút, hoặc background job):
   → Append entry vào `🔴 Active` với format:
   ```
   ### [YYYY-MM-DD HH:MM] task-slug
   - **Session**: bg job `<bg-id>` hoặc `foreground`
   - **Goal**: <1 câu>
   - **Writing dirs**: <list folders bị ghi đè — session khác né>
   - **ETA**: <ước tính>
   ```

3. **Khi task xong** (hoặc fail):
   → Move entry từ `🔴 Active` xuống `✅ Recent` (top).
   → Cắt `Recent` còn ≤20 entry gần nhất. Entry cũ hơn delete.

4. **Khi biết task sắp làm** (user đã confirm nhưng chưa start):
   → Append vào `📋 Planned` với **trigger** (cần điều kiện gì để start).

5. **KHÔNG ghi các task vụn <1 phút** (đọc file, edit 1 dòng, v.v.) — chỉ log
   việc có state persistent hoặc chạy nền.

**Quy tắc cho user**:
- Mở session mới → nói "đọc SESSION_LOG xem đang có gì" nếu cần brief
- Có thể edit file trực tiếp để thêm task cho session khác pick up
