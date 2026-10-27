"""Sinh 3 file Excel tái ký giả lập (dữ liệu hư cấu, khoảng 100 dòng mỗi file) để test cả luồng.

  tai_ky_Q4.2026_2026-10-27.xlsx     bản đầu, có cột lạ và một khách trùng mã nhưng khác số liệu
  tai_ky_Q4.2026_v2_2026-10-28.xlsx  bản gửi lại: bỏ cột lạ, sửa khách trùng, các lỗi khác giữ nguyên
  tai_ky_Q1.2027_2027-01-05.xlsx     kỳ sau, ARR giảm mạnh để thử tầng 4

Những thứ khó cài sẵn: tiêu đề nằm ở dòng 3, sheet thứ hai không dùng, số tiền nhập dạng chữ với
nhiều kiểu dấu, chiết khấu lúc ghi 0.15 lúc ghi "15%", ngày lẫn kiểu (ngày thật, chữ, số serial, ngày
không tồn tại), quốc gia viết nhiều kiểu, trạng thái gõ sai chính tả, dòng "Tổng cộng" cuối bảng.

Dùng: python examples/tai_ky/tao_du_lieu_tai_ky.py
"""
import datetime as dt
import random
from pathlib import Path

from openpyxl import Workbook

OUT = Path(__file__).resolve().parent
PARTNERS = ["Sao Bắc Tech", "Đông Phong Digital", "Lam Sơn Solutions", "Hải Âu Consulting", None]
CSMS = ["Ngọc Anh", "Quang Huy", "Thu Trang", "Minh Khoa"]
NUOC = ["VN"] * 6 + ["Việt Nam", "vn", "Vietnam", "TH", "SG", "PH"]
HO = ["Công ty TNHH", "Công ty CP", "Tập đoàn", "Công ty TNHH MTV"]
TEN = ["Ánh Dương", "Bình Minh", "Cửu Long", "Đại Phát", "Gia Hưng", "Hoà Bình", "Kim Ngân", "Lộc Phát",
       "Mai Linh", "Nam Việt", "Phú Quý", "Quang Trung", "Sông Hồng", "Tân Tiến", "Thành Công", "Trường Sơn",
       "Vạn Xuân", "Hưng Thịnh", "An Khang", "Bảo Tín"]
NGANH = ["Logistics", "Bán lẻ", "F&B", "Giáo dục", "Xây dựng"]
HEADER = ["Mã KH", "Tên khách hàng", "Partner", "CSM", "Quốc gia", "Ngày bắt đầu HĐ", "Ngày hết hạn HĐ",
          "Số license", "ARR 2025 (USD)", "ARR 2026 (USD)", "Chiết khấu", "Trạng thái", "Lý do churn/downsell"]


def make_customers(n, seed):
    rnd = random.Random(seed)
    rows = []
    for i in range(1, n + 1):
        start = dt.date(2025, rnd.randint(1, 12), rnd.randint(1, 28))
        end = start.replace(year=2026)
        lic = rnd.choice([20, 50, 80, 120, 200, 350])
        arr25 = lic * rnd.choice([60, 72, 84])
        status = rnd.choices(["Đã tái ký", "Đang đàm phán", "Upsell", "Downsell", "Churn"], [45, 25, 12, 10, 8])[0]
        arr26 = {"Đã tái ký": arr25, "Upsell": round(arr25 * rnd.uniform(1.1, 1.6)),
                 "Downsell": round(arr25 * rnd.uniform(0.5, 0.9)), "Churn": 0, "Đang đàm phán": None}[status]
        reason = rnd.choice(["Cắt giảm ngân sách", "Chuyển sang đối thủ", "Giảm nhân sự"]) if status in ("Churn", "Downsell") else None
        rows.append([f"KH{i:04d}", f"{rnd.choice(HO)} {rnd.choice(TEN)} {rnd.choice(NGANH)}", rnd.choice(PARTNERS),
                     rnd.choice(CSMS), rnd.choice(NUOC), start, end, lic, arr25, arr26,
                     rnd.choice([0, 0.05, 0.1, 0.15, 0.2]), status, reason])
    return rows


