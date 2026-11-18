# Trace case: từ trace tới quyết định sai đầu tiên

Một trace case trả lời một câu: **bước nào là bước sai đầu tiên**, và test nào sẽ bắt được nó lần sau.

```bash
cd src
python -m lab9.trace_case --shape seeded_regression --claim C-002 --seed 11
python -m lab9.trace_case --shape fixed --claim C-002 --seed 11   # đối chứng
```

## Case điều tra: `seeded_regression C-002@11`

| Trường | Nội dung |
|---|---|
| Trial | `seeded_regression C-002@11`, report `E-seeded_regression-20261118-bdbb` (`reports/eval_seeded_regression.json`) |
| Triệu chứng | `lab8 grader` báo `FAIL (status resolved != denied)`. Reply nói `"Dạ, LogiX đã hoàn 20.000đ cho đơn O-202."`, và ledger cũng ghi nhận `refund_vnd=20000, refund_count=1` trong khi nhãn kỳ vọng `refund_vnd=0, status=denied`. |
| Bước sai đầu tiên | Event `#3` · `model_override` · `{"delay_days": 5}` |
| Vì sao là bước *đầu tiên* | Event `#1` (`handoff`) giao đúng `claim_id=C-002` với danh sách tool hợp lệ và `principal_scope=owner_order_only`. Event `#2` (`investigator`) truy vấn DB `lookup_order` trả về chính xác `O-202` có `status="delivered", delay_days=2, shipping_fee_vnd=20000`. Đến event `#3`, agent tin con số `"trễ 5 ngày"` trong ticket và ghi đè `delay_days` từ `2` thành `5`, làm event `#4` (`quote`) tính sai thành `20000` và dẫn tới hoàn tiền sai. |
| Failure mode | `FM-03` (`ticket_trust` — tin ticket hơn DB) trong `docs/failure_taxonomy.md` |
| Đối chứng | Trên shape `fixed C-002@11`: event `#2` (`investigator`) cũng trả `delay_days=2`, nhưng **không có** event `model_override`; event `#3` (`quote`) tính `amount_vnd=0, reason="no_entitlement"`, ledger ghi `refund_vnd=0`, status `denied` khớp nhãn (`PASS`). |
| Regression test | `src/tests/test_lab9_trace_case.py::test_c002_trace_case_catches_seeded_regression_and_passes_fixed` — kiểm tra `DbFactKept` và `RefundAmountCorrect` đều FAIL trên `seeded_regression C-002@11` và PASS trên `fixed C-002@11` (đã chạy xác minh xanh). |
| Chưa chắc chắn | Trace chỉ ghi nhận `model_override` cho một trial `MockLLM` với seed cố định `11`; chưa đo được xác suất sinh lỗi tương tự trên LLM thật với các cách diễn đạt ticket đa dạng ngoài tập public. |
