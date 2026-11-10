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

### Hiệu chỉnh system prompt và tool declaration từ baseline v0

Dựa trên các lỗi của baseline v0, nhóm hiệu chỉnh [system prompt](../../starter_v0/artifacts/system_prompt.md) và [tool declaration](../../starter_v0/artifacts/tools.yaml) để chuẩn bị cho v1. Giả thuyết của vòng hiệu chỉnh là việc loại bỏ các chỉ dẫn khuyến khích đoán thông tin, gửi ngay và luôn chọn tool, đồng thời làm rõ điều kiện sử dụng và tham số của các tool liên quan, sẽ giảm các lỗi đã quan sát được ở v0.

Trong system prompt, nhóm thay chỉ dẫn tự đoán tài khoản hoặc URL bằng yêu cầu hỏi lại qua `clarify(response_type="text")` khi thông tin chưa có trong yêu cầu và ngữ cảnh. Các chi tiết đã được cung cấp, như số lượng bài đăng, phải được giữ lại. Với yêu cầu gửi Telegram, agent phải hỏi xác nhận nội dung qua `clarify(response_type="yes_no")` và chỉ gọi `send(confirmed=true)` sau khi người dùng xác nhận rõ ràng. Nhóm cũng bỏ yêu cầu luôn chọn một tool, quy định từ chối ngắn gọn các yêu cầu giải toán hoặc viết code độc lập ngoài nhiệm vụ research, và chỉ thông báo gửi thành công khi tool trả về `status="sent"`.

Trong tool declaration, nhóm làm rõ khi nào dùng `clarify`, điều kiện đủ thông tin để gọi `timeline` và `fetch`, cùng ý nghĩa của `send.text` và `send.confirmed`. Với `lookup`, `query` giữ chủ đề và từ khóa nội dung; loại tin và khoảng thời gian được truyền qua `topic` và `timeframe`. Khi người dùng yêu cầu tin tức, agent phải truyền rõ `topic="news"`. Quy tắc này áp dụng chung cho các chủ đề tìm kiếm, không gắn với một câu hỏi cụ thể trong bộ eval.

Các thay đổi giữ nguyên tên tool, schema, giá trị mặc định, code thực thi và bộ eval. Kiểm tra offline bằng `cd starter_v0 && .venv/bin/python -m pytest -q` đạt **62 passed, 17 skipped**; các test bị bỏ qua là TODO có sẵn trong starter. [Run v1](../../starter_v0/runs/v1_B_base_openai_20261110T182202801200.json) dùng cùng OpenAI `gpt-4o-mini` như v0: **17/20 case đạt (85%)**, 20/20 case được đo, không có lỗi provider. Vì v1 thay đổi nhiều chỉ dẫn và description cùng lúc, chưa thể xác định mức đóng góp riêng của từng thay đổi.

### Giả thuyết và hiệu chỉnh từ v1 lên v2

**Người phân tích và hiệu chỉnh:** Nguyễn Đức Khương Lam — MSSV `2A202604020`. **Provider/model đối chiếu:** OpenAI `gpt-4o-mini`. **Mốc so sánh:** [run v1](../../starter_v0/runs/v1_B_base_openai_20261110T182202801200.json), case accuracy **85% (17/20)**, đủ 20 case được đo và không có lỗi provider.

**Vấn đề quan sát được.** R01 hỏi thêm số lượng dù yêu cầu một tweet mới nhất đã có thể thực hiện; R05 xin xác nhận lại yêu cầu đọc đã có đối tượng và số lượng. R12 không còn gửi ngay nhưng hỏi nội dung bằng `text`, khác kỳ vọng `yes_no` của eval; input chưa cung cấp bản tin nên chưa thể xem việc hỏi nội dung là sai. R08 và R14 không gọi tool nhưng vẫn cung cấp lời giải/code sau câu từ chối, một vấn đề mà điểm pass tự động chưa phản ánh. Chi tiết tool calls và cơ sở phân tích nằm ở B2.

**Giả thuyết H2.** Nếu system prompt và tool declaration phân biệt rõ điều kiện thực hiện yêu cầu, hỏi thông tin, xác nhận gửi và từ chối ngoài phạm vi, agent sẽ giảm việc hỏi lại không cần thiết và tuân thủ phạm vi phản hồi tốt hơn, trong khi vẫn hỏi khi thiếu thông tin thiết yếu và xác nhận trước khi gửi. Cơ sở của giả thuyết là v1 đã yêu cầu hỏi lại và từ chối nhưng chưa làm rõ đầy đủ các điều kiện trên; log thể hiện việc hỏi thừa và phản hồi trái với câu từ chối. Đây là nhận định cần kiểm chứng, không phải nguyên nhân đã được chứng minh độc lập.

**Thay đổi đã thực hiện để chuẩn bị v2.**

