# Bộ mẫu: đơn hàng bán lẻ

File `don_hang_2026-10-01.xlsx` có 126 dòng đơn hàng hư cấu, sinh bằng `tao_du_lieu_mau.py`. Đây là cấu
hình mặc định khi mới clone, nên chỉ cần chép file Excel vào `data/raw/` rồi chạy.

Lỗi cài sẵn: một dòng trống, một đơn thiếu mã, số lượng ghi bằng chữ ("hai"), số tiền dạng chữ ("32.000"),
ngày giao trước ngày đặt, kênh bán lạ ("Facebook"), thành tiền lệch số lượng x đơn giá.

Kết quả mong đợi: giữ 123 dòng, loại 3 dòng có lý do, tầng 1 và 2 đạt, 3 cảnh báo ở tầng 3.
