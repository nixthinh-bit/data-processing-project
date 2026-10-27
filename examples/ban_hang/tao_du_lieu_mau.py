"""Sinh file Excel mẫu (dữ liệu hư cấu) có cài sẵn vài lỗi thường gặp, để chạy thử cả luồng.

Dùng: python examples/ban_hang/tao_du_lieu_mau.py   -> examples/ban_hang/don_hang_2026-10-01.xlsx
Sau đó chép file vào data/raw/ rồi chạy run.py.
"""
import datetime as dt
import random
from pathlib import Path

from openpyxl import Workbook

random.seed(7)
SAN_PHAM = {"Nước suối 500ml": 6000, "Mì ly": 12000, "Cà phê lon": 15000, "Bánh mì": 20000, "Sữa tươi 1L": 32000}
KENH = ["Cửa hàng", "Website", "Sàn TMĐT"]

wb = Workbook()
ws = wb.active
ws.title = "Don hang"
ws.append(["Mã đơn", "Ngày đặt", "Ngày giao", "Mã KH", "Sản phẩm", "SL", "Đơn giá", "Thành tiền", "Kênh bán", "Ghi chú nội bộ"])

start = dt.date(2026, 10, 1)
for i in range(1, 121):
    sp, gia = random.choice(list(SAN_PHAM.items()))
    sl = random.randint(1, 12)
    dat = start + dt.timedelta(days=random.randint(0, 20))
    giao = dat + dt.timedelta(days=random.randint(0, 3)) if random.random() > 0.15 else None
    ws.append([f"DH{i:05d}", dat, giao, f"KH{random.randint(1, 40):03d}", sp, sl, gia, sl * gia,
               random.choice(KENH), "" if random.random() > 0.2 else "gọi lại khách"])

# Các lỗi cài sẵn
ws.append([None] * 10)                                                                    # dòng trống
ws.append([None, dt.date(2026, 10, 5), None, "KH001", "Mì ly", 2, 12000, 24000, "Website", ""])   # thiếu mã đơn
ws.append(["DH00121", "05/10/2026", "06/10/2026", "KH002", "Bánh mì", "hai", 20000, 40000, "Cửa hàng", ""])  # SL là chữ
ws.append(["DH00122", "07/10/2026", None, "KH003", "Sữa tươi 1L", 5, "32.000", "160.000", "Website", ""])   # số dạng chữ, đọc được
ws.append(["DH00123", dt.date(2026, 10, 9), dt.date(2026, 10, 7), "KH004", "Cà phê lon", 3, 15000, 45000, "Cửa hàng", ""])  # giao trước đặt
ws.append(["DH00124", dt.date(2026, 10, 10), None, "KH005", "Mì ly", 4, 12000, 45000, "Facebook", ""])      # kênh lạ, lệch thành tiền

out = Path(__file__).resolve().parent / "don_hang_2026-10-01.xlsx"
wb.save(out)
print(f"Đã tạo {out}")
