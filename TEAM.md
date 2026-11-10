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
|   2 |        |      |       |        |         |

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
- Thay đổi v8, bản tích hợp v9, UI và báo cáo được lưu cùng nhánh nộp `main`; mốc commit nằm trong thông tin nhóm ở trên. Các thành viên còn lại tự bổ sung phần mình.
