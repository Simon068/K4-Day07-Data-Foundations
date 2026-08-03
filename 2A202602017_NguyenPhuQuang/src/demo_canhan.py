"""
Demo phần cá nhân — test thử toàn bộ tính năng đã implement.
Chạy: uv run python demo_canhan.py
"""
from src import (
    Document,
    FixedSizeChunker,
    SentenceChunker,
    RecursiveChunker,
    ChunkingStrategyComparator,
    compute_similarity,
    EmbeddingStore,
    KnowledgeBaseAgent,
    _mock_embed,
)

SAMPLE_TEXT = """Chính sách đổi trả hàng hóa của sàn thương mại điện tử. Người mua có quyền yêu cầu đổi trả trong vòng 7 ngày kể từ ngày nhận hàng. Sản phẩm phải còn nguyên tem, nhãn mác và chưa qua sử dụng. Trường hợp hàng bị lỗi do nhà sản xuất, người mua được hoàn tiền 100%. Người bán cần phản hồi yêu cầu đổi trả trong vòng 48 giờ. Nếu người bán không phản hồi, sàn sẽ tự động xử lý theo hướng có lợi cho người mua."""

print("=" * 60)
print("DEMO PHẦN CÁ NHÂN - LAB 7")
print("=" * 60)

# --- 1. Chunking ---
print("\n📦 1. CHUNKING STRATEGIES")
print("-" * 40)

print("\n[FixedSizeChunker] chunk_size=100, overlap=20:")
fc = FixedSizeChunker(chunk_size=100, overlap=20)
for i, c in enumerate(fc.chunk(SAMPLE_TEXT)):
    print(f"  Chunk {i}: ({len(c)} chars) {c[:60]}...")

print("\n[SentenceChunker] max_sentences_per_chunk=2:")
sc = SentenceChunker(max_sentences_per_chunk=2)
for i, c in enumerate(sc.chunk(SAMPLE_TEXT)):
    print(f"  Chunk {i}: {c[:80]}...")

print("\n[RecursiveChunker] chunk_size=150:")
rc = RecursiveChunker(chunk_size=150)
for i, c in enumerate(rc.chunk(SAMPLE_TEXT)):
    print(f"  Chunk {i}: ({len(c)} chars) {c[:80]}...")

# --- 2. ChunkingStrategyComparator ---
print("\n\n📊 2. CHUNKING STRATEGY COMPARATOR")
print("-" * 40)
comparator = ChunkingStrategyComparator()
result = comparator.compare(SAMPLE_TEXT, chunk_size=150)
for strategy, stats in result.items():
    print(f"  {strategy}: {stats['count']} chunks, avg_length={stats['avg_length']:.1f}")

# --- 3. Cosine Similarity ---
print("\n\n📐 3. COMPUTE_SIMILARITY (cosine)")
print("-" * 40)
vec_a = _mock_embed("Chính sách đổi trả hàng hóa")
vec_b = _mock_embed("Quy định hoàn trả sản phẩm")
vec_c = _mock_embed("Thời tiết hôm nay nắng đẹp")

sim_ab = compute_similarity(vec_a, vec_b)
sim_ac = compute_similarity(vec_a, vec_c)
sim_bc = compute_similarity(vec_b, vec_c)

print(f"  sim('đổi trả hàng hóa', 'hoàn trả sản phẩm') = {sim_ab:.4f}")
print(f"  sim('đổi trả hàng hóa', 'thời tiết nắng đẹp') = {sim_ac:.4f}")
print(f"  sim('hoàn trả sản phẩm', 'thời tiết nắng đẹp') = {sim_bc:.4f}")
print("  (Lưu ý: mock embedder cho điểm gần ngẫu nhiên, không phản ánh ngữ nghĩa)")

# Edge cases
print(f"  sim(zero_vec, any_vec) = {compute_similarity([0,0,0], [1,2,3])}")
print(f"  sim(same, same) = {compute_similarity([1,0,0], [1,0,0]):.4f}")
print(f"  sim(opposite) = {compute_similarity([1,0], [-1,0]):.4f}")

