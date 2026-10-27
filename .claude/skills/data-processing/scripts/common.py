"""Hàm dùng chung cho các script: đường dẫn, đọc cấu hình từ file .md, ngôn ngữ, ghi run log, ép kiểu.

Shared helpers: paths, config loading from .md files, language, run log, type parsing.

Cấu hình (data_dictionary, validation_rules) nằm trong các khối ```yaml của file Markdown
ở thư mục reference/, để người không đọc code vẫn sửa được. Tên khoá viết bằng tiếng Việt hoặc
tiếng Anh đều được (xem messages.KEY_ALIASES); bên trong code dùng tên tiếng Việt.
"""
import datetime as dt
import hashlib
import json
import re
import subprocess
from pathlib import Path

import pandas as pd
import yaml

import messages as m

SKILL_DIR = Path(__file__).resolve().parent.parent
ROOT = SKILL_DIR.parents[2]
REF_DIR = SKILL_DIR / "reference"
RAW_DIR = ROOT / "data" / "raw"
PROCESSED_DIR = ROOT / "data" / "processed"
OUTPUTS_DIR = ROOT / "outputs"
RUN_LOG_DIR = ROOT / "logs" / "run_log"

# Mã mức kiểm tra (nội bộ). Nhãn hiển thị theo ngôn ngữ lấy bằng label().
CHAN = "CHAN"
CANH_BAO = "CANH_BAO"
THU_CONG = "THU_CONG"

LANG = "vi"


def t(key, **kw):
    """Thông điệp theo ngôn ngữ đang chọn."""
    vi, en = m.MESSAGES[key]
    return (en if LANG == "en" else vi).format(**kw)


def label(level):
    return t(level)


def set_language(lang):
    """Đặt ngôn ngữ cho log, lý do loại, tên cột truy vết và tên file kết quả."""
    global LANG, SOURCE_FILE, SOURCE_ROW, TRACE_COLS, REASON, DUP_OF, RESULT_FILE, SAMPLE_FILE, SAMPLE_MATCH, SAMPLE_NOTE
    LANG = "en" if str(lang).lower().startswith("en") else "vi"
    i = 1 if LANG == "en" else 0
    names = {k: v[i] for k, v in m.NAMES.items()}
    SOURCE_FILE, SOURCE_ROW = names["SOURCE_FILE"], names["SOURCE_ROW"]
    TRACE_COLS = [SOURCE_FILE, SOURCE_ROW]
    REASON, DUP_OF = names["REASON"], names["DUP_OF"]
    RESULT_FILE, SAMPLE_FILE = names["RESULT_FILE"], names["SAMPLE_FILE"]
    SAMPLE_MATCH, SAMPLE_NOTE = names["SAMPLE_MATCH"], names["SAMPLE_NOTE"]


# Cột kỹ thuật do clean.py thêm vào để truy vết từng dòng về file và dòng Excel gốc,
# cùng các tên file, tên cột khác phụ thuộc ngôn ngữ. Giá trị đặt trong set_language().
SOURCE_FILE = SOURCE_ROW = REASON = DUP_OF = RESULT_FILE = SAMPLE_FILE = SAMPLE_MATCH = SAMPLE_NOTE = None
TRACE_COLS = []
set_language("vi")


# ---------- cấu hình ----------

def load_yaml_blocks(md_path):
    """Gộp mọi khối ```yaml trong một file Markdown thành một dict, đã đổi khoá tiếng Anh về tên nội bộ."""
    text = Path(md_path).read_text(encoding="utf-8")
    data = {}
    for block in re.findall(r"```ya?ml\s*\n(.*?)```", text, re.S):
        loaded = yaml.safe_load(block) or {}
        data.update(_normalize_keys(loaded))
    return data


def _normalize_keys(obj):
    """Đổi khoá cấu hình tiếng Anh về tên nội bộ. Không đụng tới tên cột hay giá trị của người dùng."""
    if isinstance(obj, list):
        return [_normalize_keys(x) for x in obj]
    if not isinstance(obj, dict):
        return obj
    out = {}
    for k, v in obj.items():
        key = m.KEY_ALIASES.get(k, k) if isinstance(k, str) else k
        if key == "cot" and isinstance(v, dict):
            v = {col: _normalize_keys(spec) for col, spec in v.items()}  # tên cột giữ nguyên
        elif key in m.USER_KEYED:
            pass
        else:
            v = _normalize_keys(v)
        if key in m.VALUE_ALIASES and isinstance(v, str):
            v = m.VALUE_ALIASES[key].get(v, v)
        out[key] = v
    return out


def load_dictionary():
    d = load_yaml_blocks(REF_DIR / "data_dictionary.md")
    d["cot"] = d.get("cot") or {}
    return d


def load_rules():
    rules = load_yaml_blocks(REF_DIR / "validation_rules.md")
    set_language(rules.get("ngon_ngu", "vi"))
    return rules


def active_columns(dictionary, include_computed=True):
    """Các cột chuẩn sẽ có trong kết quả (bỏ cột đánh dấu bo_qua)."""
    cols = {}
    for name, spec in dictionary["cot"].items():
        spec = spec or {}
        if spec.get("bo_qua"):
            continue
        if not include_computed and spec.get("nguon") == "tinh_toan":
            continue
        cols[name] = spec
    return cols


