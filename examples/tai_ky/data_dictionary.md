# Data dictionary: danh sách tái ký (giả lập)

Cấu hình cho bộ dữ liệu `examples/tai_ky/`. Muốn dùng thì chép file này đè lên
`.claude/skills/data-processing/reference/data_dictionary.md`. Cách khai báo từng khoá xem ở file gốc đó.

```yaml
cot:
  ma_kh:
    ten_goc: ["Mã KH"]
    kieu: string
    nghia: Mã khách hàng trong CRM, mỗi khách một dòng
    bat_buoc: true
    khoa: true
    trang_thai: xac_nhan

  ten_khach_hang:
    ten_goc: ["Tên khách hàng"]
    kieu: string
    bat_buoc: true
    trang_thai: xac_nhan

  partner:
    ten_goc: ["Partner"]
    kieu: string
    nghia: Partner quản lý khách. Trống là khách chưa gắn partner
    ty_le_trong_toi_da: 1.0
    trang_thai: xac_nhan

  csm:
    ten_goc: ["CSM"]
    kieu: string
    nghia: CSM phụ trách
    trang_thai: xac_nhan

  quoc_gia:
    ten_goc: ["Quốc gia"]
    kieu: string
    nghia: Quốc gia của khách, chuẩn hoá về mã 2 chữ
    bat_buoc: true
    anh_xa: {"Việt Nam": VN, "Vietnam": VN, "vn": VN}
    gia_tri_hop_le: [VN]
    trang_thai: xac_nhan

  ngay_bat_dau:
    ten_goc: ["Ngày bắt đầu HĐ"]
    kieu: date
    bat_buoc: true
    trang_thai: xac_nhan

  ngay_het_han:
    ten_goc: ["Ngày hết hạn HĐ"]
    kieu: date
    nghia: Ngày hết hạn hợp đồng hiện tại, là mốc tái ký
    bat_buoc: true
    trang_thai: xac_nhan

  so_license:
    ten_goc: ["Số license"]
    kieu: int
    bat_buoc: true
    min: 1
    trang_thai: xac_nhan

  arr_2025:
    ten_goc: ["ARR 2025 (USD)"]
    kieu: tien
    don_vi: USD
    nghia: Doanh thu định kỳ năm của hợp đồng hiện tại
    bat_buoc: true
    khong_am: true
    trang_thai: xac_nhan

  arr_2026:
    ten_goc: ["ARR 2026 (USD)"]
    kieu: tien
    don_vi: USD
    nghia: ARR sau tái ký. Trống khi đang đàm phán, bằng 0 khi churn
    khong_am: true
    ty_le_trong_toi_da: 0.4
    trang_thai: xac_nhan

  chiet_khau:
    ten_goc: ["Chiết khấu"]
    kieu: phan_tram
    nghia: Chiết khấu khi tái ký, lưu dạng 0..1
    min: 0
    max: 0.3
    trang_thai: xac_nhan

  trang_thai:
    ten_goc: ["Trạng thái"]
    kieu: string
    bat_buoc: true
    gia_tri_hop_le: ["Đã tái ký", "Đang đàm phán", "Upsell", "Downsell", "Churn"]
    trang_thai: xac_nhan

  ly_do:
    ten_goc: ["Lý do churn/downsell"]
    kieu: string
    ty_le_trong_toi_da: 1.0
    trang_thai: xac_nhan

  ghi_chu_kam:
    ten_goc: ["Ghi chú KAM"]
    bo_qua: true
    nghia: Ghi chú tự do của KAM, không dùng cho báo cáo (người dùng xác nhận 2026-10-27)

  # Cột do transform.py tạo
  chenh_lech_arr:
    nguon: tinh_toan
    kieu: float
    don_vi: USD
    nghia: arr_2026 trừ arr_2025, trống khi chưa có ARR 2026
    ty_le_trong_toi_da: 0.4
    trang_thai: xac_nhan
```
