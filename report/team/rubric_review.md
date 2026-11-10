# Rà soát rubric và quy tắc repo

Ngày: 10/11/2026 (GMT+7). Thành viên: Chu Nguyễn Tùng Dương — 2A202604016. Đây là biên bản bổ sung; báo cáo cá nhân/nhóm giữ nguyên khung của thầy.

## Kết luận hiện hành

V8 phát triển từ v4, thêm build_bibliography, có **20/20 base và 10/10 group chung** bằng OpenAI gpt-4o-mini. Đợt so sánh mới chạy nguyên một bộ 10 câu cho v4–v9, cùng model/evaluator/code tool; kết quả lần lượt 10/10, 10/10, 10/10, 9/10, 10/10 và 9/10. Tất cả đo đủ case và không lỗi provider. Các run dùng bộ khác không nằm trong bảng so sánh chính.

UI chạy trên Windows qua run.ps1 tại http://127.0.0.1:8000/, đã mở trong trình duyệt, chat thật gọi bibliography và saved run hiện PASS đúng. Có transcript CLI 4 lượt bằng API thật. Pytest: **200 passed, 0 skipped, 0 failed**. Tuy vậy chưa thể kết luận toàn bộ repo đủ mọi rules hoặc đủ 100 điểm.

Nhánh Lam được hợp nhất từ commit 54d010f và lưu thành v9. Base v9 đạt 19/20; group chung đạt 9/10, nên mặc định vẫn là v8. Pytest sau khi cố định bộ chung: 200 passed, 0 skipped, 0 failed. Xem [H9](review_evidence/v9_hypothesis.md), [biên bản hợp nhất](review_evidence/merge_v9_review.json), [protocol chung](review_evidence/common_group_comparison.json) và [pytest](review_evidence/pytest_tools_complete.txt).

## Từng phiên bản

| Bản | Base | Group chung v4–v9 | Lập luận từ prompt/tool YAML và run |
|---|---:|---:|---|
| v0 | 13/20 | — | Prompt bảo đoán account/URL và gửi ngay; description mơ hồ. Chỉ dùng làm baseline. |
| v1 | 17/20 | — | Bỏ đoán, thêm clarify/xác nhận, quy ước lookup args; hỏi thừa R01/R05; R12 lệch response_type. No_tool không ngăn việc vẫn trả lời ngoài phạm vi ở R08/R14. |
| v2 | 18/20 | — | Phân biệt dữ liệu thiết yếu với tùy chọn và thao tác đọc; M06 hồi quy, R12 vẫn lệch oracle. |
| v3 (v2-tool cũ) | 19/20 | — | Thêm research_paper, nhưng base không gọi tool này; không quy tăng điểm riêng cho tool mới. |
| v4 (v3 cũ) | 20/20 | 10/10 | Tách ý định chuẩn bị và duyệt nội dung; audit/alias. Run bộ cũ giữ trong history. |
| v5 | 19/20 | 10/10 | Hoàn thiện contract/routing/evidence nhưng R10 đoán tài khoản. |
| v6 | 17/20 | 10/10 | Ràng buộc missing account gây hỏi thừa R01; R11 bỏ response_type; R12 lệch kiểu hỏi. |
| v7 ban đầu | 18/20 | — | Run group lịch sử 9/10 ở candidates, không phải snapshot H7A trong phép so sánh chung. |
| v7 H7A | 18/20 | 9/10 | Giả thuyết ghi trước chạy, dùng bảng quyết định/ví dụ đối chiếu; phát sinh gọi thêm social_search M02/M06 và sai route/args G06. Không đạt mục tiêu. |
| v8, từ v4 | 20/20 | 10/10 | Thêm bibliography có test/routing riêng; phép so sánh chung vẫn giữ G05 audit. |
| v9, hợp nhất Lam vào v8 | 19/20 | 9/10 | R12 base dùng text thay yes_no; G04 group thử gửi khi chưa duyệt và đã bị chặn. R08/R14 vẫn trả lời ngoài phạm vi dù no_tool PASS. |

