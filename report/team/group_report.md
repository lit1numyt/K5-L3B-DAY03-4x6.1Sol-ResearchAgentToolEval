# Báo cáo nhóm — Day 03 Research Agent Tool Eval

> Báo cáo gồm 2 phần có hạn khác nhau:
> - **Phần A (mục 2)** — giới thiệu agent, ngắn gọn 1 trang. **Xong trước Team showdown (16:30)** để team khác hiểu nhanh agent có tool gì, làm được gì. Có thể làm thêm poster `report/team/poster.html` hoặc `poster.svg`.
> - **Phần B (mục 3–7)** — chi tiết và bằng chứng, dựa trên log thật. Hoàn thiện trước deadline nộp bài.
>
> Mỗi bảng phải trỏ được tới file thật: run JSON, transcript, commit. Cách chấm xem [RUBRIC.md](../../RUBRIC.md).

## 1. Thông tin nhóm

- Tên nhóm: 4x6.1Sol — Lớp: L3B
- Thành viên và phân công: xem [TEAM.md](../../TEAM.md).
- Provider/model dùng cho v0–v3: OpenAI / gpt-4o-mini. Các bản v4–v9 cũng dùng model này. Bản đang chạy là **v8**, phát triển từ v4; v4 gốc được giữ nguyên. V9 là cấu hình hợp nhất phần sửa của Lam, đã đo riêng nhưng chưa được chọn làm mặc định.

Trong báo cáo này, v3 là bản trước đây có tên v2-tool; v4 là bản trước đây có tên v3. Các lần chỉnh tiếp theo mang tên v5, v6, v7, v8 và v9.

## 2. Mục tiêu và cách tiếp cận — PHẦN A: Giới thiệu agent

### A1. Agent này làm được gì

Agent hỗ trợ tìm tin web và bài đăng X, đọc URL hoặc paper arXiv, tra quy định nội bộ và tổng hợp kết quả có nguồn. Từ v8, agent có thể xuất BibTeX hoặc danh sách tài liệu tham khảo từ metadata paper đã có. Việc gửi Telegram cần được xác nhận; bản web demo đang tắt gửi thật.

**Cách chạy UI:**

Từ thư mục `starter_v0/`, chạy lần đầu trên Windows:

```powershell
.\run.ps1 -InstallDependencies
```

Các lần sau chạy `.\run.ps1`, rồi mở **http://127.0.0.1:8000/**. UI đã được kiểm tra bằng trình duyệt với một yêu cầu thật. Hướng dẫn và cấu hình nằm trong [docs/UI.md](../../docs/UI.md); dependency được khai báo trong requirements.txt.

**Link dùng thử (deploy):**

> URL:

Phần link public để thành viên phụ trách deployment bổ sung. Địa chỉ localhost chỉ dùng được trên máy đang chạy server.

### A2. Tool agent có

| Tên tool | Làm được gì | Tool mới nhóm thêm? |
|---|---|---|
| clarify | Hỏi thông tin còn thiếu hoặc xin xác nhận | không |
| timeline | Lấy bài mới của một tài khoản X đã xác định | không |
| social_search | Tìm bài đăng X theo chủ đề, ưu tiên mới nhất hoặc nổi bật | không |
| lookup | Tìm thông tin và tin tức trên web | không |
| fetch | Đọc một URL đã biết | không |
| format | Trình bày các mục đã có thành bản tin | không |
| send | Gửi nội dung đã được duyệt lên private channel Telegram | không |
| policy | Tìm trong kho quy định nội bộ | không |
| papers | Tìm metadata paper arXiv | không |
| arxiv_search | Tên gọi bổ sung của papers, có thêm bộ lọc và phân trang | không, cùng implementation |
| paper_text | Đọc trích đoạn PDF của paper đã xác định | không |
| research_paper | Kết hợp tìm paper với đọc text để hỗ trợ phân tích | có |
| audit_research_evidence | Phân biệt kết quả có dữ liệu, rỗng, lỗi và gộp URL trùng | có |
| build_bibliography | Xuất BibTeX/plain từ metadata paper, cảnh báo trường còn thiếu | có, thêm ở v8 |

Audit chỉ kiểm tra cấu trúc kết quả, không xác minh thông tin đúng hay sai. research_paper và audit đã có trước lần rà soát này; build_bibliography là tool được viết thêm trong v8.

### A3. Câu hỏi mẫu để thử

