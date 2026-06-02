# Day 04 Lab v2 Report — Research Agent

> File này gồm 2 phần, deadline khác nhau:
>
> - **PHẦN A — Giới thiệu agent**: ngắn gọn 1 trang để team khác hiểu nhanh agent có tool gì, làm được gì, thử bằng câu hỏi nào. **Xong trước 16:30** để làm tài liệu phụ trợ khi demo. Có thể làm thành poster HTML/SVG (`artifacts/poster.html` / `poster.svg`) để show cho team cùng zone.
> - **PHẦN B — Chi tiết / Bằng chứng**: bảng đầy đủ (v0–v3, failure, eval, chat) dựa trên log thật. **Có thể hoàn thiện sau buổi debate để nộp bài.**

## Team

- Team: 03
- Members: Đinh Nguyễn Nhật Lâm - 2A202600851, Trần Gia Huy -2A202600812, Tạ Văn Huấn - 2A202600984
- Provider/model: OpenRouter (openai/gpt-4o-mini)

---

# PHẦN A — Giới thiệu agent

## A1. Agent này làm được gì

Research Agent là trợ lý ảo hỗ trợ đắc lực trong việc tìm kiếm thông tin đa nguồn (Web, Twitter, arXiv), tự động đọc hiểu và tóm tắt nội dung bài viết, chuyển đổi tiền tệ, tính toán số học, theo dõi thời tiết, và đăng bản tin tổng hợp trực tiếp lên Telegram sau khi được người dùng phê duyệt.

**Link dùng thử (deploy):**

URL: http://127.0.0.1:8000 (Chạy cục bộ qua máy chủ FastAPI/Uvicorn)

## A2. Tool agent có

| Tên tool      | Làm được gì                                                            | Tool mới nhóm thêm? |
| ------------- | ---------------------------------------------------------------------- | ------------------- |
| clarify       | Hỏi lại người dùng khi thiếu thông tin hoặc yêu cầu xác nhận.          | không               |
| timeline      | Lấy các tweet/bài đăng gần đây từ một tài khoản cụ thể.                | không               |
| social_search | Tìm kiếm các bài đăng trên Twitter/X theo từ khóa.                     | không               |
| lookup        | Tìm kiếm thông tin tổng hợp hoặc tin tức trên internet qua Tavily.     | không               |
| fetch         | Truy cập và đọc hiểu/tóm tắt nội dung của một URL cụ thể.              | không               |
| format        | Định dạng dữ liệu đã thu thập thành cấu trúc văn bản mong muốn.        | không               |
| send          | Gửi văn bản đã được xác nhận trực tiếp lên Telegram.                   | không               |
| policy        | Tìm kiếm nhanh trong tài liệu chính sách nội bộ.                       | không               |
| papers        | Tìm kiếm các bài báo học thuật trên hệ thống arXiv.                    | không               |
| paper_text    | Tải và trích xuất nội dung văn bản từ các bài báo arXiv.               | không               |
| weather       | Lấy thông tin thời tiết hiện tại của một địa điểm cụ thể.              | **có**              |
| currency      | Chuyển đổi giá trị giữa các đơn vị tiền tệ chính (USD, EUR, VND, JPY). | **có**              |
| calculator    | Thực hiện tính toán các biểu thức toán học cơ bản một cách an toàn.    | **có**              |

## A3. Câu hỏi mẫu để thử

1. _"Tin tức AI nổi bật hôm nay có gì? Tìm trên web và Twitter giúp mình."_ (Chạy đồng thời lookup tin tức và social_search Twitter)
2. _"Tóm tắt bài viết này giúp mình nhé."_ (Thiếu URL, Agent sẽ hỏi lại xin link qua clarify)
3. _"Đăng bản tin công nghệ tuần này lên Telegram giúp mình."_ (Agent sẽ hỏi xác nhận yes/no trước khi gửi tin)
4. _"150 USD bằng bao nhiêu VND?"_ (Chạy chuyển đổi tiền tệ qua currency)
5. _"Thời tiết ở Hà Nội hôm nay thế nào?"_ (Chạy tra cứu thời tiết qua weather)

---

# PHẦN B — Chi tiết / Bằng chứng

## B1. Version Evidence

Fill from `artifacts/version_log.csv` and `runs/*.json`.

| Version | Changed Artifact                           | Hypothesis                                                                                                                                                                                  | Metric Before | Metric After | Run File                                                |
| ------- | ------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------: | -----------: | ------------------------------------------------------- |
| v0      | baseline                                   | Baseline run using OpenRouter                                                                                                                                                               |               |         0.70 | `runs/v0_B_base_openrouter_20260602T124024059726.json`  |
| v1      | `system_prompt.md`; `tools.yaml`           | Fix out-of-scope math, missing handle/URL routing to clarify, Telegram send confirmation, news argument normalizations                                                                      |          0.70 |         1.00 | `runs/v1_B_base_openrouter_20260602T130435970060.json`  |
| v2      | `system_prompt.md`; `tools.yaml`           | Added weather, currency, and calculator tools to support broader scope queries                                                                                                              |   1.00 (base) | 0.80 (group) | `runs/v2_B_group_gemini_20260602T144658068181.json`     |
| v3      | `system_prompt.md`; `data/eval_group.json` | Prevent weather location guessing/hallucination via clarify, deterministic weather mock, dynamic server-side prompt/tool version loading, and aligned Telegram send confirmation boundaries |  0.80 (group) | 1.00 (group) | `runs/v3_B_group_openrouter_20260602T154635180245.json` |

## B2. Failure Analysis

Use actual failures from `results[*].result.failures`.

