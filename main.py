from __future__ import annotations

import os
import runpy
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def _find_demo_entrypoint() -> Path | None:
    for child in sorted(PROJECT_ROOT.iterdir()):
        if child.is_dir() and (child / "main.py").exists():
            return child / "main.py"
    return None


def _run_smoke_demo() -> None:
    from src import Document, EmbeddingStore, KnowledgeBaseAgent, _mock_embed

    store = EmbeddingStore(collection_name="demo", embedding_fn=_mock_embed)
    docs = [
        Document(id="d1", content="Python is a high-level programming language.", metadata={}),
        Document(id="d2", content="Vector databases store embeddings for similarity search.", metadata={}),
    ]
    store.add_documents(docs)

    agent = KnowledgeBaseAgent(store=store, llm_fn=lambda prompt: "Answer based on context.")
    answer = agent.answer("What is Python?")

    print("Smoke demo OK")
    print(f"Answer: {answer}")
    print(f"Store size: {store.get_collection_size()}")


def main() -> None:
    entrypoint = _find_demo_entrypoint()
    if entrypoint is not None:
        os.chdir(entrypoint.parent)
        runpy.run_path(str(entrypoint), run_name="__main__")
        return

    _run_smoke_demo()


if __name__ == "__main__":
    main()
