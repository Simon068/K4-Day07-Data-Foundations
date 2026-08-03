# Báo Cáo Cá Nhân — Lab 7: Embedding & Vector Store

**Họ tên:** Trần Tuấn Linh
**Nhóm:** [Tên nhóm]
**Ngày:** 03/08/2026

> **Nộp 1 bản / sinh viên.** Phần nhóm (lựa chọn tài liệu, thiết kế chiến lược, bộ câu hỏi đánh giá, demo) nộp chung 1 bản trong `REPORT_NHOM.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần cá nhân: 60** = Khởi động (5) + Hướng tiếp cận (10) + Hoàn thiện code (30) + Dự đoán độ tương tự (5) + Kết quả truy xuất của tôi (10).

---

## 1. Khởi động (Warm-up) — Cá nhân (5 điểm)

### Độ tương tự Cosine (Cosine Similarity) (Bài tập 1.1)

**Độ tương tự cosine cao (High cosine similarity) nghĩa là gì?**

> *Khi hai đoạn văn bản có độ tương tự cosine cao, điều đó có nghĩa là chúng đang nói về cùng một nội dung hoặc cùng một ý, dù cách dùng từ hay độ dài câu có khác nhau đến đâu. Vector embedding của hai câu này sẽ chỉ về cùng một hướng trong không gian, cho thấy mô hình nắm bắt được sự tương đồng về mặt ý nghĩa chứ không phải về mặt câu chữ.*

**Ví dụ có độ tương tự CAO:**

- Câu A: khách hàng có thể đổi trả sản phẩm trong vòng 7 ngày kể từ ngày nhận hàng.
- Câu B: bạn được hoàn trả hàng hóa nếu yêu cầu trong 7 ngày sau khi nhận.
- Tại sao tương đồng: Hai câu này dùng từ ngữ không giống nhau hoàn toàn, nhưng lại truyền tải cùng một thông tin về chính sách đổi trả trong 7 ngày, nên embedding sẽ xếp chúng gần nhau về mặt ý nghĩa.

**Ví dụ có độ tương tự THẤP:**

- Câu A: khách hàng có thể đổi trả sản phẩm trong vòng 7 ngày.
- Câu B: cửa hàng mở cửa từ 8 giờ sáng đến 9 giờ tối các ngày trong tuần.
- Tại sao khác: Hai câu này bàn về hai chủ đề khác hẳn nhau, một bên nói về chính sách đổi trả còn một bên nói về giờ mở cửa, nên không có điểm chung nào về nội dung, và vector embedding của chúng sẽ chỉ theo những hướng khác biệt rõ rệt.

**Tại sao độ tương tự cosine (cosine similarity) được ưu tiên hơn khoảng cách Euclid (Euclidean distance) cho text embeddings?**

> *Cosine similarity chỉ quan tâm đến hướng của vector, tức là nội dung và ý nghĩa của văn bản, mà bỏ qua độ dài của vector. Trong khi đó độ dài vector embedding lại dễ bị ảnh hưởng bởi những yếu tố không thật sự liên quan đến ý nghĩa như câu dài hay ngắn, số lượng từ nhiều hay ít. Vì vậy hai câu có độ dài khác nhau nhưng cùng một ý vẫn cho ra độ tương tự cosine cao, còn nếu dùng khoảng cách Euclid thì kết quả có thể bị lệch chỉ vì độ dài vector khác nhau, dù nội dung thực chất vẫn tương đồng.*

### Bài toán tính toán Chunking (Bài tập 1.2)

**Tài liệu 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**

> *Trình bày phép tính: số lượng chunk = làm tròn lên của (độ dài tài liệu - độ chồng chéo) / (kích thước chunk - độ chồng chéo)*
> *Đáp án: ta lấy (10000 - 50) chia cho (500 - 50), tức là 9950 chia cho 450, ra kết quả xấp xỉ 22,11. Làm tròn lên thì ta được 23 chunks.*

**Nếu độ chồng chéo (overlap) tăng lên 100, số lượng chunk thay đổi thế nào? Tại sao muốn độ chồng chéo nhiều hơn?**

> *Khi overlap tăng lên 100, phép tính trở thành (10000 trừ 100) chia cho (500 trừ 100), tức 9900 chia cho 400, ra khoảng 24,75, làm tròn lên là 25 chunks, nghĩa là số lượng chunk tăng lên so với trước. Người ta muốn tăng độ chồng chéo vì mỗi chunk sẽ giữ lại được nhiều ngữ cảnh của chunk liền trước, giúp tránh tình trạng một ý quan trọng bị cắt đứt ngay tại ranh giới giữa hai chunk, dù điều đó phải đánh đổi bằng việc có nhiều chunk hơn và tốn thêm dung lượng lưu trữ.*

---

## 2. Hướng tiếp cận của tôi (My Approach) — Cá nhân (10 điểm)

Giải thích cách tiếp cận của bạn khi lập trình (implement) các phần chính trong gói `src`.

### Các hàm chia nhỏ (Chunking Functions)

**`SentenceChunker.chunk`** — hướng tiếp cận:

> *Mình dùng regex `(?<=[.!?])\s+` để tách câu: đây là kiểu "lookbehind", nghĩa là chỉ cắt tại vị trí ngay sau một dấu `.`, `!` hoặc `?`, khi theo sau nó là một hoặc nhiều khoảng trắng. Vì `\s` bao gồm cả ký tự xuống dòng, nên một pattern duy nhất này tự động xử lý được cả 4 trường hợp đề bài yêu cầu (`". "`, `"! "`, `"? "` và `".\n"`) mà không cần viết 4 điều kiện riêng. Sau khi tách được danh sách câu, mình lọc bỏ các câu rỗng (do khoảng trắng thừa ở đầu/cuối văn bản), rồi gom từng nhóm `max_sentences_per_chunk` câu liên tiếp lại thành một chunk bằng cách nối chúng với dấu cách. Trường hợp ngoại lệ mình xử lý: văn bản rỗng hoặc chỉ toàn khoảng trắng thì trả về `[]` ngay từ đầu, tránh việc xử lý thêm không cần thiết.*

**`RecursiveChunker.chunk` / `_split`** — hướng tiếp cận:

> *Thuật toán hoạt động theo kiểu "thử dấu phân cách ưu tiên cao trước, thất bại thì lùi xuống dấu thấp hơn". Với mỗi đoạn văn bản, `_split` sẽ kiểm tra base case đầu tiên: nếu đoạn đó đã đủ ngắn (`len(text) <= chunk_size`) thì trả về luôn, không cần tách thêm. Nếu chưa đủ ngắn, hàm lấy dấu phân cách đầu tiên còn lại (ví dụ `"\n\n"`), tách văn bản theo dấu đó, rồi gộp các mảnh nhỏ lại với nhau cho đến khi gần đầy `chunk_size` (tránh tạo ra quá nhiều chunk vụn). Nếu một mảnh vẫn còn dài hơn `chunk_size` sau khi tách, hàm gọi đệ quy chính nó với danh sách dấu phân cách còn lại (bỏ dấu vừa dùng). Base case thứ hai là khi hết dấu phân cách để thử (`remaining_separators` rỗng) hoặc gặp dấu phân cách rỗng `""`, lúc đó hàm cắt cứng theo số ký tự để đảm bảo luôn trả về kết quả, không bao giờ chạy đệ quy vô hạn.*

### Lớp EmbeddingStore

**`add_documents` + `search`** — hướng tiếp cận:

> *Mình chọn cách lưu trữ đơn giản và nhất quán: mọi document/chunk sau khi được `_make_record` xử lý (gọi `embedding_fn` để nhúng nội dung, đóng gói lại thành dict gồm `id`, `content`, `embedding`, `metadata`) đều được append vào một list `self._store` trong bộ nhớ — đây là nguồn dữ liệu chính, dùng cho cả `search`, `search_with_filter` và `delete_document`. Nếu thư viện `chromadb` có sẵn trong môi trường, mình ghi thêm (mirror) dữ liệu đó vào collection ChromaDB, nhưng bọc trong `try/except` để việc này không bao giờ làm hỏng luồng chính nếu ChromaDB gặp lỗi. Khi tìm kiếm (`search`), mình nhúng câu truy vấn thành vector, rồi tính tích vô hướng (dot product) giữa vector truy vấn và vector của từng bản ghi đã lưu (dùng hàm `_dot` có sẵn), sắp xếp giảm dần theo điểm số và trả về `top_k` kết quả đầu tiên.*

**`search_with_filter` + `delete_document`** — hướng tiếp cận:

> *Với `search_with_filter`, mình lọc **trước** khi tìm kiếm: nếu có `metadata_filter`, mình chỉ giữ lại những bản ghi mà toàn bộ cặp key-value trong filter đều khớp với metadata của bản ghi đó (`all(record["metadata"].get(key) == value ...)`), sau đó mới chạy lại đúng logic tính điểm tương tự như hàm `search` trên tập đã lọc. Cách này đảm bảo không lãng phí công tính điểm cho những bản ghi chắc chắn không thỏa điều kiện lọc. Với `delete_document`, mình xóa bằng cách giữ lại (dùng list comprehension) chỉ những bản ghi **không thuộc** về `doc_id` cần xóa — một bản ghi được coi là "thuộc về" `doc_id` nếu `record["id"]` trùng khớp trực tiếp với `doc_id` được truyền vào, **hoặc** nếu `metadata["doc_id"]` của nó khớp. Cách kiểm tra hai lớp này giúp hàm hoạt động đúng cả với trường hợp đơn giản (mỗi document là một bản ghi độc lập, xóa theo `id`) lẫn trường hợp thực tế trong dự án (một tài liệu dài được chia thành nhiều chunk, mỗi chunk có `id` riêng nhưng cùng chia sẻ `doc_id` trong metadata).*

### Tác tử KnowledgeBaseAgent

**`answer`** — hướng tiếp cận:

> Hàm `answer` làm đúng 3 bước của mô hình RAG. Đầu tiên, gọi `self._store.search(question, top_k=top_k)` để lấy về các chunk liên quan nhất. Sau đó, mình ghép nội dung các chunk này thành một đoạn ngữ cảnh, mỗi chunk được đánh số rõ ràng dạng `[Nguồn 1]`, `[Nguồn 2]`... để LLM (và cả người đọc log) dễ biết câu trả lời dựa trên nguồn nào; nếu không tìm được chunk nào, mình thay ngữ cảnh bằng một câu thông báo rõ ràng thay vì để trống. Cuối cùng, mình xây dựng prompt gồm: chỉ dẫn cho LLM chỉ được trả lời dựa trên ngữ cảnh cung cấp (và phải nói rõ nếu ngữ cảnh không đủ, tránh bịa thông tin), phần ngữ cảnh đã ghép, và câu hỏi gốc — rồi gọi `self._llm_fn(prompt)` để lấy kết quả trả về.

## 3. Hoàn thiện code (Core Implementation) — Cá nhân (30 điểm)

Vượt qua bộ kiểm thử là điều kiện tính điểm phần này.

### Kết Quả Kiểm Thử (Test Results)

```
# Dán kết quả (output) của: pytest tests/ -v
============================== test session starts ==============================
platform win32 -- Python 3.11.9, pytest-9.1.1, pluggy-1.6.0 -- D:\Code\AI_Thuc_Chien\group\Day07_2A202601612_TranTuanLinh\.venv\Scripts\python.exe
cachedir: .pytest_cache
rootdir: D:\Code\AI_Thuc_Chien\group\Day07_2A202601612_TranTuanLinh
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
tests/test_solution.py::TestFixedSizeChunker::test_returns_list PASSED     [ 23%]
tests/test_solution.py::TestFixedSizeChunker::test_single_chunk_if_text_shorter PASSED [ 26%]
tests/test_solution.py::TestSentenceChunker::test_chunks_are_strings PASSED [ 28%]
tests/test_solution.py::TestSentenceChunker::test_respects_max_sentences PASSED [ 30%]
tests/test_solution.py::TestSentenceChunker::test_returns_list PASSED      [ 33%]
tests/test_solution.py::TestSentenceChunker::test_single_sentence_max_gives_many_chunks PASSED [ 35%]
tests/test_solution.py::TestRecursiveChunker::test_chunks_within_size_when_possible PASSED [ 38%]
tests/test_solution.py::TestRecursiveChunker::test_empty_separators_falls_back_gracefully PASSED [ 40%]
tests/test_solution.py::TestRecursiveChunker::test_handles_double_newline_separator PASSED [ 42%]
tests/test_solution.py::TestRecursiveChunker::test_returns_list PASSED     [ 45%]
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

