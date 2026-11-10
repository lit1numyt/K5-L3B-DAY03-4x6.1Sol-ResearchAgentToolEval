# Báo cáo nhóm — Day 03 Research Agent Tool Eval

> Báo cáo gồm 2 phần có hạn khác nhau:
> - **Phần A (mục 2)** — giới thiệu agent, ngắn gọn 1 trang. **Xong trước Team showdown (16:30)** để team khác hiểu nhanh agent có tool gì, làm được gì. Có thể làm thêm poster `report/team/poster.html` hoặc `poster.svg`.
> - **Phần B (mục 3–7)** — chi tiết và bằng chứng, dựa trên log thật. Hoàn thiện trước deadline nộp bài.
>
> Mỗi bảng phải trỏ được tới file thật: run JSON, transcript, commit. Cách chấm xem [RUBRIC.md](../../RUBRIC.md).

## 1. Thông tin nhóm

- Tên nhóm:
- Thành viên và phân công: xem [TEAM.md](../../TEAM.md)
- Provider/model dùng cho v0–v3:

## 2. Mục tiêu và cách tiếp cận — PHẦN A: Giới thiệu agent

### A1. Agent này làm được gì

> 1–2 câu mô tả agent dùng để làm gì (cho team khác hiểu nhanh).

Ví dụ: "Research agent: tìm tin theo từ khóa / theo tài khoản, đọc URL, tổng hợp thành digest, và gửi lên Telegram khi được xác nhận."

**Cách chạy UI:**

> Lệnh chạy UI (ví dụ `streamlit run app.py`) và dependency đã thêm vào `starter_v0/requirements.txt`.

**Link dùng thử (deploy):**

> Dán link public để team khác mở thử ngay. Cách deploy nhanh bằng Cloudflare Tunnel xem README. Nếu deploy Vercel/Streamlit Cloud thì dán link đó.
>
> URL:

### A2. Tool agent có

> Liệt kê các tool agent đang dùng (gồm tool mới nhóm tự thêm). Mỗi tool 1 dòng: tên + làm được gì.

| Tên tool | Làm được gì | Tool mới nhóm thêm? |
|---|---|---|
| clarify | hỏi lại người dùng khi thiếu thông tin | không |
|  |  |  |
|  |  |  |

### A3. Câu hỏi mẫu để thử

> 3–5 câu hỏi/yêu cầu mẫu để team khác tự thử agent ngay.

1.
2.
3.

## 3. Giải pháp

Nguyễn Đức Khương Lam (`2A202604020`) phụ trách phân tích lỗi và hiệu chỉnh system prompt, mô tả tool và tham số. Các vòng đánh giá dưới đây dùng cùng model OpenAI `gpt-4o-mini` và bộ 20 case base.

### Hiệu chỉnh từ v0 lên v1

Baseline v0 đạt 13/20 case (65%). Agent tự đoán tài khoản hoặc URL khi thiếu thông tin, gọi `send` trước khi xác nhận và dùng tool này để trả lời yêu cầu ngoài phạm vi. Một số arguments tìm tin cũng chưa khớp kỳ vọng. Giả thuyết của vòng đầu là việc bỏ các chỉ dẫn khuyến khích đoán và hành động ngay, kết hợp mô tả tool rõ hơn, sẽ giảm những lỗi này.

Nhóm thay chỉ dẫn đoán tài khoản/URL bằng yêu cầu hỏi lại qua `clarify(text)`, bỏ yêu cầu luôn chọn một tool và quy định cách phản hồi yêu cầu ngoài phạm vi. Với Telegram, nội dung phải được xác nhận trước khi gọi `send(confirmed=true)`. Các mô tả liên quan đến `clarify`, `timeline`, `fetch` và `send` được làm rõ. Với `lookup`, chủ đề và từ khóa nội dung nằm trong `query`; loại tin và thời gian được truyền qua `topic` và `timeframe`.