Xem version_log.csv và [số đo thật](review_evidence/version_summary.json). V8 lấy metric_before từ nhánh v4 (1.00), không từ v7 (0.90). Các vòng cùng thay prompt/description chỉ cho kết luận về cả cấu hình, không chứng minh tác động riêng từng câu. Một lượt 20/20 không chứng minh model ổn định ngoài suite/qua lần chạy khác.

V9 giữ schema/mặc định, đủ 14 tool và toàn bộ dữ liệu eval; chỉ hợp nhất prompt cùng bốn mô tả clarify/send. Đóng góp của Lam được giữ bằng merge có hai parent, không squash hay đổi tác giả commit. Việc v9 có hồi quy và lỗi nội dung cho thấy H9 chưa được hỗ trợ trong lần đo này; không dùng kết quả v8 để nhận thay cho v9. Báo cáo nhóm giữ khung hiện hành, nhận phân tích của Lam và cập nhật link v2-tool cũ sang tên run v3. Báo cáo cá nhân/nhận xét riêng của các thành viên khác vẫn để họ tự điền.

Các file run đổi tên nhưng giữ nguyên byte JSON; metadata version/run_id/artifact_version và đường dẫn nguồn bên trong có thể là tên cũ. v3 còn nhãn v2-tool, v4 gốc còn nhãn v3, v5/v6/v7 ban đầu còn nhãn v4. Hash và manifest giải thích ánh xạ. 19 run thăm dò đã xóa theo yêu cầu rõ ràng; không dùng chúng làm evidence. Các run chính và hồi quy vẫn còn.

## Bộ 10 câu nhóm

Bộ chính nằm trong data/eval_group.json, giữ nguyên byte của artifacts/eval_group_v4_reviewed.json: đúng 10 case, 5 single và 5 multi. Cả sáu cấu hình v4–v9 đã chạy lại trên cùng bộ này, không thay G05 theo phiên bản. Protocol ghi SHA-256 dataset/evaluator, hash snapshot, run JSON và đối chiếu tất cả input/expect của 60 kết quả với bộ cố định.

- Single: G01 kiểm tra rỗng/lỗi; G03 thiếu nội dung sau đồng ý chuẩn bị; G05 audit URL trùng; G06 đọc paper phân tích hạn chế; G07 giải thích giới hạn audit.
- Multi: G02 nhận kết quả rồi audit; G04 có nội dung nhưng chưa duyệt đăng; G08 giữ chủ đề/năm khi thêm tác giả; G09 giữ chủ đề và phân trang; G10 audit kết quả đã có trong ngữ cảnh.
- G01/G02/G05/G10 chấm đúng payload results, G08/G09 chấm cả query. G03 khác R12 vì đã đồng ý chuẩn bị; không đổi oracle base.
- V7 sai G06 vì paper_text không nhận include_text. V9 sai G04 vì send chưa được duyệt; stub ngăn gửi thật. Routing PASS không thay kiểm tra final answer hoặc luồng duyệt nhiều lượt.

Trước đợt đo chung, G05 từng bị thay bằng bibliography ở v8. Các run đó được lưu trong runs/history/bibliography_suite cùng fixture, dùng riêng để kiểm chứng tool mới. Các run group trước đợt đo chung ở history/reviewed_suite và history/v4_original_suite; không trộn chúng vào bảng so sánh chính. Việc lưu lịch sử không đồng nghĩa coi các dataset là cùng phép đo.

Đây là bộ phát triển đã được dùng khi chỉnh prompt, không phải dữ liệu kiểm tra chưa từng thấy. Mỗi snapshot chỉ chạy một lượt trong đợt chung; dữ liệu API ngoài vẫn có thể thay đổi. Multi-turn đóng gói ngữ cảnh ba lượt và chấm lượt cuối; tool_choice=required khi kỳ vọng có tool, chưa phải live chat đầu-cuối. Không sửa case cố định trong eval_base/eval_research_extension.

