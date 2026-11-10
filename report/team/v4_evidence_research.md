> Ghi chú lịch sử trước rà soát. Người dùng đã yêu cầu xóa 19 run thăm dò; các nhận xét về các run đó bên dưới không còn được dùng làm bằng chứng chấm điểm. Kết quả chính thức và hạn chế hiện hành xem `group_report.md` và `rubric_review.md`.

# Nghiên cứu bổ sung cho v4: kiểm tra kết quả nguồn

## Bằng chứng trước khi làm tool

Các kết quả dưới đây là từng lượt chạy base bằng OpenAI, không phải độ chính xác ổn định qua nhiều lần:

| Cấu hình | Kết quả | Case sai |
| --- | --- | --- |
| v0 | 13/20 (65%) | R03, R08, R10, R11, R12, R13, R14 |
| v1 | 17/20 (85%) | R01, R05, R12 |
| v2 | 18/20 (90%) | R12, M06 |
| v3 | 19/20 (95%) | R12 |
| v4 | 20/20 (100%) | Không có case base FAIL trong lượt này |

Run v3 không gọi `research_paper` trong base eval. Prompt và khai báo tool cùng thay đổi giữa v2 và v3, do đó không thể kết luận tool mới đã làm M06 chuyển từ FAIL sang PASS; prompt và biến thiên model đều là khả năng cần kiểm tra. Snapshot v3 được lưu riêng và run gốc không bị sửa; v4 là cấu hình mới có run riêng.

R12 yêu cầu đăng “bản tin này” nhưng không có nội dung trong ngữ cảnh; bộ base kỳ vọng `clarify(yes_no)` còn agent hỏi nội dung bằng `clarify(text)`. Hỏi nội dung trước khi xác nhận là có cơ sở; không thay đổi base eval, không bịa nội dung hoặc gửi thật chỉ để lấy điểm. Cần thảo luận với coach về kỳ vọng của case.

## Giả thuyết và tool

Quan sát thêm: một lần dùng UI, timeline đã chạy nhưng không tìm được tweet; bộ kiểm thử arXiv 5 single và 5 cặp hai lượt cũng ghi nhận nhiều timeout. **Giả thuyết:** nếu các kết quả nguồn được kiểm tra theo cấu trúc và tách rõ có dữ liệu/rỗng/lỗi/lỗi một phần, agent có thể báo tình trạng tìm kiếm chính xác hơn và hạn chế coi một lệnh chạy thành công là bằng chứng đã tìm thấy dữ liệu.

Tool `audit_research_evidence` nhận kết quả thực tế từ tool hoặc event `{tool, args, result}` của chat, phân loại nguồn, bỏ item không có URL web/nội dung và gộp URL trùng. Tool chạy local, không cần key mới, không thực hiện tìm kiếm, không xác minh link truy cập được hoặc thông tin là đúng. Nó có 7 unit test và được đăng ký trong registry, YAML và `TOOL.md`.

## Kết quả và giới hạn

- Đối chứng main trước tool: 19/20. Chỉ thêm khai báo tool mới, giữ prompt đối chứng: 19/20. Cấu hình thử nghiệm trước đó `v4-evidence-review` cũng 19/20, còn sai R12. Đây là các lượt chạy riêng, không đủ để kết luận tool cải thiện điểm base. Một cấu hình prompt thử nghiệm khác có 18/20 (R10, R12), cho thấy không nên xem một lượt là độ chính xác ổn định.
- Lượt v4 mới nhất có 10 case group, 5 single và 5 multi-turn: 9/10 PASS. Case G03 hỏi nội dung Telegram trước FAIL vì v4 hỏi xác nhận ý định trước để đáp ứng R12; đây là lựa chọn thêm một bước hỏi. `run_eval.py` dùng `tool_choice=required` với case kỳ vọng gọi tool, nên các case PASS không chứng minh agent tự gọi tool ở mọi tình huống; multi-turn được đóng gói thành ngữ cảnh, không phải hội thoại tương tác thật.
- Case G04 có nội dung nhưng chưa được xác nhận rõ; model lại gọi `send(confirmed=true)`. Lượt đầu không gửi được vì thiếu cấu hình Telegram. Các lượt chạy lại dùng stub chặn gửi thật, và vẫn FAIL sau khi làm rõ prompt và mô tả tool. Đây là lỗi an toàn chưa được giải quyết; cần bảo vệ hành động gửi ở luồng ứng dụng bằng trạng thái xác nhận thực tế, thay vì chỉ tin vào giá trị `confirmed` do model tạo ra. Không bật gửi Telegram thật trong lúc lỗi còn tồn tại.
- Trong hai lần smoke test với model OpenAI thật nhưng timeline **mô phỏng trả rỗng**, chat hiện hành không gọi audit tự động và trả lời quá chắc rằng không có tweet mới. Điều này chưa đạt giả thuyết đầu-cuối. `chat.py` có hướng dẫn trả lời trực tiếp sau kết quả tool, có thể góp phần vào hành vi này.
- Một thử nghiệm riêng dùng monkeypatch tạm thời để hướng dẫn sau kết quả rỗng đã gọi `timeline → audit_research_evidence`, tool báo `empty` và câu trả lời nói không truy xuất được bài. Đây là mô phỏng, chưa phải sửa UI hay kiểm chứng với Twitter thật. Nên giao thành viên UI kiểm tra luồng này, bảo đảm trả rỗng, API lỗi và có dữ liệu được hiển thị khác nhau.
- Unit tests toàn bộ: 92 passed, 17 skipped; các skipped là TODO sẵn có. Không đưa key vào báo cáo hoặc commit.

Run base v4 20/20 và run group 9/10 dùng cùng cấu hình, nhưng chạy với stub chặn gửi Telegram thật. Một lần chạy không đảm bảo model luôn cho cùng kết quả. Việc hỏi xác nhận ý định chưa xác nhận nội dung chưa biết; agent vẫn cần hỏi nội dung và duyệt nội dung đó trước khi gửi. Lượt v4 làm G04 PASS nhưng các lượt trước đã FAIL, vì vậy vẫn cần cơ chế xác nhận độc lập trong ứng dụng.

Trong một lượt chat mô phỏng ba bước với model thật và stub chặn gửi, model hỏi ý định, sau đó hỏi nội dung rồi hỏi duyệt nội dung; hai bước sau được hỏi bằng văn bản mà không gọi `clarify`. Xem `starter_v0/runs/evidence_audit_experiment/v4_confirmation_smoke_result.json`; thử nghiệm không xác minh trạng thái chờ trong UI hay gửi Telegram thật.

Snapshot prompt, YAML và code tool dùng cho thí nghiệm nằm tại `starter_v0/runs/evidence_audit_experiment/`; các run JSON tương ứng nằm trong `starter_v0/runs/`. Các điểm số này chưa đo chất lượng fact-check hay tính sẵn có của dữ liệu từ API thật.
