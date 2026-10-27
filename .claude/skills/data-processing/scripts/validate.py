"""Bước 3: kiểm tra 4 tầng tự động và chuẩn bị mẫu cho tầng 5 (người đối chiếu tay).
Step 3: four automatic check layers and a sample for layer 5 (manual review).

  Tầng 1 Cấu trúc   CHẶN      đủ cột, đúng kiểu, không trùng khoá, ô trống dưới ngưỡng, file gốc không bị sửa
  Tầng 2 Đối soát   CHẶN      số dòng và tổng tiền đầu vào khớp đầu ra + dòng bị loại
  Tầng 3 Nghiệp vụ  CẢNH BÁO  giá trị hợp lý theo data_dictionary, logic ngày
  Tầng 4 Biến động  CẢNH BÁO  lệch so với lần chạy trước vượt ngưỡng
  Tầng 5 Người      THỦ CÔNG  mau_doi_chieu.csv (review_sample.csv) trong thư mục outputs của lần chạy

Ngưỡng nằm ở reference/validation_rules.md, không sửa trong code.
Chạy riêng (sau transform.py): python validate.py --run-id 2026-10-27_run01
"""
import argparse
import hashlib
import json

import pandas as pd

import common as c

MAX_EXAMPLES = 5


def _examples(df, mask, col=None):
    rows = df[mask].head(MAX_EXAMPLES)
    parts = []
    for _, r in rows.iterrows():
        ref = f"{r[c.SOURCE_FILE]}:{r[c.SOURCE_ROW]}"
        val = r[col] if col else None
        if isinstance(val, pd.Timestamp):
            val = val.date()
        parts.append(f"{ref} ({val})" if col else ref)
    more = int(mask.sum()) - len(parts)
    return ", ".join(parts) + (c.t("more_rows", n=more) if more > 0 else "")


def _read_raw_all(rules):
    frames = [c.read_raw_file(p, rules) for p in c.raw_files(rules)]
    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame(columns=c.TRACE_COLS)


def _raw_amount(raw, dictionary, rules, std_col):
    """Giá trị tiền ở file gốc theo tên cột chuẩn. Trả về (Series số, số ô không đọc được)."""
    mapping, _, _ = c.column_map(raw.columns, dictionary)
    src = [s for s, std in mapping.items() if std == std_col]
    if not src:
        return None, 0
    fmt = rules.get("dinh_dang_so") or {}
    values, bad = [], 0
    for v in raw[src[0]]:
        try:
            values.append(c.parse_number(v, fmt))
        except c.ParseError:
            values.append(None)
            bad += 1
    return pd.Series(values, index=raw.index, dtype="float64"), bad


# ---------- tầng 1 ----------

def tang_1(final, dictionary, rules, log, checksums_before):
    r1 = rules.get("tang_1") or {}
    cols = c.active_columns(dictionary)
    log.write(c.t("L1"))

    if checksums_before is not None:
        now = {p.name: c.sha256(p) for p in c.raw_files(rules)}
        changed = [n for n, h in checksums_before.items() if now.get(n) != h]
        log.check(c.CHAN, not changed, c.t("l1_raw_same") + (c.t("l1_raw_changed", x=changed) if changed else ""))

    missing = [k for k in cols if k not in final.columns]
    log.check(c.CHAN, not missing, c.t("l1_cols") + (c.t("l1_cols_missing", x=missing) if missing else ""))
    extra = [k for k in final.columns if k not in dictionary["cot"] and k not in c.TRACE_COLS]
    log.check(c.CHAN, not extra, c.t("l1_extra") + (c.t("l1_extra_found", x=extra) if extra else ""))

    type_errors = []
    for name, spec in cols.items():
        if name not in final.columns:
            continue
        kind = (spec or {}).get("kieu", "string")
        s = final[name].dropna()
        if kind in ("int", "float", "tien"):
            bad = pd.to_numeric(s, errors="coerce").isna()
            if kind == "int" and not bad.all():
                nums = pd.to_numeric(s[~bad])
                bad = bad | (nums % 1 != 0).reindex(s.index, fill_value=False)
        elif kind == "date":
            bad = pd.to_datetime(s, errors="coerce").isna()
        else:
            continue
        if bad.any():
            type_errors.append(f"{name} ({c.t('l1_cells', n=int(bad.sum()))})")
    log.check(c.CHAN, not type_errors, c.t("l1_types") + (c.t("l1_types_bad", x=type_errors) if type_errors else ""))

    keys = r1.get("khoa") or [k for k, v in cols.items() if (v or {}).get("khoa")]
    keys = [k for k in keys if k in final.columns]
    if keys:
        dup = final.duplicated(subset=keys, keep=False)
        log.check(c.CHAN, not dup.any(), c.t("l1_keys", k=keys) + (c.t("l1_keys_dup", n=int(dup.sum()), ex=_examples(final, dup, keys[0])) if dup.any() else ""))
    else:
        log.check(c.CANH_BAO, False, c.t("l1_no_key"))

    default_ratio = float(r1.get("ty_le_trong_toi_da", 0.05))
    over = []
    for name, spec in cols.items():
        if name not in final.columns or not len(final):
            continue
        spec = spec or {}
        limit = 0.0 if spec.get("bat_buoc") else float(spec.get("ty_le_trong_toi_da", default_ratio))
        ratio = final[name].isna().mean()
        if ratio > limit:
            over.append(f"{name} {ratio:.1%} > {limit:.0%}")
    log.check(c.CHAN, not over, c.t("l1_blank", r=f"{default_ratio:.0%}") + (c.t("l1_blank_over", x=over) if over else ""))