# ---------- run, log, truy vết ----------

def new_run_id(today=None):
    today = today or dt.date.today().isoformat()
    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
    nums = []
    for p in OUTPUTS_DIR.glob(f"{today}_run*"):
        m = re.match(rf"{re.escape(today)}_run(\d+)$", p.name)
        if m:
            nums.append(int(m.group(1)))
    return f"{today}_run{(max(nums) + 1 if nums else 1):02d}"


class RunLog:
    """Script tự ghi log; mỗi dòng có giờ. Claude không viết thay vào file này."""

    def __init__(self, run_id):
        RUN_LOG_DIR.mkdir(parents=True, exist_ok=True)
        self.path = RUN_LOG_DIR / f"{run_id}.log"
        self.results = []  # (muc, dat, thong_diep)

    def write(self, line=""):
        stamp = dt.datetime.now().strftime("%H:%M:%S")
        with self.path.open("a", encoding="utf-8") as f:
            f.write(f"{stamp}  {line}\n" if line else "\n")
        print(line)

    def check(self, level, ok, message):
        if ok:
            symbol = "✓"
        elif level == CHAN:
            symbol = "✗"
        else:
            symbol = "⚠"
        self.results.append((level, ok, message))
        self.write(f"[{label(level)}] {symbol} {message}")
        return ok

    def blocking_failures(self):
        return [r for r in self.results if r[0] == CHAN and not r[1]]

    def warnings(self):
        return [r for r in self.results if r[0] == CANH_BAO and not r[1]]


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


# run.py --file ghi đè mau_ten_file cho riêng lần chạy đó
RAW_PATTERN_OVERRIDE = None


def raw_files(rules):
    pattern = RAW_PATTERN_OVERRIDE or (rules.get("nguon") or {}).get("mau_ten_file", "*.xlsx")
    return sorted(p for p in RAW_DIR.glob(pattern) if p.is_file() and not p.name.startswith(("~$", ".")))


def git_commit():
    try:
        out = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT,
                             capture_output=True, text=True, timeout=5)
        dirty = subprocess.run(["git", "status", "--porcelain", "--", ".claude"], cwd=ROOT,
                               capture_output=True, text=True, timeout=5)
        if out.returncode != 0:
            return None
        return out.stdout.strip() + ("+uncommitted" if dirty.stdout.strip() else "")
    except (OSError, subprocess.SubprocessError):
        return None


def write_json(path, data):
    Path(path).write_text(json.dumps(data, ensure_ascii=False, indent=2, default=str), encoding="utf-8")


# ---------- đọc file gốc, ép kiểu ----------

def normalize_header(name):
    return re.sub(r"\s+", " ", str(name)).strip().casefold()


def read_raw_file(path, rules):
    """Đọc một file gốc ở chế độ chỉ đọc, giữ nguyên giá trị (dtype=object), thêm cột truy vết."""
    src = rules.get("nguon") or {}
    header = int(src.get("dong_tieu_de", 1)) - 1
    sheet = src.get("sheet", 0)
    df = pd.read_excel(path, sheet_name=sheet, header=header, dtype=object)
    df.columns = [str(c).strip() for c in df.columns]
    df = df.loc[:, [c for c in df.columns if not c.startswith("Unnamed:")] or df.columns]
    df[SOURCE_FILE] = path.name
    df[SOURCE_ROW] = df.index + header + 2  # số dòng thật trong Excel
    return df.reset_index(drop=True)


def column_map(df_columns, dictionary):
    """Trả về ({ten_goc: ten_chuan}, [cot_la], [cot_bo_qua])."""
    lookup = {}
    skipped_names = set()
    for std, spec in dictionary["cot"].items():
        spec = spec or {}
        if spec.get("nguon") == "tinh_toan":
            continue
        names = spec.get("ten_goc") or [std]
        if isinstance(names, str):
            names = [names]
        for n in list(names) + [std]:
            lookup[normalize_header(n)] = std
            if spec.get("bo_qua"):
                skipped_names.add(normalize_header(n))
    mapping, unknown, skipped = {}, [], []
    for c in df_columns:
        if c in TRACE_COLS:
            continue
        key = normalize_header(c)
        if key in skipped_names:
            skipped.append(c)
        elif key in lookup:
            mapping[c] = lookup[key]
        else:
            unknown.append(c)
    return mapping, unknown, skipped


class ParseError(ValueError):
    pass


def _is_blank(v):
    if v is None:
        return True
    if isinstance(v, str):
        return v.strip() == ""
    try:
        return bool(pd.isna(v))
    except (TypeError, ValueError):
        return False


