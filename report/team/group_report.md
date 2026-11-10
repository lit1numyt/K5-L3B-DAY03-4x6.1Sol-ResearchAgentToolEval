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

> Tóm tắt các thay đổi chính trong `starter_v0/artifacts/system_prompt.md` và `starter_v0/artifacts/tools.yaml`, và tool mới nhóm viết (tên, làm gì, khi nào agent nên gọi).

### Hiệu chỉnh đề xuất cho v1 — Người 2

Nguyễn Đức Khương Lam — MSSV `2A202604020`. Dựa trên [run v0](../../starter_v0/runs/v0_B_base_openai_20261110T173859866471.json) dùng OpenAI `gpt-4o-mini`: 13/20 case pass (65%), 20/20 case được đo, không có lỗi provider.

Giả thuyết chung: thay các chỉ dẫn đoán/gửi ngay/bắt buộc chọn tool và làm rõ các description còn thiếu sẽ giảm lỗi hỏi lại, ranh giới hành động và arguments quan sát được ở v0.

| Case v0 | Vấn đề quan sát được và cơ sở sửa | Hiệu chỉnh |
|---|---|---|
| R03 | Đúng tool, topic và timeframe; query `AI news` khác `AI` nên bị chấm fail theo so khớp chuỗi. Description query chỉ ghi “Truy vấn”. | Mô tả query giữ chủ đề và từ khóa nội dung; loại tin và thời gian truyền qua topic/timeframe, không tự thêm vào query. Đây là convention chung, không hardcode đáp án AI. |
| R08, R14 | Gọi send để trả lời toán/code; prompt yêu cầu chọn tool và chưa quy định ngoài phạm vi, send chưa nói rõ Telegram. | Bỏ yêu cầu luôn chọn tool; từ chối yêu cầu toán/code độc lập ngoài nhiệm vụ research bằng văn bản; giới hạn send cho Telegram. |
| R10 | Tự chọn sama và không truyền limit=5, phù hợp với chỉ dẫn đoán tài khoản trong prompt. | Hỏi qua clarify(text) khi thiếu tài khoản; giữ số lượng đã cung cấp; làm rõ điều kiện dùng timeline. |
| R11 | Tự tạo URL example.com theo chỉ dẫn giả định URL trong prompt. | Không tạo URL; dùng clarify(text) để hỏi và làm rõ điều kiện dùng fetch. |
| R12 | Gọi send trước khi xác nhận, text là câu thông báo đã đăng; code chặn và trả needs_confirmation. | Hỏi xác nhận qua clarify(yes_no); chỉ send(confirmed=true) sau xác nhận rõ nội dung; làm rõ text là nội dung cần gửi. |
| R13 | Gọi đủ hai tool nhưng thiếu topic=news; tool chạy với mặc định general. Query cũng lệch theo cách chấm như R03. | Mô tả topic phải truyền news khi tìm tin tức; dùng convention query chung như R03. |

Chỉ sửa system prompt và các description liên quan; giữ nguyên tên tool, schema, default, code thực thi và eval case. Kiểm tra offline: `cd starter_v0 && .venv/bin/python -m pytest -q` đạt 62 passed, 17 skipped (TODO có sẵn). Run v1 dùng cùng OpenAI `gpt-4o-mini` như v0: 17/20 case pass (85%), 20/20 case được đo, không có lỗi provider. Vì v1 thay đổi nhiều chỉ dẫn và description cùng lúc, không thể quy mức tăng cho riêng một thay đổi.

## 4. Kết quả — PHẦN B: Chi tiết và bằng chứng

### B1. Version Evidence

Lấy từ `starter_v0/artifacts/version_log.csv` và `starter_v0/runs/*.json`. Chỉ dùng run có `provider_error_cases == 0` và `measured_cases == total_cases`.

| Version | Changed Artifact | Hypothesis | Metric Before | Metric After | Run File |
|---|---|---|---:|---:|---|
| v0 | baseline | Đo hành vi ban đầu | — | 0.65 | [run v0](../../starter_v0/runs/v0_B_base_openai_20261110T173859866471.json) |
| v1 | system prompt + tools.yaml | Làm rõ hỏi lại, xác nhận, phạm vi và arguments giúp giảm lỗi | 0.65 | 0.85 | [run v1](../../starter_v0/runs/v1_B_base_openai_20261110T182202801200.json) |
| v2 |  |  |  |  |  |
| v3 |  |  |  |  |  |

### B2. Failure Analysis

Lấy từ `results[*].result.failures` trong run JSON.

| Case ID | Failure Type | Actual Tool Calls | What Failed | Fix |
|---|---|---|---|---|
|  |  |  |  |  |

So với v0, R03, R08, R10, R11, R13 và R14 chuyển từ fail sang pass. R01 và R05 chuyển từ pass sang fail vì agent gọi `clarify` thay vì `timeline`. R12 vẫn fail: agent hỏi thông tin bằng `clarify(text)` trong khi case kỳ vọng `clarify(yes_no)`; cần xem xét ngữ cảnh thiếu nội dung khi phân tích.

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
