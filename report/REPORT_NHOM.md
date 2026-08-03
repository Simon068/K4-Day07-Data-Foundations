# Báo Cáo Nhóm — Lab 7: Embedding & Vector Store

**Nhóm:** Nhóm 4
**Thành viên:** Phú Quang + Quân (Role 1), Trần Kiên (Role 2), Nguyễn Hữu Huy (Role 3), Trần Linh (Role 4)
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
| 1 | Chính sách đổi trả Lazada | https://cdn.contract.alibaba.com/terms/common_platform_service/20260713181356461/20260713181356461.html?spm=a2o4n.tm80089364.9817169850.6.41892887K8GFND&lng=en | 2026-08-03 / 2026-07-29 | 2629 | doc_id=lazada-return-policy-vn, customer_role=Consumer, category=Return Policy, language=vi |
| 2 | Chính sách hoàn tiền Lazada | https://cdn.contract.alibaba.com/terms/common_platform_service/20260713182056907/20260713182056907.html?spm=a2o4n.tm80089364.9817169850.7.41892887K8GFND&lng=en | 2026-08-03 / 2026-07-29 | 2667 | doc_id=lazada-refund-policy-vn, customer_role=Consumer, category=Refund Policy, language=vi |
| 3 | Điều khoản sử dụng Lazada | https://cdn.contract.alibaba.com/terms/common_platform_service/20260713175157767/20260713175157767.html?spm=a2o4n.tm80089364.9817169850.1.41892887K8GFND&lng=en | 2026-08-03 / 2026.1 | 2560 | doc_id=lazada-term-of-use, customer_role=Consumer, category=Terms of Use, language=vi |
| 4 | Điều khoản và điều kiện mua bán Lazada | https://cdn.contract.alibaba.com/terms/common_platform_service/20260713175615185/20260713175615185.html?spm=a2o4n.tm80089364.9817169850.2.41892887K8GFND&lng=en | 2026-08-03 / 2026.1 | 2869 | doc_id=lazada-terms-and-conditions-of-sale, customer_role=Consumer, category=Sales Terms, language=vi |
| 5 | Điều khoản thanh toán Lazada | https://cdn.contract.alibaba.com/terms/common_platform_service/20260713182423790/20260713182423790.html?spm=a2o4n.tm80089364.9817169850.10.41892887K8GFND&lng=en | 2026-08-03 / 2026-07-29 | 2544 | doc_id=lazada-payment-policy-vn, customer_role=Consumer, category=Payment Terms, language=vi |

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

**Người 1 — Phú Quang + Quân (Role 1 — Code & baseline)**
- **Loại chiến lược:** FixedSizeChunker
- **Mô tả & lý do chọn cho chủ đề này:** Đây là chiến lược baseline, đơn giản và dễ kiểm soát để làm nền cho việc so sánh.
- **Code snippet (nếu custom):**
```python
chunker = FixedSizeChunker(chunk_size=500, overlap=50)
```

**Người 2 — Trần Kiên (Role 2 — Dữ liệu & metadata)**
- **Loại chiến lược:** Metadata-assisted retrieval
- **Mô tả & lý do chọn:** Trọng tâm công việc là chuẩn bị dữ liệu, metadata và đảm bảo tài liệu có đủ thông tin để retrieval hoạt động tốt hơn.
- **Code snippet (nếu custom):**
```python
metadata_filter = {"customer_role": "Consumer", "category": "Return Policy"}
```

**Người 3 — Nguyễn Hữu Huy (Role 3 — Retrieval strategy & benchmark)**
- **Loại chiến lược:** SentenceChunker
- **Mô tả & lý do chọn:** Chunk theo câu giúp giữ ý nghĩa câu và phù hợp cho các câu hỏi benchmark ngắn, rõ mục tiêu.
- **Code snippet (nếu custom):**
```python
chunker = SentenceChunker(max_sentences_per_chunk=2)
```

**Người 4 — Trần Linh (Role 4 — So sánh, báo cáo & demo)**
- **Loại chiến lược:** RecursiveChunker
- **Mô tả & lý do chọn:** Recursive chunking phù hợp vì giữ được ngữ cảnh của đoạn và vẫn chia nhỏ hợp lý cho retrieval.
- **Code snippet (nếu custom):**
```python
chunker = RecursiveChunker(chunk_size=500)
```

### So Sánh Giữa Các Thành Viên

| Thành viên | Vai trò | Chiến lược (Strategy) | Điểm truy xuất (/10) | Điểm mạnh | Điểm yếu |
|-----------|---------|-----------------------|----------------------|-----------|----------|
| Phú Quang + Quân | Người 1 – Code & baseline | FixedSizeChunker | 6 | Đơn giản, dễ kiểm soát | Có thể cắt ngang ý |
| Trần Kiên | Người 2 – Dữ liệu & metadata | Metadata-assisted retrieval | 7 | Giúp tăng độ chính xác khi lọc dữ liệu | Không thay đổi trực tiếp cấu trúc chunk |
| Nguyễn Hữu Huy | Người 3 – Retrieval strategy & benchmark | SentenceChunker | 7 | Dễ đọc, phù hợp câu hỏi ngắn | Chunk không đều |
| Trần Linh | Người 4 – So sánh, báo cáo & demo | RecursiveChunker | 8 | Giữ ngữ cảnh tốt | Chưa tối ưu cho câu hỏi rất ngắn |

**Chiến lược nào tốt nhất cho chủ đề này? Tại sao?**
> Recursive chunking tốt nhất vì nó giữ được cấu trúc ý và ngữ cảnh hơn so với các chiến lược khác, đặc biệt phù hợp với tài liệu chính sách dài và có nhiều phần.

---

## 3. Câu hỏi đánh giá & Chất lượng truy xuất (Retrieval Quality) — Nhóm (10 điểm)

### Câu hỏi đánh giá & Câu trả lời chuẩn (nhóm thống nhất)

> **Đúng 5 câu hỏi**, đa dạng, có thể kiểm chứng; **ít nhất 1 câu** cần lọc metadata mới trả lời tốt. Đây là bộ câu hỏi chung cho mọi thành viên chạy.

| # | Câu hỏi (Query) | Câu trả lời chuẩn (Gold Answer) | Chunk nào chứa thông tin? |
|---|-------|-------------------------------|--------------------------|
| 1 | Ai có thể yêu cầu đổi trả sản phẩm? | Khách hàng có thể yêu cầu đổi trả nếu sản phẩm sai mô tả, lỗi, hư hỏng hoặc không đủ điều kiện theo chính sách. | lazada-return-policy-vn |
| 2 | Khi nào đơn hàng được hoàn tiền? | Đơn hàng được hoàn tiền khi bị hủy, trả lại sản phẩm hợp lệ hoặc phát sinh lỗi về giá/thông tin. | lazada-refund-policy-vn |
| 3 | Điều khoản sử dụng có quy định gì về việc tiếp tục sử dụng dịch vụ? | Nếu người dùng tiếp tục sử dụng dịch vụ sau khi có thông báo cập nhật, được coi là đã chấp nhận các thay đổi. | lazada-term-of-use |
| 4 | Thanh toán COD có áp dụng cho mọi đơn hàng không? | Không, đơn hàng vượt hạn mức COD sẽ bắt buộc thanh toán trực tuyến. | lazada-payment-policy-vn |
| 5 | Câu hỏi cần lọc theo vai trò người bán/khách hàng? | Metadata `customer_role` và `category` giúp phân biệt nội dung cho người mua và nhà bán. | lazada-terms-and-conditions-of-sale |

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
