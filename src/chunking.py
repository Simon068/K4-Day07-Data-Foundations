from __future__ import annotations

import math
import re


class FixedSizeChunker:
    """
    Split text into fixed-size chunks with optional overlap.

    Rules:
        - Each chunk is at most chunk_size characters long.
        - Consecutive chunks share overlap characters.
        - The last chunk contains whatever remains.
        - If text is shorter than chunk_size, return [text].
    """

    def __init__(self, chunk_size: int = 500, overlap: int = 50) -> None:
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk(self, text: str) -> list[str]:
        if not text:
            return []
        if len(text) <= self.chunk_size:
            return [text]

        step = self.chunk_size - self.overlap
        chunks: list[str] = []
        for start in range(0, len(text), step):
            chunk = text[start : start + self.chunk_size]
            chunks.append(chunk)
            if start + self.chunk_size >= len(text):
                break
        return chunks


class SentenceChunker:
    """
    Split text into chunks of at most max_sentences_per_chunk sentences.

    Sentence detection: split on ". ", "! ", "? " or ".\n".
    Strip extra whitespace from each chunk.
    """

    def __init__(self, max_sentences_per_chunk: int = 3) -> None:
        self.max_sentences_per_chunk = max(1, max_sentences_per_chunk)

    def chunk(self, text: str) -> list[str]:
        if not text:
            return []

        # Split on sentence boundaries: ". ", "! ", "? ", ".\n"
        # We use a regex that keeps the delimiter attached to the preceding sentence.
        parts = re.split(r'(?<=[\.\!\?])(?:\s|\n)', text)

        # Filter out empty strings from split
        sentences = [s.strip() for s in parts if s.strip()]

        if not sentences:
            return []

        chunks: list[str] = []
        for i in range(0, len(sentences), self.max_sentences_per_chunk):
            group = sentences[i : i + self.max_sentences_per_chunk]
            chunk = " ".join(group).strip()
            if chunk:
                chunks.append(chunk)

        return chunks


class RecursiveChunker:
    """
    Recursively split text using separators in priority order.

    Default separator priority:
        ["\n\n", "\n", ". ", " ", ""]
    """

    DEFAULT_SEPARATORS = ["\n\n", "\n", ". ", " ", ""]

    def __init__(self, separators: list[str] | None = None, chunk_size: int = 500) -> None:
        self.separators = self.DEFAULT_SEPARATORS if separators is None else list(separators)
        self.chunk_size = chunk_size

    def chunk(self, text: str) -> list[str]:
        if not text:
            return []
        results = self._split(text, self.separators)
        # Filter out empty chunks
        return [c for c in results if c.strip()]

    def _split(self, current_text: str, remaining_separators: list[str]) -> list[str]:
        # Base case: text fits in chunk_size
        if len(current_text) <= self.chunk_size:
            return [current_text]

        # If no separators left, force split by chunk_size
        if not remaining_separators:
            chunks = []
            for i in range(0, len(current_text), self.chunk_size):
                chunks.append(current_text[i : i + self.chunk_size])
            return chunks

        separator = remaining_separators[0]
        next_separators = remaining_separators[1:]

        # If separator is empty string, fall back to character-level splitting
        if separator == "":
            chunks = []
            for i in range(0, len(current_text), self.chunk_size):
                chunks.append(current_text[i : i + self.chunk_size])
            return chunks

        # Split by current separator
        parts = current_text.split(separator)

        # If splitting didn't help (only 1 part), try next separator
        if len(parts) == 1:
            return self._split(current_text, next_separators)

        # Merge parts back into chunks that fit within chunk_size
        chunks: list[str] = []
        current_chunk = ""

        for i, part in enumerate(parts):
            # What the chunk would look like if we add this part
            if current_chunk:
                candidate = current_chunk + separator + part
            else:
                candidate = part

            if len(candidate) <= self.chunk_size:
                current_chunk = candidate
            else:
                # Flush current chunk if it has content
                if current_chunk:
                    chunks.append(current_chunk)
                # If the part itself exceeds chunk_size, recurse with next separators
                if len(part) > self.chunk_size:
                    sub_chunks = self._split(part, next_separators)
                    chunks.extend(sub_chunks)
                    current_chunk = ""
                else:
                    current_chunk = part

        # Don't forget the last chunk
        if current_chunk:
            chunks.append(current_chunk)

        return chunks


def _dot(a: list[float], b: list[float]) -> float:
    return sum(x * y for x, y in zip(a, b))


def compute_similarity(vec_a: list[float], vec_b: list[float]) -> float:
    """
    Compute cosine similarity between two vectors.

    cosine_similarity = dot(a, b) / (||a|| * ||b||)

    Returns 0.0 if either vector has zero magnitude.
    """
    dot_product = _dot(vec_a, vec_b)
    mag_a = math.sqrt(sum(x * x for x in vec_a))
    mag_b = math.sqrt(sum(x * x for x in vec_b))

    if mag_a == 0.0 or mag_b == 0.0:
        return 0.0

    return dot_product / (mag_a * mag_b)


class ChunkingStrategyComparator:
    """Run all built-in chunking strategies and compare their results."""

    def compare(self, text: str, chunk_size: int = 200) -> dict:
        # Fixed size chunker
        fixed_chunker = FixedSizeChunker(chunk_size=chunk_size, overlap=50)
        fixed_chunks = fixed_chunker.chunk(text)

        # Sentence chunker - estimate max_sentences to approximate chunk_size
        sentence_chunker = SentenceChunker(max_sentences_per_chunk=3)
        sentence_chunks = sentence_chunker.chunk(text)

        # Recursive chunker
        recursive_chunker = RecursiveChunker(chunk_size=chunk_size)
        recursive_chunks = recursive_chunker.chunk(text)

        def stats(chunks: list[str]) -> dict:
            count = len(chunks)
            avg_length = sum(len(c) for c in chunks) / count if count > 0 else 0
            return {
                "count": count,
                "avg_length": round(avg_length, 2),
                "chunks": chunks,
            }

        return {
            "fixed_size": stats(fixed_chunks),
            "by_sentences": stats(sentence_chunks),
            "recursive": stats(recursive_chunks),
        }
