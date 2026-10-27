---
name: data-processing
description: Process a recurring Excel file in data/raw through a fixed clean -> transform -> validate flow, with 4 automatic check layers (structure, reconciliation, business rules, drift) plus a manual review sample, exporting each run to its own folder with a log. Walks non-coders step by step through setting it up for their own data. Use when the user has just cloned the project, wants to start with their own data, received a new data file, wants to rerun a period, asks about a run's result or errors, or wants to add a column, rule or calculation. Also for Vietnamese requests such as "xử lý dữ liệu", "chạy kỳ mới", "bắt đầu với dữ liệu của tôi".
---

# Recurring Excel processing

Read `CLAUDE.md` at the project root for the 5 principles. This skill gives the order of work and the
business rules.

The people using this skill usually do not code. They know their data; you handle the technical side:

- Talk in business terms. Ask "should each customer appear only once?", not "which column is the key?".
- Do not ask the user to edit config files or code. You edit them, then say briefly what changed.
- In section B, open each step with a line "Step x/6: ..." so the user knows where they are.
- When you ask, batch the questions in one turn, with a proposed answer the user can accept or correct.
- Reply in the user's language. Keep `language` in `reference/validation_rules.md` set to that language
  (`en` or `vi`), so the log and output file names match what the user reads.

Scripts are in `scripts/`, run with `.venv/bin/python` from the project root:

| Script | Job |
|---|---|
| `run.py` | Run everything once, create a `run_id`, write the log, export the result. The everyday command |
| `profile_data.py` | Profile source files and propose a data_dictionary (at the start, or when the source layout changes) |
| `clean.py` | Rename columns per data_dictionary, parse types, filter, dedupe, exclude bad rows with a reason |
| `transform.py` | Business steps listed in `BUOC` |
| `validate.py` | The 4 check layers and the layer 5 sample |
| `common.py`, `messages.py` | Shared helpers, and every message in both languages. Rarely edited |

Configuration is read from the yaml blocks in `reference/data_dictionary.md` and
`reference/validation_rules.md`. Keys can be English (`columns`, `required`, `keep_only`...) or Vietnamese
(`cot`, `bat_buoc`, `loc_dong`...); the full alias list is `KEY_ALIASES` in `messages.py`.
Samples in `examples/`: `ban_hang` (retail orders, the default) and `tai_ky` (customer renewals). Each has
an English config (`*.md`) and a Vietnamese one (`*.vi.md`).

Output names follow `language`: `result.xlsx` / `ket_qua.xlsx`, `review_sample.csv` / `mau_doi_chieu.csv`,
trace columns `_source_file`, `_source_row` / `_file_goc`, `_dong_goc`.

## 0. First-time setup

Do this when there is no `.venv` folder, before anything else.

1. Check that `python3` (3.9 or later) exists. If not, tell the user how to install it; do not install system software yourself.
2. Create the environment: `uv venv .venv && uv pip install -p .venv -r requirements.txt` if `uv` exists,
   otherwise `python3 -m venv .venv && .venv/bin/pip install -r requirements.txt`.
3. Pick the language from how the user writes. For Vietnamese, copy `examples/ban_hang/*.vi.md` over the two
   files in `reference/` (dropping `.vi`); for English the defaults are already English.
4. Run the retail sample: copy `examples/ban_hang/don_hang_2026-10-01.xlsx` into `data/raw/` and run
   `run.py --note "sample run"`. Show the user the log and explain the 4 layers through that log. Then
   remove the sample from `data/raw/` (make it writable first) to make room for real data.

## A. Run a new period

1. Check the new file is in `data/raw/` with the received date in its name. If the user gives a file
   elsewhere, copy it in (do not move it or change it). Do not delete earlier files unless asked.
2. Run `run.py --note "<where the file came from, which period>"`. If `data/raw` holds several periods,
   add `--file "<pattern for this period>"` so only this period is read; leave older files in place.
3. Read `logs/run_log/<run_id>.log`, which the script prints. Report by quoting the BLOCK / WARN / MANUAL
   lines (`[CHẶN]`, `[CẢNH BÁO]`, `[THỦ CÔNG]` in Vietnamese) and the conclusion verbatim. Do not restate the numbers.
4. Any `✗` at BLOCK level: say it is not done. Point to the source file and row (the log gives `file.xlsx:row`),
   propose a fix (data_dictionary, a rule, a transform step). After fixing, run again; the new run gets a new `run_id`.
5. Any `⚠` warning: list them and ask which are acceptable. Record accepted ones in `logs/decisions.md`.
6. Remind the user about layer 5: open the review sample in `outputs/<run_id>/`, compare each row with the
   source by the trace columns, fill in the match column. The period is complete only when the user confirms.

