# Giả thuyết v7, lần thử A — ghi trước khi chạy

Ngày: 10/11/2026 (GMT+7).

Bằng chứng đầu vào: v7 ban đầu base 18/20, group 9/10. R10 gọi social_search với query rỗng thay vì hỏi ai; R13 đưa từ loại tin vào query; G04 gọi send khi chưa có câu hỏi duyệt nguyên văn và lời đồng ý tiếp theo.

H7A: Một bảng quyết định có thứ tự cùng các ví dụ đối chiếu tổng quát trong system prompt sẽ giúp model áp dụng ranh giới còn mơ hồ: thiếu tài khoản/chủ đề phải hỏi, tách chủ đề khỏi loại tin, và phân biệt lặp yêu cầu với duyệt nội dung. Tool description/schema củng cố cùng hợp đồng, gồm response_type bắt buộc và query social không rỗng.

Không dùng case ID, đáp án chứa tài khoản mẫu của base hoặc sửa oracle. Ví dụ dùng chủ đề và handle khác bộ eval. Không đổi provider/model hoặc code evaluator trong lần thử này.

Đạt kỳ vọng khi cùng một hash prompt/YAML có base 20/20 và group đã siết 10/10, đủ measured, 0 provider error. Đây là mục tiêu chứ chưa phải kết quả. Nếu không đạt, ghi nguyên thất bại. Một run đạt không có nghĩa agent hoàn hảo ngoài suite.

Provider/model: OpenAI gpt-4o-mini. Chạy qua script chặn send, các tool đọc vẫn thật. Các run cũ và snapshot v7 ban đầu được giữ ở thư mục candidates.