============================== 42 passed in 0.13s ===============================
```

**Số lượng bài test vượt qua (pass):** 42 / 42

---

## 4. Dự đoán độ tương tự (Similarity Predictions) — Cá nhân (5 điểm)

| Cặp | Câu A | Câu B | Dự đoán  | Điểm thực tế | Đúng? |
| ---- | ------ | ------ | ----------- | ---------------- | ------- |
| 1    |        |        | cao / thấp |                  |         |
| 2    |        |        | cao / thấp |                  |         |
| 3    |        |        | cao / thấp |                  |         |
| 4    |        |        | cao / thấp |                  |         |
| 5    |        |        | cao / thấp |                  |         |

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn ý nghĩa?**

> *Viết 2-3 câu:*

---

## 5. Kết quả truy xuất của tôi (Competition Results) — Cá nhân (10 điểm)

Chạy **5 câu hỏi đánh giá của nhóm** trên mã nguồn cá nhân của bạn trong gói `src`. **5 câu hỏi này phải trùng với các thành viên cùng nhóm** (xem `REPORT_NHOM.md`).

| # | Câu hỏi (Query) | Top-1 Chunk truy xuất được (tóm tắt) | Điểm Score | Có liên quan không? (Relevant) | Câu trả lời của Agent (tóm tắt) |
| - | ----------------- | ------------------------------------------ | ------------ | --------------------------------- | ------------------------------------- |
| 1 |                   |                                            |              |                                   |                                       |
| 2 |                   |                                            |              |                                   |                                       |
| 3 |                   |                                            |              |                                   |                                       |
| 4 |                   |                                            |              |                                   |                                       |
| 5 |                   |                                            |              |                                   |                                       |

**Bao nhiêu câu hỏi trả về chunk có liên quan trong top-3?** __ / 5

**Điều hay nhất tôi học được từ thành viên khác / nhóm khác (qua demo):**

> *Viết 2-3 câu:*

---

## Tự Đánh Giá (Phần Cá Nhân)

| Tiêu chí                                           | Điểm tự đánh giá |
| ---------------------------------------------------- | ---------------------- |
| Khởi động (Warm-up)                               | / 5                    |
| Hướng tiếp cận của tôi (My Approach)           | / 10                   |
| Hoàn thiện code (Core Implementation — tests)     | / 30                   |
| Dự đoán độ tương tự (Similarity Predictions) | / 5                    |
| Kết quả truy xuất của tôi (Competition Results) | / 10                   |
| **Tổng phần cá nhân**                      | **/ 60**         |