1. Tìm 5 tin AI trong hôm nay trên web, kèm nguồn.
2. Lấy 2 bài mới nhất của tài khoản @sama.
3. Đọc paper arXiv 2305.14314 và nêu hạn chế dựa trên nội dung truy xuất được.
4. Xuất BibTeX từ metadata paper tôi đã cung cấp, không tìm lại.
5. Giúp tôi đăng bản tin lên Telegram. (Kiểm tra agent hỏi lại trước khi gửi; demo không gửi thật.)

## 3. Giải pháp

Nhóm bắt đầu bằng việc chạy v0 để xác định lỗi trước khi sửa. Prompt ban đầu yêu cầu tự đoán tài khoản hoặc URL, gửi ngay và hoàn tất trong một bước. Những chỉ dẫn này giải thích được các lỗi thiếu hỏi lại và gọi send sai mục đích. V1 bỏ các chỉ dẫn đó, yêu cầu hỏi khi thiếu thông tin và xác nhận nội dung trước khi gửi. Phần mô tả lookup cũng tách chủ đề tìm kiếm khỏi loại tin và khoảng thời gian.

Sau v1, agent lại hỏi thừa ở những yêu cầu đọc đã rõ. V2 phân biệt thông tin thiết yếu với tham số tùy chọn, cho phép dùng giá trị mặc định và không xác nhận lại thao tác đọc. Phần phân tích và hiệu chỉnh v2 đã được ghi nhận cho **Nguyễn Đức Khương Lam — 2A202604020**. Dương phụ trách lưu kết quả và các snapshot; báo cáo không quy toàn bộ thay đổi này cho một người.

V3 tích hợp research_paper để phân biệt tìm metadata với đọc nội dung paper. V4 bổ sung audit và làm rõ ba bước Telegram: đồng ý chuẩn bị, cung cấp nội dung, rồi duyệt đúng nội dung trước khi gửi. Run base của v4 đạt 20/20. Tuy vậy, điểm tối đa ở bộ base chưa đủ để kết luận mọi tình huống đều được xử lý đúng.

Các thử nghiệm v5–v7 tiếp tục làm rõ mô tả tool và điều kiện hỏi lại, nhưng có hồi quy. V5 đoán tài khoản; v6 hỏi thừa hoặc truyền thiếu kiểu câu hỏi; v7 vẫn gọi thêm tool ở một số lượt. Nhóm giữ các kết quả này để phân tích, thay vì sửa số liệu hoặc chỉ trình bày lần chạy tốt. H7A dùng bảng quyết định và ví dụ đối chiếu cũng chưa đạt mục tiêu.

V8 chọn lại v4 làm nền và chỉ mở thêm một tác vụ: xuất tài liệu tham khảo. [Giả thuyết H8](review_evidence/v8_hypothesis.md), được ghi trước khi chạy, là một tool có phạm vi hẹp và điều kiện sử dụng rõ có thể bổ sung tác vụ mới mà giữ được kết quả base. build_bibliography nhận metadata thật, xuất BibTeX/plain và cảnh báo tác giả hoặc năm còn thiếu. Tool không tìm kiếm, không xác minh bài báo và không tự điền dữ liệu chưa có. Nó được đăng ký trong registry/YAML, có TOOL.md, 9 unit test và một case group riêng.