# ---------- tầng 2 ----------

def tang_2(final, excluded, raw, dictionary, rules, log):
    r2 = rules.get("tang_2") or {}
    mode = r2.get("che_do_dong", "giu_nguyen")
    tol = float(r2.get("sai_so_tien", 0.01))
    log.write(c.t("L2"))
    summary = {"dong_vao": len(raw), "dong_ra": len(final), "dong_loai": len(excluded), "tong_tien": {},
               "cot": sorted(c.active_columns(dictionary))}

    if mode == "giu_nguyen":
        ok = len(raw) == len(final) + len(excluded)
        log.check(c.CHAN, ok, c.t("l2_rows", i=len(raw), o=len(final), x=len(excluded))
                  + ("" if ok else c.t("l2_rows_diff", d=len(raw) - len(final) - len(excluded))))
        key = lambda df: list(zip(df[c.SOURCE_FILE].astype(str), df[c.SOURCE_ROW].astype(int)))
        seen = pd.Series(key(final) + (key(excluded) if len(excluded) else []))
        raw_keys = set(key(raw))
        lost = raw_keys - set(seen)
        doubled = seen[seen.duplicated()]
        log.check(c.CHAN, not lost and doubled.empty,
                  c.t("l2_trace")
                  + (c.t("l2_lost", n=len(lost), ex=sorted(lost)[:MAX_EXAMPLES]) if lost else "")
                  + (c.t("l2_doubled", n=len(doubled), ex=list(doubled[:MAX_EXAMPLES])) if not doubled.empty else ""))
    else:
        log.write(c.t("l2_agg", i=len(raw), o=len(final), x=len(excluded)))

    amount_cols = (r2["cot_tien"] or []) if "cot_tien" in r2 else [k for k, v in dictionary["cot"].items() if (v or {}).get("kieu") == "tien" and (v or {}).get("nguon") != "tinh_toan"]
    if "cot_tien" in r2 and not r2["cot_tien"]:
        log.check(c.CANH_BAO, True, c.t("l2_no_money_ok"))
    elif not amount_cols:
        log.check(c.CANH_BAO, False, c.t("l2_no_money"))
    excl_keys = set(zip(excluded[c.SOURCE_FILE].astype(str), excluded[c.SOURCE_ROW].astype(int))) if len(excluded) else set()
    raw_keys_series = pd.Series(list(zip(raw[c.SOURCE_FILE].astype(str), raw[c.SOURCE_ROW].astype(int))), index=raw.index)
    for col in amount_cols:
        amounts, bad = _raw_amount(raw, dictionary, rules, col)
        if amounts is None or col not in final.columns:
            log.check(c.CHAN, False, c.t("l2_col_missing", col=col))
            continue
        in_total = amounts.sum()
        excl_total = amounts[raw_keys_series.isin(excl_keys)].sum()
        out_total = pd.to_numeric(final[col], errors="coerce").sum()
        diff = in_total - out_total - excl_total
        summary["tong_tien"][col] = {"vao": in_total, "ra": out_total, "loai": excl_total}
        log.check(c.CHAN, abs(diff) <= tol,
                  c.t("l2_total", col=col, i=f"{in_total:,.2f}", o=f"{out_total:,.2f}", x=f"{excl_total:,.2f}")
                  + ("" if abs(diff) <= tol else c.t("l2_total_diff", d=f"{diff:,.2f}"))
                  + (c.t("l2_unreadable", n=bad) if bad else ""))
        if excl_total:
            reason_of = dict(zip(zip(excluded[c.SOURCE_FILE].astype(str), excluded[c.SOURCE_ROW].astype(int)), excluded[c.REASON]))
            by_reason = amounts.groupby(raw_keys_series.map(reason_of)).sum()
            parts = [f"{r}: {v:,.2f}" for r, v in by_reason.sort_values(ascending=False).items() if v]
            log.write(c.t("l2_by_reason", col=col) + "; ".join(parts))
    return summary


