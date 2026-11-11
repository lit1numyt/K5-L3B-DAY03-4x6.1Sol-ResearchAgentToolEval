# Báo cáo cá nhân — Nguyễn Đức Khương Lam — 2A202604020

## 1. Thông tin thành viên

- Họ tên: Nguyễn Đức Khương Lam — nhóm 4x6.1Sol, lớp L3B
- MSSV: 2A202604020
- Email:

## 2. Phần việc phụ trách

Em phụ trách phân tích kết quả eval, xác định nguyên nhân lỗi và hiệu chỉnh system prompt, mô tả tool. Công việc bao gồm đối chiếu các thay đổi với kết quả từng phiên bản, ghi bằng chứng vào báo cáo nhóm và kiểm tra quy trình xác nhận trước khi gửi bản tin lên Telegram.

## 3. Đóng góp cụ thể

Từ kết quả baseline v0, em phân tích các lỗi thiếu thông tin, xác nhận gửi, yêu cầu ngoài phạm vi và tham số tìm kiếm. Phần hiệu chỉnh v1 làm rõ khi nào cần hỏi lại, giới hạn sử dụng `send` và cách truyền arguments cho `lookup`. Kết quả base tăng từ 13/20 ở v0 lên 17/20 ở v1.

Sau v1, em phân tích các trường hợp hỏi thừa và điều chỉnh v2 để phân biệt thông tin bắt buộc với tham số có thể dùng mặc định. Kết quả v2 đạt 18/20 base. Phần hiệu chỉnh và phân tích được lưu tại commit `3b80d8f`; việc chạy eval và lưu snapshot có sự phối hợp của nhóm.

Khi rà soát v3, em phân tích trường hợp R14 được chấm đạt vì không gọi tool nhưng câu trả lời vẫn hướng dẫn giải bài lập trình ngoài phạm vi. Commit `54d010f` làm rõ cách xử lý yêu cầu ngoài phạm vi và quy trình duyệt bản tin Telegram. Các thay đổi này được hợp nhất vào v9 và đo riêng; v9 đạt 19/20 base và 9/10 group chung.

Trong một [hội thoại v8](../../starter_v0/transcripts/v8_openai_20261111T095230010224.transcript.json), agent gửi bản tin ngay sau khi nhận nội dung, trước khi người dùng xác nhận đăng. Từ vấn đề đó, v10 được xây dựng trên nền v8, làm rõ quy tắc duyệt trong prompt và mô tả `send.confirmed`. Bản v10 đạt **20/20 base và 10/10 group chung**, đo đủ case và không lỗi provider. Trong [lượt gửi thật](../../starter_v0/transcripts/v10_openai_20261111T113930634960.transcript.json), agent hỏi duyệt nguyên văn, chờ xác nhận rồi gọi `send`; tool trả `status: sent`. Channel nhận tin là private, được xác nhận riêng vì transcript không ghi loại channel.

Khi thử Gemini, em gặp lỗi chuyển đổi JSON Schema của tool. Bản vá provider và test được lưu trong [gemini_provider.py](../../starter_v0/providers/gemini_provider.py) và [test_gemini_provider.py](../../starter_v0/tests/test_gemini_provider.py). Test offline đạt, nhưng lần kiểm tra API sau sửa bị timeout nên chưa xác nhận được bản vá trên dịch vụ.

## 4. Bằng chứng

- Các commit `211ab0f` và `fdbe499`: hiệu chỉnh v1 và phân tích baseline; `3b80d8f`: hiệu chỉnh v2 và phân tích v1; `54d010f`: làm rõ xác nhận gửi và phạm vi nhiệm vụ.
- [Báo cáo nhóm](group_report.md), [version log](../../starter_v0/artifacts/version_log.csv), [giả thuyết v10](review_evidence/v10_hypothesis.md).
- [Base v10](../../starter_v0/runs/v10_B_base_openai_20261111T112510357943.json), [group v10](../../starter_v0/runs/v10_B_group_openai_20261111T113036089399.json), [transcript gửi thật](../../starter_v0/transcripts/v10_openai_20261111T113930634960.transcript.json) và [kết quả pytest](review_evidence/pytest_v10_rebuilt.txt): 203 passed, 0 skipped, 0 failed.
- AI và cách kiểm tra: Codex hỗ trợ đọc yêu cầu và mã nguồn, phân tích log, hiệu chỉnh prompt và mô tả tool, chạy kiểm tra và biên tập báo cáo. Các kết quả được đối chiếu với run JSON, transcript, hash prompt/tool và output pytest; nội dung các bộ eval cố định được giữ nguyên.

## 5. Tự đánh giá

Qua việc đối chiếu log, em nhận thấy điểm eval cần được đọc cùng nội dung trả lời và kết quả thực thi tool: một case không gọi tool có thể vẫn trả lời sai phạm vi, còn một lượt gửi thành công chưa chứng minh agent luôn tuân thủ bước xác nhận. V10 giữ được điểm base và group của v8 trong các lượt đo đã thực hiện, nhưng chưa có phép đo lặp để kết luận về độ ổn định. Cơ chế gửi vẫn dựa trên giá trị `confirmed` do model cung cấp.
