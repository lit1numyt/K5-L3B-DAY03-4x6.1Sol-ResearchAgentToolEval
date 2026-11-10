# Run index

**Bản hiện hành: v8**. Bảng group dưới đây chỉ dùng đợt đo chung: nguyên một bộ 10 câu (5 single + 5 multi), cùng model/evaluator/code tool, một lượt cho mỗi snapshot v4–v9.

| Bản | Base | Group chung | Vai trò |
|---|---:|---:|---|
| v0 | 13/20 | — | baseline |
| v1 | 17/20 | — | vòng 1 |
| v2 | 18/20 | — | vòng 2 |
| v3 | 19/20 | — | v2-tool cũ |
| v4 | 20/20 | 10/10 | nền của v8; v3 cũ |
| v5 | 19/20 | 10/10 | thí nghiệm hồi quy ở base |
| v6 | 17/20 | 10/10 | thí nghiệm hồi quy ở base |
| v7 | 18/20 | 9/10 | H7A, chưa đạt |
| v8 | 20/20 | 10/10 | mặc định, có bibliography |
| v9 | 19/20 | 9/10 | hợp nhất Lam, chưa chọn |

- [v4: 10/10](v4_B_group_openai_20261110T231937353625.json)
- [v5: 10/10](v5_B_group_openai_20261110T231937454478.json)
- [v6: 10/10](v6_B_group_openai_20261110T231937298715.json)
- [v7: 9/10](v7_B_group_openai_20261110T232114470645.json)
- [v8: 10/10](v8_B_group_openai_20261110T232118798370.json)
- [v9: 9/10](v9_B_group_openai_20261110T232114281236.json)

V7 sai G06 (paper_text nhận include_text không hợp lệ); v9 sai G04 (thử gửi chưa duyệt, bị blocked_for_eval). Tất cả run chung đo đủ 10 case, 0 provider error. SHA dataset và đối chiếu từng input/expect ở [protocol](../../report/team/review_evidence/common_group_comparison.json). Base dùng bộ cố định 20 câu đã có; không chạy lại base trong đợt sửa phép so sánh này.

Run group cũ nằm trong history/reviewed_suite, history/bibliography_suite và history/v4_original_suite; không đưa điểm của các bộ khác nhau vào bảng trên. Fixture bibliography cũ nằm cùng thư mục history/bibliography_suite. Run v8 ở đó vẫn là bằng chứng routing tool mới, không phải phép so sánh chung. V7 ban đầu ở candidates/v7_initial; đó là cấu hình khác snapshot H7A được so sánh ở đây.

JSON lịch sử giữ nguyên nội dung; tên file có thể khác metadata gốc. Chỉ di chuyển đường dẫn và cập nhật manifest. 19 run thăm dò đã xóa theo yêu cầu trước đó; các run hồi quy vẫn còn. evidence_audit_experiment chứa script/fixture lịch sử; arxiv là benchmark khác schema.

Eval mới chặn gửi Telegram. Routing/args PASS không bảo đảm final answer đúng hoặc chứng minh gửi thật. Transcript CLI ở ../transcripts/.