| Vấn đề | Thay đổi trong system prompt | Thay đổi trong tool declaration | Hành vi kỳ vọng |
|---|---|---|---|
| R01: hỏi số lượng không cần thiết | Chỉ hỏi khi thiếu thông tin cản trở thực hiện; dùng giá trị người dùng cung cấp, giá trị được thể hiện rõ hoặc mặc định cho tham số tùy chọn. | Làm rõ điều kiện dùng clarify; limit dùng số lượng được yêu cầu, 1 khi chỉ cần một bài mới nhất, hoặc mặc định 5 khi không chỉ định. | Gọi timeline trực tiếp, không hỏi thêm số lượng. |
| R05: xác nhận lại thao tác đọc | Thực hiện trực tiếp yêu cầu đọc đã rõ, không yêu cầu xác nhận lại. | clarify không dùng để xác nhận yêu cầu đọc đã đủ thông tin. | Gọi timeline với screenname=elonmusk và limit=10. |
| R12: chưa tách bước lấy nội dung và xác nhận | Thiếu nội dung thì hỏi bằng text; có nội dung nhưng chưa xác nhận thì hỏi bằng yes_no; chỉ gửi sau xác nhận rõ nội dung đó. | Đồng bộ clarify.response_type và điều kiện sử dụng send. | Không gửi khi chưa có nội dung hoặc chưa được xác nhận; câu hỏi phù hợp với thông tin đang thiếu. |
| R08, R14: vẫn trả lời sau câu từ chối | Phản hồi ngoài phạm vi chỉ giải thích ngắn gọn phạm vi hỗ trợ và mời yêu cầu nghiên cứu phù hợp; không kèm lời giải/code của yêu cầu đã từ chối. | Không thay đổi. | Không gọi tool và không cung cấp lời giải/code ngoài phạm vi. |

Các thay đổi áp dụng thành quy tắc chung, không chèn case ID hay đáp án mẫu vào cấu hình. Nhóm giữ nguyên quy tắc không đoán tài khoản/URL, giữ thông tin đã được cung cấp, arguments tìm tin và xác nhận trước khi gửi; không đổi tên tool, schema, giá trị mặc định, code thực thi hoặc bộ eval.

**Cách kiểm chứng.** Chạy lại toàn bộ `data/eval_base.json` với cùng provider/model bằng lệnh dưới đây, sau đó so sánh case accuracy, tool routing accuracy, argument accuracy và multiturn accuracy với v1. Kiểm tra riêng R01/R05 có chuyển sang timeline hay không; đọc cả câu hỏi của R12 và actual_text của R08/R14. Đối chiếu các case đã cải thiện từ v0 và toàn bộ case còn lại để phát hiện hồi quy. Run chỉ hợp lệ khi `provider_error_cases == 0` và `measured_cases == total_cases == 20`.

```bash
python run_eval.py --provider openai --model gpt-4o-mini --version v2 --suite base --eval-cases data/eval_base.json
```

**Tiêu chí đánh giá và giới hạn.** Giả thuyết được hỗ trợ nếu giảm được việc hỏi thừa ở R01/R05, phản hồi R08/R14 tuân thủ phạm vi và không làm mất các hành vi đúng của v1. R12 có thể vẫn không đạt kỳ vọng yes_no của evaluator khi thiếu nội dung; phải báo cáo nguyên trạng điểm chấm và đánh giá ngữ nghĩa riêng, không tính lại điểm. Vòng này cùng hiệu chỉnh việc hỏi lại và phản hồi ngoài phạm vi nên chỉ đánh giá được tác động của cả bản sửa, không xác định đóng góp riêng của từng thay đổi.

**Trạng thái kiểm chứng.** Kiểm tra offline sau sửa đạt **62 passed, 17 skipped**; các test bị bỏ qua là TODO có sẵn, không phải kết quả eval model. [Run v2](../../starter_v0/runs/v2_B_base_openai_20261110T185609495800.json) có 18/20 case đạt (90%), 20/20 case được đo và không có lỗi provider. So với v1, R01 và R05 chuyển từ fail sang pass; M06 chuyển từ pass sang fail. R12 vẫn fail vì evaluator kỳ vọng `yes_no` trong khi agent dùng `text` để hỏi nội dung còn thiếu. R08 và R14 từ chối không kèm lời giải hoặc code trong run này. Kết quả hỗ trợ một phần H2 nhưng có hồi quy M06; không thể tách tác động của từng thay đổi.

## 4. Kết quả — PHẦN B: Chi tiết và bằng chứng

### B1. Version Evidence

Lấy từ `starter_v0/artifacts/version_log.csv` và `starter_v0/runs/*.json`. Chỉ dùng run có `provider_error_cases == 0` và `measured_cases == total_cases`.

