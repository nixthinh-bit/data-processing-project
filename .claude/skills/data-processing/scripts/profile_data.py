"""Khảo sát file trong data/raw để đề xuất data_dictionary (bước 2 khi bắt đầu dự án).
Profile the files in data/raw and propose a data_dictionary (step 2 when starting).

Không sửa reference/data_dictionary.md. Kết quả ghi ra data/processed/_profile/proposed_data_dictionary.md,
mọi cột đều để `trang_thai: chua_ro` cho tới khi người dùng xác nhận nghĩa, đơn vị và giá trị hợp lệ.

Dùng / usage: python profile_data.py
"""
import re
import unicodedata

import pandas as pd
import yaml

import common as c


def slug(name):
    s = unicodedata.normalize("NFD", str(name).replace("đ", "d").replace("Đ", "D"))
    s = "".join(ch for ch in s if unicodedata.category(ch) != "Mn")
    return re.sub(r"[^a-z0-9]+", "_", s.lower()).strip("_") or "cot"


def guess_kind(series):
    s = series.dropna()
    if s.empty:
        return "string"
    if s.map(lambda v: isinstance(v, (pd.Timestamp,)) or hasattr(v, "year")).mean() > 0.9:
        return "date"
    nums = s[s.map(lambda v: isinstance(v, (int, float)) and not isinstance(v, bool))]
    if len(nums) / len(s) > 0.9:
        return "int" if nums.map(lambda v: float(v).is_integer()).all() else "float"
    return "string"


def main():
    rules = c.load_rules()
    files = c.raw_files(rules)
    if not files:
        raise SystemExit(c.t("prof_no_files", d=c.RAW_DIR))
    frames = [c.read_raw_file(p, rules) for p in files]
    df = pd.concat(frames, ignore_index=True)
    lines = [c.t("prof_title"), "",
             c.t("prof_scope", n=len(files), r=len(df), f=", ".join(p.name for p in files)), "",
             c.t("prof_header"), "|---|---|---|---|---|"]
    proposal = {}
    for col in df.columns:
        if col in c.TRACE_COLS:
            continue
        s = df[col]
        kind = guess_kind(s)
        examples = ", ".join(str(v) for v in s.dropna().unique()[:5])
        lines.append(f"| {col} | {kind} | {s.isna().mean():.0%} | {s.nunique()} | {examples} |")
        if c.LANG == "en":
            proposal[slug(col)] = {"source_names": [col], "type": kind, "meaning": "", "unit": "",
                                   "required": bool(s.notna().all()), "status": "unclear"}
        else:
            proposal[slug(col)] = {"ten_goc": [col], "kieu": kind, "nghia": "", "don_vi": "",
                                   "bat_buoc": bool(s.notna().all()), "trang_thai": "chua_ro"}
    top = "columns" if c.LANG == "en" else "cot"
    lines += ["", "```yaml", yaml.safe_dump({top: proposal}, allow_unicode=True, sort_keys=False).rstrip(), "```"]
    out = c.PROCESSED_DIR / "_profile" / "proposed_data_dictionary.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines[:len(proposal) + 6]))
    print("\n" + c.t("prof_written", f=out))


if __name__ == "__main__":
    main()
