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

    _SENTENCE_BOUNDARY = re.compile(r"(?<=[.!?])\s+")

    def __init__(self, max_sentences_per_chunk: int = 3) -> None:
        self.max_sentences_per_chunk = max(1, max_sentences_per_chunk)

    def chunk(self, text: str) -> list[str]:
        if not text or not text.strip():
            return []
 
        # Split into individual sentences, dropping empty fragments.
        raw_sentences = self._SENTENCE_BOUNDARY.split(text.strip())
        sentences = [s.strip() for s in raw_sentences if s.strip()]
 
        if not sentences:
            return []
 
        chunks: list[str] = []
        step = self.max_sentences_per_chunk
        for start in range(0, len(sentences), step):
            group = sentences[start : start + step]
            chunks.append(" ".join(group).strip())
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
        if not text or not text.strip():
            return []
        return self._split(text.strip(), self.separators)
    
    def _split(self, current_text: str, remaining_separators: list[str]) -> list[str]:
        if len(current_text) <= self.chunk_size:
            return [current_text] if current_text.strip() else []
 
        # Base case: no separator left to try -> hard character split.
        if not remaining_separators:
            return self._hard_split(current_text)
 
        separator = remaining_separators[0]
        rest_separators = remaining_separators[1:]
 
        # Empty-string separator means "just cut by character count".
        if separator == "":
            return self._hard_split(current_text)
 
        parts = current_text.split(separator)
 
        # Re-attach the separator to every part except the very last one,
        # so no text/whitespace is lost when we regroup pieces below.
        pieces = [
            part + separator if i < len(parts) - 1 else part
            for i, part in enumerate(parts)
        ]
 
        chunks: list[str] = []
        current = ""
        for piece in pieces:
            if not piece:
                continue
            if len(current) + len(piece) <= self.chunk_size:
                current += piece
                continue
 
            # Flush whatever we have accumulated so far.
            if current.strip():
                chunks.append(current)
                current = ""
 
            if len(piece) > self.chunk_size:
                # This single piece is still too big: recurse with the
                # next separator in the priority list.
                chunks.extend(self._split(piece, rest_separators))
            else:
                current = piece
 
        if current.strip():
            chunks.append(current)
 
        return chunks
 
    def _hard_split(self, text: str) -> list[str]:
        return [text[i : i + self.chunk_size] for i in range(0, len(text), self.chunk_size)]
 

def _dot(a: list[float], b: list[float]) -> float:
    return sum(x * y for x, y in zip(a, b))


def compute_similarity(vec_a: list[float], vec_b: list[float]) -> float:
    """
    Compute cosine similarity between two vectors.
 
    cosine_similarity = dot(a, b) / (||a|| * ||b||)
 
    Returns 0.0 if either vector has zero magnitude.
    """
    if not vec_a or not vec_b:
        return 0.0
 
    dot_product = _dot(vec_a, vec_b)
    norm_a = math.sqrt(sum(x * x for x in vec_a))
    norm_b = math.sqrt(sum(y * y for y in vec_b))
 
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0
 
    return dot_product / (norm_a * norm_b)
 
 
class ChunkingStrategyComparator:
    """Run all built-in chunking strategies and compare their results."""
 
    def compare(self, text: str, chunk_size: int = 200) -> dict:
        overlap = max(1, int(chunk_size * 0.1))
 
        strategies = {
            "fixed_size": FixedSizeChunker(chunk_size=chunk_size, overlap=overlap),
            "by_sentences": SentenceChunker(max_sentences_per_chunk=3),
            "recursive": RecursiveChunker(chunk_size=chunk_size),
        }
 
        results: dict = {}
        for name, chunker in strategies.items():
            chunks = chunker.chunk(text)
            lengths = [len(c) for c in chunks]
 
            results[name] = {
                "count": len(chunks),
                "avg_length": (sum(lengths) / len(lengths)) if lengths else 0.0,
                "min_length": min(lengths) if lengths else 0,
                "max_length": max(lengths) if lengths else 0,
                "chunks": chunks,
            }
 
        return results