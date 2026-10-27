# Validation rules

[English](validation_rules.md)

Ngưỡng kiểm tra và quy tắc đọc file, tách khỏi code để chỉnh mà không phải sửa script.
Ngưỡng theo từng cột (min, max, giá trị hợp lệ) nằm ở `data_dictionary.md`.

Mỗi khi gặp một lỗi dữ liệu mới, thêm một quy tắc vào đây (hoặc vào data_dictionary) và một dòng vào
mục "Lịch sử quy tắc" ở cuối file, để lần sau script tự bắt được.

## Đọc file gốc

```yaml
ngon_ngu: vi                  # vi | en: ngôn ngữ của log, lý do loại và tên file kết quả

nguon:
  mau_ten_file: "*.xlsx"      # file nào trong data/raw được đọc
  sheet: 0                    # số thứ tự hoặc tên sheet
  dong_tieu_de: 1             # dòng tiêu đề nằm ở dòng mấy trong Excel
  khoa_file_goc: true         # đặt file gốc chỉ đọc trước khi chạy

dinh_dang_so:                 # áp dụng cho ô số được nhập dạng chữ, ví dụ "1.250.000"
  thap_phan: ","
  hang_nghin: "."

dinh_dang_ngay: ["%d/%m/%Y", "%d-%m-%Y", "%Y-%m-%d"]

lam_sach:
  khi_loi_kieu: loai_dong     # loai_dong | de_trong (de_trong chỉ áp dụng cho cột không bắt buộc)
  bo_dong_trung_hoan_toan: false
  # loai_dong_khi:            # loại dòng không phải dữ liệu, chạy trước loc_dong. Ví dụ dòng tổng cuối bảng:
  #   - cot: ma_don
  #     bang: ["Tổng cộng"]
  #     ly_do: dòng tổng cộng của bảng
  # loc_dong:                 # chỉ giữ dòng có giá trị thuộc danh sách, dòng khác bị loại kèm lý do
  #   kenh: ["Website"]
  bo_trung_theo_khoa: false   # true: trùng khoá và giống hệt các cột khác thì giữ dòng đầu, loại dòng sau.
                              # Trùng khoá mà khác nội dung thì không tự chọn, tầng 1 sẽ chặn

xuat:
  giu_cot_truy_vet: true      # giữ _file_goc, _dong_goc trong ket_qua.xlsx
```

## Tầng 1: Cấu trúc (CHẶN)

```yaml
tang_1:
  ty_le_trong_toi_da: 0.05    # ô trống tối đa mỗi cột, cột bat_buoc luôn là 0
  # khoa: [ma_don]            # bỏ comment để ghi đè khoá khai báo trong data_dictionary
```

## Tầng 2: Đối soát (CHẶN)

```yaml
tang_2:
  che_do_dong: giu_nguyen     # giu_nguyen: vào = ra + loại; gop: transform có group by, chỉ so tổng tiền
  cot_tien: [thanh_tien]      # để [] nếu dữ liệu không có cột tiền; bỏ dòng này thì lấy mọi cột kieu: tien
  sai_so_tien: 0.01
```

## Tầng 3: Nghiệp vụ (CẢNH BÁO)

```yaml
tang_3:
  thu_tu_ngay:                # [a, b] nghĩa là a không được sau b
    - [ngay_dat, ngay_giao]
  ngay_khong_tuong_lai: [ngay_dat, ngay_giao]
  dieu_kien: []               # quy tắc chéo cột, xem ví dụ bên dưới
```

Quy tắc chéo cột viết bằng biểu thức pandas trên tên cột chuẩn. `khi` là điều kiện áp dụng (bỏ trống
là áp cho mọi dòng), `phai` là điều phải đúng, `muc: chan` để nâng lên mức CHẶN, `hien_cot` là cột in
ra trong ví dụ của log. Ví dụ ở `examples/tai_ky/validation_rules.md`:

```
  dieu_kien:
    - ten: Churn thì ARR 2026 bằng 0
      khi: "trang_thai == 'Churn'"
      phai: "arr_2026 == 0"
      hien_cot: arr_2026
```

## Tầng 4: Biến động (CẢNH BÁO)

So với lần chạy gần nhất không bị chặn.

```yaml
tang_4:
  lech_so_dong_pct: 20
  lech_tong_tien_pct: 20
```

## Tầng 5: Người đối chiếu

```yaml
tang_5:
  so_dong: 8                  # lấy ngẫu nhiên, cố định theo run_id nên chạy lại vẫn ra cùng mẫu
```

## Lịch sử quy tắc

| Ngày | Lỗi gặp | Quy tắc thêm |
|---|---|---|
| 2026-10-27 | (mẫu) Ngày giao trước ngày đặt | `tang_3.thu_tu_ngay: [ngay_dat, ngay_giao]` |
