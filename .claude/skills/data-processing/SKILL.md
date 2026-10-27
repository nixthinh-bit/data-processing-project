---
name: data-processing
description: Xử lý file Excel định kỳ trong data/raw theo luồng cố định clean -> transform -> validate, kiểm tra 4 tầng tự động (cấu trúc, đối soát, nghiệp vụ, biến động) và chuẩn bị mẫu đối chiếu tay, xuất kết quả theo từng lần chạy có log. Dẫn người dùng không biết code đi từng bước khi thiết lập cho bộ dữ liệu mới. Dùng khi người dùng mới clone dự án, muốn bắt đầu với dữ liệu của họ, nhận file dữ liệu mới, muốn chạy lại kỳ xử lý, hỏi về kết quả hay lỗi của một lần chạy, hoặc muốn thêm cột, quy tắc, bước tính toán mới.
---

# Xử lý dữ liệu Excel định kỳ

Đọc `CLAUDE.md` ở gốc dự án để nắm 5 nguyên tắc. Skill này mô tả thứ tự làm và quy tắc nghiệp vụ.

Người dùng skill này thường không viết code. Họ hiểu dữ liệu của mình, còn bạn lo phần kỹ thuật. Vì vậy:

- Nói bằng ngôn ngữ nghiệp vụ. Hỏi "mỗi khách chỉ được có một dòng đúng không?", đừng hỏi "cột nào là khoá".
- Không bắt người dùng tự sửa file cấu hình hay code. Bạn sửa, rồi nói ngắn gọn đã đổi gì.
- Ở mục B, mở đầu mỗi bước bằng một dòng "Bước x/6: ..." để người dùng biết đang ở đâu và còn bao nhiêu.
- Mỗi lần hỏi, gom câu hỏi lại trong một lượt, có đề xuất sẵn để người dùng chỉ cần gật hoặc sửa.

Script nằm ở `scripts/`, chạy bằng `.venv/bin/python` từ gốc dự án:

| Script | Việc |
|---|---|
| `run.py` | Chạy trọn một lần, tạo `run_id`, ghi log, xuất kết quả. Đây là lệnh dùng hằng ngày |
| `khao_sat.py` | Khảo sát file gốc và đề xuất data_dictionary (khi bắt đầu, hoặc khi file gốc đổi cấu trúc) |
| `clean.py` | Đổi tên cột theo data_dictionary, ép kiểu, lọc, tách trùng, tách dòng lỗi kèm lý do |
| `transform.py` | Các bước nghiệp vụ trong danh sách `BUOC` |
| `validate.py` | Kiểm tra 4 tầng và lấy mẫu cho tầng 5 |
| `common.py` | Hàm dùng chung, thường không cần sửa |

Cấu hình đọc từ khối yaml trong `reference/data_dictionary.md` và `reference/validation_rules.md`.
Bộ mẫu có sẵn trong `examples/`: `ban_hang` (đang là mặc định), `tai_ky`.

## 0. Thiết lập lần đầu

Làm khi chưa có thư mục `.venv`, trước mọi mục khác.

1. Kiểm tra có `python3` (3.9 trở lên). Không có thì hướng dẫn người dùng cài, đừng tự cài hệ thống.
2. Tạo môi trường: dùng `uv venv .venv && uv pip install -p .venv -r requirements.txt` nếu có `uv`,
   không thì `python3 -m venv .venv && .venv/bin/pip install -r requirements.txt`.
3. Chạy thử bộ mẫu bán hàng (chép `examples/ban_hang/don_hang_2026-10-01.xlsx` vào `data/raw/`, chạy
   `run.py --ghi-chu "chạy thử bộ mẫu"`). Cho người dùng xem log và giải thích ngắn 4 tầng kiểm tra qua
   chính log đó. Sau đó xoá file mẫu khỏi `data/raw/` (nhớ bỏ chế độ chỉ đọc trước) để chuẩn bị cho dữ liệu thật.

## A. Chạy một kỳ dữ liệu mới

1. Kiểm tra file mới đã nằm trong `data/raw/` với tên kèm ngày nhận. Nếu người dùng đưa file ở chỗ khác,
   chép vào (không di chuyển, không đổi nội dung). Không xoá file kỳ trước nếu người dùng không yêu cầu.
