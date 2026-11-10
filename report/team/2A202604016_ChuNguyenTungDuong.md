# Báo cáo cá nhân — Chu Nguyễn Tùng Dương-2A202604016

## 1. Thông tin thành viên

- Họ tên: Chu Nguyễn Tùng Dương — nhóm 4x6.1Sol, lớp L3B
- MSSV: 2A202604016
- Email:

## 2. Phần việc phụ trách

Phần việc của tôi tập trung vào chạy và lưu eval, theo dõi các phiên bản, đối chiếu lỗi với prompt và mô tả tool, rồi tổng hợp bằng chứng vào báo cáo. Ở phần bổ sung v8, tôi sử dụng Codex để hỗ trợ thêm tool bibliography, test và sửa UI.

Tôi chỉ ghi các đóng góp có thể đối chiếu với file hoặc commit. Phần hiệu chỉnh v2 đã ghi nhận cho Nguyễn Đức Khương Lam trong báo cáo nhóm; code UI và hai tool research_paper/audit đã có trước lần rà soát này không được nhận là do tôi viết mới.

## 3. Đóng góp cụ thể

Các commit 341c4ce, b7691c0, 2aaa3cb và c17dc2e lưu kết quả v0, v1, v2 và cấu hình có research_paper. Kết quả base lần lượt là 13/20, 17/20, 18/20 và 19/20. Bản v2-tool được đổi tên thành v3, còn v3 cũ thành v4; nội dung JSON gốc được giữ nguyên.

Khi phân tích, tôi đối chiếu cả cách model chọn tool và dữ liệu trả về. V0 đoán tài khoản/URL và dùng send sai mục đích. V1 giảm được các lỗi đó nhưng hỏi thừa, còn v2 có hồi quy ở M06. Đây là cơ sở để giải thích vì sao prompt cần phân biệt thông tin thực sự còn thiếu với tham số có thể dùng mặc định. Điểm no_tool cũng chưa đủ: ở v1, model vẫn trả lời ngoài phạm vi sau câu từ chối.

V4 có run base 20/20. Các thử nghiệm v5–v7 sau đó không tăng đều, nên được giữ là kết quả chưa thành công. V8 quay lại nền v4 và thử một giả thuyết hẹp hơn: thêm build_bibliography cho yêu cầu xuất tài liệu tham khảo. Tool chỉ dùng metadata đã có, cảnh báo tác giả/năm còn thiếu, kiểm tra URL và trả lỗi thay vì bịa dữ liệu. Nó có TOOL.md, registry/YAML, 9 test và một case trong bộ nhóm vẫn giữ đúng 5 single + 5 multi.

Hai run mới của v8 đạt **20/20 base và 10/10 group**, cùng hash prompt/YAML, đo đủ case và không lỗi provider. Bộ group đã thay đổi để kiểm tra tool mới; tôi không dùng chênh lệch điểm giữa các bộ group như bằng chứng model tiến bộ trên cùng phép đo.

Tôi hợp nhất phần hiệu chỉnh của Nguyễn Đức Khương Lam ở commit 54d010f vào nền v8 và lưu thành snapshot v9. Công việc của tôi là xử lý ba conflict, giữ phần audit/bibliography và khung báo cáo, rồi kiểm chứng cấu hình hợp nhất bằng Codex. Quy tắc duyệt lại nội dung gửi và từ chối theo phạm vi nhiệm vụ được ghi nhận cho Lam; tôi không nhận đó là phần mình viết mới. V9 đo riêng đạt 19/20 base và 9/10 group, không lỗi provider; R12 hỏi khác kiểu kỳ vọng, G04 gọi send khi chưa duyệt và đã bị stub chặn. R08/R14 vẫn trả lời ngoài phạm vi dù được chấm PASS vì không gọi tool. Tôi giữ v8 làm mặc định theo tiêu chí đã ghi trước khi chạy; điểm v8 được giữ riêng, không gán cho v9.

