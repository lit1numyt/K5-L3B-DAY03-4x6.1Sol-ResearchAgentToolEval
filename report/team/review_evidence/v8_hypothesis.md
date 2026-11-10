# Giả thuyết v8 — ghi trước khi chạy

Xuất phát từ snapshot v4 có run base 20/20 và group đã siết 10/10. H8: thêm một tool local chỉ dùng khi yêu cầu xuất tài liệu tham khảo, với routing rõ ràng và metadata không bịa, sẽ đáp ứng tác vụ BibTeX mới mà không làm giảm routing base. Không sửa rules/description tool cũ trong vòng này ngoài tái tuần tự hóa YAML; UI là phần kỹ thuật riêng.

Tool mới: build_bibliography, code/TOOL.md/registry/YAML và ≥3 test offline. Bộ nhóm vẫn đúng 10 case, G05 thay audit trùng phạm vi bằng export BibTeX. Bộ base và extension cố định giữ nguyên. Cùng provider OpenAI gpt-4o-mini; send bị chặn khi eval. Mục tiêu: base 20/20, group v8 10/10; chỉ ghi là đạt sau run thật. Dataset group v8 khác group v4 nên không so trực tiếp như cùng phép đo.
