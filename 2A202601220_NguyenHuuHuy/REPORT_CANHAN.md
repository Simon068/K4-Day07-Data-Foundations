# Báo Cáo Cá Nhân — Lab 7: Embedding & Vector Store

**Họ tên:** Nguyễn Hữu Huy
**MSSV:** 2A20261220
**Nhóm:** [Tên nhóm]
**Ngày:** 2026-08-03

> **Nộp 1 bản / sinh viên.** Phần nhóm (lựa chọn tài liệu, thiết kế chiến lược, bộ câu hỏi đánh giá, demo) nộp chung 1 bản trong `REPORT_NHOM.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần cá nhân: 60** = Khởi động (5) + Hướng tiếp cận (10) + Hoàn thiện code (30) + Dự đoán độ tương tự (5) + Kết quả truy xuất của tôi (10).

---

## 1. Khởi động (Warm-up) — Cá nhân (5 điểm)

### Độ tương tự Cosine (Cosine Similarity) (Bài tập 1.1)

**Độ tương tự cosine cao (High cosine similarity) nghĩa là gì?**
> Hai vector embedding chỉ về gần như cùng một hướng trong không gian nhiều chiều, nghĩa là hai đoạn văn bản mang ý nghĩa/ngữ cảnh gần giống nhau — dù cách diễn đạt (từ ngữ, độ dài câu) có thể khác nhau.

**Ví dụ có độ tương tự CAO:**
- Câu A: "Chính sách đổi trả cho phép hoàn tiền trong 30 ngày."
- Câu B: "Khách hàng có thể được hoàn tiền nếu đổi trả sản phẩm trong vòng 30 ngày kể từ ngày mua."
- Tại sao tương đồng: Hai câu diễn đạt khác nhau nhưng cùng nói về một sự kiện ngữ nghĩa (điều kiện + thời hạn hoàn tiền khi đổi trả), nên vector embedding của chúng có hướng gần nhau.

**Ví dụ có độ tương tự THẤP:**
- Câu A: "Chính sách đổi trả cho phép hoàn tiền trong 30 ngày."
- Câu B: "Hôm nay thời tiết rất đẹp và nắng ấm."
- Tại sao khác: Hai câu thuộc hai chủ đề hoàn toàn không liên quan (chính sách thương mại vs. thời tiết), không chia sẻ khái niệm hay ngữ cảnh chung, nên vector của chúng có hướng gần như độc lập với nhau.

**Tại sao độ tương tự cosine (cosine similarity) được ưu tiên hơn khoảng cách Euclid (Euclidean distance) cho text embeddings?**
> Cosine similarity chỉ quan tâm đến *hướng* của vector (tức nội dung/ý nghĩa) chứ không bị ảnh hưởng bởi *độ lớn* (magnitude) của vector — thứ thường tương quan với độ dài văn bản chứ không phải ý nghĩa. Khoảng cách Euclid lại nhạy với độ lớn, nên hai đoạn văn bản đồng nghĩa nhưng độ dài khác nhau có thể bị coi là "xa nhau" dù thực chất cùng ý.

### Bài toán tính toán Chunking (Bài tập 1.2)

**Tài liệu 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**
> *Trình bày phép tính:*
> số lượng chunk = làm_tròn_lên((10000 − 50) / (500 − 50)) = làm_tròn_lên(9950 / 450) = làm_tròn_lên(22.11) = **23**
> *Đáp án:* **23 chunks** — đã kiểm chứng thực nghiệm bằng `FixedSizeChunker(chunk_size=500, overlap=50).chunk("a"*10000)`, trả về đúng 23 phần tử.

**Nếu độ chồng chéo (overlap) tăng lên 100, số lượng chunk thay đổi thế nào? Tại sao muốn độ chồng chéo nhiều hơn?**
> làm_tròn_lên((10000 − 100) / (500 − 100)) = làm_tròn_lên(9900 / 400) = làm_tròn_lên(24.75) = **25 chunks** (kiểm chứng thực nghiệm cũng cho ra 25). Overlap lớn hơn làm bước trượt (step = chunk_size − overlap) nhỏ đi nên số chunk tăng lên; đổi lại, mỗi ranh giới chunk được "đệm" thêm ngữ cảnh từ chunk liền kề, giảm nguy cơ một câu/ý quan trọng bị cắt đúng vào điểm nối giữa hai chunk và mất mát thông tin khi truy xuất.

---

## 2. Hướng tiếp cận của tôi (My Approach) — Cá nhân (10 điểm)

Giải thích cách tiếp cận của bạn khi lập trình (implement) các phần chính trong gói `src`.

### Các hàm chia nhỏ (Chunking Functions)

**`SentenceChunker.chunk`** — hướng tiếp cận:
> Dùng regex `(?<=[.!?]) |(?<=\.)\n` để tách câu: lookbehind đảm bảo dấu kết câu (`.`, `!`, `?`) vẫn ở lại cuối câu trước, còn ký tự phân tách thật sự bị loại bỏ khỏi kết quả (khoảng trắng sau `.`/`!`/`?`, hoặc dòng mới sau `.`). Sau khi tách, tôi lọc bỏ chuỗi rỗng và `strip()` từng câu, rồi gom `max_sentences_per_chunk` câu liên tiếp thành một chunk bằng cách cắt lát danh sách theo bước nhảy đó. Edge case: văn bản rỗng trả về `[]`; văn bản không có dấu kết câu nào thì toàn bộ được coi là một "câu" duy nhất.

**`RecursiveChunker.chunk` / `_split`** — hướng tiếp cận:
> `_split` thử lần lượt các separator theo thứ tự ưu tiên (`\n\n` → `\n` → `. ` → ` ` → `""`). Base case: nếu `current_text` đã ≤ `chunk_size` thì trả về `[current_text]`; nếu hết separator mà vẫn còn dư thì cắt cứng theo `chunk_size`. Với mỗi separator, tôi tách văn bản thành các phần; nếu phần nào vẫn còn quá dài thì đệ quy tiếp với separator kế tiếp trong danh sách. Điểm khác biệt so với việc chỉ tách rồi giữ nguyên: sau khi mọi phần đã đủ nhỏ, tôi **gộp lại (re-merge)** các phần liền kề (nối bằng chính separator đã dùng) cho tới khi gần chạm `chunk_size`, để chunk giữ được nhiều ngữ cảnh nhất có thể thay vì tạo ra rất nhiều mảnh nhỏ vụn.

### Lớp EmbeddingStore

**`add_documents` + `search`** — hướng tiếp cận:
> Mỗi `Document` được nhúng qua `embedding_fn` rồi lưu thành một record `{id, content, metadata, embedding}` trong danh sách `self._store` (đồng thời mirror sang collection ChromaDB nếu thư viện này có sẵn, nhưng đây không phải đường đi bắt buộc để bài test chạy được). `search()` nhúng câu truy vấn rồi tính **tích vô hướng (dot product)** giữa vector truy vấn và từng vector đã lưu — vì các embedder (mock/local/OpenAI) đều trả về vector đã chuẩn hóa (norm = 1) nên dot product ở đây tương đương cosine similarity — sau đó sắp xếp giảm dần theo điểm và cắt lấy `top_k`.

**`search_with_filter` + `delete_document`** — hướng tiếp cận:
> Lọc **trước**: tôi duyệt `self._store`, chỉ giữ lại các record mà mọi cặp `key: value` trong `metadata_filter` đều khớp với `record["metadata"]`, rồi mới gọi lại đúng hàm tính similarity (`_search_records`) trên tập con đã lọc — nhờ vậy `top_k` luôn có ý nghĩa trong phạm vi đã lọc thay vì lọc sau khi đã chọn top_k trên toàn bộ. `delete_document(doc_id)` xóa mọi record có `metadata["doc_id"] == doc_id` (mỗi record được gán mặc định `doc_id` bằng chính `id` của nó nếu không có sẵn, nên áp dụng được cho cả Document gốc lẫn các chunk do `ingest.py` tạo ra) và trả về `True` chỉ khi thực sự có record bị xóa.

### Tác tử KnowledgeBaseAgent

**`answer`** — hướng tiếp cận:
> `answer()` gọi `store.search(question, top_k)` để lấy các chunk liên quan, ghép nội dung các chunk lại thành một khối ngữ cảnh có đánh số `[1] ... [2] ...`, rồi chèn khối này vào một prompt yêu cầu LLM **chỉ được trả lời dựa trên ngữ cảnh** (và nói rõ nếu ngữ cảnh không đủ thông tin) trước khi gọi `llm_fn(prompt)`. Cách đánh số giúp truy vết được câu trả lời dựa trên chunk nào (grounding), phục vụ trực tiếp cho việc phân tích "Grounding Quality" ở Phần 3 của lab.

---

## 3. Hoàn thiện code (Core Implementation) — Cá nhân (30 điểm)

Vượt qua bộ kiểm thử là điều kiện tính điểm phần này.

### Kết Quả Kiểm Thử (Test Results)

```
============================= test session starts =============================
platform win32 -- Python 3.14.5, pytest-9.1.1, pluggy-1.6.0
collected 42 items

