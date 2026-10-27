# Dự án xử lý dữ liệu Excel định kỳ

Dự án nhận file Excel theo kỳ, làm sạch, tính toán, kiểm tra rồi xuất kết quả. Mục tiêu là các lần chạy
cho kết quả nhất quán, có kiểm tra và truy vết được tới từng dòng của file gốc.

Quy trình chi tiết nằm ở skill `.claude/skills/data-processing/SKILL.md`. Đọc skill đó trước khi động vào dữ liệu.

Người dùng thường không viết code. Nếu chưa có thư mục `.venv`, hoặc người dùng nói muốn bắt đầu với dữ
liệu của họ, làm theo mục 0 rồi mục B của skill và dẫn họ đi từng bước.

## Nguyên tắc

1. Dữ liệu gốc trong `data/raw/` chỉ đọc. Không sửa, không ghi đè, không lưu file khác đè lên. `run.py` tự
   đặt file gốc ở chế độ chỉ đọc và kiểm tra mã băm trước và sau khi chạy.
2. Cách xử lý đã ổn định thì nằm trong script ở `scripts/`. Không viết lại code xử lý mỗi lần chạy, không
   xử lý dữ liệu bằng code tạm ngoài các script này.
3. Log kỹ thuật do script tự ghi vào `logs/run_log/`. Không tự tóm tắt hay viết thay vào log. Khi báo cáo
   cho người dùng, trích nguyên văn các dòng `[CHẶN]` và `[CẢNH BÁO]` từ log.
4. Không báo "xong" khi log còn dòng `[CHẶN] ✗`. Khi đó nói rõ lỗi nào, ở file và dòng nào, đề xuất cách sửa.
5. Không đoán ý nghĩa cột. Cột lạ hoặc chưa rõ thì hỏi người dùng, rồi ghi vào
   `reference/data_dictionary.md`. Quyết định nghiệp vụ kèm lý do ghi vào `logs/decisions.md`.

## Bản đồ thư mục

| Đường dẫn | Nội dung |
|---|---|
| `data/raw/` | File gốc, tên kèm ngày nhận, ví dụ `don_hang_2026-10-01.xlsx` |
| `data/processed/<run_id>/` | Kết quả trung gian: `01_cleaned.csv`, `01_excluded.csv`, `02_transformed.csv` |
| `outputs/<run_id>/` | Mỗi lần chạy một thư mục, không ghi đè: `ket_qua.xlsx`, `validation_report.log`, `mau_doi_chieu.csv`, `run_meta.json` |
| `logs/run_log/` | Log do script ghi, mỗi lần chạy một file |
| `logs/decisions.md` | Quyết định nghiệp vụ và lý do |
| `.claude/skills/data-processing/` | Quy trình, script, data dictionary, ngưỡng kiểm tra |

`run_id` có dạng `YYYY-MM-DD_runNN`.

## Lệnh thường dùng

```bash
.venv/bin/python .claude/skills/data-processing/scripts/run.py --ghi-chu "file tháng 10"
.venv/bin/python .claude/skills/data-processing/scripts/run.py --file "tai_ky_Q1.2027_*.xlsx"
.venv/bin/python .claude/skills/data-processing/scripts/khao_sat.py
```

Mã thoát của `run.py`: 0 là qua mọi kiểm tra CHẶN, 1 là còn lỗi CHẶN (không xuất kết quả).

## Bối cảnh riêng

Phần này để mỗi người tự điền khi dùng cho dữ liệu của mình: dữ liệu đến từ đâu, ai gửi, chu kỳ nhận,
ai dùng kết quả, có kỳ hạn gì.

- Nguồn dữ liệu: (chưa điền)
- Chu kỳ: (chưa điền)
- Người dùng kết quả: (chưa điền)
