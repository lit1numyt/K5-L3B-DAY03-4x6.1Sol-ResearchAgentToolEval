# Giả thuyết v10 — xác nhận nội dung Telegram

## Vấn đề và giả thuyết

Trong [hội thoại v8](../../../starter_v0/transcripts/v8_openai_20261111T095230010224.transcript.json), agent gọi `send` sau khi nhận nội dung, trước khi người dùng duyệt bản tin để đăng. Đồng ý chuẩn bị hoặc cung cấp nội dung chưa phải là xác nhận đăng bản tin đó.

H10: Nếu gắn việc duyệt với câu trả lời mới cho câu hỏi về nội dung cuối cùng, agent có thể tránh gửi sớm trong tình huống trên và giữ kết quả eval của v8.

## Thay đổi và kiểm chứng

Bản v10 dựa trên v8, làm rõ quy tắc duyệt trong prompt và mô tả tham số `send.confirmed`. Tên tool, mô tả `clarify`, schema, giá trị mặc định và code được giữ nguyên.

Kiểm tra R12, G03 và G04 cùng các tình huống cung cấp nội dung, từ chối và đồng ý. Sau đó chạy một lượt bộ base 20 case và bộ group chung 10 case bằng OpenAI gpt-4o-mini; giữ nguyên case và chặn `send` khi eval. Đối chiếu kết quả với v8 và kiểm tra thứ tự duyệt trong transcript. V8 vẫn là cấu hình mặc định; v10 được chọn bằng đường dẫn riêng.

## Kết quả

[Kiểm tra riêng](v10_restart_quick_check.json) đạt R12, G03 và G04; trong các lượt thử tương ứng, agent không đề xuất gửi khi từ chối và đề xuất đúng nội dung sau xác nhận. Nhánh từ chối vẫn hỏi người dùng có muốn cung cấp nội dung khác. Mỗi tình huống chỉ thử một lượt và không thực thi tool.

Bản v10 đạt **20/20 base và 10/10 group chung**; cả hai run đo đủ case, không lỗi provider và dùng cùng hash prompt/YAML. [Run base](../../../starter_v0/runs/v10_B_base_openai_20261111T112510357943.json), [run group](../../../starter_v0/runs/v10_B_group_openai_20261111T113036089399.json), [tổng hợp](v10_final_results.json) và [pytest](pytest_v10_rebuilt.txt) là bằng chứng; pytest đạt 203 passed, 0 skipped, 0 failed. Đã đối chiếu 30 input/expect với bộ eval giữ nguyên. Không chạy extension hoặc lặp nhiều lượt cho bản cuối.

Trong [lượt chat tắt gửi thật](../../../starter_v0/transcripts/v10_openai_20261111T112716781407.transcript.json), agent hỏi duyệt nội dung, chờ xác nhận rồi gọi `send` với đúng text và `confirmed=true`; [kết quả rà soát](v10_user_conversation_review.json) ghi nhận delivery bị tắt. Ở [lượt gửi thật tiếp theo](../../../starter_v0/transcripts/v10_openai_20261111T113930634960.transcript.json), agent hỏi duyệt nguyên văn, đợi người dùng xác nhận đăng rồi gọi `send`; tool trả `status: sent`. Lam xác nhận channel nhận tin là private; transcript không ghi loại channel. Một lượt gửi đúng và điểm eval không chứng minh model luôn tuân thủ quy trình.

SHA-256 prompt: `9157b3ea79d6afccffffb9390009a818a5bc339cd665b6cf1a161430557844c0`; tools: `2b96f76648302b4f53e61d61cbea237ebbd44075591f7739db531b064fe95b81`. Snapshot được lưu tại `starter_v0/artifacts/v10_candidates/rebuilt_20_of_20/`.
