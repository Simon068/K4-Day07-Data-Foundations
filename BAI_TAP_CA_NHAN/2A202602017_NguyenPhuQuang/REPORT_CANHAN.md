# Báo Cáo Cá Nhân — Lab 7: Embedding & Vector Store

**Họ tên:** Nguyễn Phú Quang
**Nhóm:** 2A202602017
**Ngày:** 2026-08-03

> **Nộp 1 bản / sinh viên.** Phần nhóm (lựa chọn tài liệu, thiết kế chiến lược, bộ câu hỏi đánh giá, demo) nộp chung 1 bản trong `REPORT_NHOM.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần cá nhân: 60** = Khởi động (5) + Hướng tiếp cận (10) + Hoàn thiện code (30) + Dự đoán độ tương tự (5) + Kết quả truy xuất của tôi (10).

---

## 1. Khởi động (Warm-up) — Cá nhân (5 điểm)

### Độ tương tự Cosine (Cosine Similarity) (Bài tập 1.1)

**Độ tương tự cosine cao (High cosine similarity) nghĩa là gì?**
> Độ tương tự cosine cao (gần 1.0) nghĩa là hai vector embedding nằm gần cùng hướng trong không gian nhiều chiều, tức hai đoạn văn bản có ý nghĩa ngữ nghĩa tương đồng — chúng nói về cùng chủ đề hoặc cùng ý tưởng dù dùng từ ngữ khác nhau.

**Ví dụ có độ tương tự CAO:**
- Câu A: "Chính sách đổi trả hàng hóa trong vòng 7 ngày"
- Câu B: "Quy định hoàn trả sản phẩm trong 1 tuần"
- Tại sao tương đồng: Cả hai câu đều nói về cùng một chủ đề (trả hàng) với cùng khoảng thời gian, chỉ khác cách diễn đạt.

**Ví dụ có độ tương tự THẤP:**
- Câu A: "Chính sách đổi trả hàng hóa trong vòng 7 ngày"
- Câu B: "Thời tiết hôm nay nắng đẹp, nhiệt độ 32 độ C"
- Tại sao khác: Hai câu thuộc chủ đề hoàn toàn khác nhau (thương mại điện tử vs thời tiết), không có mối liên hệ ngữ nghĩa.

**Tại sao độ tương tự cosine (cosine similarity) được ưu tiên hơn khoảng cách Euclid (Euclidean distance) cho text embeddings?**
> Cosine similarity chỉ đo góc giữa hai vector, bỏ qua độ dài (magnitude). Điều này quan trọng vì text embeddings có thể có độ dài khác nhau tùy thuộc vào độ dài văn bản hay cách mô hình xử lý, nhưng hướng của vector mới mang thông tin ngữ nghĩa. Euclidean distance bị ảnh hưởng bởi magnitude nên có thể cho kết quả sai lệch khi so sánh văn bản dài ngắn khác nhau.

### Bài toán tính toán Chunking (Bài tập 1.2)

**Tài liệu 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**
> *Trình bày phép tính:*
> Công thức: `ceil((doc_length - overlap) / (chunk_size - overlap))`
> = ceil((10000 - 50) / (500 - 50))
> = ceil(9950 / 450)
> = ceil(22.11)
> = **23 chunks**

**Nếu độ chồng chéo (overlap) tăng lên 100, số lượng chunk thay đổi thế nào? Tại sao muốn độ chồng chéo nhiều hơn?**
> Với overlap=100: ceil((10000 - 100) / (500 - 100)) = ceil(9900 / 400) = ceil(24.75) = **25 chunks** — tăng thêm 2 chunks. Overlap lớn hơn giúp mỗi chunk chia sẻ nhiều ngữ cảnh hơn với chunk liền kề, giảm nguy cơ cắt đứt một ý quan trọng nằm ở ranh giới giữa hai chunk, từ đó cải thiện chất lượng truy xuất.

---

## 2. Hướng tiếp cận của tôi (My Approach) — Cá nhân (10 điểm)

Giải thích cách tiếp cận của bạn khi lập trình (implement) các phần chính trong gói `src`.

### Các hàm chia nhỏ (Chunking Functions)

**`SentenceChunker.chunk`** — hướng tiếp cận:
> Dùng regex `(?<=[.!?])(?:\s|\n)` để tách câu — lookbehind kiểm tra ký tự kết thúc câu (dấu chấm, chấm than, hỏi chấm), sau đó match khoảng trắng hoặc newline. Sau khi tách, nhóm các câu lại theo `max_sentences_per_chunk` bằng cách duyệt với bước nhảy (step). Xử lý edge case: text rỗng trả về `[]`, câu cuối không có dấu phân cách vẫn được giữ lại, loại bỏ chuỗi rỗng sau khi strip.

**`RecursiveChunker.chunk` / `_split`** — hướng tiếp cận:
> Thuật toán thử separator đầu tiên trong danh sách để split text, rồi merge các phần nhỏ lại với nhau cho đến khi vượt `chunk_size`. Nếu một phần đơn lẻ vẫn quá lớn, đệ quy xuống separator tiếp theo. Base case: text đã nhỏ hơn hoặc bằng `chunk_size` thì trả về nguyên, hoặc hết separator thì force split theo `chunk_size`. Separator rỗng `""` được xử lý đặc biệt bằng cách cắt thẳng theo kích thước.

### Lớp EmbeddingStore

**`add_documents` + `search`** — hướng tiếp cận:
> Mỗi document được embed bằng `embedding_fn` và lưu dưới dạng dict chứa `{id, content, embedding, metadata}` vào list `_store`. Khi search, embed query rồi tính dot product với tất cả embeddings đã lưu, sort giảm dần theo score và trả về top_k. Nếu ChromaDB khả dụng thì dùng ChromaDB collection thay thế in-memory store.

**`search_with_filter` + `delete_document`** — hướng tiếp cận:
> `search_with_filter`: lọc **trước** khi search — duyệt qua `_store`, giữ lại các record có metadata khớp tất cả key-value trong `metadata_filter`, rồi chạy similarity search trên tập đã lọc. `delete_document`: lọc bỏ tất cả record có `metadata["doc_id"]` khớp, so sánh kích thước trước/sau để trả True/False.

### Tác tử KnowledgeBaseAgent

**`answer`** — hướng tiếp cận:
> Theo mô hình RAG 3 bước: (1) gọi `store.search(question, top_k)` để lấy chunks liên quan nhất, (2) build prompt có cấu trúc rõ ràng gồm instruction + context (đánh số từng chunk) + question, (3) gọi `llm_fn(prompt)` và trả về kết quả. Prompt yêu cầu LLM dựa vào context để trả lời và nói rõ nếu không đủ thông tin.

---

## 3. Hoàn thiện code (Core Implementation) — Cá nhân (30 điểm)

Vượt qua bộ kiểm thử là điều kiện tính điểm phần này.

### Kết Quả Kiểm Thử (Test Results)

```
============================= test session starts ==============================
platform linux -- Python 3.11.14, pytest-9.1.1, pluggy-1.6.0
rootdir: /home/tobi/Documents/AI_COURSE/DAY07_2A202602017_NguyenPhuQuang
collected 42 items