2. Chạy `run.py --ghi-chu "<nguồn file, kỳ nào>"`. Nếu `data/raw` có file của nhiều kỳ, thêm
   `--file "<mẫu tên file của kỳ này>"` để chỉ đọc đúng kỳ, các file kỳ trước để nguyên.
3. Đọc file log `logs/run_log/<run_id>.log` mà script in ra. Báo cáo cho người dùng bằng cách trích
   nguyên văn các dòng `[CHẶN]`, `[CẢNH BÁO]`, `[THỦ CÔNG]` và dòng kết luận. Không diễn giải lại số liệu.
4. Còn `[CHẶN] ✗`: nói là chưa xong. Chỉ ra file và dòng gốc liên quan (log đã có dạng `file.xlsx:dòng`),
   đề xuất cách sửa (bổ sung data_dictionary, thêm quy tắc, sửa bước transform). Sửa xong thì chạy lại,
   lần chạy mới sẽ có `run_id` mới.
5. Có `[CẢNH BÁO] ⚠`: liệt kê, hỏi người dùng cái nào chấp nhận được. Quyết định chấp nhận ghi vào
   `logs/decisions.md`.
6. Nhắc người dùng làm tầng 5: mở `outputs/<run_id>/mau_doi_chieu.csv`, so từng dòng với file gốc theo
   `_file_goc` và `_dong_goc`, điền cột `khop_file_goc`. Chỉ coi kỳ này hoàn tất khi người dùng xác nhận.

## B. Bắt đầu với bộ dữ liệu của người dùng

Làm đúng thứ tự, mỗi bước chờ người dùng xác nhận rồi mới sang bước sau. Nếu chưa có `.venv`, làm mục 0 trước.

**Bước 1/6: Nhận file.** Xin người dùng một file thật của một kỳ. Chép vào `data/raw/` với tên kèm ngày
nhận (ví dụ `doanh_thu_2026-10-27.xlsx`). Hỏi luôn file đến từ đâu, bao lâu nhận một lần, ai dùng kết quả,
rồi điền vào mục "Bối cảnh riêng" trong `CLAUDE.md`.

**Bước 2/6: Hiểu từng cột.** Chạy `khao_sat.py`, đọc `data/processed/_khao_sat/de_xuat_data_dictionary.md`.
Trình bày cho người dùng một bảng: tên cột, bạn hiểu cột đó là gì, ví dụ giá trị. Hỏi những gì chưa chắc
bằng lời nghiệp vụ:
- Mỗi dòng là một cái gì (một đơn, một khách, một giao dịch)? Cái gì không được lặp?
- Cột nào bắt buộc phải có, thiếu thì bỏ dòng đó?
- Cột tiền nào cần khớp tổng giữa file gốc và kết quả? Đơn vị gì?
- Giá trị thế nào là bất thường (âm, quá lớn, ngày ở tương lai, giá trị lạ)?
- Cột nào không cần dùng?

Ghi câu trả lời vào khối yaml của `reference/data_dictionary.md`. Cột nào người dùng chưa trả lời thì để
`trang_thai: chua_ro`, script sẽ chặn cho tới khi có câu trả lời. Ghi chú `sheet`, dòng tiêu đề, định dạng
số và ngày vào `reference/validation_rules.md` (mục `nguon`, `dinh_dang_so`, `dinh_dang_ngay`).

**Bước 3/6: Hỏi cần làm gì với dữ liệu.** Hỏi người dùng muốn kết quả cuối trông thế nào. Xếp yêu cầu vào
đúng chỗ, nói lại cho người dùng duyệt trước khi làm:

| Yêu cầu kiểu | Làm ở đâu |
|---|---|
| Chỉ giữ một phần (một vùng, một trạng thái) | `lam_sach.loc_dong` trong validation_rules |
| Bỏ dòng trùng | `khoa: true` trong data_dictionary + `lam_sach.bo_trung_theo_khoa` |
| Bỏ dòng không phải dữ liệu (dòng tổng, dòng ghi chú) | `lam_sach.loai_dong_khi` |
| Gộp cách viết khác nhau ("Việt Nam", "VN") | `anh_xa` của cột trong data_dictionary |
| Tính cột mới, xếp thứ tự, ghép bảng tra cứu | một hàm trong `BUOC` của `transform.py`, cột mới khai báo `nguon: tinh_toan` |

Nhớ: mọi việc loại dòng làm ở clean (qua cấu hình), không làm trong transform.

