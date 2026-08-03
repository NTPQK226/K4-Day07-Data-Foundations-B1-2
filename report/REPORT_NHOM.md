# Báo Cáo Nhóm — Lab 7: Embedding & Vector Store

**Nhóm:** [Tên nhóm]
**Thành viên:** [Họ tên từng thành viên]
**Ngày:** [Ngày nộp]

> **Nộp 1 bản / nhóm.** Phần cá nhân (hướng tiếp cận, kết quả riêng, dự đoán…) mỗi thành viên nộp riêng trong `REPORT_CANHAN.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần nhóm: 40** = Lựa chọn tài liệu (10) + Thiết kế chiến lược (15) + Chất lượng truy xuất (10) + Thuyết trình (5).

---

## 1. Lựa chọn tài liệu (Document Set Quality) — Nhóm (10 điểm)

### Phạm vi bộ tài liệu (Scope)

**Chủ đề (cố định theo lớp K4):** Chính sách thương mại điện tử / hỗ trợ khách hàng (thanh toán, đổi trả, giao hàng, quyền riêng tư, điều kiện người bán…).

**Phạm vi cụ thể nhóm tập trung:**
> Tập trung vào các chính sách hỗ trợ khách hàng và quy định giao dịch của nền tảng Shopee, bao gồm quy trình thanh toán, vận chuyển, đổi trả đối với người mua và các chế tài, phí sàn áp dụng cho người bán.

### Danh sách tài liệu (Data Inventory)

| # | Tên tài liệu | Nguồn (Source URL) | Ngày lấy / Phiên bản | Số ký tự | Metadata đã gán |
|---|--------------|------------|--------------------|----------|-----------------|
| 1 | Chính sách Trả hàng / Hoàn tiền | help.shopee.vn | 04-08-2026 | 3200 | `customer_role`: "buyer", `category`: "payment_and_return" |
| 2 | Hướng dẫn thanh toán qua ShopeePay | help.shopee.vn | 04-08-2026 | 2500 | `customer_role`: "buyer", `category`: "payment_and_return" |
| 3 | Phí vận chuyển và thời gian giao hàng | help.shopee.vn | 04-08-2026 | 4100 | `customer_role`: "buyer", `category`: "shipping_and_privacy" |
| 4 | Quy định bảo vệ thông tin người dùng | help.shopee.vn | 04-08-2026 | 3800 | `customer_role`: "buyer", `category`: "shipping_and_privacy" |
| 5 | Quy định các loại phí sàn dành cho Người Bán | help.shopee.vn | 04-08-2026 | 5200 | `customer_role`: "seller", `category`: "seller_policy" |
| 6 | Chính sách cấm bán hàng giả, hàng nhái | help.shopee.vn | 04-08-2026 | 4600 | `customer_role`: "seller", `category`: "seller_policy" |
| 7 | Chính sách giải quyết tranh chấp khiếu nại | help.shopee.vn | 04-08-2026 | 3100 | `customer_role`: "both", `category`: "general_rules" |
| 8 | Quy định về việc sử dụng Shopee Xu | help.shopee.vn | 04-08-2026 | 1962 | `customer_role`: "both", `category`: "general_rules" |

**Danh sách kiểm tra quản trị dữ liệu (Data governance checklist):**
- [ x ] Tập tài liệu (Corpus) chỉ chứa nguồn công khai/được phép dùng và không chứa dữ liệu cá nhân, thông tin đăng nhập hoặc tài liệu nội bộ.
- [ x ] Mỗi tài liệu có `source_url`, `retrieved_at`, `document_version` (hoặc ngày hiệu lực) trong metadata.

### Cấu trúc Metadata (Metadata Schema)

| Trường metadata | Kiểu | Ví dụ giá trị | Tại sao hữu ích cho truy xuất (retrieval)? |
|----------------|------|---------------|-------------------------------|
| `customer_role` | String | `buyer`, `seller`, `both` | Rất hữu ích để lọc (filter) các câu hỏi đặc thù. Tránh việc dùng nhầm quy định của Người mua để trả lời cho Người bán. |
| `category` | String | `seller_policy`, `general_rules` | Hữu ích khi người dùng muốn khoanh vùng tìm kiếm trong một hạng mục chính sách nhất định. |

---

## 2. Thiết kế chiến lược (Strategy Design) — Nhóm (15 điểm)

> Mỗi thành viên thử **một chiến lược khác nhau** trên cùng bộ tài liệu; nhóm tổng hợp và so sánh ở đây.

### Phân tích đường cơ sở (Baseline Analysis)

Chạy `ChunkingStrategyComparator().compare()` trên 2-3 tài liệu:

| Tài liệu | Chiến lược (Strategy) | Số lượng Chunk | Độ dài trung bình | Giữ được ngữ cảnh không? |
|-----------|----------|-------------|------------|-------------------|
| | FixedSizeChunker (`fixed_size`) | | | |
| | SentenceChunker (`by_sentences`) | | | |
| | RecursiveChunker (`recursive`) | | | |

### Chiến lược của từng thành viên

> Mỗi thành viên điền một khối dưới đây (copy thêm nếu nhóm có nhiều hơn 3 người).

**Thành viên 1 — [Tên]**
- **Loại chiến lược:** [FixedSize / Sentence / Recursive / custom]
- **Mô tả & lý do chọn cho chủ đề này:** *(2-3 câu)*
- **Code snippet (nếu custom):**
```python
# Dán mã nguồn (implementation) vào đây
```

**Thành viên 2 — [Tên]**
- **Loại chiến lược:**
- **Mô tả & lý do chọn:**
- **Code snippet (nếu custom):**

**Thành viên 3 — [Tên]**
- **Loại chiến lược:**
- **Mô tả & lý do chọn:**
- **Code snippet (nếu custom):**

### So Sánh Giữa Các Thành Viên

| Thành viên | Chiến lược (Strategy) | Điểm truy xuất (/10) | Điểm mạnh | Điểm yếu |
|-----------|----------|----------------------|-----------|----------|
| | | | | |
| | | | | |
| | | | | |

**Chiến lược nào tốt nhất cho chủ đề này? Tại sao?**
> *Viết 2-3 câu — đây là phần được đánh giá cao nhất (khả năng suy nghĩ & giải thích):*

---

## 3. Câu hỏi đánh giá & Chất lượng truy xuất (Retrieval Quality) — Nhóm (10 điểm)

### Câu hỏi đánh giá & Câu trả lời chuẩn (nhóm thống nhất)

> **Đúng 5 câu hỏi**, đa dạng, có thể kiểm chứng; **ít nhất 1 câu** cần lọc metadata mới trả lời tốt. Đây là bộ câu hỏi chung cho mọi thành viên chạy.

| # | Câu hỏi (Query) | Câu trả lời chuẩn (Gold Answer) | Chunk nào chứa thông tin? |
|---|-------|-------------------------------|--------------------------|
| 1 | Mất bao lâu để tôi nhận được tiền hoàn vào ví ShopeePay nếu hủy đơn? | Quá trình hoàn tiền vào ví ShopeePay diễn ra trong vòng 24 giờ kể từ khi Shopee chấp nhận yêu cầu. | Bài 1 (Trả hàng/Hoàn tiền) |
| 2 | Phí thanh toán cố định hiện tại trên mỗi đơn hàng thành công là bao nhiêu phần trăm? | Đối với Người bán, phí thanh toán cố định là 4% (đã bao gồm VAT) trên tổng giá trị thanh toán của người mua. | Bài 5 (Phí sàn Người Bán) |
| 3 | Làm thế nào để áp dụng mã miễn phí vận chuyển Extra? | Bạn chọn mã Freeship Extra tại mục "Shopee Voucher" ở bước thanh toán đơn hàng. | Bài 3 (Phí vận chuyển) |
| 4 | Nếu tôi phát hiện shop gửi hàng fake thì Shopee có đền bù không? | Shopee cam kết hoàn 100% giá trị đơn hàng nếu chứng minh được sản phẩm là hàng giả/nhái. | Bài 6 (Cấm hàng giả) |
| 5 | Shopee Xu của tôi sẽ hết hạn vào ngày nào? | Shopee Xu sẽ hết hạn vào ngày cuối cùng của tháng thứ 3 kể từ ngày nhận được Xu. | Bài 8 (Sử dụng Shopee Xu) |

### Tổng hợp chất lượng truy xuất của nhóm

> Cách chấm (theo `docs/SCORING.md`): **2 điểm/câu** — top-3 chứa chunk liên quan + agent trả lời đúng (2), có liên quan nhưng thiếu/không ở top-1 (1), không có trong top-3 (0).

| # | Câu hỏi | Chiến lược tốt nhất cho câu này | Có chunk liên quan trong top-3? | Ghi chú |
|---|---------|-------------------------------|-------------------------------|---------|
| 1 | | | | |
| 2 | | | | |
| 3 | | | | |
| 4 | | | | |
| 5 | | | | |

**Lọc bằng metadata có giúp ích không? Ở câu hỏi nào?**
> *Viết 2-3 câu:*

---

## 4. Thuyết trình (Demo) & Bài học nhóm — Nhóm (5 điểm)

**Những phân tích (insights) hay nhất nhóm sẽ trình bày:**
> *Liệt kê 2-3 ý:*

**Bài học rút ra khi so sánh trong nhóm:**
> *Viết 2-3 câu — cùng tài liệu nhưng chiến lược khác nhau dẫn tới khác biệt gì?*

**Nếu làm lại, nhóm sẽ thay đổi gì trong chiến lược dữ liệu (data strategy)?**
> *Viết 2-3 câu:*

---

## Tự Đánh Giá (Phần Nhóm)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Lựa chọn tài liệu (Document Set Quality) | / 10 |
| Thiết kế chiến lược (Strategy Design) | / 15 |
| Chất lượng truy xuất (Retrieval Quality) | / 10 |
| Thuyết trình (Demo) | / 5 |
| **Tổng phần nhóm** | **/ 40** |
