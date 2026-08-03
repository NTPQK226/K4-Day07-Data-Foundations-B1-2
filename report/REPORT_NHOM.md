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
| cam-ban-hang-gia.md | FixedSizeChunker (`fixed_size`) | 33 | 200 | Kém — hay cắt đứt câu giữa chừng |
| cam-ban-hang-gia.md | SentenceChunker (`by_sentences`) | 9 | 555 | Tốt — giữ trọn ngữ nghĩa câu |
| cam-ban-hang-gia.md | RecursiveChunker (`recursive`) | 12 | 415 | Tốt — cắt theo dấu phân cách tự nhiên |
| cam-ban-hang-gia.md | MarkdownHeadingChunker (`markdown`) | 8 | 600 | Xuất sắc — phân chia theo tiêu đề chính sách |

### Chiến lược của từng thành viên

**Thành viên 1 — Nguyễn Hữu Công**
- **Loại chiến lược:** FixedSizeChunker (chunk_size=600, overlap=100)
- **Mô tả & lý do chọn cho chủ đề này:** Dễ cài đặt, dùng làm baseline để so sánh. Cắt văn bản thành các khối có kích thước cố định, sử dụng overlap để tránh mất thông tin ở phần giao cắt.

**Thành viên 2 — Tạ Quốc Tuấn**
- **Loại chiến lược:** RecursiveChunker (chunk_size=500)
- **Mô tả & lý do chọn:** Cố gắng tách văn bản tự nhiên theo thứ tự ưu tiên các ký tự phân cách (đoạn, câu, từ). Phù hợp với văn bản chính sách có cấu trúc đa dạng.

**Thành viên 3 — Nguyễn Thanh Phong**
- **Loại chiến lược:** SentenceChunker (max_sentences=3)
- **Mô tả & lý do chọn:** Văn bản quy định thường chia theo câu hoàn chỉnh. Việc tách theo số lượng câu giúp giữ trọn ngữ nghĩa, tránh bị cắt đoạn vô nghĩa.

**Thành viên 4 — Nguyễn Tuấn Dương**
- **Loại chiến lược:** MarkdownHeadingChunker (custom)
- **Mô tả & lý do chọn:** Chuyên trị các file chính sách định dạng Markdown bằng cách phân tách nội dung dựa trên cấu trúc các heading (Tiêu đề mục lục). Giữ được hoàn toàn ngữ cảnh của một điều khoản cụ thể.
- **Code snippet (nếu custom):**
```python
    def chunk(self, text: str) -> list[str]:
        parts = re.split(r'(?m)^(#+ .*?\n)', text)
        chunks = []
        current_chunk = ""
        for part in parts:
            if not part: continue
            if re.match(r'^#+ ', part):
                if current_chunk.strip(): chunks.append(current_chunk.strip())
                current_chunk = part
            else: current_chunk += part
        if current_chunk.strip(): chunks.append(current_chunk.strip())
        return chunks if chunks else [text.strip()]
```

### So Sánh Giữa Các Thành Viên

| Thành viên | Chiến lược (Strategy) | Điểm truy xuất (/10) | Điểm mạnh | Điểm yếu |
|-----------|----------|----------------------|-----------|----------|
| Công | FixedSize(600, 100) | 2/10 | Dễ cài đặt, luôn đảm bảo chunk đều nhau | Dễ chia cắt cụm từ, câu, làm hỏng ý nghĩa ngữ cảnh |
| Tuấn | Recursive(500) | 4/10 | Tách văn bản tự nhiên hơn FixedSize | Vẫn có rủi ro nếu một câu quá dài không có dấu ngắt |
| Phong | Sentence(3) | 4/10 | Giữ vẹn toàn ngữ nghĩa của từng nhóm câu | Các chunk có kích thước chênh lệch lớn |
| Dương | MarkdownHeading | 4/10 | Hoàn hảo cho các file nội quy/chính sách Markdown | Một mục tiêu đề quá dài sẽ tạo ra chunk rất to |

**Chiến lược nào tốt nhất cho chủ đề này? Tại sao?**
> *Chiến lược MarkdownHeadingChunker và RecursiveChunker là tối ưu nhất. Vì tài liệu Shopee là dạng Markdown phân mục lục chính sách, việc cắt theo cấu trúc heading hoặc ký tự phân cách đoạn văn giúp bảo toàn trọn vẹn ngữ cảnh của từng điều khoản thay vì cắt ngang bừa bãi.*
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

