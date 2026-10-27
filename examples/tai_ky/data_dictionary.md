# Data dictionary: customer renewals (simulated)

[Tiếng Việt](data_dictionary.vi.md)

Configuration for the `examples/tai_ky/` sample. To use it, copy this file over
`.claude/skills/data-processing/reference/data_dictionary.md`. Key meanings are explained in that file.
The source headers are in Vietnamese because the simulated CRM export is Vietnamese.

```yaml
columns:
  ma_kh:
    source_names: ["Mã KH"]
    type: string
    meaning: Customer ID in the CRM, one row per customer
    required: true
    key: true
    status: confirmed

  ten_khach_hang:
    source_names: ["Tên khách hàng"]
    type: string
    meaning: Customer name
    required: true
    status: confirmed

  partner:
    source_names: ["Partner"]
    type: string
    meaning: Partner managing the customer. Blank means no partner yet
    max_blank_ratio: 1.0
    status: confirmed

  csm:
    source_names: ["CSM"]
    type: string
    meaning: Customer success manager in charge
    status: confirmed

  quoc_gia:
    source_names: ["Quốc gia"]
    type: string
    meaning: Customer country, normalised to a 2-letter code
    required: true
    map: {"Việt Nam": VN, "Vietnam": VN, "vn": VN}
    allowed_values: [VN]
    status: confirmed

  ngay_bat_dau:
    source_names: ["Ngày bắt đầu HĐ"]
    type: date
    meaning: Contract start date
    required: true
    status: confirmed

  ngay_het_han:
    source_names: ["Ngày hết hạn HĐ"]
    type: date
    meaning: End date of the current contract, the renewal date
    required: true
    status: confirmed

  so_license:
    source_names: ["Số license"]
    type: int
    meaning: Number of licenses
    required: true
    min: 1
    status: confirmed

  arr_2025:
    source_names: ["ARR 2025 (USD)"]
    type: money
    unit: USD
    meaning: Annual recurring revenue of the current contract
    required: true
    non_negative: true
    status: confirmed

  arr_2026:
    source_names: ["ARR 2026 (USD)"]
    type: money
    unit: USD
    meaning: ARR after renewal. Blank while negotiating, 0 on churn
    non_negative: true
    max_blank_ratio: 0.4
    status: confirmed

  chiet_khau:
    source_names: ["Chiết khấu"]
    type: percent
    meaning: Renewal discount, stored as 0..1
    min: 0
    max: 0.3
    status: confirmed

  trang_thai:
    source_names: ["Trạng thái"]
    type: string
    meaning: Renewal status
    required: true
    allowed_values: ["Đã tái ký", "Đang đàm phán", "Upsell", "Downsell", "Churn"]
    status: confirmed

  ly_do:
    source_names: ["Lý do churn/downsell"]
    type: string
    meaning: Reason for churn or downsell
    max_blank_ratio: 1.0
    status: confirmed

  ghi_chu_kam:
    source_names: ["Ghi chú KAM"]
    skip: true
    meaning: Free-text KAM note, not used for reporting (confirmed by the user 2026-10-27)

  # Columns created by transform.py
  chenh_lech_arr:
    source: computed
    type: float
    unit: USD
    meaning: arr_2026 minus arr_2025, blank while ARR 2026 is unknown
    max_blank_ratio: 0.4
    status: confirmed
```
