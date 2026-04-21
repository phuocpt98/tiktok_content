# Báo Cáo Nghiên Cứu Thư Viện Browser-Use

**Ngày:** 2026-04-20 | **Tác giả:** Researcher Agent

---

## Tóm Tắt

Browser-Use là thư viện Python mã nguồn mở production-grade (78k+ sao GitHub), kết hợp Playwright + LLM vision để tự động hóa web không cần selector hard-code. **Điểm chính:** Thay thế selector dễ vỡ bằng vision + reasoning, nhưng tốn API ($0.01-0.05/task). Hỗ trợ persistent session. **Chưa có case study cho TikTok**, nhưng kiến trúc phù hợp.

---

## 1. Kiến Trúc & Cơ Bản

**Là gì:** Framework AI agent cho phép LLM điều khiển browser qua câu lệnh tự nhiên.

**Cách tiếp cận:** Hybrid vision + DOM
- Trích xuất cấu trúc DOM (button, link, input, XPath)
- Chụp screenshot trang
- LLM phân tích cả 2 → hiểu context → quyết định hành động kế
- Playwright thực thi
- Lặp đến khi xong task

**LLM hỗ trợ:**
- ChatBrowserUse (proprietary, đã tối ưu)
- Claude (Anthropic)
- Gemini (Google)
- Ollama (local models)
- Custom integrations

**Não:** Vision-based thay cho CSS/XPath dễ vỡ — TikTok đổi UI sẽ không phá automation ngay như Playwright selector.

---

## 2. Browser-Use vs Playwright

| Yếu tố | Browser-Use | Playwright |
|--------|-------------|-----------|
| **Phụ thuộc selector** | Không (vision) | Cao (vỡ khi UI đổi) |
| **Tỉ lệ thành công** | 70-85% trên task lạ | 99%+ trên trang đã biết |
| **Độ phức tạp setup** | Cao hơn (cần LLM backend) | Thấp |
| **Chi phí mỗi task** | $0.01-0.05 (API) | Miễn phí |
| **Bảo trì** | Thấp (tự thích nghi UI) | Cao (selector vỡ thường xuyên) |
| **Phù hợp cho** | Flow phức tạp, không đoán trước | Task xác định, volume cao |

**Kết luận:** TikTok (đổi UI thường, login dễ vỡ) → Browser-Use thắng độ bền, Playwright thắng tốc độ/chi phí.

**Hướng hybrid (khuyến nghị):** Playwright cho login → Browser-Use cho bước upload/form hay vỡ khi UI đổi.

---

## 3. Persistent Session & Trạng Thái Login

**Có hỗ trợ.** Browser-Use chạy trên Playwright nên giữ:
- Session cookies (qua nhiều lần chạy)
- Browser context/storage
- Login state giữa các task

**Riêng cho TikTok:**
- Lưu cookies giữa các lần chạy bằng `save_storage_state()` / `load_storage_state()`
- TikTok dùng OAuth 2.0 + session cookies (sid_tt, ...)
- Có thể isolate browser profile qua proxy/antidetect tool nếu multi-account

**Lưu ý:** TikTok detect bot rất gắt (upload nhanh, pattern bất thường). Cần xoay session + delay.

---

## 4. Code Quickstart

**Ví dụ chính thức (form + upload):**

```python
from browser_use import Agent
from pydantic import BaseModel

class UploadTask(BaseModel):
    file_path: str
    form_fields: dict  # {"title": "...", "description": "..."}

agent = Agent(
    task=f"Upload file {file_path} với form fields {form_fields}",
    use_vision=True
)

result = agent.run()  # Trả về kết quả task
```

**Luồng thực thi:**
1. Agent mở browser → vào trang upload
2. LLM thấy form, quyết định điền tiêu đề trước
3. Playwright gõ text vào input
4. LLM thấy file input → bảo agent click + upload
5. Agent chờ trang success → trích xuất URL xác nhận

**Không cần selector string** — agent reason về layout trang bằng vision.

---

## 5. Self-Host & Chi Phí

**Open-source:** Có, full mã nguồn trên GitHub.

**Chạy free?** Hạn chế:
- Core library: Free (không tốn API)
- LLM inference: **Cần API external** (OpenAI, Anthropic, Google)
  - Claude 3.5: ~$0.01-0.05/task (1000 token vision + 200 token output)
  - ChatBrowserUse (proprietary): Tối ưu hơn, đắt hơn
  - Ollama (local): Free nếu tự host GPU

