from typing import Callable

from .store import EmbeddingStore


class KnowledgeBaseAgent:
    """
    An agent that answers questions using a vector knowledge base.

    Retrieval-augmented generation (RAG) pattern:
        1. Retrieve top-k relevant chunks from the store.
        2. Build a prompt with the chunks as context.
        3. Call the LLM to generate an answer.
    """

    def __init__(self, store: EmbeddingStore, llm_fn: Callable[[str], str]) -> None:
        self.store = store
        self.llm_fn = llm_fn

    def answer(self, question: str, top_k: int = 3) -> str:
        retrieved_chunks = self.store.search(question, top_k=top_k)
        if retrieved_chunks:
            context = "\n\n".join(
                f"[{index}] {chunk['content']}" for index, chunk in enumerate(retrieved_chunks, start=1)
            )
        else:
            context = "No relevant context found."

        prompt = (
            f"Question: {question}\n\n"
            f"Use the following retrieved context to answer:\n{context}\n\n"
            "Answer briefly and clearly."
        )
        return self.llm_fn(prompt)