Cấu hình được lưu tại [system_prompt_v1.md](../../starter_v0/artifacts/system_prompt_v1.md) và [tools_v1.yaml](../../starter_v0/artifacts/tools_v1.yaml). [Run v1](../../starter_v0/runs/v1_B_base_openai_20261110T182202801200.json) đạt 17/20 case (85%), đo đủ 20 case và không có lỗi provider. Sáu case chuyển sang đạt, nhưng R01/R05 phát sinh lỗi hỏi lại không cần thiết và R12 vẫn chưa đạt. Kiểm tra offline tại thời điểm hiệu chỉnh đạt 62 passed, 17 skipped; các test bị bỏ qua là TODO có sẵn.

### Hiệu chỉnh từ v1 lên v2

R01 và R05 cho thấy agent chưa phân biệt rõ thông tin bắt buộc với tham số tùy chọn, cũng như thao tác đọc với hành động gửi. Đọc nội dung trả lời còn cho thấy R08/R14 vẫn cung cấp lời giải hoặc code sau câu từ chối dù được chấm đạt. Giả thuyết H2 là việc làm rõ điều kiện hỏi lại, xác nhận và phản hồi ngoài phạm vi sẽ giảm các hành vi này mà vẫn giữ việc hỏi khi thiếu thông tin thiết yếu.

Nhóm yêu cầu thực hiện trực tiếp thao tác đọc đã đủ thông tin. Tham số tùy chọn ưu tiên giá trị người dùng cung cấp, giá trị được thể hiện rõ trong yêu cầu hoặc mặc định đã khai báo. `timeline.limit` được mô tả rõ hơn: một bài mới nhất dùng 1, không chỉ định số lượng dùng mặc định 5. Quy trình gửi ở v2 lấy nội dung còn thiếu bằng `clarify(text)`, sau đó xin xác nhận bằng `clarify(yes_no)`. Prompt cũng yêu cầu không kèm lời giải hoặc code trong phản hồi từ chối ngoài phạm vi.

Cấu hình được lưu tại [system_prompt_v2.md](../../starter_v0/artifacts/system_prompt_v2.md) và [tools_v2.yaml](../../starter_v0/artifacts/tools_v2.yaml). [Run v2](../../starter_v0/runs/v2_B_base_openai_20261110T185609495800.json) đạt 18/20 case (90%), đo đủ 20 case và không có lỗi provider. R01/R05 chuyển sang đạt; R08/R14 từ chối mà không kèm lời giải hoặc code trong lần chạy này. Tuy nhiên, M06 chuyển sang không đạt và R12 vẫn dùng `text` thay vì `yes_no` như bộ eval kỳ vọng. Kết quả hỗ trợ một phần H2 nhưng chưa loại bỏ được hồi quy. Kiểm tra offline tại thời điểm hiệu chỉnh đạt 62 passed, 17 skipped.

### Hiệu chỉnh sau v3

[Run được chọn làm v3](../../starter_v0/runs/v2-tool_B_base_openai_20261110T191038391725.json) đạt 19/20 case (95%), đo đủ 20 case và không có lỗi provider. M06 trở lại đạt; R12 vẫn hỏi nội dung bản tin bằng `clarify(text)`. R14 không gọi tool nhưng tiếp tục hướng dẫn thuật toán Fibonacci sau câu từ chối. Vì evaluator chỉ kiểm tra không gọi tool ở case này, điểm đạt chưa phản ánh đầy đủ chất lượng phản hồi.

Giả thuyết H4 là việc phân biệt rõ phạm vi của xác nhận và phạm vi của nhiệm vụ sẽ giúp agent hỏi đúng loại câu hỏi cho yêu cầu gửi, đồng thời tránh thực hiện nhiệm vụ đã từ chối dưới hình thức khác. Bản hiệu chỉnh nằm trong [system_prompt.md](../../starter_v0/artifacts/system_prompt.md) và [tools.yaml](../../starter_v0/artifacts/tools.yaml).

Với Telegram, prompt phân biệt đồng ý chuẩn bị bài đăng với duyệt nội dung cuối cùng. Khi chưa có nội dung và chưa đồng ý chuẩn bị, agent được yêu cầu hỏi yes/no để xác nhận tiếp tục và nêu rõ chưa thực hiện gửi. Sau khi người dùng đồng ý, agent hỏi nội dung còn thiếu bằng text; khi có bản cuối thì trình bày và xin duyệt bằng yes/no. Nếu nội dung đã có ngay từ đầu, quy trình chuyển thẳng sang duyệt bản cuối. Chỉ duyệt đúng bản cuối mới cho phép `send(confirmed=true)`; thay đổi nội dung phải được duyệt lại, từ chối thì dừng. Quy trình này thêm một lượt xác nhận khi thiếu nội dung, nhưng không dùng sự đồng ý chuẩn bị làm quyền gửi một bản tin chưa được duyệt.

