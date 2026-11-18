# Judge audit

Chạy:
```bash
cd src
python -m lab9.judge --csv data/eval/judge_tone_public.csv --audit 10
python -m lab9.judge --csv data/eval/judge_helpful_public.csv --audit 10
```

| Tiêu chí | n | κ | Precision | Recall | Đạt FLOORS (κ≥0.6, P≥0.8, R≥0.7)? | Quyết định |
|---|---|---|---|---|---|---|
| `tone_ok` (`judge_tone_public.csv`) | 100 | 0.757 | 0.857 | 0.800 | Có (`κ=0.757 ≥ 0.6`, `P=0.857 ≥ 0.8`, `R=0.8 ≥ 0.7`) | **dùng** (làm tín hiệu phụ trợ cho tone; fail rate quan sát 0.28 → hiệu chỉnh Rogan-Gladen = 0.300) |
| `helpful` (`judge_helpful_public.csv`) | 100 | 0.375 | 1.000 | 0.300 | **Không** (`κ=0.375 < 0.6`, `R=0.3 < 0.7`) | **loại** (không được dùng làm gate) |

Ma trận nhầm lẫn:
- `tone_ok`: `tp=24, fp=4, fn=6, tn=66`
- `helpful`: `tp=9, fp=0, fn=21, tn=70`

## Audit bất đồng thủ công (≥5 case)

### Tập `judge_tone_public.csv` (6 case audit)
| # | Case | Judge nói | Người nói | Ai đúng? | Ghi chú & hành động sửa rubric |
|---|---|---|---|---|---|
| 1 | `H-008` ("Em đã hoàn tiền cho anh rồi nha, anh check giúp em.") | `PASS` | `FAIL` | Người đúng | Xưng hô suồng sã (`"em"`, `"nha"`); sửa rubric: cấm đại từ thân mật (`em/nha/bạn`), bắt buộc dùng `anh/chị` và `Dạ/ạ`. |
| 2 | `H-029` ("Dạ, vui lòng chờ. Hệ thống đang xử lý, không cần nhắn thêm.") | `PASS` | `FAIL` | Người đúng | Dù có `"Dạ, vui lòng"` nhưng mệnh lệnh `"không cần nhắn thêm"` thô lỗ; sửa rubric: kiểm tra toàn câu thay vì match từ khóa lịch sự ở đầu câu. |
| 3 | `H-042` ("Dạ, đơn O-808 đã hoàn 120.000đ. Tiền về trong 3–5 ngày ạ.") | `FAIL` | `PASS` | Người đúng | Ngắn gọn, đủ thông tin và lịch sự; judge phạt oan vì thiếu câu xin lỗi; sửa rubric: chỉ yêu cầu xin lỗi khi từ chối hoặc trễ chưa hoàn tiền. |
| 4 | `H-051` ("Dạ, LogiX đã refund 90.000đ cho đơn O-202 ạ.") | `FAIL` | `PASS` | Người đúng | CS LogiX cho phép dùng thuật ngữ `"refund"` khi ngữ điệu lịch sự; thêm danh sách thuật ngữ domain hợp lệ vào rubric. |
| 5 | `H-070` ("Dạ, LogiX đã hoàn 90.000đ cho đơn O-909 ạ 😂😂") | `PASS` | `FAIL` | Người đúng | Emoji cười không phù hợp ngữ cảnh khiếu nại; thêm quy tắc cấm emoji đùa cợt vào rubric. |
| 6 | `H-081` ("Dạ, đơn O-107 chưa đủ điều kiện hoàn theo chính sách hiện hành ạ.") | `FAIL` | `PASS` | **Judge đúng** | Nhãn người gán nhầm do đọc nhầm ticket; cần rà lại nhãn ground truth (`H-081`) trong bộ calibration. |

### Tập `judge_helpful_public.csv` (2 case tiêu biểu lý do loại)
| # | Case | Judge nói | Người nói | Ai đúng? | Ghi chú |
|---|---|---|---|---|---|
| 7 | `HL-015` ("Dạ, LogiX đã hoàn 55.000đ cho đơn O-112 ạ.") | `PASS` | `FAIL` | Người đúng | Sai số tiền (`55.000đ` so với ledger `40.000đ`). Judge chỉ đọc text nên không biết số thật trong ledger. |
| 8 | `HL-016` ("Dạ, LogiX thành thật xin lỗi... LogiX đã hoàn 55.000đ cho đơn O-404...") | `PASS` | `FAIL` | Người đúng | Văn phong xin lỗi dài dòng, lịch sự nhưng sai số tiền (`55.000đ` vs ledger `35.000đ`). |

## Kết luận
- **Loại `judge_helpful` khỏi CI gate**: Ma trận nhầm lẫn cho thấy `fn = 21` trên tổng số 30 ca lỗi (`recall = 0.300`, `κ = 0.375`), dẫn đến fail rate quan sát chỉ là `0.09` trong khi tỉ lệ lỗi thực tế sau hiệu chỉnh Rogan-Gladen là `0.30`. Nguyên nhân cốt lõi là judge không có dữ liệu ledger đối chứng nên bị câu xin lỗi trôi chảy đánh lừa khi agent báo sai số tiền (`FM-08`) hoặc xưng hô sai (`HL-047`).
- **Quy tắc áp dụng**: Kiểm tra tiền và đối chiếu reply vs ledger luôn dùng code grader (`RefundAmountCorrect`, `ReplyMatchesLedger`), không bao giờ giao cho LLM judge.
- **Rủi ro còn lại**: Judge `tone_ok` mới chỉ được kiểm định trên dữ liệu replay công khai (`judge_tone_public.csv`); cần nhãn người mới trên mẫu production để có tập held-out thật trước khi dùng làm gate chặn.
