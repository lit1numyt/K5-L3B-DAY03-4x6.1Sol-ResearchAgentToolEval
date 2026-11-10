# Artifact versions

system_prompt.md và tools.yaml hiện trùng byte với **v8**. V8 phát triển từ snapshot v4, chỉ thêm routing/declaration build_bibliography; không thay snapshot v4.

v0/v1/v2 là lịch sử; v3 là v2-tool cũ; v4 là v3 cũ có base 20/20; v5/v6/v7 là các thí nghiệm có hồi quy. V8 có run mới base 20/20 và group 10/10. Không dựng lại lịch sử tăng đều.

- v7_candidates/initial/: snapshot lần v7 đầu, ứng với runs/candidates/v7_initial/.
- eval_group_v4.json: suite nguyên thủy.
- eval_group_v4_reviewed.json: suite đã siết dùng cho v4/v5/v6/v7.
- data/eval_group.json: suite v8, thay G05 bằng bibliography, giữ 5 single + 5 multi.
- research_paper_v4.py: implementation trước bổ sung validate/error handling chung, không phải tool đăng ký riêng.

Run JSON giữ metadata gốc dù đổi tên file; đối chiếu hash, version_log.csv và manifest ở report/team/review_evidence/. H7A và H8 ghi trước lần chạy tương ứng. Metric/hypothesis không được sửa để tạo đường tăng giả.