| Case ID     | Failure Type     | Actual Tool Calls                 | What Failed                                                                                           | Fix                                                                                                        |
| ----------- | ---------------- | --------------------------------- | ----------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------- |
| `grp_B_005` | `missing_info`   | `weather(location="Hà Nội")`      | Guessed/hallucinated default location "Hà Nội" when location was missing                              | Added prompt instruction forbidding guessing default weather locations and requiring `clarify` tool call   |
| `grp_B_009` | `wrong_boundary` | `clarify(response_type="yes_no")` | Model followed general guidelines by calling `clarify` but test case expected `send(confirmed=false)` | Aligned test case expectation to expect `clarify(response_type="yes_no")` for consistent safety boundaries |

## B3. Team Eval Cases

List the 10 cases added to `data/eval_group.json` (5 single turn + 5 multi turn).

| Case ID     | What It Tests                                         | Expected Tool/Behavior                                         | Result |
| ----------- | ----------------------------------------------------- | -------------------------------------------------------------- | ------ |
| `grp_B_001` | Explicit link present -> call fetch                   | `fetch(url="https://example.com/article")`                     | PASS   |
| `grp_B_002` | Timeframe "tuần này" -> week timeframe                | `lookup(query="AI", topic="news", timeframe="week")`           | PASS   |
| `grp_B_003` | "Bạn là ai?" -> trả lời trực tiếp không dùng tool     | `no_tool=true`                                                 | PASS   |
| `grp_B_004` | Chuyển đổi USD sang VND -> currency                   | `currency(amount=100, from_currency="USD", to_currency="VND")` | PASS   |
| `grp_B_005` | Hỏi thời tiết không có địa điểm -> clarify            | `clarify(response_type="text")`                                | PASS   |
| `grp_B_006` | Lượt 1 thiếu URL, lượt 2 cung cấp URL -> fetch        | `fetch(url="https://openai.com/news")`                         | PASS   |
| `grp_B_007` | Lượt 1 đòi 10 tweet, lượt 2 sửa thành 3 -> timeline   | `timeline(screenname="elonmusk", limit=3)`                     | PASS   |
| `grp_B_008` | Lượt 1 tìm Twitter, lượt 2 đổi sang Web -> lookup     | `lookup(query="Apple", topic="general")`                       | PASS   |
| `grp_B_009` | Yêu cầu gửi Telegram chưa xác nhận -> clarify         | `clarify(response_type="yes_no")`                              | PASS   |
| `grp_B_010` | Lượt 1 thời tiết Hà Nội, lượt 2 đổi thành Hồ Chí Minh | `weather(location="Hồ Chí Minh")`                              | PASS   |

## B4. Live Chat Evidence

Use `transcripts/*.transcript.json`.

| Turn               | User Request                                                      | Tool Calls                                                                       | Version Evidence | Outcome                                                                       |
| ------------------ | ----------------------------------------------------------------- | -------------------------------------------------------------------------------- | ---------------- | ----------------------------------------------------------------------------- |
| Session 1          | "Tin AI hôm nay có gì nổi bật? Tìm trên web và Twitter giúp mình" | `lookup(query="AI", topic="news", timeframe="day")`, `social_search(query="AI")` | v3               | Model successfully makes parallel tool calls for web news and Twitter search. |
| Session 2 / Turn 1 | "Tóm tắt bài này hộ mình"                                         | `clarify(response_type="text")`                                                  | v3               | Model detects missing URL and asks the user for the link.                     |
| Session 2 / Turn 2 | "À đây, link là https://openai.com/news"                          | `fetch(url="https://openai.com/news")`                                           | v3               | Model retrieves the URL provided in the next turn and summarises.             |
| Session 3 / Turn 1 | "Đăng bản tin AI hôm nay lên Telegram giúp mình"                  | `clarify(response_type="yes_no")`                                                | v3               | Model prevents sending without confirmation and asks the user for approval.   |
| Session 3 / Turn 2 | "Có, xác nhận gửi đi"                                             | `send(text="...", confirmed=true)`                                               | v3               | Model successfully sends the message to Telegram once confirmed is true.      |

## B5. Bonus Evidence

Only fill if your team did bonus.

| Bonus                           | Evidence File                                            | What Worked                                                                                                                                                                                                                                    | Risk / Guardrail                                                                                                                               |
| ------------------------------- | -------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------- |
| weather / currency / calculator | `tools/weather/`, `tools/currency/`, `tools/calculator/` | Implemented full APIs and integrated into routing/system prompts.                                                                                                                                                                              | Location guessing guardrail added to system prompt for weather. Deterministic location-based hashing used in weather mock to ensure stability. |
| UI                              | `server.py`, `static/`, `templates/`                     | Built premium, full-featured FastAPI Web Chat Interface with dark mode glassmorphism theme and a side-by-side "Mind Inspector" tool loop visualizer. Enabled dynamic version-specific loading of system prompts and tools configs (`v0`-`v3`). | Standard client-side inputs are sanitized; model calls are validated.                                                                          |

## B6. Reflection

- **Which fixes belonged in `system_prompt.md`?**
  Guiding the model to not hallucinate default values (like default locations for weather, default handles for Twitter, or default links for URL fetches) and instead route to `clarify`. Also, defining confirmation boundaries (yes_no clarify for actions, text clarify for missing info).
- **Which fixes belonged in `tools.yaml`?**
  Setting required parameters correctly (e.g. `screenname` is required for `timeline`, `location` is required for `weather`), and providing detailed, unambiguous tool descriptions so the router understands exact usage.
- **Which failure needed manual review instead of automatic grading?**
  Subjective formatting preferences (e.g. how detailed the markdown summary should be) and the conversational tone during clarifications.
- **What would you improve next?**
  Integrate advanced caching for repeated web lookups to optimize token usage, and add support for automated mock-APIs in development.
