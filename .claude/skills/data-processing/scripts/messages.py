"""Messages in two languages, and English aliases for configuration keys.

Thông điệp hai ngôn ngữ và tên khoá cấu hình tiếng Anh.
Chọn ngôn ngữ bằng `language: en` hoặc `language: vi` trong validation_rules.md (mặc định vi).
Mỗi thông điệp là một cặp (vi, en). Thêm thông điệp mới thì thêm cả hai.
"""

MESSAGES = {
    # nhãn mức kiểm tra / check levels
    "CHAN": ("CHẶN", "BLOCK"),
    "CANH_BAO": ("CẢNH BÁO", "WARN"),
    "THU_CONG": ("THỦ CÔNG", "MANUAL"),

    # common: đọc giá trị / parsing
    "not_number": ("'{v}' không phải số", "'{v}' is not a number"),
    "num_ambiguous": ("'{v}' mơ hồ: có thể là số thập phân hoặc số có dấu hàng nghìn kiểu khác",
                      "'{v}' is ambiguous: it could be a decimal or a number with a different thousands separator"),
    "num_format": ("'{v}' không đúng định dạng số đã khai báo", "'{v}' does not match the declared number format"),
    "not_int": ("'{v}' không phải số nguyên", "'{v}' is not a whole number"),
    "pct_ambiguous": ("'{v}' không rõ là {a}% hay {b}%, cần ghi dạng 0.15 hoặc 15%",
                      "'{v}' is unclear: {a}% or {b}%? Write it as 0.15 or 15%"),
    "date_format": ("'{v}' không khớp định dạng ngày {f}", "'{v}' does not match the date formats {f}"),
    "not_bool": ("'{v}' không phải có/không", "'{v}' is not yes/no"),

    # clean
    "stop_unclear": ("Cột chưa rõ nghĩa trong data_dictionary: {cols}. Hỏi người dùng rồi cập nhật trước khi chạy.",
                     "Columns marked unclear in data_dictionary: {cols}. Ask the user and update it before running."),
    "stop_no_files": ("Không có file nào trong {d} khớp mẫu tên file.", "No file in {d} matches the file pattern."),
    "stop_unknown_cols": ("{f}: có cột chưa có trong data_dictionary: {cols}. Không đoán nghĩa, hỏi người dùng.",
                          "{f}: columns not in data_dictionary: {cols}. Do not guess their meaning, ask the user."),
    "clean_file": ("clean: {f} có {n} dòng, {m} cột khớp", "clean: {f} has {n} row(s), {m} columns matched"),
    "clean_skipped": (", bỏ qua {x}", ", skipped {x}"),
    "clean_missing": (", THIẾU {x}", ", MISSING {x}"),
    "r_blank": ("dòng trống", "blank row"),
    "type_blank_log": ("clean: {f} dòng {r} cột {col}: {e}, để trống theo quy tắc",
                       "clean: {f} row {r} column {col}: {e}, left blank per rule"),
    "r_required": ("{col}: bắt buộc nhưng trống", "{col}: required but blank"),
    "r_exact_dup": ("trùng hoàn toàn với một dòng trước", "exact duplicate of an earlier row"),
    "r_outside": ("{col} ngoài phạm vi lọc {a}", "{col} outside the filter {a}"),
    "r_key_dup": ("trùng {k}, giống hệt dòng được giữ", "duplicate {k}, identical to the kept row"),
    "clean_summary": ("clean: giữ {k} dòng, loại {x} dòng (lý do ở 01_excluded.csv)",
                      "clean: kept {k} row(s), excluded {x} row(s) (reasons in 01_excluded.csv)"),
    "clean_reason_line": ("clean:   {n} dòng: {r}", "clean:   {n} row(s): {r}"),
    "dedupe_nokey": ("clean: bo_trung_theo_khoa bật nhưng chưa khai báo cột khoá, bỏ qua",
                     "clean: dedupe_by_key is on but no key column is declared, skipped"),
    "dedupe_summary": ("clean: tách trùng theo {k}: {g} nhóm trùng, loại {n} dòng",
                       "clean: dedupe by {k}: {g} duplicate group(s), excluded {n} row(s)"),
    "dedupe_conflicts": ("; {n} nhóm trùng nhưng khác nội dung, giữ nguyên để tầng 1 chặn",
                         "; {n} group(s) share a key but differ, kept so layer 1 blocks"),

    # transform
    "tf_step_added": (" thêm cột {a}", " added columns {a}"),
    "tf_undeclared": ("transform: cột mới chưa khai báo trong data_dictionary: {a}",
                      "transform: new columns not declared in data_dictionary: {a}"),
    "tf_summary": ("transform: {n} dòng vào, {m} dòng ra", "transform: {n} row(s) in, {m} row(s) out"),

    # validate: chung
    "more_rows": (", ... và {n} dòng khác", ", ... and {n} more rows"),
    "eg": ("vd", "e.g."),

    # tầng 1
    "L1": ("--- Tầng 1: Cấu trúc ---", "--- Layer 1: Structure ---"),
    "l1_raw_same": ("File gốc không bị sửa trong lúc chạy", "Source files not modified during the run"),
    "l1_raw_changed": (": KHÁC {x}", ": CHANGED {x}"),
    "l1_cols": ("Đủ cột theo data_dictionary", "All columns from data_dictionary present"),
    "l1_cols_missing": (": thiếu {x}", ": missing {x}"),
    "l1_extra": ("Không có cột chưa khai báo", "No undeclared columns"),
    "l1_extra_found": (": {x} chưa có trong data_dictionary", ": {x} not in data_dictionary"),
    "l1_types": ("Đúng kiểu dữ liệu", "Correct data types"),
    "l1_types_bad": (": sai ở {x}", ": wrong in {x}"),
    "l1_cells": ("{n} ô", "{n} cell(s)"),
    "l1_keys": ("Không trùng khoá {k}", "No duplicate keys {k}"),
    "l1_keys_dup": (": {n} dòng trùng, vd {ex}", ": {n} duplicate row(s), e.g. {ex}"),
    "l1_no_key": ("Chưa khai báo cột khoá (khoa: true) nên không kiểm tra trùng",
                  "No key column declared (key: true), duplicates not checked"),
    "l1_blank": ("Ô trống dưới ngưỡng (mặc định {r})", "Blank cells under threshold (default {r})"),
    "l1_blank_over": (": vượt ở {x}", ": over in {x}"),

    # tầng 2
    "L2": ("--- Tầng 2: Đối soát ---", "--- Layer 2: Reconciliation ---"),
    "l2_rows": ("Số dòng: vào {i} = ra {o} + loại {x}", "Rows: in {i} = out {o} + excluded {x}"),
    "l2_rows_diff": (" (lệch {d})", " (off by {d})"),
    "l2_trace": ("Mỗi dòng gốc có mặt đúng một lần ở kết quả hoặc danh sách loại",
                 "Every source row appears exactly once in the result or the excluded list"),
    "l2_lost": (": mất {n} dòng, vd {ex}", ": {n} row(s) lost, e.g. {ex}"),
    "l2_doubled": (": lặp {n} dòng, vd {ex}", ": {n} row(s) repeated, e.g. {ex}"),
    "l2_agg": ("Số dòng: vào {i}, ra {o}, loại {x} (chế độ gộp, không so số dòng)",
               "Rows: in {i}, out {o}, excluded {x} (aggregate mode, row counts not compared)"),
    "l2_no_money_ok": ("Bộ dữ liệu không có cột tiền (tang_2.cot_tien: []), bỏ qua đối soát tổng tiền",
                       "Dataset has no amount columns (amount_columns: []), amount totals not reconciled"),
    "l2_no_money": ("Chưa khai báo cột tiền (tang_2.cot_tien) nên không đối soát tổng tiền",
                    "No amount columns declared (amount_columns), amount totals not reconciled"),
    "l2_col_missing": ("Tổng {col}: không tìm thấy cột ở file gốc hoặc kết quả",
                       "Total {col}: column not found in the source or the result"),
    "l2_total": ("Tổng {col}: vào {i} = ra {o} + loại {x}", "Total {col}: in {i} = out {o} + excluded {x}"),
    "l2_total_diff": (" (lệch {d})", " (off by {d})"),
    "l2_unreadable": ("; {n} ô gốc không đọc được thành số, đều nằm trong danh sách loại",
                      "; {n} source cells could not be read as numbers, all in the excluded list"),
    "l2_by_reason": ("    tiền {col} bị loại theo lý do: ", "    excluded {col} by reason: "),

    # tầng 3
    "L3": ("--- Tầng 3: Nghiệp vụ ---", "--- Layer 3: Business rules ---"),
    "l3_range": ("{col} trong khoảng [{lo}, {hi}]", "{col} within [{lo}, {hi}]"),
    "l3_range_bad": (": {n} dòng ngoài khoảng, vd {ex}", ": {n} row(s) out of range, e.g. {ex}"),
    "l3_allowed": ("{col} thuộc danh sách hợp lệ", "{col} in the allowed values"),
    "l3_allowed_bad": (": {n} dòng lạ, vd {ex}", ": {n} unexpected value(s), e.g. {ex}"),
    "l3_date_order": ("{a} không sau {b}", "{a} not after {b}"),
    "l3_rows_bad": (": {n} dòng sai, vd {ex}", ": {n} row(s) fail, e.g. {ex}"),
    "l3_rule_error": ("Quy tắc '{name}' không chạy được: {e}", "Rule '{name}' could not run: {e}"),
    "l3_future": ("{col} không nằm ở tương lai", "{col} not in the future"),
    "l3_future_bad": (": {n} dòng, vd {ex}", ": {n} row(s), e.g. {ex}"),
    "l3_none": ("Chưa có quy tắc nghiệp vụ nào (min/max/gia_tri_hop_le/thu_tu_ngay)",
                "No business rules defined yet (min/max/allowed_values/date_order)"),

    # tầng 4
    "L4": ("--- Tầng 4: Biến động ---", "--- Layer 4: Drift ---"),
    "l4_none": ("Chưa có lần chạy đạt trước đó với cùng bộ cột để so sánh",
                "No earlier passing run with the same columns to compare against"),
    "l4_rows": ("Số dòng ra {n} so với {prev} ({old}): {p} (ngưỡng ±{lim}%)",
                "Rows out {n} vs {prev} ({old}): {p} (threshold ±{lim}%)"),
    "l4_total": ("Tổng {col} so với {prev}: {p} (ngưỡng ±{lim}%)", "Total {col} vs {prev}: {p} (threshold ±{lim}%)"),

    # tầng 5
    "L5": ("--- Tầng 5: Người đối chiếu ---", "--- Layer 5: Human review ---"),
    "l5_skip": ("Chưa lấy mẫu đối chiếu vì còn lỗi mức CHẶN", "No review sample taken because BLOCK checks failed"),
    "l5_todo": ("☐ Mở file gốc, đối chiếu {n} dòng trong {f}, điền cột {col} (co/khong)",
                "☐ Open the source file, compare the {n} row(s) in {f}, fill in column {col} (yes/no)"),

    # run
    "run_header": ("=== Lần chạy {r} lúc {t} ===", "=== Run {r} at {t} ==="),
    "run_git": ("phiên bản script (git): {g}", "script version (git): {g}"),
    "run_nogit": ("chưa có git", "no git"),
    "run_note": ("ghi chú: {x}", "note: {x}"),
    "run_file": ("chỉ đọc file khớp: {x}", "only reading files matching: {x}"),
    "run_lock": ("raw: đặt chỉ đọc cho {f}", "raw: set {f} read-only"),
    "run_raw": ("raw: {f}  sha256 {h}...  {s} byte", "raw: {f}  sha256 {h}...  {s} bytes"),
    "run_conclusion": ("=== Kết luận ===", "=== Conclusion ==="),
    "run_blocked": ("CHƯA XONG: {n} lỗi mức CHẶN. Không xuất file kết quả.",
                    "NOT DONE: {n} BLOCK failures. No result file exported."),
    "run_done": ("Đã xuất {f} ({n} dòng). Cảnh báo: {w}. Còn chờ đối chiếu tay (tầng 5).",
                 "Exported {f} ({n} row(s)). Warnings: {w}. Waiting for manual review (layer 5)."),

    # khao_sat / profile
    "prof_title": ("# Đề xuất data_dictionary", "# Proposed data_dictionary"),
    "prof_scope": ("Khảo sát {n} file, {r} dòng: {f}", "Profiled {n} file(s), {r} row(s): {f}"),
    "prof_header": ("| Cột gốc | Kiểu đoán | % trống | Số giá trị khác nhau | Ví dụ |",
                    "| Source column | Guessed type | % blank | Distinct values | Examples |"),
    "prof_written": ("Đã ghi {f}", "Wrote {f}"),
    "prof_no_files": ("Không có file nào trong {d}", "No files in {d}"),
}