tests/test_solution.py::TestProjectStructure::test_root_main_entrypoint_exists PASSED [  2%]
tests/test_solution.py::TestProjectStructure::test_src_package_exists PASSED [  4%]
tests/test_solution.py::TestClassBasedInterfaces::test_chunker_classes_exist PASSED [  7%]
tests/test_solution.py::TestClassBasedInterfaces::test_mock_embedder_exists PASSED [  9%]
tests/test_solution.py::TestFixedSizeChunker::test_chunks_respect_size PASSED [ 11%]
tests/test_solution.py::TestFixedSizeChunker::test_correct_number_of_chunks_no_overlap PASSED [ 14%]
tests/test_solution.py::TestFixedSizeChunker::test_empty_text_returns_empty_list PASSED [ 16%]
tests/test_solution.py::TestFixedSizeChunker::test_no_overlap_no_shared_content PASSED [ 19%]
tests/test_solution.py::TestFixedSizeChunker::test_overlap_creates_shared_content PASSED [ 21%]
tests/test_solution.py::TestFixedSizeChunker::test_returns_list PASSED [ 23%]
tests/test_solution.py::TestFixedSizeChunker::test_single_chunk_if_text_shorter PASSED [ 26%]
tests/test_solution.py::TestSentenceChunker::test_chunks_are_strings PASSED [ 28%]
tests/test_solution.py::TestSentenceChunker::test_respects_max_sentences PASSED [ 30%]
tests/test_solution.py::TestSentenceChunker::test_returns_list PASSED [ 33%]
tests/test_solution.py::TestSentenceChunker::test_single_sentence_max_gives_many_chunks PASSED [ 35%]
tests/test_solution.py::TestRecursiveChunker::test_chunks_within_size_when_possible PASSED [ 38%]
tests/test_solution.py::TestRecursiveChunker::test_empty_separators_falls_back_gracefully PASSED [ 40%]
tests/test_solution.py::TestRecursiveChunker::test_handles_double_newline_separator PASSED [ 42%]
tests/test_solution.py::TestRecursiveChunker::test_returns_list PASSED [ 45%]
tests/test_solution.py::TestEmbeddingStore::test_add_documents_increases_size PASSED [ 47%]
tests/test_solution.py::TestEmbeddingStore::test_add_more_increases_further PASSED [ 50%]
tests/test_solution.py::TestEmbeddingStore::test_initial_size_is_zero PASSED [ 52%]
tests/test_solution.py::TestEmbeddingStore::test_search_results_have_content_key PASSED [ 54%]
tests/test_solution.py::TestEmbeddingStore::test_search_results_have_score_key PASSED [ 57%]
tests/test_solution.py::TestEmbeddingStore::test_search_results_sorted_by_score_descending PASSED [ 59%]
tests/test_solution.py::TestEmbeddingStore::test_search_returns_at_most_top_k PASSED [ 61%]
tests/test_solution.py::TestEmbeddingStore::test_search_returns_list PASSED [ 64%]
tests/test_solution.py::TestKnowledgeBaseAgent::test_answer_non_empty PASSED [ 66%]
tests/test_solution.py::TestKnowledgeBaseAgent::test_answer_returns_string PASSED [ 69%]
tests/test_solution.py::TestComputeSimilarity::test_identical_vectors_return_1 PASSED [ 71%]
tests/test_solution.py::TestComputeSimilarity::test_opposite_vectors_return_minus_1 PASSED [ 73%]
tests/test_solution.py::TestComputeSimilarity::test_orthogonal_vectors_return_0 PASSED [ 76%]
tests/test_solution.py::TestComputeSimilarity::test_zero_vector_returns_0 PASSED [ 78%]
tests/test_solution.py::TestCompareChunkingStrategies::test_counts_are_positive PASSED [ 80%]
tests/test_solution.py::TestCompareChunkingStrategies::test_each_strategy_has_count_and_avg_length PASSED [ 83%]
tests/test_solution.py::TestCompareChunkingStrategies::test_returns_three_strategies PASSED [ 85%]
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_filter_by_department PASSED [ 88%]
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_no_filter_returns_all_candidates PASSED [ 90%]
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_returns_at_most_top_k PASSED [ 92%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_reduces_collection_size PASSED [ 95%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_returns_false_for_nonexistent_doc PASSED [ 97%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_returns_true_for_existing_doc PASSED [100%]
============================== 42 passed in 0.14s ==============================
```

**Số lượng bài test vượt qua (pass):** 42 / 42

---

## 4. Dự đoán độ tương tự (Similarity Predictions) — Cá nhân (5 điểm)

| Cặp | Câu A | Câu B | Dự đoán | Điểm thực tế | Đúng? |
|------|-----------|-----------|---------|--------------|-------|
| 1 | "Chính sách đổi trả hàng hóa" | "Quy định hoàn trả sản phẩm" | cao | -0.1285 | Sai |
| 2 | "Chính sách đổi trả hàng hóa" | "Thời tiết hôm nay nắng đẹp" | thấp | -0.0347 | Đúng |
| 3 | "Giao hàng miễn phí cho đơn trên 500k" | "Miễn phí vận chuyển đơn hàng lớn" | cao | 0.0143 | Sai |
| 4 | "Python là ngôn ngữ lập trình bậc cao" | "Rắn python sống ở vùng nhiệt đới" | thấp | 0.0891 | Đúng |
| 5 | "Người bán cần xác minh danh tính" | "Người bán cần xác minh danh tính" | cao | 1.0000 | Đúng |

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn ý nghĩa?**
> Cặp 1 bất ngờ nhất — hai câu gần nghĩa ("đổi trả" vs "hoàn trả") nhưng mock embedder cho điểm âm (-0.1285). Điều này minh chứng rõ ràng rằng mock embedder sinh vector từ MD5 hash nên hoàn toàn không mang thông tin ngữ nghĩa. Với embedder thật (sentence-transformers), cặp 1 sẽ cho điểm rất cao vì hai câu đồng nghĩa. Bài học: chất lượng embedding quyết định hoàn toàn hiệu quả retrieval.

---

## 5. Kết quả truy xuất của tôi (Competition Results) — Cá nhân (10 điểm)

Chạy **5 câu hỏi đánh giá của nhóm** trên mã nguồn cá nhân của bạn trong gói `src`. **5 câu hỏi này phải trùng với các thành viên cùng nhóm** (xem `REPORT_NHOM.md`).

| # | Câu hỏi (Query) | Top-1 Chunk truy xuất được (tóm tắt) | Điểm Score | Có liên quan không? (Relevant) | Câu trả lời của Agent (tóm tắt) |
|---|-------|--------------------------------|-------|-----------|------------------------|
| 1 | Chính sách đổi trả hàng như thế nào? | "Người bán có trách nhiệm phản hồi theo quy trình của sàn..." | 0.189 | Có | Dựa trên ngữ cảnh: người mua gửi yêu cầu, người bán phản hồi |
| 2 | Người bán cần điều kiện gì để đăng bán? | "Người bán chịu trách nhiệm cung cấp thông tin sản phẩm chính xác..." | 0.149 | Có | Cần cung cấp giá, mô tả, tình trạng hàng chính xác |
| 3 | Hàng bị lỗi do nhà sản xuất thì xử lý ra sao? | "Người bán có trách nhiệm phản hồi theo quy trình..." | 0.189 | Một phần | Context có đề cập hàng lỗi nhưng chunk chứa thông tin chính không ở top-1 |
| 4 | Sản phẩm nào bị cấm đăng bán? | "Sản phẩm bị hạn chế hoặc bị cấm không được đăng bán" | 0.149 | Có | Sản phẩm bị hạn chế/cấm không được đăng |
| 5 | Thời hạn đổi trả là bao lâu? | "Người mua cần gửi yêu cầu đổi trả trong thời hạn..." | 0.113 | Có | Trong thời hạn được nêu trên trang sản phẩm |

**Bao nhiêu câu hỏi trả về chunk có liên quan trong top-3?** 5 / 5

**Điều hay nhất tôi học được từ thành viên khác / nhóm khác (qua demo):**
> (Phần này sẽ được bổ sung sau khi hoàn thành buổi demo nhóm — so sánh chiến lược chunking giữa các thành viên để thấy tác động của chunk_size, separator, và metadata filter lên chất lượng retrieval.)

---

## Tự Đánh Giá (Phần Cá Nhân)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Khởi động (Warm-up) | 5 / 5 |
| Hướng tiếp cận của tôi (My Approach) | 10 / 10 |
| Hoàn thiện code (Core Implementation — tests) | 30 / 30 |
| Dự đoán độ tương tự (Similarity Predictions) | 4 / 5 |
| Kết quả truy xuất của tôi (Competition Results) | 8 / 10 |
| **Tổng phần cá nhân** | **57 / 60** |
