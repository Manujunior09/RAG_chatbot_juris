import re
from typing import List
from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.core.config import settings


def chunk_fixed(text: str) -> List[str]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
        separators=["\n\n", "\n", ".", " "],
        length_function=len,
    )
    return [c for c in splitter.split_text(text) if len(c.strip()) >= 30]


def chunk_semantic(text: str) -> List[str]:
    parts = re.compile(r"(?=\bArticle\s+\d+)", re.IGNORECASE).split(text)
    chunks = []
    for part in parts:
        part = part.strip()
        if not part:
            continue
        if len(part) <= settings.chunk_size:
            chunks.append(part)
        else:
            header = part[:80]
            splitter = RecursiveCharacterTextSplitter(
                chunk_size=settings.chunk_size,
                chunk_overlap=settings.chunk_overlap,
                separators=["\n\n", "\n", ". ", " "],
            )
            for i, sc in enumerate(splitter.split_text(part)):
                chunks.append(sc if i == 0 else f"[suite {header}] {sc}")
    return [c for c in chunks if len(c) >= 30]


def chunk(text: str, strategy: str = "semantic") -> List[str]:
    return chunk_fixed(text) if strategy == "fixed" else chunk_semantic(text)
