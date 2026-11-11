# Team

## Thông tin nhóm

- Tên nhóm: 4x6.1Sol
- Lớp: L3B
- Repo nhóm: `K5-L3B-DAY03-4x6.1Sol-ResearchAgentToolEval` (xem [SUBMISSION.md](SUBMISSION.md))
- URL repo, nhánh nộp, commit chốt: [GitHub](https://github.com/lit1numyt/K5-L3B-DAY03-4x6.1Sol-ResearchAgentToolEval), nhánh `main`; [commit đầu nhánh main](https://github.com/lit1numyt/K5-L3B-DAY03-4x6.1Sol-ResearchAgentToolEval/commit/main).

## Thành viên

| STT | Họ tên | MSSV | Email | GitHub | Vai trò |
| --: | ------ | ---- | ----- | ------ | ------- |
|   1 | Chu Nguyễn Tùng Dương | 2A202604016 |       |        | Eval, versioning, phân tích; bổ sung v8 và rà soát UI có AI hỗ trợ |
|   2 | Nguyễn Đức Khương Lam | 2A202604020 |       |        | Phân tích eval, hiệu chỉnh prompt và mô tả tool, kiểm tra v10 |

## Cá nhân

Mỗi thành viên đồng thời tạo một báo cáo riêng trong `report/` theo dạng:

```text
report/team/MSSV_HoTen.md
```

Ví dụ: `report/team/20241234_NguyenVanAn.md`.

Sao chép mục dưới đây cho từng thành viên.

## ChuNguyenTungDuong-2A202604016

### Phần việc phụ trách

- Chạy/lưu eval, theo dõi phiên bản, đối chiếu lỗi và tổng hợp bằng chứng vào báo cáo.

### Đóng góp cụ thể

- Lưu baseline và các run qua commit 341c4ce, b7691c0, 2aaa3cb, c17dc2e.
- Trong phần bổ sung v8, dùng Codex hỗ trợ thêm build_bibliography, test/case eval, sửa UI và kiểm tra bằng API/trình duyệt thật. Không nhận tác giả UI ban đầu hoặc các tool đã có.

### Bằng chứng

- [Báo cáo cá nhân](report/team/2A202604016_ChuNguyenTungDuong.md), [báo cáo nhóm](report/team/group_report.md), [version log](starter_v0/artifacts/version_log.csv).
- Hợp nhất commit 54d010f của Nguyễn Đức Khương Lam thành v9, giữ tác giả và chạy kiểm chứng riêng (19/20 base, 9/10 group). V8 vẫn là mặc định; không nhận phần hiệu chỉnh của Lam là do mình viết.
- Cố định cùng 10 case group cho v4–v9 và chạy lại sáu cấu hình; xem [protocol và kết quả](report/team/review_evidence/common_group_comparison.json).
- Hoàn thiện test tool (200 passed, 0 skipped, 0 failed), phát hiện/sửa guard boolean của send bằng regression offline.
- Thay đổi v8, bản tích hợp v9, UI và báo cáo được lưu cùng nhánh nộp `main`; mốc commit nằm trong thông tin nhóm ở trên. Các thành viên còn lại tự bổ sung phần mình.

## NguyenDucKhuongLam-2A202604020

### Phần việc phụ trách

- Phân tích kết quả eval, hiệu chỉnh system prompt và mô tả tool; kiểm tra quy trình xác nhận Telegram.

### Đóng góp cụ thể

- Phân tích và hiệu chỉnh v2; làm rõ phạm vi nhiệm vụ và xác nhận gửi trong commit 54d010f, sau đó được hợp nhất vào v9.
- Phân tích lỗi gửi sớm ở v8 và hiệu chỉnh v10 từ nền v8. Các lượt eval v10 được lưu riêng: 20/20 base và 10/10 group chung; thử xác nhận trước khi gửi, sau đó có transcript tool trả gửi thành công.

### Bằng chứng

- [Báo cáo cá nhân](report/team/2A202604020_NguyenDucKhuongLam.md), [giả thuyết và kết quả v10](report/team/review_evidence/v10_hypothesis.md), [version log](starter_v0/artifacts/version_log.csv).

## NguyenHuuAn-2A202604024

### Phần việc phụ trách

- Bổ sung tool mới và chứng minh code của tool hoạt động đúng.

### Đóng góp cụ thể

- commit `1c577d3` tại branch `codex/find-article-candidates`, tuy nhiên chưa được merge vào branch `main` do tool mới hoạt động không đúng. Điểm benchmark tăng ảo do model hoạt động không nhất quán.

### Bằng chứng

- [Báo cáo cá nhân](report/team/2A202604024_NguyenHuuAn.md)
- Chưa có bằng chứng tại branch `main` do hiểu sai vấn đề và chưa hoàn thành nhiệm vụ được giao. Các tool không cải thiện benchmark đều chưa được đẩy lên.