Sau v8, nhóm hợp nhất [commit 54d010f của Nguyễn Đức Khương Lam](https://github.com/lit1numyt/K5-L3B-DAY03-4x6.1Sol-ResearchAgentToolEval/commit/54d010f4b233f763b3d5b51eb8a10e794595f14d) thành v9. Phần phân tích của Lam chỉ ra rằng không gọi tool chưa đồng nghĩa đã từ chối đúng: ở v3, R14 vẫn hướng dẫn thuật toán Fibonacci sau câu từ chối. V9 vì vậy giới hạn theo nhiệm vụ, không chỉ theo định dạng code hay văn xuôi; việc giải thích phương pháp từ nguồn nghiên cứu vẫn thuộc phạm vi.

Về Telegram, v9 phân biệt đồng ý chuẩn bị với duyệt bản cuối. Khi đã có nội dung, agent chuyển thẳng sang xin duyệt; nội dung thay đổi phải được duyệt lại, người dùng từ chối thì dừng. Mô tả clarify và send được đồng bộ với quy trình này. [H9](review_evidence/v9_hypothesis.md) kế thừa giả thuyết H4 trong nhánh Lam; tên v9 giúp tránh nhầm với các phiên bản nhóm đã đo. Dương phụ trách hợp nhất và kiểm chứng với Codex hỗ trợ. Quy tắc audit, bibliography, đủ 14 tool và schema/mặc định của v8 được giữ. Kết quả v8 không được dùng thay cho phép đo v9.

UI dùng lại vòng gọi tool của agent. Trong lần rà soát, nhóm sửa cách đọc run đã lưu để tránh hiển thị FAIL sai, sửa trạng thái sau khi tool chạy, thông báo lỗi và danh sách Markdown. Lệnh PowerShell giúp chạy đúng môi trường Python trên Windows; adapter UI cũ cũng đã bỏ các import mẫu chưa được tích hợp. Phần sửa UI và code tool được kiểm tra riêng, không dùng để suy ra tác động của từng câu prompt.

## 4. Kết quả — PHẦN B: Chi tiết và bằng chứng

### B1. Version Evidence

Lấy từ `starter_v0/artifacts/version_log.csv` và `starter_v0/runs/*.json`. Chỉ dùng run có `provider_error_cases == 0` và `measured_cases == total_cases`.

| Version | Changed Artifact | Hypothesis | Metric Before | Metric After | Run File |
|---|---|---|---:|---:|---|
| v0 | baseline | Đo hành vi ban đầu | — | 0.65 | [run v0](../../starter_v0/runs/v0_B_base_openai_20261110T173859866471.json) |
| v1 | prompt + tools | Làm rõ hỏi lại, xác nhận, phạm vi và args | 0.65 | 0.85 | [run v1](../../starter_v0/runs/v1_B_base_openai_20261110T182202801200.json) |
| v2 | prompt + tools | Phân biệt thao tác đọc rõ ràng với thông tin còn thiếu | 0.85 | 0.90 | [run v2](../../starter_v0/runs/v2_B_base_openai_20261110T185609495800.json) |
| v3 | prompt + tools; research_paper | Kiểm tra base sau khi tích hợp tool paper | 0.90 | 0.95 | [run v3](../../starter_v0/runs/v3_B_base_openai_20261110T191038391725.json) |
| v4 | prompt + tools; audit | Tách ý định chuẩn bị với duyệt nội dung | 0.95 | 1.00 | [run v4](../../starter_v0/runs/v4_B_base_openai_20261110T213656627758.json) |
| v5 | prompt + tools | Hoàn thiện điều kiện chọn tool và dữ liệu kiểm tra | 1.00 | 0.95 | [run v5](../../starter_v0/runs/v5_B_base_openai_20261110T215904815187.json) |
| v6 | prompt + timeline description | Làm rõ điều kiện thiếu tài khoản | 0.95 | 0.85 | [run v6](../../starter_v0/runs/v6_B_base_openai_20261110T220250416618.json) |
| v7 | prompt + tools; ví dụ đối chiếu | H7A: áp dụng ranh giới theo thứ tự rõ hơn | 0.85 | 0.90 | [run v7](../../starter_v0/runs/v7_B_base_openai_20261110T221854221652.json) |
| v8 | prompt + tools; build_bibliography | H8: thêm xuất bibliography, giữ kết quả base | 1.00 (v4) | 1.00 | [run v8](../../starter_v0/runs/v8_B_base_openai_20261110T223125274893.json) |
| v9 | prompt + 4 mô tả clarify/send; hợp nhất Lam | H9: làm rõ duyệt nội dung và phạm vi nhiệm vụ, giữ routing | 1.00 (v8) | 0.95 | [run v9](../../starter_v0/runs/v9_B_base_openai_20261110T230751104659.json) |

Metric trong bảng là tỷ lệ case đúng tool và arguments của bộ base. Tất cả run đều dùng OpenAI gpt-4o-mini, đo đủ 20 case và không có lỗi provider. **V8 đạt 20/20 base và [10/10 group](../../starter_v0/runs/v8_B_group_openai_20261110T223032240551.json)**, cùng hash prompt `28df43d23d49…` và tools `1985f521a55c…`. V8 được phát triển từ v4 nên mốc trước của H8 là 1.00 của v4.

V9 đạt **19/20 base và [9/10 group](../../starter_v0/runs/v9_B_group_openai_20261110T230818905094.json)**, đo đủ case, không lỗi provider và dùng cùng bộ group với v8. Hai run cùng hash prompt `980d47d87a9e…` và tools `c4dc31cfea7c…`. Kết quả chưa đáp ứng điều kiện chọn v9 đã ghi trước trong H9, nên nhóm giữ v8 làm mặc định; v9 vẫn được lưu để đối chiếu và giữ đóng góp của Lam trong lịch sử merge.

V5–v7 không làm điểm tăng đều và không được coi là các lần cải tiến thành công. V7 ban đầu cũng có run 18/20 base, 9/10 group trong thư mục candidates; H7A mới vẫn 18/20 và 9/10. Những run này được giữ. Rubric cho phép phiên bản không tăng điểm nếu phân tích trung thực.

Các bộ group có thay đổi: [run v4 trên bộ nguyên thủy](../../starter_v0/runs/history/v4_original_suite/v4_B_group_openai_20261110T213600677281.json) đạt 9/10, bản đã siết arguments đạt 10/10, còn bản v8 thay G05 bằng bibliography. Run dùng bộ nguyên thủy được chuyển vào history để phân biệt với bằng chứng chính; nội dung JSON không đổi. Vì vậy không dùng chênh lệch điểm group giữa các bộ để khẳng định model tiến bộ trên cùng phép đo. Một số vòng cũng sửa đồng thời prompt và description, nên chưa tách được tác động của từng thay đổi. Riêng base v3 không gọi research_paper, do đó không thể quy mức tăng điểm cho tool đó.

Run JSON lịch sử giữ nguyên nội dung dù đổi tên file; metadata bên trong có thể còn tên cũ. [Manifest](review_evidence/consecutive_version_manifest.json) và [bảng tổng hợp](review_evidence/version_summary.json) giúp đối chiếu. Hai hash chỉ xác định prompt/YAML, không bao gồm mọi thay đổi code. Các eval mới chặn send, nên không phải bằng chứng gửi Telegram thật.

### B2. Failure Analysis

Bảng dưới phân tích đủ 7 case FAIL của [v0](../../starter_v0/runs/v0_B_base_openai_20261110T173859866471.json). Failure Type phản ánh lỗi quan sát được; ở R03/R13, nhãn case là wrong_tool nhưng tên tool thực tế đã đúng.

| Case ID | Failure Type | Actual Tool Calls | What Failed | Fix |
|---|---|---|---|---|
| R03_web_news_routing | wrong_arg_value | lookup(query="AI news", topic="news", timeframe="day") | Query khác chuỗi "AI" mà evaluator kỳ vọng; chưa đủ cơ sở nói truy vấn sai nghĩa. | Tách chủ đề khỏi loại tin/thời gian trong mô tả args. |
| R08_out_of_scope | out_of_scope | send(text=lời giải tích phân) | Dùng send cho yêu cầu ngoài phạm vi. | Bỏ yêu cầu luôn chọn tool; từ chối ngắn bằng text. |
| R10_missing_handle | missing_info | timeline(screenname="sama") | Tự chọn tài khoản khi chưa biết người dùng muốn xem ai. | Hỏi tài khoản; giữ số lượng đã được yêu cầu. |
| R11_missing_url | missing_info | fetch(url="https://example.com/article") | Tự tạo URL thay vì hỏi. | Chỉ đọc URL đã có trong yêu cầu hoặc ngữ cảnh. |
| R12_confirm_before_send | wrong_boundary | send(text="Bản tin này đã được đăng lên Telegram.") | Gọi send trước xác nhận, dùng câu thông báo làm nội dung gửi. Tool đã chặn, chưa gửi thật. | Lấy và duyệt nội dung cụ thể trước send(confirmed=true). |
| R13_parallel_web_and_tweets | wrong_arg_value | lookup(query="AI news") + social_search(query="AI", search_type="Latest") | Có đủ hai tool nhưng lookup thiếu topic=news; query cũng khác kỳ vọng. | Làm rõ topic/timeframe và quy ước query. |
| R14_out_of_scope_coding | out_of_scope | send(text=code Fibonacci) | Dùng send để trả lời yêu cầu viết code. | Giới hạn send cho Telegram và từ chối tác vụ ngoài phạm vi. |

V1 sửa được phần lớn lỗi v0 nhưng hỏi thừa ở R01/R05. R08/R14 được chấm PASS vì không gọi tool, song actual_text vẫn chứa lời giải/code sau câu từ chối. V2 làm rõ cách từ chối và thao tác đọc, nhưng M06 hồi quy. Đây là lý do phải đọc cả nội dung trả lời, không chỉ tỷ lệ PASS.

Ở v3, R14 được chấm PASS do không gọi tool nhưng vẫn hướng dẫn thuật toán Fibonacci; phân tích của Lam được kiểm tra lại trên run gốc. Đây là cơ sở cho quy tắc v9 không thực hiện nhiệm vụ đã từ chối bằng giả mã, công thức hoặc hướng dẫn tương đương. R10 của v0 chỉ được tính lỗi tự đoán tài khoản; việc không truyền limit riêng không tạo lỗi số lượng vì mặc định 5 đã trùng yêu cầu.

Ở các bản thử sau v4, v5 sai R10; v6 sai R01/R11/R12; v7 ban đầu còn lỗi gửi sớm ở G04. H7A khắc phục các lỗi nhắm tới trong lượt đó nhưng gọi thêm social_search ở M02/M06 và gửi include_text vào paper_text không nhận tham số này. V8 không có FAIL trong base/group đã chạy, nhưng vẫn cần kiểm tra các hành vi ngoài phạm vi máy chấm.

V9 không đạt R12 vì dùng clarify(text) thay vì yes_no. Ở G04, model gọi send(confirmed=true) cho nội dung chưa được duyệt; stub trả blocked_for_eval nên không gửi Telegram thật. R08/R14 được chấm PASS do không gọi tool, nhưng khi đọc actual_text vẫn thấy lời giải tích phân và code Fibonacci. Vì vậy H9 chưa được hỗ trợ trong lượt đo này, kể cả ở chất lượng từ chối mà điểm tự động không phản ánh. Chưa thể quy nguyên nhân riêng cho một câu sửa hoặc kết luận về mọi lần chạy.

### B3. Team Eval Cases

Liệt kê đúng 10 case trong `starter_v0/data/eval_group.json` (5 single turn + 5 multi turn). Cột Result là kết quả v8 được chọn làm mặc định; v9 dùng lại đúng bộ này và sai G04, các case còn lại PASS.

| Case ID | What It Tests | Expected Tool/Behavior | Result |
|---|---|---|---|
| G01_audit_empty_and_failed_sources | Single: Phân biệt nguồn rỗng và API lỗi | audit với results đúng input | PASS |
| G02_audit_after_results_multiturn | Multi: Dùng kết quả được bổ sung qua hội thoại | audit với results trong hội thoại | PASS |
| G03_telegram_missing_content | Single: Đã đồng ý chuẩn bị nhưng chưa có nội dung | clarify(response_type="text") | PASS |
| G04_telegram_confirm_known_content_multiturn | Multi: Có nội dung nhưng chưa duyệt đăng | clarify(response_type="yes_no"), chưa send | PASS |
| G05_build_bibliography | Single: Xuất tài liệu tham khảo bằng tool mới v8 | build_bibliography, đúng papers và format="bibtex" | PASS |
| G06_research_paper_limitations | Single: Đọc nội dung để phân tích paper cụ thể | research_paper, ID đúng và include_text=true | PASS |
| G07_audit_capabilities_without_tools | Single: Giải thích giới hạn audit, không gọi thừa | Không gọi tool | PASS |
| G08_paper_filter_carryover | Multi: Giữ ngữ cảnh khi bổ sung bộ lọc tác giả | arxiv_search, giữ chủ đề/năm và thêm author | PASS |
| G09_paper_pagination | Multi: Giữ chủ đề và chuyển sang trang paper tiếp | arxiv_search, giữ query, start=5, max_results=5 | PASS |
| G10_audit_retained_results | Multi: Kiểm tra các kết quả đã có trong ngữ cảnh | audit với results đã có | PASS |

Cả ba bộ đều giữ 5 single + 5 multi: v4 gốc dùng eval_group_v4.json; v4 chạy lại và v5–v7 dùng eval_group_v4_reviewed.json; v8–v9 dùng data/eval_group.json. Ở v4–v7, G05 kiểm tra audit nguồn trùng; từ v8, G05 kiểm tra bibliography. Các case multi là ngữ cảnh hội thoại đóng gói để chấm lượt cuối, không phải năm phiên chat tương tác đầy đủ.

[Run group v8](../../starter_v0/runs/v8_B_group_openai_20261110T223032240551.json) đo đủ 10 case, không có lỗi provider. G05 thay một case audit trùng phạm vi để kiểm tra tool mới; số single/multi vẫn là 5/5. Các case audit kiểm tra cả dữ liệu truyền vào; G08/G09 kiểm tra cả chủ đề giữ lại. Hai bộ eval cố định của thầy không bị sửa.

Bộ này chấm lượt chọn tool cuối trong ngữ cảnh nhiều lượt, chưa phải hội thoại tương tác đầy đủ. Evaluator dùng tool_choice=required khi kỳ vọng có tool. G04 vẫn cần xem câu hỏi có duyệt đúng nội dung không; G06 cần đọc phần phân tích; G07 cần nói đúng giới hạn audit; G09 chưa chứng minh IDs thực tế không trùng. Các giới hạn này không được suy ra từ điểm 10/10.

### B4. Live Chat Evidence

Lấy từ `starter_v0/transcripts/*.transcript.json`. Bằng chứng dưới đây thuộc v8 đang được chọn; không đổi nhãn transcript thành v9.

| Turn | User Request | Tool Calls | Version Evidence | Outcome |
|---|---|---|---|---|
| 1 | Hỏi quy định trích dẫn nguồn trong bản tin | policy | [transcript v8](../../starter_v0/transcripts/v8_openai_20261110T223458159061.transcript.json) | policy chạy nhưng chưa tìm được đoạn phù hợp; agent không bịa nguồn |
| 2 | Yêu cầu tóm tắt 2 tweet nhưng chưa nêu tài khoản | Không gọi tool | [transcript v8](../../starter_v0/transcripts/v8_openai_20261110T223458159061.transcript.json) | Agent hỏi tên tài khoản bằng text; chưa gọi clarify |
| 3 | Bổ sung tài khoản @sama, giữ số lượng 2 | timeline | [transcript v8](../../starter_v0/transcripts/v8_openai_20261110T223458159061.transcript.json) | Lấy 2 bài thật, trả tóm tắt kèm liên kết |
| 4 | Yêu cầu đăng bản tin lên Telegram | Không gọi tool | [transcript v8](../../starter_v0/transcripts/v8_openai_20261110T223458159061.transcript.json) | Agent hỏi lại bằng text, chưa send; demo tắt delivery |

Bốn lượt dùng [prompt theo kịch bản](review_evidence/live_demo_prompts.txt), model và tool đọc chạy thật. Transcript không phải hội thoại con người được viết lại. `--disable-send` được ghi trong metadata; không có gửi Telegram thật. Lượt 2/4 cho thấy agent biết hỏi, nhưng chưa chứng minh trạng thái chờ qua clarify vì model hỏi trực tiếp bằng text.

Trên trình duyệt, UI đã gọi build_bibliography thành công và hiển thị thông báo bỏ tác giả bị thiếu. [Ảnh UI](review_evidence/ui_v8_full.png) và [ảnh saved PASS](review_evidence/ui_saved_pass.png) bổ sung cho kiểm tra này, không thay transcript. Phần live demo hoặc nhận xét của các thành viên khác để họ tự bổ sung.

### B5a. Required Evidence — Tool mới, unit test, UI

| Item | Evidence File | What Worked | Risk / Guardrail |
|---|---|---|---|
| Tool mới build_bibliography (v8) | [tool.py](../../starter_v0/tools/build_bibliography/tool.py), [TOOL.md](../../starter_v0/tools/build_bibliography/TOOL.md), registry/YAML | Xuất BibTeX/plain từ metadata đã có; bỏ nguồn trùng, báo trường thiếu | Không tìm kiếm/xác minh; input sai trả error dict |
| Tool nhóm research_paper và audit | Code/TOOL.md trong tools/; registry/YAML | Bổ sung validate, xử lý lỗi và test | Hai tool đã có trước phiên này; không tính alias arxiv_search là tool mới |
| Unit test tool mới (≥ 3 test/tool) | [test_tools_todo.py](../../starter_v0/tests/test_tools_todo.py), [test audit](../../starter_v0/tests/test_audit_research_evidence.py), [pytest](review_evidence/pytest_v9.txt) | Bibliography 9 test; research_paper 12; audit 10. Toàn suite: **130 passed, 14 skipped, 0 failed** | Test offline; 14 skip là TODO tool starter |
| UI (lệnh chạy + link dùng thử) | [UI docs](../../docs/UI.md), [run.ps1](../../starter_v0/run.ps1), [UI tests](../../starter_v0/tests/test_web_app.py), ảnh B4 | 12 test UI/loop; đã chạy chat thật và mở saved run đúng | Chạy local; public link chờ bổ sung; Telegram mặc định tắt |

Ví dụ, unit test kiểm tra tool bibliography không bịa năm/tác giả khi thiếu metadata và trả lỗi với URL không dùng được. Eval chọn đúng tên tool chưa đủ phát hiện các lỗi code này. Regression UI kiểm tra một saved case PASS phải được hiển thị đúng, đồng thời giữ thông báo lỗi tool.

### B5. Bonus Evidence

Chỉ điền nếu nhóm làm bonus (ghi riêng, tối đa 10 điểm). Tool có sẵn (`send`, `policy`, `papers`, `paper_text`) không tự được bonus.

| Bonus | Evidence File | What Worked | Risk / Guardrail |
|---|---|---|---|
| Small Local Model | xem B7 |  |  |
| Hơn 3 tool mới (≥ 4) |  |  |  |
| `send` gửi thật lên Telegram sau xác nhận | transcript |  |  |
| Test challenge (0 skipped / regression test) | `pytest` output |  |  |

Hiện chưa nhận bonus: còn 14 skipped; regression UI/evaluator không tự tính là bug tool starter. Nhóm có 3 tool mới, chưa đủ mốc 4; chưa có bằng chứng model local hoặc gửi Telegram thật. Các thành viên tự bổ sung nếu có bằng chứng phù hợp.

### B7. Small Local Model Challenge (bonus)

Chỉ điền nếu nhóm làm bonus này.

| Version | Model (provider) | Prompt/Tools | case_accuracy | tool_routing | argument | multiturn | Run File |
|---|---|---|---|---|---|---|---|
| v3 | (cloud) | v3 |  |  |  |  |  |
| v3-<model> | (ollama) | v3 |  |  |  |  |  |
| v3-<model> | (ollama) | v3 |  |  |  |  |  |
| v4-local |  |  |  |  |  |  |  |
| v5-local |  |  |  |  |  |  |  |

Lỗi đặc thù của model nhỏ (đếm từ run JSON):

| Failure Pattern | Count | Example Case | Fix Tried | Helped? |
|---|---|---|---|---|
| wrong / hallucinated tool |  |  |  |  |
| invalid JSON args (`_invalid_json_arguments`) |  |  |  |  |
| no tool call / answered directly |  |  |  |  |
| missed `clarify` |  |  |  |  |
| repeated / unnecessary calls |  |  |  |  |

- Cái gì giúp model nhỏ gọi tool đúng hơn nhất? Bằng chứng?
- Bản prompt tối ưu cho local chạy trên model cloud thì sao?
- Khi nào nhóm sẽ chọn model local thay vì cloud cho agent này?

## 5. Khó khăn và cách xử lý

Khi đối chiếu R12 và G03 cũ, nhóm thấy hai case đang kiểm tra khác giai đoạn của yêu cầu gửi. Bộ base được giữ nguyên; G03 được làm rõ là đã đồng ý chuẩn bị nhưng chưa có nội dung. Những lần đổi bộ group đều được ghi lại để tránh so sánh nhầm.

Các sửa đổi v5–v7 làm rõ một số quy tắc nhưng gây lỗi mới. Nhóm không tiếp tục thay mọi thứ cùng lúc, mà lấy v4 làm nền cho H8: thêm riêng chức năng bibliography. Kết quả v8 giữ được 20/20 base và đạt 10/10 group mới; các run hồi quy vẫn còn.

Lần hợp nhất với Lam có conflict ở prompt, YAML và báo cáo vì cả hai nhánh cùng sửa các phần này. Nhóm lấy v8 làm nền, chỉ nhận quy tắc mới có liên quan vào snapshot v9, giữ schema và 14 tool, rồi đo lại. Việc v9 có hồi quy được ghi nguyên trạng; cấu hình chạy chính quay về v8 theo tiêu chí đã đặt trước.

Về kỹ thuật, Python hệ thống thiếu FastAPI nên test phải chạy trong .venv của repo. UI cũng từng nhận raw run thay vì cấu trúc evaluation/actual, dẫn tới hiển thị FAIL sai; lỗi này đã được sửa và có regression test. Sau khi hợp nhất, pytest vẫn đạt 130 passed, 14 skipped, 0 failed; đây là kiểm tra offline, không thay kết quả eval model.

Phần deployment và khó khăn riêng của các thành viên khác để họ bổ sung. Chưa có bằng chứng Phần A hoàn thành trước 16:30; báo cáo không ghi lùi thời gian.

## 6. Tổng hợp đóng góp

Chi tiết đóng góp của từng thành viên nằm trong [TEAM.md](../../TEAM.md) và các báo cáo cá nhân `report/team/MSSV_HoTen.md`.

Chu Nguyễn Tùng Dương — 2A202604016 có bằng chứng chạy/lưu eval và versioning qua các commit 341c4ce, b7691c0, 2aaa3cb và c17dc2e. Trong phần bổ sung v8, Codex hỗ trợ viết build_bibliography, test, case group, sửa UI và tổng hợp bằng chứng. Thay đổi v8 và báo cáo được lưu trên nhánh nộp `main`; xem mốc commit trong [TEAM.md](../../TEAM.md). Không quy tác giả hai tool đã có hoặc UI ban đầu cho Dương.

Nguyễn Đức Khương Lam — 2A202604020 có phần phân tích/hiệu chỉnh v2 và commit 54d010f làm rõ xác nhận gửi, phạm vi từ chối và phân tích kết quả v0–v3. Nhóm nhận phần hiệu chỉnh này trong v9, đối chiếu với log thật và giữ nguyên tác giả commit khi merge. Báo cáo cá nhân, nhận xét trải nghiệm và thông tin còn lại của Lam cùng các thành viên khác để họ tự bổ sung.

## 7. Hạn chế và hướng cải thiện — B6. Reflection

- Fix nào thuộc `system_prompt.md`? Điều kiện hỏi lại, phạm vi nghiên cứu, giữ ngữ cảnh và xác nhận trước hành động. V8 chỉ thêm chỉ dẫn dùng bibliography vào nền v4; v9 thử quy tắc xác nhận và từ chối do Lam hiệu chỉnh nhưng chưa được chọn.
- Fix nào thuộc `tools.yaml`? Mô tả khi dùng/không dùng và ý nghĩa args. Với tool mới, metadata phải có sẵn, format là bibtex/plain và không tự điền dữ liệu thiếu. Validate implementation và TOOL.md là lớp kiểm tra riêng.
- Failure nào cần review thủ công thay vì chấm tự động? Nội dung trả lời ngoài phạm vi dù no_tool, câu hỏi duyệt đúng nội dung ở G04, phân tích paper có căn cứ ở G06 và việc lặp IDs ở G09. Demo CLI cũng cho thấy hỏi bằng text chưa đồng nghĩa gọi clarify đúng luồng.
- Nếu có thêm một vòng, nhóm sẽ thử giả thuyết nào? Tách từng ranh giới, dùng một bộ câu hỏi chưa dùng để sửa prompt, và kiểm tra việc duyệt nguyên văn trước send bằng trạng thái ứng dụng độc lập với model.

V8 đạt điểm tối đa ở hai suite đã chạy, nhưng chưa đủ cơ sở nhận toàn bộ rubric. V9 được hợp nhất và lưu riêng với kết quả 19/20, 9/10; nhóm không đổi nhãn các run tốt của v8 để thay bằng chứng cho v9. V8 vẫn thừa hưởng một số description còn chung chung và quy tắc tin cậy nguồn chưa đầy đủ của v4. UI đã chạy local và có transcript thật, song public URL, thời điểm hoàn thành Phần A và phần các thành viên khác còn thiếu. Khi bật gửi thật, code vẫn dựa vào confirmed do model đưa vào; web demo hiện chặn delivery. Các giới hạn này cần được giữ trong kết luận, không che bằng điểm 20/20.

## 8. Tài liệu tham khảo

- [RUBRIC.md](../../RUBRIC.md), [RULES.md](../../RULES.md), [CHECKPOINTS.md](../../CHECKPOINTS.md), [SUBMISSION.md](../../SUBMISSION.md) và README của repo.
- [Tool folder contract](../../starter_v0/tools/README.md), prompt/YAML, code tool, run và transcript được dẫn ở từng mục.
- [Biên bản rà soát](rubric_review.md), [giả thuyết H8](review_evidence/v8_hypothesis.md), [H9](review_evidence/v9_hypothesis.md), [biên bản hợp nhất](review_evidence/merge_v9_review.json), [pytest](review_evidence/pytest_v9.txt), [bảng số đo](review_evidence/version_summary.json) và [hướng dẫn UI](../../docs/UI.md).
- AI hỗ trợ: Codex. Nội dung được kiểm tra bằng file thật, hash, unit test, API run và trình duyệt; không dùng nhận xét của AI thay cho bằng chứng.
- Tài liệu ngoài hoặc code/dữ liệu của các thành viên khác: để thành viên liên quan bổ sung.