# ---------- tầng 3 ----------

def tang_3(final, dictionary, rules, log):
    r3 = rules.get("tang_3") or {}
    cols = c.active_columns(dictionary)
    log.write(c.t("L3"))
    checked = 0
    for name, spec in cols.items():
        spec = spec or {}
        if name not in final.columns:
            continue
        s = final[name]
        lo = 0 if spec.get("khong_am") and spec.get("min") is None else spec.get("min")
        hi = spec.get("max")
        if lo is not None or hi is not None:
            checked += 1
            vals = pd.to_datetime(s, errors="coerce") if spec.get("kieu") == "date" else pd.to_numeric(s, errors="coerce")
            lo_v = pd.Timestamp(lo) if spec.get("kieu") == "date" and lo is not None else lo
            hi_v = pd.Timestamp(hi) if spec.get("kieu") == "date" and hi is not None else hi
            bad = pd.Series(False, index=s.index)
            if lo_v is not None:
                bad |= vals < lo_v
            if hi_v is not None:
                bad |= vals > hi_v
            log.check(c.CANH_BAO, not bad.any(), c.t("l3_range", col=name, lo=lo if lo is not None else "...", hi=hi if hi is not None else "...")
                      + (c.t("l3_range_bad", n=int(bad.sum()), ex=_examples(final, bad, name)) if bad.any() else ""))
        allowed = spec.get("gia_tri_hop_le")
        if allowed:
            checked += 1
            bad = s.notna() & ~s.astype(str).isin([str(a) for a in allowed])
            log.check(c.CANH_BAO, not bad.any(), c.t("l3_allowed", col=name)
                      + (c.t("l3_allowed_bad", n=int(bad.sum()), ex=_examples(final, bad, name)) if bad.any() else ""))

    for pair in r3.get("thu_tu_ngay") or []:
        a, b = pair
        if a in final.columns and b in final.columns:
            checked += 1
            da, db = pd.to_datetime(final[a], errors="coerce"), pd.to_datetime(final[b], errors="coerce")
            bad = da.notna() & db.notna() & (da > db)
            log.check(c.CANH_BAO, not bad.any(), c.t("l3_date_order", a=a, b=b)
                      + (c.t("l3_rows_bad", n=int(bad.sum()), ex=_examples(final, bad, b)) if bad.any() else ""))

    for rule in r3.get("dieu_kien") or []:
        checked += 1
        level = c.CHAN if str(rule.get("muc", "")).casefold() in ("chan", "chặn") else c.CANH_BAO
        try:
            applies = final.eval(rule["khi"], engine="python") if rule.get("khi") else pd.Series(True, index=final.index)
            holds = final.eval(rule["phai"], engine="python")
        except Exception as e:  # biểu thức viết sai trong validation_rules
            log.check(c.CHAN, False, c.t("l3_rule_error", name=rule.get("ten"), e=e))
            continue
        bad = pd.Series(applies, index=final.index).fillna(False).astype(bool) & ~pd.Series(holds, index=final.index).fillna(False).astype(bool)
        show = rule.get("hien_cot") or None
        log.check(level, not bad.any(), rule.get("ten", rule["phai"])
                  + (c.t("l3_rows_bad", n=int(bad.sum()), ex=_examples(final, bad, show)) if bad.any() else ""))

    for col in r3.get("ngay_khong_tuong_lai") or []:
        if col in final.columns:
            checked += 1
            bad = pd.to_datetime(final[col], errors="coerce") > pd.Timestamp.today().normalize()
            log.check(c.CANH_BAO, not bad.any(), c.t("l3_future", col=col)
                      + (c.t("l3_future_bad", n=int(bad.sum()), ex=_examples(final, bad, col)) if bad.any() else ""))
    if not checked:
        log.check(c.CANH_BAO, False, c.t("l3_none"))