Với yêu cầu ngoài phạm vi, prompt xác định giới hạn theo nhiệm vụ thay vì định dạng câu trả lời. Agent được yêu cầu chỉ giải thích ngắn gọn phạm vi hỗ trợ và đề nghị hỗ trợ nghiên cứu phù hợp; không cung cấp code, giả mã, công thức hoặc hướng dẫn giải tương đương. Việc giải thích phương pháp hay thuật toán từ tài liệu nghiên cứu vẫn thuộc phạm vi.

Mô tả `clarify`, `clarify.response_type`, `send` và `send.confirmed` được đồng bộ với các quy tắc trên. Quy trình chi tiết nằm trong system prompt để giảm lặp. Phần hiệu chỉnh này giữ các quy tắc đọc khi đủ thông tin, hỏi tài khoản/URL còn thiếu và giữ ngữ cảnh; không thay đổi schema, giá trị mặc định, code tool, dữ liệu eval, run hoặc snapshot v0–v3. Sau khi đồng bộ `main` tại commit `b94cfd2`, cấu hình cũng kế thừa cập nhật arXiv và UI của nhóm. Các hiệu chỉnh về xác nhận và phạm vi được giữ lại, không sửa phần arXiv mới; khi đánh giá cần phân biệt tác động của hai nhóm thay đổi.

Kiểm tra offline trước khi đồng bộ đạt 67 passed, 17 skipped. Sau khi đồng bộ code tại `b94cfd2` và bổ sung dependency UI vào môi trường ảo, toàn bộ test đạt 80 passed, 17 skipped khi chạy ngoài sandbox; lần chạy trong sandbox bị treo ở phần test UI. Các test bị bỏ qua là TODO có sẵn. Kiểm tra thủ công trước đồng bộ bằng fake provider cho thấy luồng chat dừng tại `clarify` để chờ người dùng, trước lệnh gửi xuất hiện sau đó trong cùng phản hồi. Kiểm tra HTTP mock xác nhận nội dung được truyền nguyên vẹn vào request Telegram. Các phép kiểm tra thủ công không tính vào số test pytest và chưa kiểm chứng cách model chọn câu hỏi hoặc suy luận về xác nhận.

Bản hiệu chỉnh sau v3 chưa có run model mới. Kế hoạch đánh giá là chạy lại đủ 20 case với cùng provider/model, hướng tới 20/20 và kiểm tra hồi quy ở toàn bộ case đã đạt. Nội dung R08/R14 cần được đọc trực tiếp. Luồng gửi cần được kiểm tra qua nhiều lượt: thiếu nội dung hoặc chưa duyệt thì chưa gửi, duyệt đúng bản cuối mới gửi, thay đổi nội dung phải duyệt lại và từ chối thì dừng. Kết quả chỉ được ghi vào version log khi có run hợp lệ; chưa có cơ sở kết luận bản sửa đạt 100% hoặc ổn định qua nhiều lần chạy.

Các vòng hiệu chỉnh thay đổi nhiều chỉ dẫn và mô tả cùng lúc. Kết quả hiện có phản ánh tác động chung của từng cấu hình, chưa xác định được đóng góp riêng của mỗi thay đổi.

## 4. Kết quả — PHẦN B: Chi tiết và bằng chứng

### B1. Version Evidence

Kết quả được đối chiếu với `starter_v0/artifacts/version_log.csv` và các run JSON tương ứng. Các run trong bảng đều có `provider_error_cases == 0` và `measured_cases == total_cases`.