def parse_number(v, fmt):
    """Đọc số. Ô số thật giữ nguyên; ô chữ phải đúng định dạng khai báo (dinh_dang_so).
    Chuỗi đọc được theo hai cách (vd "5,040" khi dấu thập phân là ",") bị coi là mơ hồ và báo lỗi, không đoán."""
    if _is_blank(v):
        return None
    if isinstance(v, bool):
        raise ParseError(t("not_number", v=v))
    if isinstance(v, (int, float)):
        return float(v)
    s = str(v).strip()
    s = re.sub(r"(?i)(vnđ|vnd|đ|usd|\$|₫)", "", s).replace(" ", "").replace("\u00a0", "")
    neg = s.startswith("(") and s.endswith(")") or s.startswith("-")
    s = s.strip("()").lstrip("+-")
    dec = re.escape(fmt.get("thap_phan", ","))
    thou = re.escape(fmt.get("hang_nghin", "."))
    grouped = rf"\d{{1,3}}({thou}\d{{3}})+({dec}\d+)?"
    plain = rf"\d+({dec}\d+)?"
    if re.fullmatch(grouped, s):
        pass
    elif re.fullmatch(plain, s):
        if re.fullmatch(rf"\d{{1,3}}{dec}\d{{3}}", s):
            raise ParseError(t("num_ambiguous", v=v))
    else:
        raise ParseError(t("num_format", v=v))
    n = float(s.replace(fmt.get("hang_nghin", "."), "").replace(fmt.get("thap_phan", ","), "."))
    return -n if neg else n


def parse_percent(v, fmt):
    """Tỷ lệ lưu dạng 0..1. "15%" thành 0.15. Số trần lớn hơn 1 (vd 15) không rõ là 15% hay 1500%, báo lỗi."""
    if _is_blank(v):
        return None
    if isinstance(v, str) and v.strip().endswith("%"):
        return parse_number(v.strip()[:-1], fmt) / 100
    n = parse_number(v, fmt)
    if n is not None and abs(n) > 1:
        raise ParseError(t("pct_ambiguous", v=v, a=f"{n:g}", b=f"{n * 100:g}"))
    return n


def parse_date(v, formats):
    if _is_blank(v):
        return None
    if isinstance(v, (dt.datetime, pd.Timestamp)):
        return pd.Timestamp(v).normalize()
    if isinstance(v, dt.date):
        return pd.Timestamp(v)
    if isinstance(v, (int, float)) and 20000 < float(v) < 80000:  # số serial của Excel
        return pd.Timestamp("1899-12-30") + pd.Timedelta(days=float(v))
    s = str(v).strip()
    for f in formats:
        try:
            return pd.Timestamp(dt.datetime.strptime(s, f))
        except ValueError:
            continue
    raise ParseError(t("date_format", v=v, f=formats))


def parse_string(v):
    if _is_blank(v):
        return None
    if isinstance(v, float) and v.is_integer():
        return str(int(v))
    return re.sub(r"\s+", " ", str(v)).strip()


_BOOL = {"có": True, "co": True, "yes": True, "y": True, "true": True, "1": True, "x": True,
         "không": False, "khong": False, "no": False, "n": False, "false": False, "0": False}


def parse_bool(v):
    if _is_blank(v):
        return None
    key = str(v).strip().casefold()
    if key in _BOOL:
        return _BOOL[key]
    raise ParseError(t("not_bool", v=v))


def parse_value(v, spec, rules):
    kind = (spec or {}).get("kieu", "string")
    fmt = (spec or {}).get("dinh_dang_so") or rules.get("dinh_dang_so") or {}
    if kind == "phan_tram":
        return parse_percent(v, fmt)
    if kind in ("int", "float", "tien"):
        n = parse_number(v, fmt)
        if n is not None and kind == "int":
            if not float(n).is_integer():
                raise ParseError(t("not_int", v=v))
            return int(n)
        return n
    if kind == "date":
        return parse_date(v, rules.get("dinh_dang_ngay") or ["%d/%m/%Y", "%Y-%m-%d"])
    if kind == "bool":
        return parse_bool(v)
    val = parse_string(v)
    mapping = (spec or {}).get("anh_xa")
    if mapping and val is not None:
        lookup = {str(k).casefold(): t for k, t in mapping.items()}
        val = lookup.get(val.casefold(), val)
    return val


def coerce_frame(df, columns):
    """Ép kiểu pandas cho bảng đã sạch (dùng khi đọc lại CSV trung gian)."""
    out = df.copy()
    for name, spec in columns.items():
        if name not in out.columns:
            continue
        kind = (spec or {}).get("kieu", "string")
        if kind == "int":
            out[name] = pd.to_numeric(out[name], errors="coerce").astype("Int64")
        elif kind in ("float", "tien", "phan_tram"):
            out[name] = pd.to_numeric(out[name], errors="coerce").astype("float64")
        elif kind == "date":
            out[name] = pd.to_datetime(out[name], errors="coerce")
        elif kind == "bool":
            out[name] = out[name].map(lambda x: None if _is_blank(x) else str(x).strip() in ("True", "true", "1")).astype("boolean")
        else:
            out[name] = out[name].map(parse_string).astype("string")
    return out


def run_dir(run_id):
    return PROCESSED_DIR / run_id


def save_csv(df, path):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False, encoding="utf-8-sig")


def read_csv(path, columns):
    df = pd.read_csv(path, dtype=str, keep_default_na=True, encoding="utf-8-sig")
    return coerce_frame(df, columns)
