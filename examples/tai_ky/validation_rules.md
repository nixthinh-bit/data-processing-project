# Validation rules: customer renewals (simulated)

[Tiếng Việt](validation_rules.vi.md)

Configuration for the `examples/tai_ky/` sample. To use it, copy this file over
`.claude/skills/data-processing/reference/validation_rules.md`.

```yaml
language: en

source:
  file_pattern: "tai_ky_*.xlsx"
  sheet: "Tai ky"             # the "Ghi chu" sheet is notes, not data
  header_row: 3               # rows 1 and 2 are the table title and a source note
  lock_raw_files: true

number_format:
  decimal: ","
  thousands: "."

date_formats: ["%d/%m/%Y", "%Y-%m-%d"]

cleaning:
  on_type_error: drop_row
  drop_exact_duplicates: false
  drop_rows_when:             # runs before keep_only, so the totals row is not labelled "outside VN"
    - column: ten_khach_hang
      equals: ["Tổng cộng", "Tổng", "Total"]
      reason: totals row of the table, not a customer
  keep_only:
    quoc_gia: [VN]
  dedupe_by_key: true

export:
  keep_trace_columns: true
```

```yaml
layer_1:
  max_blank_ratio: 0.05

layer_2:
  row_mode: preserve
  amount_columns: [arr_2025, arr_2026]
  amount_tolerance: 0.01

layer_3:
  date_order:
    - [ngay_bat_dau, ngay_het_han]
  no_future_dates: [ngay_bat_dau]
  conditions:
    - name: Churn means ARR 2026 is 0
      when: "trang_thai == 'Churn'"
      must: "arr_2026 == 0"
      show_column: arr_2026
    - name: Churn and Downsell need a reason
      when: "trang_thai in ['Churn', 'Downsell']"
      must: "ly_do.notna()"
      show_column: trang_thai
    - name: Upsell means ARR 2026 above ARR 2025
      when: "trang_thai == 'Upsell'"
      must: "arr_2026 > arr_2025"
      show_column: arr_2026
    - name: Downsell means ARR 2026 below ARR 2025 and above 0
      when: "trang_thai == 'Downsell'"
      must: "(arr_2026 < arr_2025) & (arr_2026 > 0)"
      show_column: arr_2026
    - name: Closed deals (renewed, upsell, downsell) must have ARR 2026
      when: "trang_thai in ['Đã tái ký', 'Upsell', 'Downsell']"
      must: "arr_2026.notna()"
      show_column: trang_thai

layer_4:
  max_row_change_pct: 20
  max_amount_change_pct: 20

layer_5:
  sample_rows: 8
```

## Rule history

| Date | Problem found | Rule added |
|---|---|---|
| 2026-10-27 | The "Tổng cộng" totals row was labelled "outside VN"; 861,240 USD of the excluded amount was actually the totals row | `cleaning.drop_rows_when` on `ten_khach_hang` |
