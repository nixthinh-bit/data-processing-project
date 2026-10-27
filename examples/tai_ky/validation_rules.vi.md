# Validation rules: danh sách tái ký (giả lập)

[English](validation_rules.md)

Cấu hình cho bộ dữ liệu `examples/tai_ky/`. Muốn dùng thì chép file này đè lên
`.claude/skills/data-processing/reference/validation_rules.md`.

```yaml
ngon_ngu: vi                  # vi | en: ngôn ngữ của log, lý do loại và tên file kết quả

nguon:
  mau_ten_file: "tai_ky_*.xlsx"
  sheet: "Tai ky"             # sheet "Ghi chu" không phải dữ liệu
  dong_tieu_de: 3             # 2 dòng đầu là tiêu đề bảng và ghi chú nguồn
  khoa_file_goc: true

dinh_dang_so:
  thap_phan: ","
  hang_nghin: "."

dinh_dang_ngay: ["%d/%m/%Y", "%Y-%m-%d"]

lam_sach:
  khi_loi_kieu: loai_dong
  bo_dong_trung_hoan_toan: false
  loai_dong_khi:              # chạy trước loc_dong, để dòng tổng không bị gắn nhầm lý do "ngoài vùng"
    - cot: ten_khach_hang
      bang: ["Tổng cộng", "Tổng"]
      ly_do: dòng tổng cộng của bảng, không phải khách hàng
  loc_dong:
    quoc_gia: [VN]
  bo_trung_theo_khoa: true

xuat:
  giu_cot_truy_vet: true
```

```yaml
tang_1:
  ty_le_trong_toi_da: 0.05

tang_2:
  che_do_dong: giu_nguyen
  cot_tien: [arr_2025, arr_2026]
  sai_so_tien: 0.01

tang_3:
  thu_tu_ngay:
    - [ngay_bat_dau, ngay_het_han]
  ngay_khong_tuong_lai: [ngay_bat_dau]
  dieu_kien:
    - ten: Churn thì ARR 2026 bằng 0
      khi: "trang_thai == 'Churn'"
      phai: "arr_2026 == 0"
      hien_cot: arr_2026
    - ten: Churn và Downsell phải có lý do
      khi: "trang_thai in ['Churn', 'Downsell']"
      phai: "ly_do.notna()"
      hien_cot: trang_thai
    - ten: Upsell thì ARR 2026 lớn hơn ARR 2025
      khi: "trang_thai == 'Upsell'"
      phai: "arr_2026 > arr_2025"
      hien_cot: arr_2026
    - ten: Downsell thì ARR 2026 nhỏ hơn ARR 2025 và lớn hơn 0
      khi: "trang_thai == 'Downsell'"
      phai: "(arr_2026 < arr_2025) & (arr_2026 > 0)"
      hien_cot: arr_2026
    - ten: Đã chốt (tái ký, upsell, downsell) thì phải có ARR 2026
      khi: "trang_thai in ['Đã tái ký', 'Upsell', 'Downsell']"
      phai: "arr_2026.notna()"
      hien_cot: trang_thai

tang_4:
  lech_so_dong_pct: 20
  lech_tong_tien_pct: 20

tang_5:
  so_dong: 8
```

## Lịch sử quy tắc

| Ngày | Lỗi gặp | Quy tắc thêm |
|---|---|---|
| 2026-10-27 | Dòng "Tổng cộng" cuối bảng bị gắn nhầm lý do "ngoài VN"; 861.240 USD trong tiền bị loại thực ra là dòng tổng | `lam_sach.loai_dong_khi` theo `ten_khach_hang` |
