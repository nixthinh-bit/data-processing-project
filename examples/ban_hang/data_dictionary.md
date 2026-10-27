# Data dictionary

Ý nghĩa, kiểu, đơn vị và giá trị hợp lệ của từng cột. Script đọc khối `yaml` bên dưới, phần chữ
xung quanh chỉ để người đọc.

> Cấu hình hiện tại là của bộ mẫu bán hàng (`examples/ban_hang/`). Các bộ mẫu khác nằm cạnh đó trong
> `examples/`. Khi dùng cho dữ liệu của bạn, nhờ Claude làm theo mục B trong SKILL.md, khối yaml này sẽ
> được thay bằng cột của bạn.

## Cách khai báo một cột

| Khoá | Ý nghĩa |
|---|---|
| `ten_goc` | Danh sách tên cột có thể gặp trong file gốc (không phân biệt hoa thường, khoảng trắng thừa) |
| `kieu` | `string`, `int`, `float`, `tien`, `phan_tram`, `date`, `bool`. Cột `tien` được đối soát tổng ở tầng 2. `phan_tram` lưu dạng 0..1, nhận "15%" hoặc 0.15, còn số trần như 15 bị coi là mơ hồ |
| `dinh_dang_so` | Định dạng số riêng cho cột này, ví dụ `{thap_phan: ".", hang_nghin: ","}` cho số kiểu Mỹ |
| `anh_xa` | Chuẩn hoá giá trị chữ trước khi kiểm, ví dụ `{"Việt Nam": VN, "vn": VN}` (không phân biệt hoa thường) |
| `nghia`, `don_vi` | Ghi bằng lời, để người sau hiểu |
| `bat_buoc` | `true` thì ô trống làm dòng bị loại ở bước clean |
| `khoa` | `true` nếu cột là (một phần) khoá; tầng 1 chặn khi trùng |
| `min`, `max`, `khong_am` | Khoảng hợp lệ, tầng 3 cảnh báo khi vượt |
| `gia_tri_hop_le` | Danh sách giá trị được phép, tầng 3 cảnh báo giá trị lạ |
| `ty_le_trong_toi_da` | Ngưỡng ô trống riêng cho cột này (ghi đè ngưỡng chung ở validation_rules) |
| `nguon: tinh_toan` | Cột do transform.py tạo, không có trong file gốc |
| `bo_qua: true` | Cột có trong file gốc nhưng cố ý không dùng |
| `trang_thai` | `xac_nhan` hoặc `chua_ro`. Còn cột `chua_ro` thì lần chạy bị chặn |

```yaml
cot:
  ma_don:
    ten_goc: ["Mã đơn", "Ma don", "Order ID"]
    kieu: string
    nghia: Mã đơn hàng do hệ thống bán hàng sinh ra
    bat_buoc: true
    khoa: true
    trang_thai: xac_nhan

  ngay_dat:
    ten_goc: ["Ngày đặt"]
    kieu: date
    nghia: Ngày khách đặt đơn
    bat_buoc: true
    min: 2020-01-01
    trang_thai: xac_nhan

  ngay_giao:
    ten_goc: ["Ngày giao"]
    kieu: date
    nghia: Ngày giao thành công, trống nếu chưa giao
    ty_le_trong_toi_da: 0.3
    trang_thai: xac_nhan

  ma_khach:
    ten_goc: ["Mã KH", "Mã khách hàng"]
    kieu: string
    nghia: Mã khách hàng
    bat_buoc: true
    trang_thai: xac_nhan

  san_pham:
    ten_goc: ["Sản phẩm"]
    kieu: string
    nghia: Tên sản phẩm
    trang_thai: xac_nhan

  so_luong:
    ten_goc: ["SL", "Số lượng"]
    kieu: int
    don_vi: cái
    bat_buoc: true
    min: 1
    max: 1000
    trang_thai: xac_nhan

  don_gia:
    ten_goc: ["Đơn giá"]
    kieu: tien
    don_vi: VND
    khong_am: true
    trang_thai: xac_nhan

  thanh_tien:
    ten_goc: ["Thành tiền"]
    kieu: tien
    don_vi: VND
    nghia: Số tiền khách trả cho dòng đơn, đã gồm chiết khấu
    bat_buoc: true
    khong_am: true
    trang_thai: xac_nhan

  kenh:
    ten_goc: ["Kênh bán"]
    kieu: string
    gia_tri_hop_le: ["Cửa hàng", "Website", "Sàn TMĐT"]
    trang_thai: xac_nhan

  ghi_chu_noi_bo:
    ten_goc: ["Ghi chú nội bộ"]
    bo_qua: true
    nghia: Ghi chú tự do của nhân viên, không dùng cho báo cáo

  # Cột do transform.py tạo
  thang:
    nguon: tinh_toan
    kieu: string
    nghia: Tháng đặt hàng YYYY-MM
    trang_thai: xac_nhan

  chenh_lech_thanh_tien:
    nguon: tinh_toan
    kieu: float
    don_vi: VND
    nghia: thanh_tien trừ so_luong x don_gia. Khác 0 là có chiết khấu hoặc nhập sai
    min: 0
    max: 0
    ty_le_trong_toi_da: 0.1
    trang_thai: xac_nhan
```
