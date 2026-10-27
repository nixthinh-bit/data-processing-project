"""Bước 1: chuẩn hoá định dạng, bỏ dòng lỗi.  /  Step 1: normalise formats, drop bad rows.

Đọc mọi file trong data/raw (chỉ đọc), đổi tên cột về tên chuẩn theo data_dictionary,
ép kiểu từng ô, tách dòng lỗi ra file riêng kèm lý do. Không đoán: cột lạ hoặc cột còn
"chua_ro" trong data_dictionary thì dừng lại.

Kết quả: data/processed/<run_id>/01_cleaned.csv và 01_excluded.csv
Chạy riêng: python clean.py --run-id 2026-10-27_run01
"""
import argparse
import sys

import pandas as pd

import common as c


class StopRun(Exception):
    """Lỗi buộc dừng cả lần chạy, cần người dùng bổ sung thông tin."""


def clean(run_id, log):
    dictionary = c.load_dictionary()
    rules = c.load_rules()
    clean_rules = rules.get("lam_sach") or {}
    on_type_error = clean_rules.get("khi_loi_kieu", "loai_dong")
    drop_dupes = clean_rules.get("bo_dong_trung_hoan_toan", False)
    row_filter = clean_rules.get("loc_dong") or {}
    drop_when = clean_rules.get("loai_dong_khi") or []
    dedupe_by_key = clean_rules.get("bo_trung_theo_khoa", False)

    unclear = [k for k, v in dictionary["cot"].items() if (v or {}).get("trang_thai") == "chua_ro" and not (v or {}).get("bo_qua")]
    if unclear:
        raise StopRun(c.t("stop_unclear", cols=", ".join(unclear)))

    files = c.raw_files(rules)
    if not files:
        raise StopRun(c.t("stop_no_files", d=c.RAW_DIR))

    columns = c.active_columns(dictionary, include_computed=False)
    kept, excluded, mapped = [], [], set()
    for path in files:
        raw = c.read_raw_file(path, rules)
        mapping, unknown, skipped = c.column_map(raw.columns, dictionary)
        if unknown:
            raise StopRun(c.t("stop_unknown_cols", f=path.name, cols=unknown))
        mapped.update(mapping.values())
        missing = [k for k in columns if k not in mapping.values()]
        log.write(c.t("clean_file", f=path.name, n=len(raw), m=len(mapping))
                  + (c.t("clean_skipped", x=skipped) if skipped else "")
                  + (c.t("clean_missing", x=missing) if missing else ""))

        for _, row in raw.iterrows():
            values = row.drop(labels=c.TRACE_COLS)
            trace = {c.SOURCE_FILE: row[c.SOURCE_FILE], c.SOURCE_ROW: int(row[c.SOURCE_ROW])}
            if all(c._is_blank(v) for v in values):
                excluded.append({**trace, c.REASON: c.t("r_blank"), **_raw_values(row, mapping)})
                continue
            out, reasons = dict(trace), []
            for src, std in mapping.items():
                spec = columns.get(std) or {}
                try:
                    val = c.parse_value(row[src], spec, rules)
                except c.ParseError as e:
                    if on_type_error == "de_trong" and not spec.get("bat_buoc"):
                        log.write(c.t("type_blank_log", f=path.name, r=trace[c.SOURCE_ROW], col=std, e=e))
                        val = None
                    else:
                        reasons.append(f"{std}: {e}")
                        continue
                if val is None and spec.get("bat_buoc"):
                    reasons.append(c.t("r_required", col=std))
                out[std] = val
            outside = _drop_reason(out, drop_when) or _filter_reason(out, row_filter)
            if outside:
                excluded.append({**trace, c.REASON: outside, **_raw_values(row, mapping)})
            elif reasons:
                excluded.append({**trace, c.REASON: "; ".join(reasons), **_raw_values(row, mapping)})
            else:
                kept.append(out)

    cleaned = pd.DataFrame(kept, columns=c.TRACE_COLS + [k for k in columns if k in mapped])
    if drop_dupes and len(cleaned):
        value_cols = [k for k in cleaned.columns if k not in c.TRACE_COLS]
        dup = cleaned.duplicated(subset=value_cols, keep="first")
        for _, r in cleaned[dup].iterrows():
            excluded.append({c.SOURCE_FILE: r[c.SOURCE_FILE], c.SOURCE_ROW: r[c.SOURCE_ROW],
                             c.REASON: c.t("r_exact_dup"), **{k: r[k] for k in value_cols}})
        cleaned = cleaned[~dup]
    if dedupe_by_key and len(cleaned):
        cleaned = _dedupe_by_key(cleaned, columns, excluded, log)

    excluded_df = pd.DataFrame(excluded) if excluded else pd.DataFrame(columns=c.TRACE_COLS + [c.REASON])
    out_dir = c.run_dir(run_id)
    c.save_csv(cleaned, out_dir / "01_cleaned.csv")
    c.save_csv(excluded_df, out_dir / "01_excluded.csv")
    log.write(c.t("clean_summary", k=len(cleaned), x=len(excluded_df)))
    if len(excluded_df):
        for reason, n in excluded_df[c.REASON].value_counts().head(10).items():
            log.write(c.t("clean_reason_line", n=n, r=reason))
    return cleaned, excluded_df