| Version | Changed Artifact | Hypothesis | Metric Before | Metric After | Run File |
|---|---|---|---:|---:|---|
| v0 | baseline | Đo hành vi ban đầu | — | 0.65 | [run v0](../../starter_v0/runs/v0_B_base_openai_20261110T173859866471.json) |
| v1 | system prompt + tools.yaml | Làm rõ hỏi lại, xác nhận, phạm vi và arguments giúp giảm lỗi | 0.65 | 0.85 | [run v1](../../starter_v0/runs/v1_B_base_openai_20261110T182202801200.json) |
| v2 | system prompt + tools.yaml | H2: phân biệt điều kiện thực hiện, hỏi thông tin, xác nhận gửi và từ chối ngoài phạm vi | 0.85 | 0.90 | [run v2](../../starter_v0/runs/v2_B_base_openai_20261110T185609495800.json) |
| v3 | system prompt + tools.yaml; thêm `research_paper` | Kiểm tra bộ base sau khi tích hợp tool mới | 0.90 | 0.95 | [run v2-tool](../../starter_v0/runs/v2-tool_B_base_openai_20261110T191038391725.json) |

Nhóm chọn cấu hình trong run trên làm v3; lệnh chạy thực tế dùng nhãn `v2-tool`, được giữ nguyên trong run JSON và `artifact_version`. Cấu hình này bổ sung khai báo `research_paper` và hướng dẫn dùng tool so với v2. Run đạt 19/20 case, đo đủ 20 case và không có lỗi provider; M06 chuyển từ fail sang pass, R12 vẫn fail do `clarify(text)` khác kỳ vọng `yes_no`. Không thể quy cải thiện cho tool mới chỉ từ một run: không có case base nào trong run gọi `research_paper`. Cần eval riêng để kiểm tra routing tới tool này.

### B2. Failure Analysis

Theo [run baseline v0](../../starter_v0/runs/v0_B_base_openai_20261110T173859866471.json), model OpenAI `gpt-4o-mini` đạt **13/20 case (65%)**. Cả 20 case đều được đo và không có lỗi provider. Bảng dưới đối chiếu 7 case không đạt với prompt, tool declaration và kết quả tool để xác định cơ sở hiệu chỉnh.

| Case ID | Failure Type | Actual Tool Calls | What Failed | Fix |
|---|---|---|---|---|
| R03_web_news_routing | `wrong_arg_value` | `lookup(query="AI news", topic="news", timeframe="day", max_results=5)` | Chọn đúng tool, loại tin và thời gian; query khác `AI` nên không đạt theo cách chấm so khớp chuỗi. Mô tả query chưa có quy ước tách chủ đề khỏi loại tin; chưa có bằng chứng truy vấn sai về ngữ nghĩa. | Làm rõ query giữ chủ đề và từ khóa nội dung, còn loại tin và thời gian truyền qua topic/timeframe. |
| R08_out_of_scope | `out_of_scope` | `send(text=<lời giải tích phân>)` | Gọi tool cho yêu cầu ngoài phạm vi. Prompt chưa quy định cách xử lý và yêu cầu luôn chọn tool; mô tả send chưa nói rõ đích gửi Telegram. | Bỏ yêu cầu luôn chọn tool, quy định từ chối bằng văn bản và làm rõ send không phải kênh trả lời trong cuộc chat. |
| R10_missing_handle | `missing_info` | `timeline(screenname="sama")` | Tự chọn tài khoản khi người dùng chưa cung cấp. Prompt trực tiếp khuyến khích đoán tài khoản; mô tả clarify/timeline chưa nêu rõ điều kiện hỏi lại. Việc không truyền limit không phải lỗi số lượng riêng ở case này vì mặc định 5 trùng yêu cầu. | Yêu cầu hỏi tài khoản bằng clarify(text), không tự chọn tài khoản; giữ thông tin đã được cung cấp khi tiếp tục. |
| R11_missing_url | `missing_info` | `fetch(url="https://example.com/article")` | Tự tạo URL thay vì hỏi lại, phù hợp với chỉ dẫn giả định URL trong prompt; mô tả fetch chưa ràng buộc nguồn URL. | Bỏ chỉ dẫn giả định URL; chỉ dùng fetch khi URL đã có trong yêu cầu hoặc ngữ cảnh, nếu thiếu thì hỏi qua clarify(text). |
| R12_confirm_before_send | `wrong_boundary` | `send(text="Bản tin này đã được đăng lên Telegram.")` | Gọi send trước xác nhận và dùng câu thông báo đã đăng làm nội dung gửi. Prompt yêu cầu gửi ngay; description và tham số confirmed chưa giải thích điều kiện xác nhận. Tool thực tế trả needs_confirmation, chưa gửi thành công. | Hỏi xác nhận qua clarify(yes_no); chỉ gọi send sau khi nội dung được xác nhận, truyền nội dung thực tế qua text và confirmed=true. |
| R13_parallel_web_and_tweets | `wrong_arg_value` | `lookup(query="AI news", timeframe="day", max_results=5)` và `social_search(query="AI", search_type="Latest", limit=5)` | Gọi đủ hai tool nhưng thiếu topic=news, khiến lookup chạy với mặc định general. Mô tả topic chỉ ghi “Phân loại”. Query cũng khác kỳ vọng như R03. | Yêu cầu truyền rõ topic=news khi tìm tin tức và áp dụng quy ước query như R03. |
| R14_out_of_scope_coding | `out_of_scope` | `send(text=<code Fibonacci>)` | Dùng send để trả lời yêu cầu viết code ngoài phạm vi; cùng vấn đề về phạm vi, yêu cầu chọn tool và mô tả send như R08. | Áp dụng chung quy tắc từ chối yêu cầu ngoài phạm vi bằng văn bản và giới hạn send cho hành động gửi Telegram. |

