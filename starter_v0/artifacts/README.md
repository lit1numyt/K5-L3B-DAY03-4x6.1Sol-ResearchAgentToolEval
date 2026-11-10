# Artifact versions

system_prompt.md và tools.yaml trùng byte với **v8**, cấu hình mặc định. Các snapshot v0–v9 giữ nguyên; đợt sửa phép so sánh không sửa prompt, description hay code tool.

V3 là v2-tool cũ; v4 là v3 cũ, có base 20/20. V5–v7 có hồi quy ở base. V8 thêm build_bibliography trên nền v4. V9 hợp nhất quy tắc xác nhận Telegram/phạm vi nhiệm vụ của Lam; base 19/20, group chung 9/10 nên chưa được chọn. V8 giữ base 20/20 và group chung mới đo 10/10.

**Bộ group chung:** data/eval_group.json giữ nguyên byte của eval_group_v4_reviewed.json. V4–v9 đều được đo lại trên cùng 10 câu, đúng 5 single + 5 multi; G05 là audit nguồn trùng. Không thay G05 theo tool mà phiên bản có. Protocol/hash/input verification nằm trong report/team/review_evidence/common_group_comparison.json.

- eval_group_v4.json: bộ group nguyên thủy, chỉ dùng đối chiếu lịch sử.
- eval_group_v4_reviewed.json: snapshot của bộ đã siết và nay là bộ so sánh chung.
- runs/history/bibliography_suite/eval_cases.json: bộ từng thay G05 bằng bibliography; giữ riêng để kiểm tra tool mới, không trộn điểm với bảng chung.
- v7_candidates/initial/: cấu hình v7 ban đầu, khác snapshot H7A chính.
- research_paper_v4.py: implementation trước sửa validate/error handling; không phải tool đăng ký riêng.

Các run group cũ chuyển vào history, giữ nguyên JSON; version_log.csv đánh dấu historical và có sáu dòng group chung mới. H7A/H8/H9 vẫn ghi đúng bối cảnh trước từng lượt thử, không viết lại giả thuyết lịch sử theo kết quả sau này. Một phép đo chung mới không biến bộ phát triển thành bộ kiểm tra chưa từng thấy.