# Tên file và cột kết quả theo ngôn ngữ / output names by language
NAMES = {
    "SOURCE_FILE": ("_file_goc", "_source_file"),
    "SOURCE_ROW": ("_dong_goc", "_source_row"),
    "REASON": ("ly_do_loai", "exclusion_reason"),
    "DUP_OF": ("trung_voi_dong", "duplicate_of"),
    "RESULT_FILE": ("ket_qua.xlsx", "result.xlsx"),
    "SAMPLE_FILE": ("mau_doi_chieu.csv", "review_sample.csv"),
    "SAMPLE_MATCH": ("khop_file_goc", "matches_source"),
    "SAMPLE_NOTE": ("ghi_chu", "note"),
}

# Khoá cấu hình tiếng Anh -> tên nội bộ. Áp cho tên khoá, không áp cho tên cột của người dùng.
KEY_ALIASES = {
    # validation_rules
    "language": "ngon_ngu",
    "source": "nguon",
    "file_pattern": "mau_ten_file",
    "header_row": "dong_tieu_de",
    "lock_raw_files": "khoa_file_goc",
    "number_format": "dinh_dang_so",
    "decimal": "thap_phan",
    "thousands": "hang_nghin",
    "date_formats": "dinh_dang_ngay",
    "cleaning": "lam_sach",
    "on_type_error": "khi_loi_kieu",
    "drop_exact_duplicates": "bo_dong_trung_hoan_toan",
    "drop_rows_when": "loai_dong_khi",
    "column": "cot",
    "equals": "bang",
    "reason": "ly_do",
    "keep_only": "loc_dong",
    "dedupe_by_key": "bo_trung_theo_khoa",
    "export": "xuat",
    "keep_trace_columns": "giu_cot_truy_vet",
    "layer_1": "tang_1", "layer_2": "tang_2", "layer_3": "tang_3", "layer_4": "tang_4", "layer_5": "tang_5",
    "max_blank_ratio": "ty_le_trong_toi_da",
    "key": "khoa",
    "row_mode": "che_do_dong",
    "amount_columns": "cot_tien",
    "amount_tolerance": "sai_so_tien",
    "date_order": "thu_tu_ngay",
    "no_future_dates": "ngay_khong_tuong_lai",
    "conditions": "dieu_kien",
    "name": "ten",
    "when": "khi",
    "must": "phai",
    "level": "muc",
    "show_column": "hien_cot",
    "max_row_change_pct": "lech_so_dong_pct",
    "max_amount_change_pct": "lech_tong_tien_pct",
    "sample_rows": "so_dong",
    # data_dictionary
    "columns": "cot",
    "source_names": "ten_goc",
    "type": "kieu",
    "meaning": "nghia",
    "unit": "don_vi",
    "required": "bat_buoc",
    "non_negative": "khong_am",
    "allowed_values": "gia_tri_hop_le",
    "map": "anh_xa",
    "skip": "bo_qua",
    "status": "trang_thai",
}

VALUE_ALIASES = {
    "kieu": {"money": "tien", "percent": "phan_tram", "text": "string"},
    "trang_thai": {"confirmed": "xac_nhan", "unclear": "chua_ro"},
    "nguon": {"computed": "tinh_toan"},
    "khi_loi_kieu": {"drop_row": "loai_dong", "leave_blank": "de_trong"},
    "che_do_dong": {"preserve": "giu_nguyen", "aggregate": "gop"},
    "muc": {"block": "chan"},
}

# Các khoá mà bên dưới là tên cột hoặc giá trị của người dùng, không dịch khoá con
USER_KEYED = {"anh_xa", "loc_dong"}