## B. Start with the user's own data

Follow this order and wait for the user's confirmation before each next step. Do section 0 first if there is no `.venv`.

**Step 1/6: Get the file.** Ask for one real file from one period. Copy it into `data/raw/` with the received
date in the name (e.g. `revenue_2026-10-27.xlsx`). Ask where it comes from, how often it arrives and who uses
the result, and fill in the "Project context" section of `CLAUDE.md`.

**Step 2/6: Understand each column.** Run `profile_data.py` and read `data/processed/_profile/proposed_data_dictionary.md`.
Show the user a table: column name, what you think it is, sample values. Ask what is unclear in business terms:
- What is one row (an order, a customer, a transaction)? What must not repeat?
- Which columns must be filled, so a blank drops the row?
- Which amount columns must add up between the source and the result? In what unit?
- What counts as abnormal (negative, too large, future dates, unexpected values)?
- Which columns are not needed?

Write the answers into the yaml block of `reference/data_dictionary.md`. Columns the user has not answered
stay `status: unclear`; the scripts block until they are answered. Record sheet, header row, number and date
formats in `reference/validation_rules.md` (`source`, `number_format`, `date_formats`).

**Step 3/6: Ask what to do with the data.** Ask what the final result should look like. Put each request in
the right place and read it back for approval before doing it:

| Request | Where |
|---|---|
| Keep only part of the data (a region, a status) | `cleaning.keep_only` in validation_rules |
| Remove duplicates | `key: true` in data_dictionary + `cleaning.dedupe_by_key` |
| Drop rows that are not data (totals, notes) | `cleaning.drop_rows_when` |
| Merge spellings ("Viet Nam", "VN") | the column's `map` in data_dictionary |
| New columns, sorting, lookup joins | a function in `BUOC` in `transform.py`; declare new columns with `source: computed` |

Remember: every row removal happens in clean (through config), never in transform.

**Step 4/6: First run.** Run `run.py`. The first goal is layers 1 and 2 passing. Read the log, explain each
`✗` in plain words and fix the config until they pass. Show rows in, out and excluded with the main reasons
(from the log), then open a few rows of the result file.

**Step 5/6: The user checks and confirms.** Give the user the review sample. Ask whether the result is what
they wanted. Fix and rerun until they say it is right. Record every decision (how duplicates are handled,
what is filtered, why rows with warnings are kept) as an entry in `logs/decisions.md`.

**Step 6/6: Lock the check rules and explain later periods.** Propose layer 3 thresholds (ranges,
cross-column `conditions`) and layer 4 thresholds (how much change vs the previous period triggers a warning)
based on the data just run; write them after the user approves. Finish with a short how-to for later periods:
drop the new file into `data/raw/` and say "run the new period"; the rest follows section A.

## C. When a new data problem appears

A new problem (found in layer 5, or a result that looks wrong) must become a rule so the scripts catch it next time:

1. Add a rule to `validation_rules.md` or to the column in `data_dictionary.md`. Available rule types:
   min, max, allowed_values, map, date_order, conditions (cross-column), drop_rows_when (non-data rows such
   as totals), keep_only, dedupe_by_key.
2. Add a line to the "Rule history" table at the end of `validation_rules.md`.
3. If the kind of check does not exist in `validate.py` yet, add a check to the matching layer function with
   `log.check(c.CHAN or c.CANH_BAO, passed, message)`. Read thresholds from the rules, never hard-code them.
   Add any new message text to `messages.py` in both languages.
4. Run again to confirm the new rule catches the problem.

## D. Use a sample from examples/

When the user wants to try a sample (e.g. "run the renewal sample"): copy that sample's `data_dictionary.md`
and `validation_rules.md` (or the `.vi.md` versions, renamed) into `reference/`, its `transform.py` over
`scripts/transform.py`, its Excel files into `data/raw/`, then run as in section A. If `reference/` holds the
user's own configuration, ask first, because it will be overwritten.

## Business rules

- Never delete rows in `transform.py`. Rows to drop go through `clean.py` so they get a reason in
  `01_excluded.csv`; otherwise layer 2 blocks because the row counts do not match.
- Never "tidy up" source values. Wrong values get a layer 3 warning and a question to the user.
- The trace columns must survive every step. Never drop them in transform.
- If a calculation changes from the previous period, record it in `logs/decisions.md` before running,
  because layer 4 will flag the change.
- Never edit an earlier run's `outputs/` folder. For a different result, run again.
- Layer 4 compares with the latest passing run that has the same columns (so a sample run is never compared
  with real data), in `run_id` order rather than data period order. Rerunning an old period after a newer one
  makes that run's drift warning meaningless; say so when reporting.

(Add dataset-specific rules below.)
