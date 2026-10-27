# Sample: customer renewals (simulated)

[Tiếng Việt](#bộ-thử-danh-sách-tái-ký-giả-lập)

Three fictional Excel files, about 100 customers each, to test the whole flow with harder data than the
retail sample. Regenerate them with `python examples/tai_ky/tao_du_lieu_tai_ky.py`. The data has Vietnamese
headers and values; the configuration exists in English (`*.md`) and Vietnamese (`*.vi.md`).

What the processing does: keep VN customers only, one row per customer ID, compute the ARR change, sort by partner.

Planted difficulties: header on row 3, a notes sheet, an unknown column "Ghi chú KAM", amounts typed as text
("4.200", "$5,040"), discounts written as "15%" or 15, mixed dates (text, Excel serial, 31/02), several
spellings of the country, a misspelled status, churn with ARR left, downsell without a reason, negative
licenses, duplicate customer IDs (one identical pair, one with different numbers), a blank row and a
"Tổng cộng" totals row.

## The runs in log_mau/ (logs in Vietnamese)

| Run | File | Result | What happened next |
|---|---|---|---|
| run01 | Q4 first version | BLOCK at clean: unknown column "Ghi chú KAM" | User says to ignore it, declared with `skip: true` |
| run02 | Q4 first version | BLOCK at layer 1: KH0031 duplicated with different ARR. No result, no review sample | Sender sends a corrected v2 |
| run03 | Q4 v2 (`--file`) | Pass, 72 customers, 6 warnings. The excluded list shows the totals row labelled "outside VN" | Rule `drop_rows_when` added |
| run04 | Q4 v2 | Pass, the totals row has its own reason. Layer 4 vs run03: 0% change | |
| run05 | Q1.2027 (`--file`) | Pass, layer 4 warns ARR 2026 is down 43.8% vs run04 | User confirms real churn or a file problem |

The configuration here is the final version (after run04). To replay from the start, copy
`data_dictionary.md`, `validation_rules.md` and `transform.py` into the skill, remove the `ghi_chu_kam` block
and the `drop_rows_when` block, then copy each Excel file into `data/raw/` in the order above.

## Bộ thử: danh sách tái ký (giả lập)

Ba file Excel hư cấu, mỗi file khoảng 100 khách, dùng để thử cả luồng với dữ liệu khó hơn bộ mẫu bán hàng.
Sinh lại bằng `python examples/tai_ky/tao_du_lieu_tai_ky.py`. Cấu hình tiếng Việt là các file `.vi.md`.

Yêu cầu xử lý: chỉ giữ khách VN, mỗi mã KH một dòng, tính chênh lệch ARR, xếp theo partner.

Những thứ khó cài trong file: tiêu đề ở dòng 3, có sheet ghi chú, cột lạ "Ghi chú KAM", số tiền dạng chữ
("4.200", "$5,040"), chiết khấu lúc "15%" lúc 15, ngày lẫn kiểu (chữ, số serial, 31/02), quốc gia viết
nhiều kiểu, trạng thái gõ sai, churn mà còn ARR, downsell thiếu lý do, license âm, khách trùng mã (một cặp
giống hệt, một cặp khác số liệu), dòng trống và dòng "Tổng cộng".

Bảng các lần chạy ở trên áp dụng y nguyên; log trong `log_mau/` viết bằng tiếng Việt. Muốn chạy lại từ đầu
thì chép `data_dictionary.vi.md`, `validation_rules.vi.md` (bỏ đuôi `.vi`) và `transform.py` vào skill, xoá
khối `ghi_chu_kam` và `loai_dong_khi`, rồi chép từng file Excel vào `data/raw/` theo thứ tự trong bảng.
