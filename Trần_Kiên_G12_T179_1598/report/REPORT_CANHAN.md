# Báo Cáo Cá Nhân — Lab 7: Embedding & Vector Store

**Họ tên:** Trần Kiên_G12_T179_1598
**Nhóm:** ClaudeMax 
**Ngày:** 03/08/2026

> **Nộp 1 bản / sinh viên.** Phần nhóm (lựa chọn tài liệu, thiết kế chiến lược, bộ câu hỏi đánh giá, demo) nộp chung 1 bản trong `REPORT_NHOM.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần cá nhân: 60** = Khởi động (5) + Hướng tiếp cận (10) + Hoàn thiện code (30) + Dự đoán độ tương tự (5) + Kết quả truy xuất của tôi (10).

---

## 1. Khởi động (Warm-up) — Cá nhân (5 điểm)

### Độ tương tự Cosine (Cosine Similarity) (Bài tập 1.1)

**Độ tương tự cosine cao (High cosine similarity) nghĩa là gì?**
> Khi hai đoạn văn bản có vector gần nhau trong không gian embedding, cosine similarity cao, tức là chúng có ý nghĩa tương đồng về ngữ nghĩa.

**Ví dụ có độ tương tự CAO:**
- Câu A: "The cat is sleeping on the sofa."
- Câu B: "The cat is sleeping on the couch."
- Tại sao tương đồng: cùng nói về một hành động và một đối tượng rất gần nhau về nghĩa.

**Ví dụ có độ tương tự THẤP:**
- Câu A: "I love machine learning."
- Câu B: "I dislike rainy weather."
- Tại sao khác: hai câu có chủ đề khác nhau và không chia sẻ ngữ nghĩa rõ ràng.

**Tại sao độ tương tự cosine (cosine similarity) được ưu tiên hơn khoảng cách Euclid (Euclidean distance) cho text embeddings?**
> Cosine tập trung vào hướng của vector, phù hợp hơn khi so sánh ý nghĩa văn bản, trong khi khoảng cách Euclid nhạy với độ lớn vector hơn là nội dung ngữ nghĩa.

### Bài toán tính toán Chunking (Bài tập 1.2)

**Tài liệu 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**
> Công thức: $\lceil (10000 - 50) / (500 - 50) \rceil = \lceil 9500 / 450 \rceil = 22$ chunk.
>
> **Đáp án:** 22 chunks.

**Nếu độ chồng chéo (overlap) tăng lên 100, số lượng chunk thay đổi thế nào? Tại sao muốn độ chồng chéo nhiều hơn?**
> Khi overlap tăng, bước dịch chuyển giữa các chunk nhỏ hơn, nên số chunk sẽ tăng lên. Độ chồng chéo giúp giữ ngữ cảnh liên tục giữa các chunk, đặc biệt hữu ích cho retrieval.

---

## 2. Hướng tiếp cận của tôi (My Approach) — Cá nhân (10 điểm)

Giải thích cách tiếp cận của bạn khi lập trình (implement) các phần chính trong gói `src`.

### Các hàm chia nhỏ (Chunking Functions)

**`SentenceChunker.chunk`** — hướng tiếp cận:
> Tôi dùng regex để tách các câu bằng các dấu kết thúc như `.`, `!`, `?`, rồi gom nhóm theo số câu tối đa cho mỗi chunk. Trường hợp văn bản rỗng hoặc không có dấu câu rõ ràng thì vẫn trả về một chunk hợp lệ để tránh lỗi.

**`RecursiveChunker.chunk` / `_split`** — hướng tiếp cận:
> Thuật toán làm việc đệ quy: chọn separator theo thứ tự ưu tiên, nếu một đoạn có thể tách được thì tách, nếu không thì dùng separator tiếp theo. Trường hợp cơ sở là khi đoạn văn bản đã nhỏ hơn hoặc bằng `chunk_size`, lúc đó dừng lại và trả về chunk hiện tại.

### Lớp EmbeddingStore

**`add_documents` + `search`** — hướng tiếp cận:
> Tôi lưu mỗi document dưới dạng bản ghi có `content`, `metadata` và embedding. Khi search, tôi nhúng câu hỏi rồi so sánh với các embedding đã lưu bằng dot product để lấy top-k gần nhất.

**`search_with_filter` + `delete_document`** — hướng tiếp cận:
> Tôi áp dụng filter trước khi tìm kiếm để giảm không gian tìm kiếm, sau đó chạy similarity search trên các bản ghi còn lại. Xóa document bằng cách lọc theo `doc_id` và loại bỏ toàn bộ các chunk thuộc document đó.

### Tác tử KnowledgeBaseAgent

**`answer`** — hướng tiếp cận:
> Tôi lấy top-k chunks từ store, nối chúng thành context rồi tạo prompt có câu hỏi và ngữ cảnh. Cách này giúp agent trả lời dựa trên tài liệu được truy xuất thay vì tự suy đoán.

---

## 3. Hoàn thiện code (Core Implementation) — Cá nhân (30 điểm)

Vượt qua bộ kiểm thử là điều kiện tính điểm phần này.

### Kết Quả Kiểm Thử (Test Results)

```
pytest tests/ -v
```

**Số lượng bài test vượt qua (pass):** 42 / 42

---

## 4. Dự đoán độ tương tự (Similarity Predictions) — Cá nhân (5 điểm)

| Cặp | Câu A | Câu B | Dự đoán | Điểm thực tế | Đúng? |
|------|-----------|-----------|---------|--------------|-------|
| 1 | The cat is sleeping on the sofa. | The cat is sleeping on the couch. | cao | -0.1255 | Không |
| 2 | I love machine learning. | I dislike rainy weather. | thấp | 0.076 | Không |
| 3 | Python is a programming language. | Python is used for software development. | cao | -0.036 | Không |
| 4 | The company ships products worldwide. | The weather is sunny today. | thấp | 0.0055 | Có |
| 5 | A vector database stores embeddings. | Embeddings are numerical representations of text. | cao | -0.1185 | Không |

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn ý nghĩa?**
> Điều bất ngờ nhất là các score không luôn phản ánh trực giác ngữ nghĩa vì mock embeddings chỉ là vector giả định. Điều này cho thấy chất lượng retrieval phụ thuộc rất nhiều vào embedding backend và dữ liệu đầu vào.

---

## 5. Kết quả truy xuất của tôi (Competition Results) — Cá nhân (10 điểm)

Chạy **5 câu hỏi đánh giá của nhóm** trên mã nguồn cá nhân của bạn trong gói `src`. **5 câu hỏi này phải trùng với các thành viên cùng nhóm** (xem `REPORT_NHOM.md`).

| # | Câu hỏi (Query) | Top-1 Chunk truy xuất được (tóm tắt) | Điểm Score | Có liên quan không? (Relevant) | Câu trả lời của Agent (tóm tắt) |
|---|-------|--------------------------------|-------|-----------|------------------------|
| 1 | What is Python? | Vector databases store embeddings for similarity search. | 0.0582 | Không | Trả lời ngắn gọn dựa trên context thu được |
| 2 | What is machine learning? | Machine learning uses algorithms to learn from data. | 0.105 | Có | Trả lời đúng về chủ đề machine learning |
| 3 | What do vector databases store? | Vector databases store embeddings for similarity search. | -0.024 | Có | Trả lời đúng về embeddings |
| 4 | Tell me about Python programming | Machine learning uses algorithms to learn from data. | 0.075 | Không | Không đủ liên quan |
| 5 | What is used to learn from data? | Machine learning uses algorithms to learn from data. | -0.0295 | Có | Trả lời đúng về machine learning |

**Bao nhiêu câu hỏi trả về chunk có liên quan trong top-3?** 3 / 5

**Điều hay nhất tôi học được từ thành viên khác / nhóm khác (qua demo):**
> Tôi học được rằng việc chọn chunking strategy và metadata filter có tác động lớn đến chất lượng retrieval. Một số câu hỏi có thể tốt hơn khi dùng chunk nhỏ và có metadata phù hợp.

---

## Tự Đánh Giá (Phần Cá Nhân)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Khởi động (Warm-up) | 5 / 5 |
| Hướng tiếp cận của tôi (My Approach) | 10 / 10 |
| Hoàn thiện code (Core Implementation — tests) | 30 / 30 |
| Dự đoán độ tương tự (Similarity Predictions) | 5 / 5 |
| Kết quả truy xuất của tôi (Competition Results) | 8 / 10 |
| **Tổng phần cá nhân** | **58 / 60** |
