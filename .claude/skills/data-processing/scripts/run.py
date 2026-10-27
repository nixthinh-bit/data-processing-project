"""Chạy trọn một lần: raw -> clean -> transform -> validate -> outputs -> logs.

Mỗi lần chạy có run_id dạng YYYY-MM-DD_runNN, một thư mục outputs riêng (không ghi đè)
và một file log riêng trong logs/run_log/. Nếu còn lỗi mức CHẶN thì không xuất file kết quả
và thoát với mã 1.

Dùng: python run.py [--ghi-chu "nhận file tháng 10 từ phòng kế toán"] [--file "don_hang_2026-10-*.xlsx"]
"""
import argparse
import datetime as dt
import os
import stat
import sys

import common as c
from clean import StopRun, clean
from transform import transform
from validate import validate


def protect_raw(files, log):
    """Đặt file gốc ở chế độ chỉ đọc và ghi lại mã băm để tầng 1 kiểm tra không bị sửa."""
    checksums = {}
    for p in files:
        mode = p.stat().st_mode
        if mode & (stat.S_IWUSR | stat.S_IWGRP | stat.S_IWOTH):
            os.chmod(p, mode & ~(stat.S_IWUSR | stat.S_IWGRP | stat.S_IWOTH))
            log.write(f"raw: đặt chỉ đọc cho {p.name}")
        checksums[p.name] = c.sha256(p)
        log.write(f"raw: {p.name}  sha256 {checksums[p.name][:16]}...  {p.stat().st_size:,} byte")
    return checksums


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--ghi-chu", default="", help="ghi chú cho lần chạy, lưu vào log và run_meta.json")
    ap.add_argument("--file", default=None, help="mẫu tên file trong data/raw cho lần chạy này, vd \"tai_ky_Q1.2027_*.xlsx\"")
    args = ap.parse_args()
    c.RAW_PATTERN_OVERRIDE = args.file

    run_id = c.new_run_id()
    out_dir = c.OUTPUTS_DIR / run_id
    out_dir.mkdir(parents=True)
    log = c.RunLog(run_id)
    rules = c.load_rules()
    started = dt.datetime.now()

    log.write(f"=== Lần chạy {run_id} lúc {started:%Y-%m-%d %H:%M:%S} ===")
    log.write(f"phiên bản script (git): {c.git_commit() or 'chưa có git'}")
    ref_hashes = {p.name: c.sha256(p)[:16] for p in sorted(c.REF_DIR.glob("*.md"))}
    log.write(f"reference: {ref_hashes}")
    if args.ghi_chu:
        log.write(f"ghi chú: {args.ghi_chu}")
    if args.file:
        log.write(f"chỉ đọc file khớp: {args.file}")

    meta = {"run_id": run_id, "bat_dau": started.isoformat(timespec="seconds"), "ghi_chu": args.ghi_chu, "file": args.file,
            "git": c.git_commit(), "reference": ref_hashes}
    files = c.raw_files(rules)
    meta["file_goc"] = checksums = protect_raw(files, log) if (rules.get("nguon") or {}).get("khoa_file_goc", True) else {p.name: c.sha256(p) for p in files}

    try:
        log.write("--- clean ---")
        clean(run_id, log)
        log.write("--- transform ---")
        transform(run_id, log)
        final, summary = validate(run_id, log, out_dir, checksums)
    except StopRun as e:
        log.check(c.CHAN, False, str(e))
        final, summary = None, {}

    blocking, warnings = log.blocking_failures(), log.warnings()
    meta.update({"ket_thuc": dt.datetime.now().isoformat(timespec="seconds"), "doi_soat": summary,
                 "so_loi_chan": len(blocking), "so_canh_bao": len(warnings),
                 "trang_thai": "CHAN" if blocking else ("CANH_BAO" if warnings else "DAT")})

    log.write("=== Kết luận ===")
    if blocking:
        log.write(f"CHƯA XONG: {len(blocking)} lỗi mức CHẶN. Không xuất file kết quả.")
    else:
        keep_trace = (rules.get("xuat") or {}).get("giu_cot_truy_vet", True)
        export = final if keep_trace else final.drop(columns=c.TRACE_COLS)
        export.to_excel(out_dir / "ket_qua.xlsx", index=False)
        log.write(f"Đã xuất {out_dir.name}/ket_qua.xlsx ({len(final)} dòng). Cảnh báo: {len(warnings)}. Còn chờ đối chiếu tay (tầng 5).")

    c.write_json(out_dir / "run_meta.json", meta)
    (out_dir / "validation_report.log").write_text(log.path.read_text(encoding="utf-8"), encoding="utf-8")
    sys.exit(1 if blocking else 0)


if __name__ == "__main__":
    main()