Evaluator từng sorted list object gây TypeError. Phần chuẩn hóa dict/list object và regression test được giữ nguyên cho toàn bộ đợt đo; không nới matcher hoặc sửa expected args để tăng điểm.

## Tool mới và tác giả đóng góp

C4 bắt buộc ít nhất một tool mới của nhóm: tool.py, TOOL.md, đăng ký registry/YAML, ≥3 test và eval routing. Repo đã có research_paper/audit_research_evidence khi phiên này bắt đầu; không nhận chúng là mới viết từ đầu trong phiên hoặc là tác phẩm riêng của Dương.

- **build_bibliography** thực sự thêm mới ở v8 trong phiên Codex hỗ trợ: BibTeX/plain từ metadata có thật, title/URL bắt buộc, tác giả/năm chỉ dùng nếu có, cảnh báo trường thiếu, bỏ nguồn trùng, URL lỗi/input sai trả error dict. Có **16 test** (9 trong file TODO bắt buộc, 7 trong test_tools_regression.py) và G05 của bộ bibliography bổ sung route tới tool. Không search/fact-check, không key/side effect.
- research_paper được bổ sung validate kiểu/khoảng và error handling, giữ paper khi PDF lỗi; **14 test**.
- audit_research_evidence được xử lý input thiếu, test empty/error/partial/duplicate; **10 test** (3 trong TODO + 7 riêng).
- arxiv_search là alias của papers, không tính tool mới. Tool metadata được sửa enum, local_file_write và action confirmation; contract test kiểm tra mạnh hơn.

## UI và live chat theo C6

Đã sửa saved-run adapter (raw run từng làm frontend hiện FAIL giả), tên phiên bản theo file/nhãn gốc, lọc fixture, trạng thái tool_called, lỗi HTTP, danh sách Markdown và launcher Windows. Adapter UI cũ đã bỏ imports placeholder, delegate agent thật. Có **12 test UI/loop**, đã kiểm tra trình duyệt thật; ảnh trong review_evidence và hướng dẫn docs/UI.md.

Transcript v8 có 4 prompt kịch bản, provider/tool đọc chạy thật, không phải hội thoại con người được bịa lại: policy; thiếu tài khoản; bổ sung sama và lấy 2 bài thật; yêu cầu Telegram. Delivery bị tắt bằng --disable-send và được ghi metadata. Model hỏi text trực tiếp ở lượt 2/4, không gọi clarify; báo cáo giữ nguyên trace, không nhận là đã kiểm chứng trạng thái waiting đầu-cuối. Policy lượt 1 không tìm thấy đoạn phù hợp, không bịa là đã có nguồn.

Link localhost chứng minh UI local chạy, không thay public/demo URL. Chưa deploy/tunnel public trong phiên; để phần đó cho người phụ trách bổ sung. README Scope nêu Streamlit/Vercel trong khi CP5 cho phép UI khác; rubric C6 chấm chạy được theo hướng dẫn. Nếu coach bắt buộc framework cụ thể, cần xác nhận với coach, không tự tuyên bố FastAPI đáp ứng điều kiện đó.

## Đối chiếu C1–C8

