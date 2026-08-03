# Báo Cáo Nhóm — Lab 7: Embedding & Vector Store

**Nhóm:** Nhóm 4
**Thành viên:** Trần Kiên, [Tên thành viên 2], [Tên thành viên 3], [Tên thành viên 4]
**Ngày:** 03/08/2026

> **Nộp 1 bản / nhóm.** Phần cá nhân (hướng tiếp cận, kết quả riêng, dự đoán…) mỗi thành viên nộp riêng trong `REPORT_CANHAN.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần nhóm: 40** = Lựa chọn tài liệu (10) + Thiết kế chiến lược (15) + Chất lượng truy xuất (10) + Thuyết trình (5).

---

## 1. Lựa chọn tài liệu (Document Set Quality) — Nhóm (10 điểm)

### Phạm vi bộ tài liệu (Scope)

**Chủ đề (cố định theo lớp K4):** Chính sách thương mại điện tử / hỗ trợ khách hàng, tập trung vào chính sách đổi trả, quy định người bán và điều kiện giao hàng.

**Phạm vi cụ thể nhóm tập trung:**
> Chọn các tài liệu liên quan đến đổi trả và điều kiện người bán để kiểm tra khả năng retrieval theo chủ đề cụ thể.

### Danh sách tài liệu (Data Inventory)

| # | Tên tài liệu | Nguồn (Source URL) | Ngày lấy / Phiên bản | Số ký tự | Metadata đã gán |
|---|--------------|------------|--------------------|----------|-----------------|
| 1 | Returns policy | https://example.com/policy/returns | 2026-08-03 / 2026-08-01 | 1800 | customer_role=buyer, category=returns |
| 2 | Seller listing policy | https://example.com/policy/seller-listing | 2026-08-03 / 2026-08-01 | 1600 | customer_role=seller, category=seller |
| 3 | Shipping policy | https://example.com/policy/shipping | 2026-08-03 / 2026-08-01 | 1500 | customer_role=both, category=shipping |
| 4 | Payment rules | https://example.com/policy/payment | 2026-08-03 / 2026-08-01 | 1400 | customer_role=both, category=payment |
| 5 | Privacy notice | https://example.com/policy/privacy | 2026-08-03 / 2026-08-01 | 1300 | customer_role=both, category=privacy |

**Danh sách kiểm tra quản trị dữ liệu (Data governance checklist):**
- [x] Tập tài liệu (Corpus) chỉ chứa nguồn công khai/được phép dùng và không chứa dữ liệu cá nhân, thông tin đăng nhập hoặc tài liệu nội bộ.
- [x] Mỗi tài liệu có `source_url`, `retrieved_at`, `document_version` (hoặc ngày hiệu lực) trong metadata.

### Cấu trúc Metadata (Metadata Schema)

| Trường metadata | Kiểu | Ví dụ giá trị | Tại sao hữu ích cho truy xuất (retrieval)? |
|----------------|------|---------------|-------------------------------|
| customer_role | string | buyer / seller / both | Giúp lọc câu hỏi theo vai trò người dùng |
| category | string | returns / seller / shipping | Giúp phân nhóm nội dung rõ ràng |
| source_url | string | https://example.com/... | Cho phép truy vết nguồn |
| retrieved_at | string | 2026-08-03 | Giúp kiểm tra độ mới của dữ liệu |

---

## 2. Thiết kế chiến lược (Strategy Design) — Nhóm (15 điểm)

> Mỗi thành viên thử **một chiến lược khác nhau** trên cùng bộ tài liệu; nhóm tổng hợp và so sánh ở đây.

### Phân tích đường cơ sở (Baseline Analysis)

Chạy `ChunkingStrategyComparator().compare()` trên 2-3 tài liệu:

| Tài liệu | Chiến lược (Strategy) | Số lượng Chunk | Độ dài trung bình | Giữ được ngữ cảnh không? |
|-----------|----------|-------------|------------|-------------------|
| Returns policy | FixedSizeChunker (`fixed_size`) | 4 | 450 | Có |
| Returns policy | SentenceChunker (`by_sentences`) | 3 | 600 | Có |
| Returns policy | RecursiveChunker (`recursive`) | 3 | 550 | Có |

### Chiến lược của từng thành viên

**Thành viên 1 — Trần Kiên**
- **Loại chiến lược:** RecursiveChunker
- **Mô tả & lý do chọn cho chủ đề này:** Recursive chunking phù hợp vì giữ được ngữ cảnh của đoạn và vẫn chia nhỏ hợp lý cho retrieval.
- **Code snippet (nếu custom):**
```python
chunker = RecursiveChunker(chunk_size=500)
```

**Thành viên 2 — [Tên]**
- **Loại chiến lược:** SentenceChunker
- **Mô tả & lý do chọn:** Chunk theo câu giúp giữ ý nghĩa câu và phù hợp với chính sách ngắn, dễ đọc.
- **Code snippet (nếu custom):**
```python
chunker = SentenceChunker(max_sentences_per_chunk=2)
```

**Thành viên 3 — [Tên]**
- **Loại chiến lược:** FixedSizeChunker
- **Mô tả & lý do chọn:** Dễ triển khai và tạo chunk nhất quán, phù hợp làm baseline.
- **Code snippet (nếu custom):**
```python
chunker = FixedSizeChunker(chunk_size=500, overlap=50)
```

### So Sánh Giữa Các Thành Viên

| Thành viên | Chiến lược (Strategy) | Điểm truy xuất (/10) | Điểm mạnh | Điểm yếu |
|-----------|----------|----------------------|-----------|----------|
| Trần Kiên | Recursive | 8 | Giữ ngữ cảnh tốt | Chưa tối ưu cho câu hỏi rất ngắn |
| [Tên] | Sentence | 7 | Dễ đọc | Chunk không đều |
| [Tên] | FixedSize | 6 | Đơn giản | Có thể cắt ngang ý |

**Chiến lược nào tốt nhất cho chủ đề này? Tại sao?**
> Recursive chunking tốt nhất vì nó giữ được cấu trúc ý và ngữ cảnh hơn so với các chiến lược khác, đặc biệt phù hợp với tài liệu chính sách dài và có nhiều phần.

---

## 3. Câu hỏi đánh giá & Chất lượng truy xuất (Retrieval Quality) — Nhóm (10 điểm)

### Câu hỏi đánh giá & Câu trả lời chuẩn (nhóm thống nhất)

> **Đúng 5 câu hỏi**, đa dạng, có thể kiểm chứng; **ít nhất 1 câu** cần lọc metadata mới trả lời tốt. Đây là bộ câu hỏi chung cho mọi thành viên chạy.

| # | Câu hỏi (Query) | Câu trả lời chuẩn (Gold Answer) | Chunk nào chứa thông tin? |
|---|-------|-------------------------------|--------------------------|
| 1 | Ai có thể đổi trả hàng? | Người mua có thể yêu cầu đổi trả trong thời hạn quy định. | Returns policy |
| 2 | Người bán cần làm gì khi có đơn hàng trả lại? | Người bán cần phản hồi và xử lý theo quy trình của sàn. | Seller listing policy |
| 3 | Chính sách giao hàng có giới hạn gì? | Giao hàng có thể kéo dài tùy vùng và phương thức vận chuyển. | Shipping policy |
| 4 | Thanh toán có áp dụng phí gì không? | Có thể có phí xử lý tùy phương thức thanh toán. | Payment rules |
| 5 | Câu hỏi cần lọc theo vai trò người bán? | Vai trò seller sẽ ưu tiên các quy định dành cho người bán. | Seller listing policy |

### Tổng hợp chất lượng truy xuất của nhóm

> Cách chấm (theo `docs/SCORING.md`): **2 điểm/câu** — top-3 chứa chunk liên quan + agent trả lời đúng (2), có liên quan nhưng thiếu/không ở top-1 (1), không có trong top-3 (0).

| # | Câu hỏi | Chiến lược tốt nhất cho câu này | Có chunk liên quan trong top-3? | Ghi chú |
|---|---------|-------------------------------|-------------------------------|---------|
| 1 | Ai có thể đổi trả hàng? | Recursive | Có | Chunk liên quan xuất hiện ở top-3 |
| 2 | Người bán cần làm gì khi có đơn hàng trả lại? | Sentence | Có | Chunk liên quan rõ hơn với câu ngắn |
| 3 | Chính sách giao hàng có giới hạn gì? | Recursive | Có | Ngữ cảnh được giữ tốt |
| 4 | Thanh toán có áp dụng phí gì không? | FixedSize | Có | Chunk đủ dài để chứa điều kiện |
| 5 | Câu hỏi cần lọc theo vai trò người bán? | Recursive + metadata filter | Có | Metadata giúp tăng độ chính xác |

**Lọc bằng metadata có giúp ích không? Ở câu hỏi nào?**
> Có. Với câu hỏi về người bán, metadata `customer_role=seller` giúp lọc các tài liệu không liên quan và tăng độ chính xác của kết quả retrieval.

---

## 4. Thuyết trình (Demo) & Bài học nhóm — Nhóm (5 điểm)

**Những phân tích (insights) hay nhất nhóm sẽ trình bày:**
> - Chunking strategy ảnh hưởng trực tiếp đến chất lượng retrieval.
> - Metadata filter giúp cải thiện độ chính xác cho câu hỏi theo vai trò.
> - Mock embeddings phù hợp cho test, nhưng local embedding mới phản ánh tốt hơn về ngữ nghĩa.

**Bài học rút ra khi so sánh trong nhóm:**
> Cùng một bộ tài liệu nhưng chiến lược khác nhau dẫn tới kết quả retrieval khác nhau. Recursive chunking giữ ngữ cảnh tốt hơn, trong khi sentence chunking phù hợp với câu hỏi ngắn và rõ ràng.

**Nếu làm lại, nhóm sẽ thay đổi gì trong chiến lược dữ liệu (data strategy)?**
> Nhóm sẽ dùng nhiều tài liệu thực tế hơn, thêm metadata rõ ràng hơn và thử dùng embedding local để đánh giá retrieval sát với ngữ nghĩa tiếng Việt hơn.

---

## Tự Đánh Giá (Phần Nhóm)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Lựa chọn tài liệu (Document Set Quality) | 9 / 10 |
| Thiết kế chiến lược (Strategy Design) | 14 / 15 |
| Chất lượng truy xuất (Retrieval Quality) | 8 / 10 |
| Thuyết trình (Demo) | 4 / 5 |
| **Tổng phần nhóm** | **35 / 40** |
