"""Bước 2: tính toán, ghép bảng, tạo cột mới.  /  Step 2: calculations, joins, new columns.

Đây là phần riêng của từng người. Mỗi bước nghiệp vụ là một hàm nhận DataFrame và trả về
DataFrame, rồi khai báo trong BUOC theo đúng thứ tự chạy. Quy ước:
  - Cột mới phải khai báo trong data_dictionary với `nguon: tinh_toan`.
  - Không xoá dòng ở đây. Muốn loại dòng thì làm ở clean.py để có lý do trong 01_excluded.csv,
    nếu không tầng 2 (đối soát) sẽ chặn.
  - Nếu cần gộp dòng (group by), đổi `tang_2.che_do_dong: gop` trong validation_rules.md.
  - Bảng tra cứu (danh mục khách, bảng giá...) để trong data/raw/tra_cuu/ và đọc bằng read_lookup().

them_thang, kiem_thanh_tien là ví dụ cho bộ dữ liệu mẫu trong examples/. Thay bằng logic của bạn khi đã chốt.

Kết quả: data/processed/<run_id>/02_transformed.csv
Chạy riêng (sau clean.py): python transform.py --run-id 2026-10-27_run01
"""
import argparse

import pandas as pd

import common as c


def read_lookup(name, **kwargs):
    """Đọc một bảng tra cứu trong data/raw/tra_cuu/ (chỉ đọc)."""
    return pd.read_excel(c.RAW_DIR / "tra_cuu" / name, dtype=object, **kwargs)


# ---------- các bước nghiệp vụ (ví dụ) ----------

def them_thang(df):
    """Tháng đặt hàng dạng YYYY-MM, dùng để tổng hợp theo kỳ."""
    if "ngay_dat" in df:
        df["thang"] = df["ngay_dat"].dt.strftime("%Y-%m")
    return df


def kiem_thanh_tien(df):
    """Chênh lệch giữa thành tiền trong file và số lượng x đơn giá. Tầng 3 cảnh báo nếu khác 0."""
    if {"thanh_tien", "so_luong", "don_gia"} <= set(df.columns):
        df["chenh_lech_thanh_tien"] = (df["thanh_tien"] - df["so_luong"] * df["don_gia"]).round(2)
    return df


def tinh_chenh_lech_arr(df):
    """ARR 2026 trừ ARR 2025. Khách đang đàm phán (chưa có ARR 2026) để trống."""
    df["chenh_lech_arr"] = df["arr_2026"] - df["arr_2025"]
    return df


def xep_theo_partner(df):
    """Xếp theo partner rồi mã KH. Khách chưa có partner xếp cuối."""
    return df.sort_values(["partner", "ma_kh"], key=lambda s: s.str.casefold(),
                          na_position="last", kind="stable").reset_index(drop=True)


# Bộ dữ liệu tái ký giả lập (examples/tai_ky)
BUOC = [
    tinh_chenh_lech_arr,
    xep_theo_partner,
]


# ---------- khung chạy, thường không cần sửa ----------

def transform(run_id, log):
    c.load_rules()  # đặt ngôn ngữ
    dictionary = c.load_dictionary()
    columns = c.active_columns(dictionary)
    df = c.read_csv(c.run_dir(run_id) / "01_cleaned.csv", columns)
    n_in = len(df)
    for step in BUOC:
        before = set(df.columns)
        df = step(df)
        added = [col for col in df.columns if col not in before]
        log.write(f"transform: {step.__name__}" + (c.t("tf_step_added", a=added) if added else ""))
    undeclared = [col for col in df.columns if col not in dictionary["cot"] and col not in c.TRACE_COLS]
    if undeclared:
        log.write(c.t("tf_undeclared", a=undeclared))
    c.save_csv(df, c.run_dir(run_id) / "02_transformed.csv")
    log.write(c.t("tf_summary", n=n_in, m=len(df)))
    return df


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--run-id", required=True)
    args = ap.parse_args()
    transform(args.run_id, c.RunLog(args.run_id))


if __name__ == "__main__":
    main()
