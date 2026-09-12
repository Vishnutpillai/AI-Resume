from dataclasses import dataclass


@dataclass
class TextChunk:
    chunk_id: int
    text: str
    source: str


class TextChunker:
    """
    Split resume/job text into retrieval-friendly chunks.

    The chunker prefers section boundaries and then applies
    character-based limits to avoid excessively large chunks.
    """

    def __init__(self, chunk_size: int = 500, overlap: int = 100):
        if chunk_size <= 0:
            raise ValueError("chunk_size must be greater than zero.")

        if overlap < 0:
            raise ValueError("overlap cannot be negative.")

        if overlap >= chunk_size:
            raise ValueError("overlap must be smaller than chunk_size.")

        self.chunk_size = chunk_size
        self.overlap = overlap

    def split_text(self, text: str, source: str = "unknown") -> list[TextChunk]:
        if not text or not text.strip():
            return []

        normalized_text = text.replace("\r\n", "\n").strip()

        sections = [
            section.strip()
            for section in normalized_text.split("\n\n")
            if section.strip()
        ]

        chunks: list[TextChunk] = []

        for section in sections:
            section_chunks = self._split_section(section)

            for chunk_text in section_chunks:
                chunks.append(
                    TextChunk(
                        chunk_id=len(chunks),
                        text=chunk_text,
                        source=source,
                    )
                )

        return chunks

    def _split_section(self, text: str) -> list[str]:
        if len(text) <= self.chunk_size:
            return [text]

        chunks: list[str] = []
        start = 0

        while start < len(text):
            end = min(start + self.chunk_size, len(text))
            chunk = text[start:end].strip()

            if chunk:
                chunks.append(chunk)

            if end >= len(text):
                break

            start = end - self.overlap

        return chunks


def chunk_text(
    text: str,
    source: str = "unknown",
    chunk_size: int = 500,
    overlap: int = 100,
) -> list[TextChunk]:
    chunker = TextChunker(
        chunk_size=chunk_size,
        overlap=overlap,
    )

    return chunker.split_text(
        text=text,
        source=source,
    )