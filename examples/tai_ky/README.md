# Bộ thử: danh sách tái ký (giả lập)

Ba file Excel hư cấu, mỗi file khoảng 100 khách, dùng để thử cả luồng với dữ liệu khó hơn bộ mẫu bán hàng.
Sinh lại bằng `python examples/tai_ky/tao_du_lieu_tai_ky.py`.

Yêu cầu xử lý: chỉ giữ khách VN, mỗi mã KH một dòng, tính chênh lệch ARR, xếp theo partner.

Những thứ khó cài trong file: tiêu đề ở dòng 3, có sheet ghi chú, cột lạ "Ghi chú KAM", số tiền dạng chữ
("4.200", "$5,040"), chiết khấu lúc "15%" lúc 15, ngày lẫn kiểu (chữ, số serial, 31/02), quốc gia viết
nhiều kiểu, trạng thái gõ sai, churn mà còn ARR, downsell thiếu lý do, license âm, khách trùng mã (một cặp
giống hệt, một cặp khác số liệu), dòng trống và dòng "Tổng cộng".

## Các lần chạy trong log_mau/

| Lần | File | Kết quả | Ai làm gì sau đó |
|---|---|---|---|
| run01 | Q4 bản đầu | CHẶN ngay ở clean: cột lạ "Ghi chú KAM" | Người dùng nói bỏ qua cột này, khai báo `bo_qua: true` |
| run02 | Q4 bản đầu | CHẶN ở tầng 1: KH0031 trùng mã nhưng ARR khác. Không xuất kết quả, không lấy mẫu | Bên gửi gửi lại file v2 |
| run03 | Q4 v2 (`--file`) | Đạt, 72 khách, 6 cảnh báo. Soi danh sách loại thấy dòng "Tổng cộng" bị gắn nhầm lý do "ngoài VN" | Thêm quy tắc `loai_dong_khi` |
| run04 | Q4 v2 | Đạt, dòng tổng có lý do riêng. Tầng 4 so với run03: lệch 0% | |
| run05 | Q1.2027 (`--file`) | Đạt, tầng 4 cảnh báo ARR 2026 giảm 43,8% so với run04 | Người dùng xác nhận đây là churn thật hay lỗi file |

Cấu hình trong thư mục này là bản cuối (sau run04). Muốn chạy lại từ đầu thì chép `data_dictionary.md`,
`validation_rules.md`, `transform.py` vào skill, xoá khối `ghi_chu_kam` và `loai_dong_khi`, rồi chép từng
file Excel vào `data/raw/` theo thứ tự trên.
