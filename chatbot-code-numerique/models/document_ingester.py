import hashlib
import re
import os
from datetime import datetime
from typing import List, Dict, Any
import chromadb
from sentence_transformers import SentenceTransformer
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pypdf import PdfReader
from docx import Document
import csv

class UnsupportedFormatError(Exception):
    pass

class DocumentIngester:
    def __init__(self, db_path: str = "./chroma_db",
                 embedding_model: str = "paraphrase-multilingual-MiniLM-L12-v2",
                 chunk_size: int = 500,
                 chunk_overlap: int = 100,
                 strategy: str = "semantic"):  # "fixed" ou "semantic"
        self.db_path = db_path
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.strategy = strategy
        self.model = SentenceTransformer(embedding_model)
        self.client = chromadb.PersistentClient(path=db_path)
        self.collection = self.client.get_or_create_collection(
            "documents",
            metadata={"hnsw:space": "cosine"}
        )

    # ------------------- Extraction selon le format (Q1.1) -------------------
    def _extract_text(self, file_path: str) -> str:
        ext = os.path.splitext(file_path)[1].lower()
        if ext in ['.txt', '.md']:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        elif ext == '.pdf':
            reader = PdfReader(file_path)
            return "\n".join([page.extract_text() or "" for page in reader.pages])
        elif ext == '.docx':
            doc = Document(file_path)
            return "\n".join([para.text for para in doc.paragraphs])
        elif ext == '.csv':
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                return "\n".join([", ".join(row) for row in reader])
        else:
            raise UnsupportedFormatError(f"Format {ext} non supporté")

    # ------------------- Découpage (Q1.2) -------------------
    def _chunk_fixed(self, text: str) -> List[str]:
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            separators=["\n\n", "\n", ".", " "],
            length_function=len
        )
        chunks = splitter.split_text(text)
        # Filtrer les chunks trop petits (<30 caractères)
        return [c for c in chunks if len(c.strip()) >= 30]

    def _chunk_semantic(self, text: str) -> List[str]:
        # Découper sur les frontières d'articles juridiques
        article_pattern = re.compile(r'(?=\bArticle\s+\d+)', re.IGNORECASE)
        parts = article_pattern.split(text)

        chunks = []
        for part in parts:
            part = part.strip()
            if not part:
                continue
            if len(part) <= self.chunk_size:
                chunks.append(part)
            else:
                # Trop long : sous-découper en préservant l'entête de l'article
                header = part[:80]
                splitter = RecursiveCharacterTextSplitter(
                    chunk_size=self.chunk_size,
                    chunk_overlap=self.chunk_overlap,
                    separators=["\n\n", "\n", ". ", " "],
                )
                sub_chunks = splitter.split_text(part)
                for i, sc in enumerate(sub_chunks):
                    chunks.append(sc if i == 0 else f"[suite {header}] {sc}")

        return [c for c in chunks if len(c) >= 30]

    def _chunk(self, text: str) -> List[str]:
        if self.strategy == "fixed":
            return self._chunk_fixed(text)
        else:
            return self._chunk_semantic(text)

    # ------------------- Indexation avec métadonnées et gestion des doublons  -------------------
    def ingest(self, file_path: str) -> None:
        filename = os.path.basename(file_path)
        print(f"Traitement de {filename}...")

        # Supprimer les anciens chunks du même document
        existing = self.collection.get(where={"source": filename})
        if existing['ids']:
            self.collection.delete(ids=existing['ids'])
            print(f"  → {len(existing['ids'])} anciens chunks supprimés")

        raw_text = self._extract_text(file_path)
        chunks = self._chunk(raw_text)
        if not chunks:
            print("  Aucun chunk valide généré.")
            return

        # Générer les embeddings
        embeddings = self.model.encode(chunks).tolist()

        # Préparer les métadonnées
        ids = []
        metadatas = []
        now = datetime.now().isoformat()
        total = len(chunks)
        for idx, chunk in enumerate(chunks):
            chunk_id = f"{hashlib.md5(chunk.encode()).hexdigest()}_{idx}"
            ids.append(chunk_id)
            metadatas.append({
                "source": filename,
                "format": os.path.splitext(filename)[1][1:],
                "chunk_index": idx,
                "total_chunks": total,
                "date_ingestion": now,
                "taille_chars": len(chunk)
            })

        # Ajout à ChromaDB
        self.collection.add(ids=ids, embeddings=embeddings, documents=chunks, metadatas=metadatas)
        print(f"  → {len(chunks)} nouveaux chunks indexés")

    # ------------------- Statistiques  -------------------
    def get_stats(self) -> Dict[str, Any]:
        total = self.collection.count()
        if total == 0:
            return {"total_chunks": 0, "documents": {}, "taille_moyenne_chunk": 0, "date_derniere_ingestion": None}
        all_meta = self.collection.get()['metadatas']
        doc_stats = {}
        total_chars = 0
        last_ingestion = None
        for meta in all_meta:
            src = meta['source']
            doc_stats[src] = doc_stats.get(src, 0) + 1
            total_chars += meta['taille_chars']
            if not last_ingestion or meta['date_ingestion'] > last_ingestion:
                last_ingestion = meta['date_ingestion']
        return {
            "total_chunks": total,
            "documents": doc_stats,
            "taille_moyenne_chunk": total_chars / total,
            "date_derniere_ingestion": last_ingestion
        }