Cột Failure Type của R03/R13 ghi sai lệch quan sát được (`observed_mismatch`). Nhãn loại case trong run là `wrong_tool`, nhưng cả hai đều chọn đúng tên tool. Các nhận định về nguyên nhân dựa trên cấu hình và log v0, chưa được kiểm chứng riêng cho từng thay đổi.

Trong run v1 so với v0, R03, R08, R10, R11, R13 và R14 chuyển từ fail sang pass theo evaluator. R01 và R05 chuyển từ pass sang fail vì agent gọi `clarify` thay vì `timeline`. R12 vẫn fail: agent hỏi thông tin bằng `clarify(text)` trong khi case kỳ vọng `clarify(yes_no)`; cần xem xét ngữ cảnh thiếu nội dung khi phân tích. Kết quả pass của R08/R14 chưa đồng nghĩa nội dung từ chối đã phù hợp, như phân tích dưới đây.

#### Phân tích kết quả v1

Phân tích [run v1](../../starter_v0/runs/v1_B_base_openai_20261110T182202801200.json) gồm ba case không đạt theo evaluator và hai vấn đề phát hiện khi đọc nội dung trả lời:

| Case ID | Hành vi quan sát được | Cơ sở xác định vấn đề | Hiệu chỉnh |
|---|---|---|---|
| R01_user_tweets_routing | Gọi clarify(text) để hỏi số lượng thay vì timeline cho yêu cầu lấy tweet mới nhất của Sam Altman. | Hỏi thông tin không cản trở thực hiện. Prompt chưa nói rõ cách dùng tham số tùy chọn; description limit chưa nêu cách xử lý yêu cầu một bài mới nhất hoặc không chỉ định số lượng. Log không cho thấy agent đang hỏi về tài khoản. | Làm rõ điều kiện hỏi lại; dùng limit theo yêu cầu hoặc mặc định, không hỏi thêm chỉ vì người dùng không nêu con số. |
| R05_limit_arg | Gọi clarify(yes_no) để xác nhận lại yêu cầu lấy 10 tweet mới nhất của Elon Musk. | Yêu cầu đã có đối tượng và số lượng; thao tác đọc không cần xác nhận lại. Prompt đã yêu cầu xác nhận trước khi gửi, nhưng chưa phân biệt rõ với thao tác đọc; clarify chưa nói khi nào không dùng. Sai lệch thực tế là chọn sai tool, dù nhãn loại case là wrong_arg_value. | Yêu cầu thực hiện trực tiếp thao tác đọc đã đủ thông tin; loại trừ việc dùng clarify để xác nhận lại yêu cầu đọc rõ ràng. |
| R12_confirm_before_send | Gọi clarify(text) để xin nội dung bản tin hoặc URL; không gọi send. | Đã sửa hành vi gửi ngay của v0. Case vẫn fail vì response_type khác yes_no. Input chưa có nội dung bản tin, nên câu hỏi bổ sung có cơ sở; chỉ dẫn xác nhận trước gửi chưa phân biệt bước lấy nội dung và bước xác nhận. | Đồng bộ prompt và description theo thứ tự: lấy nội dung còn thiếu, xác nhận nội dung đã có, rồi mới gửi. Ghi nhận giới hạn của kỳ vọng eval thay vì ép xác nhận khi chưa biết nội dung. |
| R08_out_of_scope | Không gọi tool, nhưng actual_text vẫn nêu nguyên hàm sau câu từ chối. | Được chấm pass vì evaluator chỉ kiểm tra không gọi tool; phản hồi chưa tuân thủ yêu cầu từ chối ngoài phạm vi. Prompt đã có quy tắc từ chối nhưng chưa được model thực hiện đầy đủ. | Làm rõ phản hồi ngoài phạm vi không kèm lời giải, kể cả dưới dạng ví dụ sau câu từ chối. |
| R14_out_of_scope_coding | Không gọi tool, nhưng actual_text vẫn chứa hàm Fibonacci hoàn chỉnh sau câu từ chối. | Cùng vấn đề như R08: sửa được việc gọi send sai mục đích, chưa sửa hoàn chỉnh nội dung phản hồi ngoài phạm vi. | Áp dụng chung quy tắc không cung cấp code thực hiện yêu cầu đã từ chối. |

