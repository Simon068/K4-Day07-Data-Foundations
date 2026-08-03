"""Role 3 benchmark: sentence-based chunking + 5-question retrieval benchmark.

Run:
    python scripts/role3_benchmark.py

This script uses the local `src` package (student solution) and the mock
embedder to avoid external API calls.
"""
from __future__ import annotations

import json
import os
import sys

# Ensure project root is on sys.path so `src` package is importable when running script
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from src import Document, EmbeddingStore, SentenceChunker, _mock_embed


def build_docs_from_text(text: str, max_sentences: int = 1) -> list[Document]:
    chunker = SentenceChunker(max_sentences_per_chunk=max_sentences)
    chunks = chunker.chunk(text)
    docs = [Document(id=f"chunk_{i}", content=chunk, metadata={"source": "role3_benchmark"}) for i, chunk in enumerate(chunks)]
    return docs


def main() -> None:
    # A multi-topic text to exercise sentence chunking
    long_text = (
        "The quick brown fox jumps over the lazy dog. "
        "A fox is a small omnivorous mammal. "
        "Dogs are loyal companions and working animals. "
        "Brown bears live in forests across the northern hemisphere. "
        "Jumping is a physical activity that requires leg strength. "
        "Machine learning uses algorithms to learn from data. "
        "Vector databases store embeddings for similarity search. "
        "Python is a high-level programming language. "
    )

    docs = build_docs_from_text(long_text, max_sentences=1)

    store = EmbeddingStore(collection_name="role3_kb", embedding_fn=_mock_embed)
    store.add_documents(docs)

    queries = [
        "What is Python?",
        "Where do brown bears live?",
        "How does vector search work?",
        "What animals are loyal companions?",
        "What is machine learning?",
    ]

    benchmark_results = {}
    for q in queries:
        hits = store.search(q, top_k=3)
        benchmark_results[q] = hits
        print(f"\nQuery: {q}")
        for i, h in enumerate(hits, start=1):
            content_preview = h['content'][:200].replace('\n', ' ')
            print(f"Top {i}: score={h['score']:.4f} content='{content_preview}' metadata={h.get('metadata')}")

    with open("scripts/role3_results.json", "w", encoding="utf-8") as fh:
        json.dump(benchmark_results, fh, ensure_ascii=False, indent=2)

    print("\nBenchmark complete. Results saved to scripts/role3_results.json")


if __name__ == "__main__":
    main()