| Tiêu chí | Có | Còn thiếu/giới hạn |
|---|---|---|
| C1, 10 điểm | v0 hợp lệ, hash/snapshot, 7 lỗi B2 | Chưa lưu preflight riêng; không tự chấm thay thầy. |
| C2, 15 điểm | 14 tên tool v8, routing/boundary, contract test xanh | Thừa hưởng một số description mơ hồ/trust boundary chưa đầy đủ của v4; G04 cần review nguyên văn. Chưa nhận đủ C2. |
| C3, 20 điểm | Đủ v0–v3, v4–v9 bổ sung, hash/run/metric/hypothesis | Rubric không bắt tăng điểm mỗi vòng; phải ghi đúng hồi quy. Một số vòng thay nhiều thứ. |
| C4, 15 điểm | Tool mới v8 đủ code/TOOL.md/registry/YAML, 16 test; ≥3 test hai tool nhóm khác; 0 failed | Không tính alias là tool mới hoặc nhận code cũ là mới viết. |
| C5, 10 điểm | Một bộ cố định 5/5, sáu run v4–v9 hợp lệ; routing bibliography kiểm tra riêng | Chưa chấm đủ final answer/injection/luồng tương tác; bộ phát triển, không phải holdout. |
| C6, 10 điểm | UI local, lệnh chạy, browser verification, transcript API thật 4 lượt | Thiếu public URL; model hỏi text chưa dùng clarify trong demo. Không dùng ảnh thay transcript. |
| C7, 10 điểm | Báo cáo đúng khung, link evidence thật | Phần A trước 16:30 chưa có bằng chứng; phần deployment/thành viên khác chừa trống. |
| C8, 10 điểm | Báo cáo đúng tên Dương, commit kỹ thuật thật; thay đổi v8 lưu trên main | Thành viên khác tự điền TEAM/báo cáo. |

Test challenge đáp ứng điều kiện 0 skipped và có regression sửa bug send: chỉ boolean True mới cho phép HTTP, chuỗi/số truthy không được coi là xác nhận. Toàn suite 200 passed, 0 skipped, 0 failed; xem test_tools_regression.py và pytest_tools_complete.txt. Theo rubric, phần này là 1 điểm bonus tách riêng. Các bonus khác chưa có đủ bằng chứng: chỉ 3 tool nhóm mới, chưa có 2 model local hoặc gửi Telegram thật.

## Benchmark arXiv bổ sung

Đã xem rubric riêng và sample_5single_5multi_seed20261110: 5 câu đơn + 5 cặp hai lượt = **15 lượt**, schema khác, không thay C5. Manifest ghi các cặp ghép từ câu độc lập, không phải hội thoại bắt buộc dùng ngữ cảnh được thiết kế riêng. Single đạt 2/5 case, 34/50 điểm, một CF06; multi 7/10 lượt, 76/100 điểm, 0 critical failure. Log có timeout/429 và ghi chú bỏ chấm params dù trace có field đó; người phụ trách cần kiểm tra cơ chế xác định schema trước khi kết luận. Không sửa phần benchmark riêng của họ.

## Quy tắc và giới hạn cuối

Không đổi case cố định, tạo metric/transcript/commit giả, force-push hay sửa ngày. Không in key. Không thấy .env/.venv/arxiv_papers được Git theo dõi; kiểm tra này không thay quét toàn lịch sử trước khi nộp. Thay đổi được lưu trên nhánh nộp main; xem mốc commit trong [TEAM.md](../../TEAM.md).

Sau đợt group, guard kiểu confirmed của send được siết thành boolean True và có regression. Việc này không đổi model routing, dataset hoặc kết quả sáu run vì tất cả đã dùng stub send; không cần chạy lại để tìm điểm cao hơn. Toàn bộ 14 test TODO đã được hoàn thiện; papers/arxiv_search và paper_text có test metadata, filters, lỗi tải/đọc PDF và giới hạn excerpt. Không coi số test là bằng chứng đã phủ mọi nhánh.

Eval chặn send và UI mặc định tắt delivery. Khi bật gửi, code vẫn tin confirmed do model cấp; chưa có state duyệt nguyên văn độc lập. Các smoke test audit cũ có mô phỏng và chưa chứng minh vòng chat luôn audit rỗng/lỗi. Điểm 20/20 và 10/10 là kết quả suite, không phải bảo đảm toàn agent hoàn hảo hoặc đủ mọi rules.