tests/test_solution.py .......................................... [100%]

============================= 42 passed in 0.08s ==============================
```

**Số lượng bài test vượt qua (pass):** 42 / 42

---

## 4. Dự đoán độ tương tự (Similarity Predictions) — Cá nhân (5 điểm)

> Dùng `MockEmbedder` (mặc định của lab, `_mock_embed`) qua `compute_similarity(embed(a), embed(b))`. Ngưỡng quy ước để đọc bảng: điểm ≥ 0.15 → "cao", < 0.15 → "thấp".

| Cặp | Câu A | Câu B | Dự đoán | Điểm thực tế | Đúng? |
|------|-----------|-----------|---------|--------------|-------|
| 1 | "Con mèo đang ngủ trên ghế sofa." | "Chú mèo nằm ngủ trên chiếc ghế dài." (gần như đồng nghĩa) | cao | -0.1548 | Sai |
| 2 | "Chính sách đổi trả cho phép hoàn tiền trong 30 ngày." | "Khách hàng được hoàn tiền nếu đổi trả trong vòng 30 ngày." (diễn giải lại) | cao | 0.0256 | Sai |
| 3 | "Con mèo đang ngủ trên ghế sofa." | "Chính phủ vừa công bố chính sách thuế mới." (chủ đề khác hẳn) | thấp | 0.2246 | Sai |
| 4 | "Người bán phải xác nhận đơn hàng trong 24 giờ." | "Hôm nay trời nắng đẹp và rất trong xanh." (chủ đề khác hẳn) | thấp | 0.0309 | Đúng |
| 5 | "Python is a high-level programming language." | "Python là một ngôn ngữ lập trình bậc cao." (cùng ý, khác ngôn ngữ) | cao | 0.1246 | Sai (sát ngưỡng) |

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn ý nghĩa?**
> Bất ngờ nhất là cặp 1: hai câu gần như đồng nghĩa lại có điểm **âm** (-0.1548), còn cặp 3 (hai câu hoàn toàn khác chủ đề) lại có điểm cao nhất trong cả 5 cặp (0.2246) — chỉ 1/5 dự đoán đúng. Điều này khớp với cảnh báo trong README: `MockEmbedder` chỉ là hàm băm (MD5) xác định theo chuỗi ký tự để phục vụ unit test có thể lặp lại, chứ không được huấn luyện để biểu diễn ngữ nghĩa — hai chuỗi khác nhau (dù đồng nghĩa) tạo ra hai vector gần như ngẫu nhiên, không liên quan gì đến ý nghĩa thật. Điều này cho thấy "có embedding" không đồng nghĩa với "có ngữ nghĩa" — chất lượng truy xuất phụ thuộc hoàn toàn vào việc embedder có thực sự được huấn luyện trên dữ liệu ngôn ngữ hay không (đây là lý do Giai đoạn 2 của lab bắt buộc dùng `EMBEDDING_PROVIDER=local` thay vì mock khi so sánh chiến lược retrieval).

---

## 5. Kết quả truy xuất của tôi (Competition Results) — Cá nhân (10 điểm)

Chạy **5 câu hỏi đánh giá của nhóm** trên mã nguồn cá nhân của bạn trong gói `src`. **5 câu hỏi này phải trùng với các thành viên cùng nhóm** (xem `REPORT_NHOM.md`).

> **⚠️ Chưa hoàn thành — đang chờ nhóm.** Phần này cần chạy đúng **5 câu hỏi đánh giá đã được cả nhóm thống nhất** (bảng ở `REPORT_NHOM.md` — Phần 3), trên bộ tài liệu thật của nhóm (5-10 tài liệu công khai). Hiện `REPORT_NHOM.md` chưa được điền và `data/k4_ecommerce/` mới chỉ là dữ liệu khởi động (`.md` ghi rõ "Nhóm cần bổ sung nguồn chính sách công khai... trước khi viết gold answer" — chưa dùng để chấm benchmark được). Pipeline cá nhân (`ingest.py` + `EmbeddingStore` + `KnowledgeBaseAgent`) đã chạy thử thành công với dữ liệu khởi động này (xem `main.py`), nhưng bảng dưới đây cần điền lại bằng **câu hỏi + tài liệu thật của nhóm** trước khi nộp.

| # | Câu hỏi (Query) | Top-1 Chunk truy xuất được (tóm tắt) | Điểm Score | Có liên quan không? (Relevant) | Câu trả lời của Agent (tóm tắt) |
|---|-------|--------------------------------|-------|-----------|------------------------|
| 1 | | | | | |
| 2 | | | | | |
| 3 | | | | | |
| 4 | | | | | |
| 5 | | | | | |

**Bao nhiêu câu hỏi trả về chunk có liên quan trong top-3?** __ / 5 *(chờ bộ câu hỏi + dữ liệu chính thức của nhóm)*

**Điều hay nhất tôi học được từ thành viên khác / nhóm khác (qua demo):**
> *Chờ buổi demo với nhóm — điền sau khi so sánh chiến lược chunking/metadata với các thành viên khác (Bài tập 3.4-3.5).*

---

## Tự Đánh Giá (Phần Cá Nhân)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Khởi động (Warm-up) | 5 / 5 |
| Hướng tiếp cận của tôi (My Approach) | 10 / 10 |
| Hoàn thiện code (Core Implementation — tests) | 30 / 30 |
| Dự đoán độ tương tự (Similarity Predictions) | 5 / 5 |
| Kết quả truy xuất của tôi (Competition Results) | 0 / 10 *(chờ bộ câu hỏi + dữ liệu nhóm — xem Phần 5)* |
| **Tổng phần cá nhân** | **50 / 60** *(tạm tính, sẽ đạt 60/60 sau khi hoàn thành Phần 5)* |
