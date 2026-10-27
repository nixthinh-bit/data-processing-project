# Validation rules

[Tiếng Việt](validation_rules.vi.md)

Check thresholds and file reading rules, kept out of the code so they can change without editing scripts.
Per-column thresholds (min, max, allowed values) live in `data_dictionary.md`.

Whenever a new data problem turns up, add a rule here (or in data_dictionary) and a line to "Rule history"
at the end, so the scripts catch it next time. Vietnamese key names also work, see `validation_rules.vi.md`.

## Reading the source file

```yaml
language: en                  # en | vi: language of the log, exclusion reasons and output file names

source:
  file_pattern: "*.xlsx"      # which files in data/raw are read
  sheet: 0                    # sheet index or name
  header_row: 1               # Excel row that holds the column headers
  lock_raw_files: true        # set source files read-only before running

number_format:                # for numbers typed as text, e.g. "1.250.000"
  decimal: ","
  thousands: "."

date_formats: ["%d/%m/%Y", "%d-%m-%Y", "%Y-%m-%d"]

cleaning:
  on_type_error: drop_row     # drop_row | leave_blank (leave_blank only applies to non-required columns)
  drop_exact_duplicates: false
  # drop_rows_when:           # drop rows that are not data, runs before keep_only. E.g. a totals row:
  #   - column: ma_don
  #     equals: ["Total"]
  #     reason: totals row of the table
  # keep_only:                # keep only rows whose value is in the list, others are excluded with a reason
  #   kenh: ["Website"]
  dedupe_by_key: false        # true: rows with the same key and identical other columns keep the first one.
                              # Same key but different content is never resolved automatically, layer 1 blocks

export:
  keep_trace_columns: true    # keep _source_file, _source_row in result.xlsx
```

## Layer 1: Structure (BLOCK)

```yaml
layer_1:
  max_blank_ratio: 0.05       # default blank threshold per column, required columns are always 0
  # key: [ma_don]             # uncomment to override the key declared in data_dictionary
```

## Layer 2: Reconciliation (BLOCK)

```yaml
layer_2:
  row_mode: preserve          # preserve: in = out + excluded; aggregate: transform groups rows, only totals compared
  amount_columns: [thanh_tien] # [] if the data has no amount column; remove the line to use every type: money column
  amount_tolerance: 0.01
```

## Layer 3: Business rules (WARN)

```yaml
layer_3:
  date_order:                 # [a, b] means a must not be after b
    - [ngay_dat, ngay_giao]
  no_future_dates: [ngay_dat, ngay_giao]
  conditions: []              # cross-column rules, see the example below
```

Cross-column rules are pandas expressions on the standard column names. `when` is the condition for the
rule to apply (leave it out to apply to every row), `must` is what has to hold, `level: block` raises it to
BLOCK, `show_column` is printed in the log examples. Example from `examples/tai_ky/validation_rules.md`:

```
  conditions:
    - name: Churn means ARR 2026 is 0
      when: "trang_thai == 'Churn'"
      must: "arr_2026 == 0"
      show_column: arr_2026
```

## Layer 4: Drift (WARN)

Compared with the latest passing run that has the same columns.

```yaml
layer_4:
  max_row_change_pct: 20
  max_amount_change_pct: 20
```

## Layer 5: Human review

```yaml
layer_5:
  sample_rows: 8              # random, fixed per run_id so a rerun gives the same sample
```

## Rule history

| Date | Problem found | Rule added |
|---|---|---|
| 2026-10-27 | (sample) Delivery date before order date | `layer_3.date_order: [ngay_dat, ngay_giao]` |
