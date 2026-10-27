# Xử lý dữ liệu Excel định kỳ với Claude Code

[English](README.md)

Mỗi tuần, mỗi tháng bạn nhận một file Excel và phải làm sạch, lọc, tính toán theo cùng một cách. Dự án này
biến việc đó thành một quy trình cố định: thả file vào, nói với Claude "chạy kỳ mới", nhận lại kết quả kèm
biên bản kiểm tra. Lần nào cũng chạy cùng một bộ script nên kết quả nhất quán. Dòng nào bị loại đều có lý
do, dòng kết quả nào cũng truy ngược được về dòng Excel gốc.

Bạn không cần biết code. Claude hỏi bạn về dữ liệu, rồi tự cấu hình.

Dùng được bằng tiếng Việt và tiếng Anh. Claude trả lời theo ngôn ngữ bạn viết, và một dòng cấu hình
(`language: vi` hoặc `en`) đổi ngôn ngữ của log, lý do loại dòng và tên file kết quả.

## Bắt đầu

Cần có [Claude Code](https://claude.com/claude-code) và Python 3.9 trở lên.

```bash
git clone https://github.com/nixthinh-bit/data-processing-project.git
```

Mở thư mục vừa clone bằng Claude Code rồi nói:

> Tôi mới clone dự án này, hãy hướng dẫn tôi bắt đầu với dữ liệu của tôi.

Claude sẽ cài môi trường, chạy thử bộ mẫu để bạn xem kết quả trông thế nào, rồi dẫn bạn qua 6 bước:

| Bước | Bạn làm | Claude làm |
|---|---|---|
| 1. Nhận file | Đưa một file Excel thật của một kỳ | Chép vào `data/raw/`, hỏi file đến từ đâu, ai dùng kết quả |
| 2. Hiểu từng cột | Trả lời vài câu: mỗi dòng là gì, cái gì không được lặp, cột tiền nào phải khớp tổng | Khảo sát file, đề xuất ý nghĩa từng cột, ghi lại câu trả lời |
| 3. Nói cần làm gì | Mô tả kết quả bạn muốn: lọc gì, bỏ trùng thế nào, tính thêm cột gì, xếp ra sao | Chuyển yêu cầu thành cấu hình và các bước xử lý, đọc lại cho bạn duyệt |
| 4. Chạy thử | Xem kết quả và log | Chạy, giải thích từng lỗi bằng lời thường, sửa tới khi qua các kiểm tra bắt buộc |
| 5. Kiểm và chốt | Đối chiếu tay vài dòng với file gốc, nói đúng hay chưa | Sửa và chạy lại, ghi các quyết định của bạn vào sổ |
| 6. Chốt quy tắc | Duyệt ngưỡng cảnh báo Claude đề xuất | Ghi ngưỡng, hướng dẫn bạn cách chạy các kỳ sau |

Từ kỳ sau, bạn chỉ cần thả file mới vào `data/raw/` và nói "chạy kỳ mới".

## Mỗi lần chạy được kiểm tra những gì

| Tầng | Kiểm tra | Nếu sai |
|---|---|---|
| 1. Cấu trúc | Đủ cột, đúng kiểu, không trùng, ô trống trong ngưỡng, file gốc không bị sửa | Chặn, không xuất kết quả |
| 2. Đối soát | Số dòng vào = ra + bị loại, tổng tiền khớp | Chặn, không xuất kết quả |
| 3. Nghiệp vụ | Giá trị hợp lý: không âm, đúng khoảng, đúng thứ tự ngày, quy tắc chéo cột | Cảnh báo |
| 4. Biến động | Lệch nhiều so với kỳ trước | Cảnh báo |
| 5. Người | Vài dòng ngẫu nhiên để bạn đối chiếu tay | Bạn xác nhận |

Kết quả mỗi lần chạy nằm trong một thư mục riêng ở `outputs/`, không bao giờ ghi đè lần trước. Log nằm ở
`logs/run_log/`, do script ghi chứ không phải Claude tóm tắt. Vài dòng trong một log thật:

```
clean:   1 dòng: arr_2025: '$5,040' mơ hồ: có thể là số thập phân hoặc số có dấu hàng nghìn kiểu khác
[CHẶN] ✓ Số dòng: vào 103 = ra 72 + loại 31
[CHẶN] ✗ Không trùng khoá ['ma_kh']: 2 dòng trùng, vd tai_ky_Q4.2026_2026-10-27.xlsx:34 (KH0031), ...
[CẢNH BÁO] ⚠ Churn thì ARR 2026 bằng 0: 1 dòng sai, vd tai_ky_Q4.2026_v2_2026-10-28.xlsx:15 (3000.0)
```

## Bộ mẫu

| Thư mục | Nội dung |
|---|---|
| `examples/ban_hang/` | Đơn hàng bán lẻ, có vài lỗi cài sẵn. Là cấu hình mặc định khi mới clone |
| `examples/tai_ky/` | Danh sách tái ký khách hàng, khó hơn: tiêu đề ở dòng 3, số tiền nhiều kiểu, khách trùng mã, dòng tổng cuối bảng. Có sẵn log của 5 lần chạy để xem |

Mỗi bộ mẫu có cấu hình tiếng Anh (`*.md`) và tiếng Việt (`*.vi.md`).

Muốn xem bộ nào thì nói với Claude, ví dụ "cho tôi chạy thử bộ tái ký".

## Dữ liệu của bạn ở đâu

File gốc, file trung gian, kết quả và log nằm trong `.gitignore`. Nếu bạn đẩy bản của mình lên git, chỉ có
cấu hình và script lên theo, dữ liệu vẫn chỉ ở trên máy.

## Dành cho người muốn tự sửa

Mọi thứ riêng cho từng bộ dữ liệu nằm ở 3 file trong `.claude/skills/data-processing/`:
`reference/data_dictionary.md` (ý nghĩa cột), `reference/validation_rules.md` (lọc, tách trùng, ngưỡng
kiểm tra) và `scripts/transform.py` (các bước tính toán). Quy trình đầy đủ ở `SKILL.md` (viết bằng tiếng
Anh, Claude vẫn trả lời bạn bằng tiếng Việt). Tên khoá cấu hình viết tiếng Việt hay tiếng Anh đều được,
danh sách đối chiếu ở `scripts/messages.py`.

Giới hạn hiện tại: mỗi bản clone phục vụ một loại file định kỳ (có 2 loại thì clone 2 lần), phù hợp file
tới vài chục nghìn dòng.

## Giấy phép

MIT
