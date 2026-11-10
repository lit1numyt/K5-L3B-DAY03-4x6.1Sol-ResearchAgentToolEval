# Run index

**Bản hiện hành: v8**, phát triển từ v4 và thêm build_bibliography. V4 gốc vẫn giữ nguyên.

| Bản | Base | Group | Vai trò |
|---|---:|---:|---|
| v0 | 13/20 | — | baseline |
| v1 | 17/20 | — | vòng 1 |
| v2 | 18/20 | — | vòng 2 |
| v3 | 19/20 | — | v2-tool cũ |
| v4 | 20/20 | 10/10 suite đã siết | nền của v8; v3 cũ |
| v5 | 19/20 | 10/10 | thí nghiệm hồi quy |
| v6 | 17/20 | 10/10 | thí nghiệm hồi quy |
| v7 H7A | 18/20 | 9/10 | thí nghiệm chưa đạt |
| v8 | 20/20 | 10/10 suite v8 | hiện hành, có tool mới |
| v9 | 19/20 | 9/10 cùng suite v8 | hợp nhất Lam, chưa chọn làm mặc định |

V8 dùng v8_B_base_openai_20261110T223125274893.json và v8_B_group_openai_20261110T223032240551.json, cùng hash. V4 base gốc v4_B_base_openai_20261110T213656627758.json còn nguyên. Group v4 cũ 9/10 trên dataset khác, giữ trong [history/v4_original_suite](history/v4_original_suite/v4_B_group_openai_20261110T213600677281.json); v4_B_group_openai_20261110T221923054166.json là group đã siết 10/10. Group v8 thay G05 bằng bibliography nên không coi cùng dataset.

V9 dùng v9_B_base_openai_20261110T230751104659.json và v9_B_group_openai_20261110T230818905094.json, cùng snapshot v9, đủ measured và 0 provider error. R12 sai response_type; G04 gọi send trước khi duyệt và bị blocked_for_eval. R08/R14 vẫn trả lời ngoài phạm vi dù no_tool PASS. H9 chưa đạt điều kiện chọn, nên cấu hình mặc định vẫn là v8. V9 giữ nguyên kết quả để đối chiếu; không chạy lại chỉ để tìm điểm cao hơn.

V7 ban đầu ở candidates/v7_initial/, snapshot ở artifacts/v7_candidates/initial/. JSON lịch sử giữ nguyên byte nên metadata version/run_id/đường dẫn có thể khác tên file mới; dùng hash và manifest đối chiếu. 19 run thăm dò đã xóa theo yêu cầu, các run chính vẫn còn. evidence_audit_experiment chứa script/fixture lịch sử; arxiv là benchmark khác schema.

Eval mới chặn gửi Telegram. Routing/args PASS không bảo đảm dữ liệu/final answer đúng. Transcript CLI thật ở ../transcripts/.
