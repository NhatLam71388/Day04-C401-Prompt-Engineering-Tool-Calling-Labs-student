# Day 04 Lab v2 Report — Research Agent

## Team

- Team: Cognitive Lab 
- Members: (Thành viên nhóm)
- Provider/model: OpenRouter (google/gemini-2.0-flash-exp:free)

## Final Metrics

- Final version: v3
- Final artifact_version: 3
- Best base run file: runs/v3_base_...
- Base case accuracy: 100%
- Base tool routing accuracy: 100%
- Base argument accuracy: 100%
- Group eval run file: N/A
- Group eval accuracy: N/A
- Chat transcript file: transcripts/v3...

## Báo Cáo Tối Ưu Hóa (V0 - V3)

Sự cải thiện khả năng của AI Agent qua 4 phiên bản:

### 1. Version V0 & V1 (Bản gốc)
- **Tình trạng:** Khả năng định tuyến (routing) rất yếu. Khi thiếu dữ liệu, AI tự động đoán mò (hallucinate) các tham số như URL `example.com` hay tự gọi tool `send` mà không cần xác nhận.
- **Vấn đề cốt lõi:** System Prompt chưa có luật chặt chẽ, AI có xu hướng cố gắng thực thi lệnh bằng mọi giá.

### 2. Version V2 (Few-Shot Prompting)
- **Cải tiến:** Đưa vào các ví dụ mẫu (Examples of Correct Tool Usage).
- **Kết quả:** AI đã bắt đầu hiểu được các ngữ cảnh đặc biệt, ví dụ như biết từ chối viết code, hoặc biết gọi tool `clarify` (Hỏi lại người dùng) khi được yêu cầu đăng bài lên Telegram mà chưa có xác nhận nội dung.

### 3. Version V3 (Advanced Routing - Luồng tư duy 3 bước)
- **Cải tiến:** Áp dụng thuật toán ép AI phải tư duy theo 3 bước trước khi hành động:
  - **Scope Check:** Có nằm trong phạm vi kiến thức không?
  - **Argument Check:** Có đủ tham số (như link web, địa điểm) chưa?
  - **Action Check:** Hành động này có an toàn và được xác nhận chưa?
- **Kết quả:** Đạt tỷ lệ chính xác tuyệt đối (100% Accuracy). Zero Hallucination. AI trở nên cực kỳ thông minh, tuyệt đối không gọi tool bừa bãi và biết tự động dừng lại hỏi user khi thiếu dữ kiện.

---

## Các Công Cụ Mới Được Bổ Sung (Bonus Tools)

Ngoài các công cụ tìm kiếm và đọc web mặc định, chúng tôi đã tích hợp thêm 3 công cụ (Tools) mạnh mẽ để biến Agent thành một trợ lý đa năng toàn diện:

### 1. Công cụ Thời Tiết (`weather`)
- **Khả năng:** Truy xuất dữ liệu thời tiết theo thời gian thực (Real-time) cho bất kỳ tỉnh/thành phố hoặc quốc gia nào trên thế giới.
- **Cách hoạt động:** Được nâng cấp để fetch trực tiếp từ API miễn phí `wttr.in`. Trả về chính xác tình trạng (Nắng, Mưa, Mây) và nhiệt độ (°C) chuẩn xác tại thời điểm hỏi.

### 2. Công cụ Tính Toán Cơ Bản (`calculator`)
- **Khả năng:** Thực hiện các phép tính toán học (cộng, trừ, nhân, chia) một cách chính xác 100% mà không bị phụ thuộc vào nhược điểm tính toán yếu của LLM.
- **Cách hoạt động:** Agent sẽ trích xuất biểu thức toán học từ câu hỏi của người dùng và gọi tool này để tính ra kết quả cuối cùng thay vì tự suy đoán.

### 3. Công cụ Quy Đổi Tiền Tệ (`currency`)
- **Khả năng:** Tra cứu và quy đổi nhanh tỷ giá giữa các loại tiền tệ (Ví dụ: USD sang VND, EUR sang JPY).
- **Cách hoạt động:** Khi người dùng có nhu cầu mua sắm hoặc xem tin tức tài chính, AI có thể tự động gọi tool này để dịch các con số tiền tệ quốc tế sang mệnh giá quen thuộc của người dùng.

---

## Failure Analysis (Lịch sử Sửa lỗi)

| Case ID | Failure Type | Actual Tool Calls | What Failed | Fix |
|---|---|---|---|---|
| R01_missing_loc | missing_info | `weather(location="Hà Nội")` | Tự đoán địa điểm thay vì gọi tool `clarify` | Thêm luật Step 2: Argument Check |
| R02_send_unconfirmed | security_risk | `send(text="...")` | Tự động gửi tin nhắn khi user chưa xác nhận | Thêm luật Step 3: Action Check |
| R03_out_of_scope | out_of_scope | `lookup(query="python")` | Dùng tool tìm kiếm để giải bài tập lập trình | Thêm luật Step 1: Scope Check |

## Reflection & Tổng kết
Hệ thống Research Agent hiện tại không chỉ xuất sắc vượt qua các kịch bản đánh giá phức tạp của Lab 4 mà còn trở thành một trợ lý thực tế hữu dụng thông qua việc loại bỏ hoàn toàn Mock Data, thay thế bằng Live API cho cả tính năng Tìm kiếm Wikipedia, Đọc Web và Xem Thời Tiết thật.