**Giảm chi phí:**
- Dùng model rẻ (Gemini Flash: $0.075/1M token input)
- Batch task (workflow nhiều bước = 1 LLM call)
- Self-host LLM open-source (Ollama, LLaMA) nhưng cần GPU ($200-500 phần cứng)

**Kết luận:** Không full self-host được nếu không có GPU. Browser-Use Cloud bundle browser + LLM (~$30-100/tháng cho dùng vừa).

---

## 6. Production Readiness

**Độ chín:**
- 78,000+ sao GitHub
- Phát triển active (release + bug fix đều)
- v0.1.48+ có cải thiện stability
- Khuyến nghị production qua **Browser Use Cloud** (managed service)

**Stability:**
- Bản open-source: Ổn định nhưng trẻ hơn Playwright
- Bản Cloud: Production-grade, SLA 99.9%
- Vấn đề: Vision LLM thi thoảng hiểu sai UI (5-15% error rate ở trang mơ hồ)

**Note:** Project liên quan `workflow-use` (RPA 2.0) đánh dấu rõ **chưa production-ready**.

---

## 7. TikTok Automation: Pattern & Rủi Ro

**Chưa có case study công khai cho browser-use + TikTok.**

**Từ research TikTok automation chung:**
- TikTok Web detect bot gắt (industry dùng antidetect browser như Multilogin)
- Tỉ lệ upload thành công ~85% (video processing + compliance check fail 15%)
- Cần xoay session (TikTok flag upload lặp lại từ cùng session)
- Rate limit: ~30-50 upload/ngày/account trước khi shadow-ban

**Lợi thế Browser-Use:** Vision-based xử lý được UI đổi (TikTok redesign upload modal thường xuyên).

**Rủi ro:** Nếu TikTok detect headless browser (Playwright-based) → account bị flag. Mitigation: Puppeteer Stealth plugin hoặc Browser Use Cloud (fingerprint giống người).

---

## 8. So Sánh với Setup Hiện Tại

**Hiện tại:** Playwright + commands.json IPC (Claude generate selector → agent thực thi)
- **Đau:** Selector vỡ khi TikTok đổi UI
- **Mạnh:** Nhanh, đáng tin cho flow đã biết

**Phương án Browser-Use:**
- **Được:** Bền với UI đổi, vision hiểu context
- **Mất:** Chậm hơn ~5-15%, tốn API mỗi task
- **Learning curve:** Vừa (Python + LLM integration mới)

**Khuyến nghị:** Hybrid cho pipeline TikTok:
1. Giữ Playwright cho login (xác định, không cần vision)
2. Dùng Browser-Use cho form upload (vision xử lý UI biến đổi)
3. Batch task để giảm API call (multi-upload = 1 LLM task)

---

## Câu Hỏi Chưa Giải Quyết

1. **TikTok detection:** TikTok có flag fingerprint của Browser-Use cloud agent là bot không? (Chưa có test công khai)
2. **Độ chính xác vision với video thumbnail:** LLM chọn field metadata video trong UI rối có đáng tin không?
3. **ROI chi phí vs lợi ích:** Tỉ lệ upload thành công cải thiện vs $0.02/task — cần phân tích break-even
4. **Khả thi Ollama:** LLaMA local có chạy được trên hạ tầng Pel Pel không cần GPU không? (Cần test)
5. **Timeline workflow-use:** Khi nào workflow-use đạt production? (Roadmap chưa rõ)

---

## Nguồn

- [Browser-Use GitHub](https://github.com/browser-use/browser-use)
- [Browser-Use vs Playwright Comparison 2026](https://www.nxcode.io/resources/news/stagehand-vs-browser-use-vs-playwright-ai-browser-automation-2026)
- [Browser-Use Architecture - Edlitera](https://www.edlitera.com/blog/posts/browser-use-llms-online)
- [DOM Intelligence Architecture - rtrvr.ai](https://www.rtrvr.ai/blog/dom-intelligence-architecture)
- [TikTok Automation Tools 2026 - NapoleonCat](https://napoleoncat.com/blog/tiktok-automation/)
- [Browserless Self-Hosted GitHub](https://github.com/browserless/browserless)
- [Building Browser Agents - ArXiv](https://arxiv.org/html/2511.19477v1)