# ---------- tầng 4 ----------

def _previous_meta(run_id, columns):
    """Lần chạy đạt gần nhất trước run_id có cùng bộ cột (cùng loại dữ liệu)."""
    metas = []
    for p in sorted(c.OUTPUTS_DIR.glob("*_run*/run_meta.json")):
        if p.parent.name >= run_id:
            continue
        meta = json.loads(p.read_text(encoding="utf-8"))
        if meta.get("trang_thai") != "CHAN" and (meta.get("doi_soat") or {}).get("cot") == columns:
            metas.append(meta)
    return metas[-1] if metas else None


def tang_4(run_id, summary, rules, log):
    r4 = rules.get("tang_4") or {}
    log.write(c.t("L4"))
    prev = _previous_meta(run_id, summary["cot"])
    if not prev:
        log.check(c.CANH_BAO, True, c.t("l4_none"))
        return
    pr = prev["doi_soat"]
    lim_rows = float(r4.get("lech_so_dong_pct", 20))
    lim_amt = float(r4.get("lech_tong_tien_pct", 20))

    def pct(new, old):
        return 0.0 if old == 0 and new == 0 else (float("inf") if old == 0 else (new - old) / abs(old) * 100)

    p = pct(summary["dong_ra"], pr["dong_ra"])
    log.check(c.CANH_BAO, abs(p) <= lim_rows, c.t("l4_rows", n=summary["dong_ra"], prev=prev["run_id"], old=pr["dong_ra"], p=f"{p:+.1f}%", lim=f"{lim_rows:g}"))
    for col, t in summary["tong_tien"].items():
        old = (pr.get("tong_tien") or {}).get(col)
        if old is None:
            continue
        p = pct(t["ra"], old["ra"])
        log.check(c.CANH_BAO, abs(p) <= lim_amt, c.t("l4_total", col=col, prev=prev["run_id"], p=f"{p:+.1f}%", lim=f"{lim_amt:g}"))


# ---------- tầng 5 ----------

def tang_5(run_id, final, dictionary, rules, log, out_dir):
    r5 = rules.get("tang_5") or {}
    n = min(int(r5.get("so_dong", 8)), len(final))
    log.write(c.t("L5"))
    if log.blocking_failures():
        log.write(f"[{c.label(c.THU_CONG)}] {c.t('l5_skip')}")
        return
    if not n:
        return
    sample = final.sample(n=n, random_state=int(hashlib.md5(run_id.encode()).hexdigest()[:8], 16))
    keep = c.TRACE_COLS + [k for k in c.active_columns(dictionary) if k in sample.columns]
    sample = sample[keep].copy()
    sample[c.SAMPLE_MATCH] = ""
    sample[c.SAMPLE_NOTE] = ""
    c.save_csv(sample, out_dir / c.SAMPLE_FILE)
    log.write(f"[{c.label(c.THU_CONG)}] " + c.t("l5_todo", n=n, f=f"{out_dir.name}/{c.SAMPLE_FILE}", col=c.SAMPLE_MATCH))


def validate(run_id, log, out_dir, checksums_before=None):
    rules = c.load_rules()
    dictionary = c.load_dictionary()
    cols = c.active_columns(dictionary)
    d = c.run_dir(run_id)
    final = c.read_csv(d / "02_transformed.csv", cols)
    excluded = pd.read_csv(d / "01_excluded.csv", dtype=str, encoding="utf-8-sig")
    raw = _read_raw_all(rules)

    tang_1(final, dictionary, rules, log, checksums_before)
    summary = tang_2(final, excluded, raw, dictionary, rules, log)
    tang_3(final, dictionary, rules, log)
    tang_4(run_id, summary, rules, log)
    tang_5(run_id, final, dictionary, rules, log, out_dir)
    return final, summary


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--run-id", required=True)
    args = ap.parse_args()
    out_dir = c.OUTPUTS_DIR / args.run_id
    out_dir.mkdir(parents=True, exist_ok=True)
    log = c.RunLog(args.run_id)
    validate(args.run_id, log, out_dir)
    raise SystemExit(1 if log.blocking_failures() else 0)


if __name__ == "__main__":
    main()