# --- 4. EmbeddingStore ---
print("\n\n🗄️  4. EMBEDDING STORE")
print("-" * 40)
store = EmbeddingStore(collection_name="demo", embedding_fn=_mock_embed)

docs = [
    Document(id="policy-returns", content="Người mua có quyền đổi trả trong 7 ngày.", metadata={"customer_role": "buyer", "category": "returns"}),
    Document(id="policy-shipping", content="Giao hàng miễn phí cho đơn trên 500k.", metadata={"customer_role": "buyer", "category": "shipping"}),
    Document(id="policy-seller", content="Người bán cần xác minh danh tính trước khi đăng bán.", metadata={"customer_role": "seller", "category": "listing"}),
    Document(id="policy-payment", content="Thanh toán qua ví điện tử hoặc thẻ ngân hàng.", metadata={"customer_role": "both", "category": "payment"}),
    Document(id="policy-privacy", content="Thông tin cá nhân được bảo mật theo quy định pháp luật.", metadata={"customer_role": "both", "category": "privacy"}),
]

store.add_documents(docs)
print(f"  Collection size sau add: {store.get_collection_size()}")

print("\n  [search] query='đổi trả hàng', top_k=3:")
results = store.search("đổi trả hàng", top_k=3)
for i, r in enumerate(results, 1):
    print(f"    {i}. score={r['score']:.4f} | {r['content'][:60]}")

print("\n  [search_with_filter] query='quy định', filter={customer_role: seller}:")
results = store.search_with_filter("quy định", top_k=3, metadata_filter={"customer_role": "seller"})
for i, r in enumerate(results, 1):
    print(f"    {i}. score={r['score']:.4f} | role={r['metadata']['customer_role']} | {r['content'][:50]}")

print("\n  [delete_document] xóa 'policy-returns':")
deleted = store.delete_document("policy-returns")
print(f"    Deleted: {deleted}, size sau xóa: {store.get_collection_size()}")
deleted_again = store.delete_document("policy-returns")
print(f"    Xóa lại lần 2: {deleted_again} (expected False)")

# --- 5. KnowledgeBaseAgent ---
print("\n\n🤖 5. KNOWLEDGE BASE AGENT (RAG)")
print("-" * 40)

def fake_llm(prompt: str) -> str:
    """Simulate LLM — trả về context nhận được để verify RAG hoạt động."""
    # Extract context portion
    if "Context:" in prompt and "Question:" in prompt:
        ctx_start = prompt.index("Context:") + len("Context:\n")
        ctx_end = prompt.index("\n\nQuestion:")
        context = prompt[ctx_start:ctx_end]
        return f"Dựa trên ngữ cảnh truy xuất được:\n{context[:200]}..."
    return "Không tìm thấy ngữ cảnh phù hợp."

agent = KnowledgeBaseAgent(store=store, llm_fn=fake_llm)
answer = agent.answer("Làm sao để thanh toán đơn hàng?")
print(f"  Q: Làm sao để thanh toán đơn hàng?")
print(f"  A: {answer[:200]}")

# --- 6. Full pipeline with ingest ---
print("\n\n🔄 6. FULL PIPELINE (ingest.py + data/k4_ecommerce)")
print("-" * 40)
from ingest import build_knowledge_base
kb = build_knowledge_base("data/k4_ecommerce", embedding_fn=_mock_embed)
print(f"  Loaded {kb.get_collection_size()} chunks from data/k4_ecommerce/")

results = kb.search("người bán cần làm gì khi đăng bán", top_k=2)
for i, r in enumerate(results, 1):
    print(f"  {i}. score={r['score']:.3f} | doc_id={r['metadata'].get('doc_id')}")
    print(f"     {r['content'][:100]}...")

print("\n" + "=" * 60)
print("✅ TẤT CẢ TÍNH NĂNG CÁ NHÂN HOẠT ĐỘNG BÌNH THƯỜNG!")
print("=" * 60)