**Bước 4/6: Chạy thử lần đầu.** Chạy `run.py`. Mục tiêu đầu tiên là tầng 1 và 2 qua hết. Đọc log, giải
thích từng dòng `✗` bằng lời thường và sửa cấu hình cho tới khi qua. Cho người dùng xem số dòng vào, ra,
bị loại và lý do loại chính (từ log), rồi mở vài dòng của `ket_qua.xlsx`.

**Bước 5/6: Người dùng kiểm và chốt.** Đưa người dùng `mau_doi_chieu.csv` để đối chiếu tay. Hỏi kết quả
có đúng ý không. Sửa và chạy lại tới khi người dùng nói đúng. Mỗi quyết định (cách xử lý trùng, lọc gì, vì
sao giữ dòng có cảnh báo) ghi một mục vào `logs/decisions.md`.

**Bước 6/6: Chốt quy tắc kiểm tra và hướng dẫn kỳ sau.** Đề xuất ngưỡng tầng 3 (khoảng hợp lệ, quy tắc
chéo cột `dieu_kien`) và tầng 4 (lệch bao nhiêu % so với kỳ trước thì cảnh báo) dựa trên dữ liệu vừa chạy,
người dùng duyệt rồi ghi vào. Kết thúc bằng hướng dẫn ngắn cho các kỳ sau: thả file mới vào `data/raw/`
và nói "chạy kỳ mới", phần còn lại làm theo mục A.

## C. Khi gặp lỗi dữ liệu mới

Một lỗi mới (người dùng phát hiện ở tầng 5, hoặc thấy kết quả lạ) phải biến thành một quy tắc để lần sau
script tự bắt:

1. Thêm quy tắc vào `validation_rules.md` hoặc vào cột tương ứng trong `data_dictionary.md`.
   Các loại đã có sẵn: min, max, gia_tri_hop_le, anh_xa, thu_tu_ngay, dieu_kien (chéo cột),
   loai_dong_khi (dòng không phải dữ liệu như dòng tổng), loc_dong, bo_trung_theo_khoa.
2. Ghi một dòng vào bảng "Lịch sử quy tắc" cuối `validation_rules.md`.
3. Nếu loại kiểm tra chưa có trong `validate.py`, thêm một khối check mới vào hàm của tầng phù hợp,
   dùng `log.check(c.CHAN hoặc c.CANH_BAO, dat, thong_diep)`, đọc ngưỡng từ rules chứ không viết cứng.
4. Chạy lại để xác nhận quy tắc mới bắt được lỗi.

## D. Dùng một bộ mẫu trong examples/

Khi người dùng muốn xem thử một bộ mẫu (ví dụ "cho tôi xem bộ tái ký"): chép `data_dictionary.md`,
`validation_rules.md` của bộ đó vào `reference/`, `transform.py` của bộ đó đè lên `scripts/transform.py`,
chép file Excel của bộ đó vào `data/raw/`, rồi chạy như mục A. Trước khi chép, nếu `reference/` đang chứa
cấu hình dữ liệu thật của người dùng thì hỏi trước, vì sẽ bị ghi đè.

## Quy tắc nghiệp vụ

- Không xoá dòng trong `transform.py`. Dòng cần loại phải đi qua `clean.py` để có lý do trong
  `01_excluded.csv`, nếu không tầng 2 sẽ chặn vì số dòng không khớp.
- Không sửa giá trị gốc cho "đẹp". Giá trị sai thì để tầng 3 cảnh báo và hỏi người dùng.
- Cột `_file_goc`, `_dong_goc` phải đi theo mọi bước để truy vết. Không bỏ hai cột này trong transform.
- Đổi cách tính so với kỳ trước thì ghi vào `logs/decisions.md` trước khi chạy, vì tầng 4 sẽ báo lệch.
- Không sửa thư mục `outputs/` của lần chạy cũ. Muốn kết quả khác thì chạy lần mới.
- Tầng 4 so với lần chạy đạt gần nhất có cùng bộ cột (nên lần chạy bộ mẫu không bị đem ra so với dữ liệu
  thật), theo thứ tự run_id chứ không theo kỳ dữ liệu. Chạy lại một kỳ cũ sau
  kỳ mới thì cảnh báo biến động của lần đó không có ý nghĩa, ghi rõ khi báo cáo.

(Phần dưới để bổ sung quy tắc riêng của từng bộ dữ liệu.)
