# Recurring Excel data processing

This project takes an Excel file each period, cleans it, calculates, checks and exports the result. The
goal is consistent results across runs, with checks, and every output row traceable to its source row.

The full procedure is the skill `.claude/skills/data-processing/SKILL.md`. Read it before touching data.

Users usually do not code. If there is no `.venv` folder, or the user says they want to start with their
own data, follow section 0 then section B of the skill and walk them through it step by step. Reply in the
user's language (English or Vietnamese) and keep `language` in `reference/validation_rules.md` matching it.

## Principles

1. Source data in `data/raw/` is read only. Never edit, overwrite or save over it. `run.py` sets source
   files read-only and compares their checksums before and after the run.
2. Stable processing lives in the scripts in `scripts/`. Do not rewrite processing code for each run and
   do not process data with throwaway code outside these scripts.
3. The scripts write the technical log in `logs/run_log/`. Never summarise or write into the log yourself.
   When reporting, quote the BLOCK and WARN lines (`[CHẶN]`, `[CẢNH BÁO]` in Vietnamese) verbatim.
4. Never call a run done while the log has a BLOCK `✗` line. Say which check failed, in which file and row,
   and propose a fix.
5. Never guess what a column means. Ask about unknown or unclear columns, then record the answer in
   `reference/data_dictionary.md`. Record business decisions and their reasons in `logs/decisions.md`.

## Folder map

| Path | Contents |
|---|---|
| `data/raw/` | Source files, named with the date received, e.g. `orders_2026-10-01.xlsx` |
| `data/processed/<run_id>/` | Intermediate files: `01_cleaned.csv`, `01_excluded.csv`, `02_transformed.csv` |
| `outputs/<run_id>/` | One folder per run, never overwritten: result file, `validation_report.log`, review sample, `run_meta.json` |
| `logs/run_log/` | Logs written by the scripts, one per run |
| `logs/decisions.md` | Business decisions and why |
| `.claude/skills/data-processing/` | Procedure, scripts, data dictionary, check thresholds |

`run_id` looks like `YYYY-MM-DD_runNN`.

## Common commands

```bash
.venv/bin/python .claude/skills/data-processing/scripts/run.py --note "October file"
.venv/bin/python .claude/skills/data-processing/scripts/run.py --file "orders_2026-10-*.xlsx"
.venv/bin/python .claude/skills/data-processing/scripts/profile_data.py
```

`--ghi-chu` works the same as `--note`. Exit code of `run.py`: 0 means every BLOCK check passed, 1 means
a BLOCK check failed (no result exported).

## Project context

Each user fills this in for their own data: where it comes from, who sends it, how often, who uses the
result, any deadlines.

- Data source: (not filled in)
- Frequency: (not filled in)
- Result used by: (not filled in)