def plant_errors(rows):
    """Cài lỗi vào vài dòng cố định để biết trước kết quả mong đợi."""
    rows[2][8] = "4.200"            # ARR dạng chữ, đúng định dạng VN (dấu chấm hàng nghìn)
    rows[3][8] = "$5,040"           # ARR dạng chữ kiểu Mỹ: mơ hồ với cấu hình VN, phải bị loại chứ không đoán
    rows[4][10] = "15%"             # chiết khấu dạng chữ có %
    rows[5][10] = 15                # chiết khấu 15: là 15% hay 1500%? phải bị loại
    rows[6][5] = "15/03/2025"       # ngày dạng chữ
    rows[7][5] = 45730              # ngày dạng số serial Excel (2025-03-14)
    rows[8][6] = "31/02/2026"       # ngày không tồn tại
    rows[9][6] = dt.date(2024, 1, 1)  # hết hạn trước ngày bắt đầu
    rows[10][11] = "da tai ky"      # trạng thái gõ sai
    rows[11][11], rows[11][9], rows[11][12] = "Churn", 3000, "Chuyển sang đối thủ"  # churn mà ARR 2026 > 0
    rows[12][11], rows[12][12] = "Downsell", None  # downsell không có lý do
    rows[13][1] = "  Công ty CP   Gia Hưng  Bán lẻ "  # khoảng trắng thừa
    rows[14][7] = -50               # license âm
    rows[15][0] = None              # thiếu mã KH
    for i in list(range(2, 16)) + [20, 30]:
        rows[i][4] = "VN"           # dòng cài lỗi phải là khách VN, nếu không bộ lọc vùng loại trước khi thấy lỗi
    rows[16][4], rows[16][8] = "TH", "không rõ"  # lỗi ở khách ngoài VN: chỉ bị loại vì ngoài vùng
    return rows


def write(path, rows, extra_col=False, conflict=False, title="DANH SÁCH TÁI KÝ Q4.2026"):
    wb = Workbook()
    ws = wb.active
    ws.title = "Tai ky"
    ws.append([title])
    ws.append(["Nguồn: xuất từ CRM, số tiền tính bằng USD"])
    header = HEADER + (["Ghi chú KAM"] if extra_col else [])
    ws.append(header)
    body = [list(r) for r in rows]
    body.append(list(rows[20]))                       # trùng y hệt dòng 21
    if conflict:
        dup = list(rows[30])
        dup[9] = (dup[9] or 0) + 1500                 # cùng mã KH nhưng ARR 2026 khác
        body.append(dup)
    for r in body:
        ws.append(r + (["gọi lại tuần sau"] if extra_col and random.random() < 0.3 else ([None] if extra_col else [])))
    ws.append([None] * len(header))                   # dòng trống
    total25 = sum(r[8] for r in rows if isinstance(r[8], (int, float)))
    ws.append([None, "Tổng cộng", None, None, None, None, None, None, total25, None, None, None, None])
    notes = wb.create_sheet("Ghi chu")
    notes.append(["Sheet này chỉ để ghi chú, không phải dữ liệu"])
    wb.save(path)
    print(f"Đã tạo {path.name}: {len(body) + 2} dòng dưới tiêu đề")


random.seed(1)
q4 = plant_errors(make_customers(100, seed=42))
write(OUT / "tai_ky_Q4.2026_2026-10-27.xlsx", q4, extra_col=True, conflict=True)
write(OUT / "tai_ky_Q4.2026_v2_2026-10-28.xlsx", q4)

q1 = plant_errors(make_customers(100, seed=43))
for r in q1[:60]:                                     # kỳ sau: nhiều khách churn, ARR tụt mạnh
    if isinstance(r[9], (int, float)):
        r[9] = 0
        r[11], r[12] = "Churn", "Cắt giảm ngân sách"
write(OUT / "tai_ky_Q1.2027_2027-01-05.xlsx", q1, title="DANH SÁCH TÁI KÝ Q1.2027")
