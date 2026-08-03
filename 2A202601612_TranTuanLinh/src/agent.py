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
        self._store = store
        self._llm_fn = llm_fn

    def answer(self, question: str, top_k: int = 3) -> str:
        retrieved = self._store.search(question, top_k=top_k)

        if not retrieved:
            context = "(Không tìm thấy tài liệu liên quan trong knowledge base.)"
        else:
            context = "\n\n".join(
                f"[Nguồn {i + 1}]: {record['content']}"
                for i, record in enumerate(retrieved)
            )

        prompt = (
            "Bạn là một trợ lý trả lời câu hỏi dựa trên ngữ cảnh được cung cấp.\n"
            "Chỉ sử dụng thông tin có trong ngữ cảnh dưới đây để trả lời. "
            "Nếu ngữ cảnh không chứa đủ thông tin, hãy nói rõ là bạn không có "
            "đủ dữ liệu để trả lời chính xác.\n\n"
            f"Ngữ cảnh:\n{context}\n\n"
            f"Câu hỏi: {question}\n"
            "Trả lời:"
        )

        return self._llm_fn(prompt)