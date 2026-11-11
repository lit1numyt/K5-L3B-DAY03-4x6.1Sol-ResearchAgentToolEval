# Báo cáo cá nhân — Đồng Hữu Nguyên Khoa

## 1. Thông tin thành viên

- Họ tên: Đồng Hữu Nguyên Khoa — nhóm 4x6.1Sol, lớp L3B
- MSSV: 2A202604000
- Email: 26ai.khoadhn@vinuni.edu.vn

## 2. Phần việc phụ trách

Phần việc của em tập trung vào phát triển giao diện người dùng cho chatbot, xây dựng công cụ tìm kiếm bài báo khoa học trên arXiv tích hợp với agent thông qua cơ chế function calling, và thiết kế bộ test để kiểm tra khả năng sử dụng tool của agent. Bên cạnh phần triển khai kỹ thuật, em cũng tham gia thảo luận, định hướng và điều phối các thay đổi trong nhóm liên quan đến agent guardrail và prompt engineering nhằm cải thiện độ chính xác, tính nhất quán trong quá trình xử lý yêu cầu của chatbot.

## 3. Đóng góp cụ thể

Em trực tiếp phát triển phần giao diện người dùng (UI) cho chatbot, tập trung vào việc xây dựng các thành phần giao tiếp giữa người dùng và agent, hỗ trợ quá trình nhập yêu cầu và hiển thị phản hồi. Phần triển khai được lưu trong thư mục `research-chatbot-ui` và `starter_v0/app`.

Đối với chức năng tìm kiếm tài liệu khoa học, em phát triển công cụ **arXiv Search** dưới dạng function calling để agent có thể chủ động truy vấn và lấy thông tin từ kho bài báo arXiv khi nhận được yêu cầu phù hợp. Công cụ này giúp mở rộng khả năng tra cứu tài liệu học thuật của chatbot, thay vì chỉ giới hạn ở kiến thức có sẵn trong model. Em phụ trách triển khai phần tool và tích hợp cơ chế gọi công cụ với agent.

Để kiểm tra độ chính xác của chức năng tool calling, em xây dựng bộ kiểm thử gồm **20 test case single-turn và 10 test case multi-turn**. Các test case được thiết kế để kiểm tra khả năng nhận diện ý định tìm kiếm, lựa chọn và gọi đúng tool, xử lý tham số đầu vào cũng như duy trì ngữ cảnh khi yêu cầu tìm kiếm được tiếp nối qua nhiều lượt hội thoại. Bộ kiểm thử được lưu trong `starter_v0/arxiv-function-test`.

Ngoài các phần triển khai trực tiếp, em tham gia thảo luận và điều phối hướng phát triển của nhóm đối với cơ chế **agent guardrail**. Trong quá trình làm việc, em cùng các thành viên trao đổi về những trường hợp agent có thể đưa ra phản hồi thiếu chính xác, lựa chọn tool chưa phù hợp hoặc xử lý yêu cầu chưa đúng phạm vi. Từ đó, nhóm xem xét điều chỉnh prompt và bổ sung các nguyên tắc kiểm soát hành vi của agent nhằm cải thiện độ tin cậy và độ chính xác của kết quả trả về.

Bên cạnh đó, em cũng tham gia định hướng các thay đổi về prompting, trao đổi với các thành viên để thống nhất cách tiếp cận và phân chia công việc trong quá trình cải thiện agent. Mục tiêu là không chỉ làm cho chatbot có khả năng gọi tool mà còn đảm bảo agent hiểu đúng yêu cầu, sử dụng công cụ đúng thời điểm và tổng hợp kết quả phù hợp với ngữ cảnh hội thoại.

## 4. Bằng chứng

- File/commit/PR:
  - `research-chatbot-ui/`: Phần giao diện chatbot do em phát triển.
  - `starter_v0/app/`: Các thành phần ứng dụng liên quan đến giao diện và triển khai chatbot.
  - `starter_v0/arxiv-function-test/`: Bộ 20 test case single-turn và 10 test case multi-turn cho chức năng arXiv tool calling.
  - `requirements.txt`: Các thư viện và dependency phục vụ quá trình triển khai.

- AI/công cụ đã dùng và cách tự kiểm tra kết quả:
  - Sử dụng các công cụ AI hỗ trợ quá trình phát triển, đọc và chỉnh sửa code.
  - Kiểm tra chức năng tìm kiếm arXiv thông qua các test case đã xây dựng, tập trung vào khả năng nhận diện yêu cầu và lựa chọn tool của agent.
  - Kiểm tra giao diện chatbot trong quá trình triển khai và tích hợp với phần xử lý của agent.
  - Các nội dung thảo luận về guardrail và prompting được thực hiện trong quá trình phối hợp với các thành viên trong nhóm.

## 5. Tự đánh giá

Trong quá trình thực hiện bài lab, em đã hai thành phần quan trọng của sản phẩm là giao diện chatbot và chức năng tìm kiếm bài báo khoa học thông qua tool calling. Bên cạnh đó, việc xây dựng bộ test riêng cho arXiv giúp em hiểu rõ hơn cách đánh giá một agent sử dụng công cụ, đặc biệt là sự khác biệt giữa khả năng trả lời thông thường và khả năng lựa chọn, sử dụng tool đúng với yêu cầu của người dùng.

Em cũng nhận thấy rằng việc xây dựng một agent không chỉ dừng lại ở việc tích hợp LLM và các công cụ bên ngoài. Chất lượng của agent còn phụ thuộc đáng kể vào cách thiết kế prompt, cơ chế kiểm soát hành vi và khả năng xử lý những tình huống không nằm trong luồng sử dụng thông thường. Qua quá trình thảo luận về guardrail và prompting, em hiểu rõ hơn tầm quan trọng của việc phối hợp giữa các thành viên để thống nhất hướng phát triển, thay vì chỉ tập trung tối ưu từng thành phần riêng lẻ.

Một kinh nghiệm quan trọng em rút ra là cần kiểm thử chức năng tool calling bằng cả single-turn và multi-turn. Một agent có thể lựa chọn đúng công cụ trong một câu hỏi độc lập nhưng vẫn gặp khó khăn khi phải duy trì ngữ cảnh qua nhiều lượt hội thoại. Vì vậy, việc xây dựng các tình huống kiểm thử có hệ thống là cần thiết để đánh giá hành vi thực tế của agent.

Nhìn chung, bài lab giúp em cải thiện kỹ năng phát triển ứng dụng tích hợp LLM, thiết kế function calling, kiểm thử agent và phối hợp phát triển sản phẩm theo nhóm. Trong các lần triển khai tiếp theo, em muốn chú trọng hơn vào việc chuẩn hóa bộ đánh giá, đo lường kết quả trước và sau mỗi lần thay đổi prompt, đồng thời cải thiện cơ chế guardrail để đảm bảo agent hoạt động chính xác và ổn định hơn. Ngoài ra, em thấy em cần chú ý hơn đến lab requirements và hạn chế bị phình scope of work.