def _drop_reason(out, drop_when):
    """Lý do loại theo lam_sach.loai_dong_khi (vd dòng "Tổng cộng" cuối bảng), ngược lại None."""
    for rule in drop_when:
        values = rule["bang"] if isinstance(rule["bang"], list) else [rule["bang"]]
        val = out.get(rule["cot"])
        if val is not None and str(val).casefold() in [str(x).casefold() for x in values]:
            return rule.get("ly_do") or f"{rule['cot']} = '{val}'"
    return None


def _filter_reason(out, row_filter):
    """Lý do loại nếu dòng nằm ngoài phạm vi lọc (lam_sach.loc_dong), ngược lại trả về None."""
    for col, allowed in row_filter.items():
        allowed = allowed if isinstance(allowed, list) else [allowed]
        if out.get(col) not in allowed:
            return c.t("r_outside", col=col, a=allowed)
    return None


def _dedupe_by_key(cleaned, columns, excluded, log):
    """Trùng khoá và giống hệt các cột khác: giữ dòng đầu, loại dòng sau kèm tham chiếu dòng giữ lại.
    Trùng khoá mà khác nội dung thì không tự chọn, giữ nguyên để tầng 1 chặn và hỏi người dùng."""
    keys = [k for k, v in columns.items() if (v or {}).get("khoa") and k in cleaned.columns]
    if not keys:
        log.write(c.t("dedupe_nokey"))
        return cleaned
    value_cols = [k for k in cleaned.columns if k not in c.TRACE_COLS]
    dup = cleaned[cleaned.duplicated(subset=keys, keep=False)]
    drop, conflicts = [], 0
    for _, grp in dup.groupby(keys, dropna=False, sort=False):
        if len(grp[value_cols].drop_duplicates()) > 1:
            conflicts += 1
            continue
        first = grp.iloc[0]
        ref = f"{first[c.SOURCE_FILE]}:{first[c.SOURCE_ROW]}"
        for idx, r in grp.iloc[1:].iterrows():
            excluded.append({c.SOURCE_FILE: r[c.SOURCE_FILE], c.SOURCE_ROW: r[c.SOURCE_ROW],
                             c.REASON: c.t("r_key_dup", k="+".join(keys)),
                             c.DUP_OF: ref, **{k: r[k] for k in value_cols}})
            drop.append(idx)
    log.write(c.t("dedupe_summary", k=keys, g=dup.groupby(keys, dropna=False).ngroups, n=len(drop))
              + (c.t("dedupe_conflicts", n=conflicts) if conflicts else ""))
    return cleaned.drop(index=drop)


def _raw_values(row, mapping):
    """Giữ giá trị gốc (chưa ép kiểu) của dòng bị loại, đặt theo tên chuẩn để đối soát."""
    return {std: row[src] for src, std in mapping.items()}


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--run-id", default=None)
    args = ap.parse_args()
    run_id = args.run_id or c.new_run_id()
    log = c.RunLog(run_id)
    try:
        clean(run_id, log)
    except StopRun as e:
        log.write(f"[{c.label(c.CHAN)}] ✗ {e}")
        sys.exit(2)


if __name__ == "__main__":
    main()