UI được sửa cách đọc run đã lưu, trạng thái tool, thông báo lỗi và lệnh chạy Windows. Kiểm tra bằng trình duyệt cho thấy chat thật gọi được bibliography và saved run hiện PASS đúng. Demo CLI có 4 lượt bằng API thật; Telegram bị tắt. Ở lượt thiếu tài khoản và yêu cầu đăng, model hỏi bằng text thay vì gọi clarify, nên báo cáo ghi đúng hạn chế này.

## 4. Bằng chứng

- File/commit/PR:
  - 341c4ce: baseline v0; b7691c0: kết quả v1; 2aaa3cb: v2 và snapshot; c17dc2e: cấu hình paper và run nay mang tên v3.
  - [Version log](../../starter_v0/artifacts/version_log.csv), [báo cáo nhóm](group_report.md), [giả thuyết H8](review_evidence/v8_hypothesis.md), [giả thuyết H9](review_evidence/v9_hypothesis.md) và [biên bản hợp nhất](review_evidence/merge_v9_review.json).
  - [Tool mới](../../starter_v0/tools/build_bibliography/tool.py), [unit test](../../starter_v0/tests/test_tools_todo.py), [output pytest sau hợp nhất](review_evidence/pytest_v9.txt): **130 passed, 14 skipped, 0 failed**.
  - [Base v8](../../starter_v0/runs/v8_B_base_openai_20261110T223125274893.json), [group v8](../../starter_v0/runs/v8_B_group_openai_20261110T223032240551.json), [transcript 4 lượt](../../starter_v0/transcripts/v8_openai_20261110T223458159061.transcript.json) và [UI docs](../../docs/UI.md).
  - [Base v9](../../starter_v0/runs/v9_B_base_openai_20261110T230751104659.json), [group v9](../../starter_v0/runs/v9_B_group_openai_20261110T230818905094.json) và [commit hiệu chỉnh của Lam](https://github.com/lit1numyt/K5-L3B-DAY03-4x6.1Sol-ResearchAgentToolEval/commit/54d010f4b233f763b3d5b51eb8a10e794595f14d).
  - Phần bổ sung v8, lần hợp nhất v9, UI và báo cáo được lưu trên nhánh nộp `main`; mốc commit ghi trong [TEAM.md](../../TEAM.md).
- AI/công cụ đã dùng và cách tự kiểm tra kết quả:
  - Codex hỗ trợ đọc repo, viết code/test, phân tích và biên tập báo cáo. Các bước kiểm tra gồm so hash với run, chạy pytest trong .venv, chạy API thật và thử UI trong trình duyệt. Hai bộ eval cố định của thầy được giữ nguyên.
  - Tool đọc và provider trong demo chạy thật; send bị chặn. Không dùng dữ liệu mô phỏng để nhận là đã gửi Telegram hoặc đã có một phiên chat của con người. Tôi cần tự đọc và giải thích được các thay đổi khi bảo vệ bài.

## 5. Tự đánh giá

Phần baseline, versioning, tool mới v8 và kiểm tra UI đã có bằng chứng để đối chiếu. V8 giữ được điểm base của v4 trong lượt đo này, nhưng chưa chứng minh độ ổn định ở mọi lần chạy. V9 cũng chưa đạt tiêu chí chọn làm mặc định. Các vòng có hồi quy cho thấy không nên coi việc viết prompt dài và chi tiết hơn là chắc chắn tốt hơn.

Phần còn thiếu là public URL, bằng chứng trạng thái clarify đầu-cuối và cơ chế duyệt nội dung độc lập với model khi gửi thật. Thông tin các thành viên khác cũng cần được hoàn thiện trước khi nộp. Tôi không nhận các phần này là đã xong.

Nhận xét trải nghiệm cá nhân sau khi tự đọc và chạy lại: [Tự điền].
