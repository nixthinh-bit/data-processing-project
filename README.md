# Recurring Excel processing with Claude Code

[Tiếng Việt](README.vi.md)

Every week or month you get an Excel file and clean, filter and calculate it the same way. This project
turns that into a fixed routine: drop the file in, tell Claude "run the new period", and get the result
back with a check report. Every run uses the same scripts, so results are consistent. Every excluded row
has a reason, and every output row traces back to its original Excel row.

You do not need to code. Claude asks you about your data and does the configuration.

Works in English and Vietnamese. Claude replies in the language you write in, and one setting
(`language: en` or `vi`) switches the log, exclusion reasons and output file names.

## Getting started

You need [Claude Code](https://claude.com/claude-code) and Python 3.9 or later.

```bash
git clone https://github.com/nixthinh-bit/data-processing-project.git
```

Open the folder in Claude Code and say:

> I just cloned this project, walk me through starting with my own data.

Claude sets up the environment, runs the sample so you can see what a result looks like, then takes you
through 6 steps:

| Step | You | Claude |
|---|---|---|
| 1. Hand over a file | Give one real Excel file from one period | Copies it into `data/raw/`, asks where it comes from and who uses the result |
| 2. Understand the columns | Answer a few questions: what one row is, what must not repeat, which amounts must reconcile | Profiles the file, proposes a meaning for each column, records your answers |
| 3. Say what you need | Describe the result: what to filter, how to dedupe, what to calculate, how to sort | Turns that into configuration and processing steps, reads it back for approval |
| 4. First run | Look at the result and the log | Runs it, explains each error in plain words, fixes until the blocking checks pass |
| 5. Check and confirm | Compare a few rows with the source by hand, say whether it is right | Fixes and reruns, records your decisions |
| 6. Lock the rules | Approve the warning thresholds Claude proposes | Saves them and shows you how to run later periods |

After that, drop each new file into `data/raw/` and say "run the new period".

## What every run checks

| Layer | Check | If it fails |
|---|---|---|
| 1. Structure | All columns, right types, no duplicates, blanks under threshold, source file untouched | Blocked, no result exported |
| 2. Reconciliation | Rows in = rows out + excluded, amount totals match | Blocked, no result exported |
| 3. Business | Values make sense: not negative, in range, dates in order, cross-column rules | Warning |
| 4. Drift | Large change vs the previous period | Warning |
| 5. Human | A few random rows for you to compare by hand | You confirm |

Each run gets its own folder in `outputs/` and never overwrites an earlier one. Logs in `logs/run_log/`
are written by the scripts, not summarised by Claude. A few lines from a real log:

```
clean:   1 row(s): arr_2025: '$5,040' is ambiguous: it could be a decimal or a number with a different thousands separator
[BLOCK] ✓ Rows: in 103 = out 72 + excluded 31
[BLOCK] ✗ No duplicate keys ['ma_kh']: 2 duplicate row(s), e.g. tai_ky_Q4.2026_2026-10-27.xlsx:34 (KH0031), ...
[WARN] ⚠ Churn means ARR 2026 is 0: 1 row(s) fail, e.g. tai_ky_Q4.2026_v2_2026-10-28.xlsx:15 (3000.0)
```

## Samples

| Folder | What it is |
|---|---|
| `examples/ban_hang/` | Retail orders with a few planted errors. The default configuration after cloning |
| `examples/tai_ky/` | Customer renewal list, harder: header on row 3, mixed number formats, duplicate IDs, a totals row. Includes logs from 5 runs (in Vietnamese) |

Each sample has an English configuration (`*.md`) and a Vietnamese one (`*.vi.md`). The sample data
itself has Vietnamese headers and values.

To try one, ask Claude, for example "run the renewal sample for me".

## Where your data stays

Source files, intermediate files, outputs and logs are git-ignored. If you push your own copy, only the
configuration and scripts go with it.

## If you want to edit things yourself

Everything specific to a dataset lives in 3 files under `.claude/skills/data-processing/`:
`reference/data_dictionary.md` (column meanings), `reference/validation_rules.md` (filters, dedupe,
thresholds) and `scripts/transform.py` (calculation steps). The full procedure is in `SKILL.md`.
Config keys can be written in English or Vietnamese; the alias list is in `scripts/messages.py`.

Current limits: one clone serves one kind of recurring file (clone twice for two), and it suits files up to
a few tens of thousands of rows. Code comments are mostly in Vietnamese.

## License

MIT