| # | Câu hỏi | Chiến lược tốt nhất cho câu này | Có chunk liên quan trong top-3? | Điểm | Ghi chú |
|---|---------|-------------------------------|-------------------------------|------|---------|
| 1 | Mất bao lâu để hoàn tiền ShopeePay? | RecursiveChunker (Tuấn) | Có | 1/2 | Tuấn truy xuất được chunk thuộc tài liệu thanh toán ShopeePay (liên quan đến ví) nhưng thiếu thông tin thời gian hoàn tiền cụ thể. |
| 2 | Phí thanh toán cố định là bao nhiêu %? | FixedSizeChunker (Công - có filter) | Không | 0/2 | Không ai tìm được vì corpus thiếu % cụ thể, tuy nhiên filter của Công thu hẹp đúng tệp người bán rất tốt. |
| 3 | Cách áp dụng mã miễn phí vận chuyển Extra? | RecursiveChunker (Tuấn) | Có | 1/2 | Tuấn truy xuất được chunk về quy định vận chuyển, có liên quan mảng giao hàng nhưng thiếu cách áp mã chi tiết. |
| 4 | Phát hiện shop gửi hàng fake có đền bù không? | FixedSizeChunker (Công) / MarkdownHeading (Dương) | Có | 1/2 | Top-1 của Công có thông tin khiếu nại, Top-2 của Dương có chữ "hàng giả" và "bồi thường". Thiếu khẳng định đền bù 100%. |
| 5 | Shopee Xu hết hạn vào ngày nào? | SentenceChunker (Phong) / MarkdownHeading (Dương) | Có (Top-3) | 1/2 | Nhóm tìm được phần giới hạn sử dụng Xu ở top-3, nhưng không có ngày hết hạn chính xác. |

**Lọc bằng metadata có giúp ích không? Ở câu hỏi nào?**
> *Rất hữu ích, đặc biệt ở câu 2 (Phí thanh toán). Bằng cách lọc `customer_role=seller`, nhóm đã loại bỏ 6/8 tài liệu không liên quan, giảm nhiễu (noise) đáng kể cho mô hình tìm kiếm, dù kết quả cuối vẫn phụ thuộc vào độ đầy đủ của corpus.*

---

## 4. Thuyết trình (Demo) & Bài học nhóm — Nhóm (5 điểm)

**Những phân tích (insights) hay nhất nhóm sẽ trình bày:**
> - Corpus đóng vai trò sinh tử: 5/5 câu hỏi đều tìm đúng miền chủ đề nhưng đa số không có thông tin chi tiết để trả lời.
> - Embedding nén câu theo từ vựng nên các câu khác ý định (mua vs trả) vẫn cho điểm tương đồng cao.
> - Cắt văn bản theo cấu trúc tự nhiên (như `MarkdownHeadingChunker` hay `RecursiveChunker`) cho ra văn cảnh dễ hiểu và phục vụ LLM tốt hơn cắt cứng (`FixedSizeChunker`).

**Bài học rút ra khi so sánh trong nhóm:**
> *Cùng một bộ tài liệu, nhưng chiến lược cắt khác nhau tạo ra sự phân mảng ý nghĩa rất khác biệt. `FixedSize` làm mất ý, `Sentence` giữ trọn ý nhưng độ dài không đều, trong khi `MarkdownHeading` gom nhóm tốt nhưng dễ phình to nếu mục tiêu đề dài.*

**Nếu làm lại, nhóm sẽ thay đổi gì trong chiến lược dữ liệu (data strategy)?**
> *Nhóm sẽ tăng cường độ chi tiết của corpus (ví dụ scrape sâu hơn vào các bài viết con của Shopee) thay vì chỉ lấy các chính sách chung chung. Cải thiện metadata phong phú hơn (thêm tags chi tiết).*

---

## Tự Đánh Giá (Phần Nhóm)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Lựa chọn tài liệu (Document Set Quality) | 10 / 10 |
| Thiết kế chiến lược (Strategy Design) | 15 / 15 |
| Chất lượng truy xuất (Retrieval Quality) | 4 / 10 |
| Thuyết trình (Demo) | 3 / 5 |
| **Tổng phần nhóm** | **32 / 40** |