| Version | Changed Artifact | Hypothesis | Metric Before | Metric After | Run File |
|---|---|---|---:|---:|---|
| v0 | baseline | Đo hành vi ban đầu | — | 0.65 | [run v0](../../starter_v0/runs/v0_B_base_openai_20261110T173859866471.json) |
| v1 | system prompt + tools.yaml | Làm rõ hỏi lại, xác nhận, phạm vi và arguments giúp giảm lỗi | 0.65 | 0.85 | [run v1](../../starter_v0/runs/v1_B_base_openai_20261110T182202801200.json) |
| v2 | system prompt + tools.yaml | H2: phân biệt điều kiện thực hiện, hỏi thông tin, xác nhận gửi và từ chối ngoài phạm vi | 0.85 | 0.90 | [run v2](../../starter_v0/runs/v2_B_base_openai_20261110T185609495800.json) |
| v3 |  |  |  |  |  |

### B2. Failure Analysis

Theo [run baseline v0](../../starter_v0/runs/v0_B_base_openai_20261110T173859866471.json), model OpenAI `gpt-4o-mini` đạt **13/20 case (65%)**. Cả 20 case đều được đo và không có lỗi provider. Bảng dưới đối chiếu 7 case không đạt với prompt, tool declaration và kết quả tool để xác định cơ sở hiệu chỉnh.

| Case ID | Failure Type | Actual Tool Calls | What Failed | Fix |
|---|---|---|---|---|
| R03_web_news_routing | `wrong_arg_value` | `lookup(query="AI news", topic="news", timeframe="day", max_results=5)` | Chọn đúng tool, loại tin và thời gian; query khác `AI` nên không đạt theo cách chấm so khớp chuỗi. Mô tả query chưa có quy ước tách chủ đề khỏi loại tin; chưa có bằng chứng truy vấn sai về ngữ nghĩa. | Làm rõ query giữ chủ đề và từ khóa nội dung, còn loại tin và thời gian truyền qua topic/timeframe. |
| R08_out_of_scope | `out_of_scope` | `send(text=<lời giải tích phân>)` | Gọi tool cho yêu cầu ngoài phạm vi. Prompt chưa quy định cách xử lý và yêu cầu luôn chọn tool; mô tả send chưa nói rõ đích gửi Telegram. | Bỏ yêu cầu luôn chọn tool, quy định từ chối bằng văn bản và làm rõ send không phải kênh trả lời trong cuộc chat. |
| R10_missing_handle | `missing_info` | `timeline(screenname="sama")` | Tự chọn tài khoản khi người dùng chưa cung cấp và không truyền số lượng 5. Prompt trực tiếp khuyến khích đoán tài khoản; mô tả clarify/timeline chưa nêu rõ điều kiện hỏi lại. | Yêu cầu hỏi tài khoản bằng clarify(text), không tự chọn tài khoản và giữ số lượng người dùng đã cung cấp. |
| R11_missing_url | `missing_info` | `fetch(url="https://example.com/article")` | Tự tạo URL thay vì hỏi lại, phù hợp với chỉ dẫn giả định URL trong prompt; mô tả fetch chưa ràng buộc nguồn URL. | Bỏ chỉ dẫn giả định URL; chỉ dùng fetch khi URL đã có trong yêu cầu hoặc ngữ cảnh, nếu thiếu thì hỏi qua clarify(text). |
| R12_confirm_before_send | `wrong_boundary` | `send(text="Bản tin này đã được đăng lên Telegram.")` | Gọi send trước xác nhận và dùng câu thông báo đã đăng làm nội dung gửi. Prompt yêu cầu gửi ngay; description và tham số confirmed chưa giải thích điều kiện xác nhận. Tool thực tế trả needs_confirmation, chưa gửi thành công. | Hỏi xác nhận qua clarify(yes_no); chỉ gọi send sau khi nội dung được xác nhận, truyền nội dung thực tế qua text và confirmed=true. |
| R13_parallel_web_and_tweets | `wrong_arg_value` | `lookup(query="AI news", timeframe="day", max_results=5)` và `social_search(query="AI", search_type="Latest", limit=5)` | Gọi đủ hai tool nhưng thiếu topic=news, khiến lookup chạy với mặc định general. Mô tả topic chỉ ghi “Phân loại”. Query cũng khác kỳ vọng như R03. | Yêu cầu truyền rõ topic=news khi tìm tin tức và áp dụng quy ước query như R03. |
| R14_out_of_scope_coding | `out_of_scope` | `send(text=<code Fibonacci>)` | Dùng send để trả lời yêu cầu viết code ngoài phạm vi; cùng vấn đề về phạm vi, yêu cầu chọn tool và mô tả send như R08. | Áp dụng chung quy tắc từ chối yêu cầu ngoài phạm vi bằng văn bản và giới hạn send cho hành động gửi Telegram. |