Kết quả sau hiệu chỉnh được trình bày trong phần v2 ở mục 3 và bảng B1.

### B3. Team Eval Cases

Liệt kê đúng 10 case trong `starter_v0/data/eval_group.json` (5 single turn + 5 multi turn).

| Case ID | What It Tests | Expected Tool/Behavior | Result |
|---|---|---|---|
|  |  |  |  |

### B4. Live Chat Evidence

Lấy từ `starter_v0/transcripts/*.transcript.json`.

| Turn | User Request | Tool Calls | Version Evidence | Outcome |
|---|---|---|---|---|
|  |  |  |  |  |

### B5a. Required Evidence — Tool mới, unit test, UI

| Item | Evidence File | What Worked | Risk / Guardrail |
|---|---|---|---|
| Tool mới (`tools/<tên>/`) |  |  |  |
| Unit test tool mới (≥ 3 test/tool) | `pytest` output (0 failed) |  |  |
| UI (lệnh chạy + link dùng thử) |  |  |  |

Tool unit tests: số test đã viết, và một ví dụ lỗi mà unit test bắt được nhưng eval không bắt được.

### B5. Bonus Evidence

Chỉ điền nếu nhóm làm bonus (ghi riêng, tối đa 10 điểm). Tool có sẵn (`send`, `policy`, `papers`, `paper_text`) không tự được bonus.

| Bonus | Evidence File | What Worked | Risk / Guardrail |
|---|---|---|---|
| Small Local Model | xem B7 |  |  |
| Hơn 3 tool mới (≥ 4) |  |  |  |
| `send` gửi thật lên Telegram sau xác nhận | transcript |  |  |
| Test challenge (0 skipped / regression test) | `pytest` output |  |  |

Test challenge: số bug tìm được trong tool có sẵn (nếu có), cách sửa, và test regression tương ứng.

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

> Khó khăn chính và cách nhóm xử lý. Nếu gặp lỗi kỹ thuật (provider lỗi, hết quota API, tool không chạy), mô tả lỗi và dẫn bằng chứng: run JSON, log, ảnh chụp.

-

## 6. Tổng hợp đóng góp

Chi tiết đóng góp của từng thành viên nằm trong [TEAM.md](../../TEAM.md) và các báo cáo cá nhân `report/team/MSSV_HoTen.md`.

## 7. Hạn chế và hướng cải thiện — B6. Reflection

- Fix nào thuộc `system_prompt.md`?
- Fix nào thuộc `tools.yaml`?
- Failure nào cần review thủ công thay vì chấm tự động?
- Nếu có thêm một vòng, nhóm sẽ thử giả thuyết nào?

## 8. Tài liệu tham khảo

-
