# Giả thuyết v9 — ghi trước khi chạy

V9 hợp nhất commit `54d010f` của Nguyễn Đức Khương Lam vào nền v8 (`a794c7e`). H9: làm rõ việc duyệt đúng nội dung, duyệt lại sau sửa, dừng khi từ chối và giới hạn theo nhiệm vụ sẽ cải thiện cách diễn đạt ranh giới mà giữ được routing/arguments của v8. Phần này kế thừa giả thuyết H4 trong nhánh Lam; chỉ số phiên bản được đổi thành v9 để không trùng lịch sử nhóm.

Prompt giữ quy tắc arXiv, audit và bibliography của v8; nhận quy trình Telegram và quy tắc ngoài phạm vi từ Lam. YAML chỉ thay bốn mô tả tương ứng của clarify/send, giữ schema, mặc định và đủ 14 tool. Không sửa code tool, snapshot v0–v8, run cũ hoặc nội dung các bộ eval.

Chạy một lượt base 20 case và group hiện tại 10 case bằng OpenAI gpt-4o-mini, cùng snapshot v9. Tool gửi bị thay bằng stub; các tool đọc và model vẫn gọi thật. Chỉ dùng run đo đủ case và không lỗi provider. Kiểm tra thủ công actual_text ở R08/R14 và câu hỏi R12/G03/G04; điểm tự động chưa chứng minh toàn bộ luồng duyệt nội dung.

Quy tắc chọn mặc định, ghi trước chạy: chỉ chọn v9 nếu base 20/20, group 10/10 và không phát hiện vấn đề ranh giới trong phần review. Nếu có hồi quy, giữ v8 mặc định và lưu nguyên v9 như kết quả tích hợp chưa được chọn. Không chỉnh tiếp rồi chạy nhiều lần để chọn điểm đẹp. Điểm v8 không được gán lại cho v9. Các kiểm tra tương tác mô phỏng, nếu có, không được nhận là hành vi thật của model.