Failure Type của R03 và R13 trong bảng phản ánh sai lệch quan sát được (`observed_mismatch`); nhãn loại case trong run là `wrong_tool`, nhưng cả hai đều chọn đúng tên tool. Các cơ sở trên là giả thuyết dựa trên nội dung cấu hình và log v0; tác động của từng thay đổi chưa được kiểm chứng riêng bằng eval sau hiệu chỉnh.

So với v0, R03, R08, R10, R11, R13 và R14 chuyển từ fail sang pass. R01 và R05 chuyển từ pass sang fail vì agent gọi `clarify` thay vì `timeline`. R12 vẫn fail: agent hỏi thông tin bằng `clarify(text)` trong khi case kỳ vọng `clarify(yes_no)`; cần xem xét ngữ cảnh thiếu nội dung khi phân tích.

#### Phân tích kết quả v1

Bằng chứng: [run v1](../../starter_v0/runs/v1_B_base_openai_20261110T182202801200.json). Bảng dưới phân biệt lỗi do evaluator ghi nhận với vấn đề phát hiện khi đọc nội dung trả lời. Các nhận định về nguyên nhân là cơ sở đặt giả thuyết, không phải kết luận nhân quả đã được kiểm chứng độc lập.

| Case ID | Hành vi quan sát được | Cơ sở xác định vấn đề | Hiệu chỉnh |
|---|---|---|---|
| R01_user_tweets_routing | Gọi clarify(text) để hỏi số lượng thay vì timeline cho yêu cầu lấy tweet mới nhất của Sam Altman. | Hỏi thông tin không cản trở thực hiện. Prompt chưa nói rõ cách dùng tham số tùy chọn; description limit chưa nêu cách xử lý yêu cầu một bài mới nhất hoặc không chỉ định số lượng. Log không cho thấy agent đang hỏi về tài khoản. | Làm rõ điều kiện hỏi lại; dùng limit theo yêu cầu hoặc mặc định, không hỏi thêm chỉ vì người dùng không nêu con số. |
| R05_limit_arg | Gọi clarify(yes_no) để xác nhận lại yêu cầu lấy 10 tweet mới nhất của Elon Musk. | Yêu cầu đã có đối tượng và số lượng; thao tác đọc không cần xác nhận lại. Prompt đã yêu cầu xác nhận trước khi gửi, nhưng chưa phân biệt rõ với thao tác đọc; clarify chưa nói khi nào không dùng. Sai lệch thực tế là chọn sai tool, dù nhãn loại case là wrong_arg_value. | Yêu cầu thực hiện trực tiếp thao tác đọc đã đủ thông tin; loại trừ việc dùng clarify để xác nhận lại yêu cầu đọc rõ ràng. |
| R12_confirm_before_send | Gọi clarify(text) để xin nội dung bản tin hoặc URL; không gọi send. | Đã sửa hành vi gửi ngay của v0. Case vẫn fail vì response_type khác yes_no. Input chưa có nội dung bản tin, nên câu hỏi bổ sung có cơ sở; chỉ dẫn xác nhận trước gửi chưa phân biệt bước lấy nội dung và bước xác nhận. | Đồng bộ prompt và description theo thứ tự: lấy nội dung còn thiếu, xác nhận nội dung đã có, rồi mới gửi. Ghi nhận giới hạn của kỳ vọng eval thay vì ép xác nhận khi chưa biết nội dung. |
| R08_out_of_scope | Không gọi tool, nhưng actual_text vẫn nêu nguyên hàm sau câu từ chối. | Được chấm pass vì evaluator chỉ kiểm tra không gọi tool; phản hồi chưa tuân thủ yêu cầu từ chối ngoài phạm vi. Prompt đã có quy tắc từ chối nhưng chưa được model thực hiện đầy đủ. | Làm rõ phản hồi ngoài phạm vi không kèm lời giải, kể cả dưới dạng ví dụ sau câu từ chối. |
| R14_out_of_scope_coding | Không gọi tool, nhưng actual_text vẫn chứa hàm Fibonacci hoàn chỉnh sau câu từ chối. | Cùng vấn đề như R08: sửa được việc gọi send sai mục đích, chưa sửa hoàn chỉnh nội dung phản hồi ngoài phạm vi. | Áp dụng chung quy tắc không cung cấp code thực hiện yêu cầu đã từ chối. |

Việc kiểm chứng vòng tiếp theo cần chạy lại toàn bộ 20 case với cùng provider/model, đối chiếu cả metric và actual_text. Ngoài R01, R05 và R12, cần kiểm tra các case đã cải thiện từ v0, nội dung R08/R14 và sáu case multi-turn để đánh giá hồi quy. Chỉ sử dụng run có `provider_error_cases == 0` và `measured_cases == total_cases`.

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
