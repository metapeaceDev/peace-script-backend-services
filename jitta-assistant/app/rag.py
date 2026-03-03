from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List

import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction

from .logger import get_logger
from .runtime_diagnostics import resolve_embedding_device


logger = get_logger(__name__)


@dataclass
class RagResult:
    documents: List[str]
    metadatas: List[dict]


class RagStore:
    def __init__(self, persist_dir: Path, embed_model: str, embed_device: str = "auto") -> None:
        """
        Initialize RAG store with ChromaDB.

        Args:
            persist_dir: Directory to store ChromaDB data
            embed_model: Sentence transformer model name
        """
        try:
            persist_dir.mkdir(parents=True, exist_ok=True)
            self._client = chromadb.PersistentClient(path=str(persist_dir))
            
            # Diagnostic resolution of device
            device_info = resolve_embedding_device(embed_device)
            
            # Explicit logging for confirmation
            if device_info.resolved == "cuda":
                logger.info("🚀 GPU CHECK PASSED: RAG Store using CUDA (NVIDIA GPU)")
            elif device_info.resolved == "mps":
                logger.info("🚀 GPU CHECK PASSED: RAG Store using MPS (Apple Silicon)")
            else:
                logger.warning(f"⚠️ GPU CHECK FAILED: Falling back to {device_info.resolved}. Reason: {device_info.reason}")
                
            self.embedding_device = device_info.resolved
            
            logger.info(f"Initializing RAG with device: {self.embedding_device} (requested: {embed_device})")

            try:
                self._embed = SentenceTransformerEmbeddingFunction(
                    model_name=embed_model,
                    device=self.embedding_device,
                )
                logger.info(f"Embedding model loaded on {self.embedding_device}")
            except TypeError:
                logger.warning("SentenceTransformerEmbeddingFunction does not support 'device' argument. Falling back to default (likely CPU).")
                self._embed = SentenceTransformerEmbeddingFunction(model_name=embed_model)
                self.embedding_device = "unknown"

            self._collection = self._client.get_or_create_collection(
                name="jitta_knowledge",
                embedding_function=self._embed,
            )
            logger.info(
                "RAG store initialized with %s documents (embed_model=%s, device=%s)",
                self._collection.count(),
                embed_model,
                self.embedding_device,
            )
        except Exception as e:
            logger.error(f"Failed to initialize RAG store: {e}")
            raise

    def add_text(self, text: str, source: str) -> None:
        """
        Add text to the knowledge base.

        Args:
            text: Text content to add
            source: Source identifier for the text
        """
        if not text or not text.strip():
            logger.warning("Empty text provided to add_text")
            return

        if not source or not source.strip():
            logger.warning("Empty source provided to add_text")
            source = "unknown"

        try:
            chunks = _split_text(text)
            if not chunks:
                logger.warning("No chunks generated from text")
                return

            ids = [f"{source}::{i}" for i in range(len(chunks))]
            metadatas = [{"source": source, "chunk": i} for i in range(len(chunks))]

            self._collection.add(documents=chunks, metadatas=metadatas, ids=ids)
            logger.debug(f"Added {len(chunks)} chunks from source '{source}'")
        except Exception as e:
            logger.error(f"Failed to add text from source '{source}': {e}")
            raise

    def ingest_dir(self, root: Path) -> int:
        """
        Ingest all text files from a directory, excluding common ignore folders.

        Args:
            root: Root directory to scan

        Returns:
            Number of files ingested
        """
        if not root.exists() or not root.is_dir():
            logger.error(f"Directory does not exist: {root}")
            return 0

        # Define exclusions
        exclude_dirs = {
            ".git", ".venv", "node_modules", "__pycache__", "dist", "build", 
            "coverage", ".idea", ".vscode", "tmp", "logs"
        }
        
        # Define allowed extensions
        allowed_extensions = {
            ".txt", ".md", ".py", ".js", ".ts", ".json", 
            ".yaml", ".yml", ".sh", ".ps1", ".html", ".css", ".sql", ".rs", ".go", ".java", ".c", ".cpp"
        }

        count = 0
        try:
            for path in root.rglob("*"):
                # Prune excluded directories
                if path.is_dir():
                    if path.name in exclude_dirs:
                        continue
                
                # Check for file and extension
                if path.is_file() and path.suffix.lower() in allowed_extensions:
                    # Double check parent directories for exclusion
                    if any(part in exclude_dirs for part in path.parts):
                        continue

                    try:
                        text = path.read_text(encoding="utf-8", errors="ignore")
                        if text.strip():
                            # Use relative path as source for cleaner context
                            try:
                                rel_source = str(path.relative_to(root))
                            except ValueError:
                                rel_source = str(path)
                                
                            self.add_text(text, source=f"file://{rel_source}")
                            count += 1
                            if count % 10 == 0:
                                logger.info(f"Ingested {count} files...")
                    except Exception as e:
                        logger.warning(f"Failed to read file {path}: {e}")
                        continue
                        
        except Exception as e:
            logger.error(f"Failed to ingest directory {root}: {e}")
            raise

        logger.info(f"Ingested total {count} files from {root}")
        return count

    def query(self, text: str, top_k: int) -> RagResult:
        """
        Query the knowledge base.

        Args:
            text: Query text
            top_k: Number of results to return

        Returns:
            RagResult with documents and metadata
        """
        if not text or not text.strip():
            logger.warning("Empty query text provided")
            return RagResult([], [])

        try:
            result = self._collection.query(query_texts=[text], n_results=top_k)
            docs = result.get("documents", [[]])[0]
            metas = result.get("metadatas", [[]])[0]

            logger.debug(f"Query returned {len(docs)} results")
            return RagResult(documents=docs, metadatas=metas)
        except Exception as e:
            logger.error(f"Failed to query RAG: {e}")
            return RagResult([], [])


def _split_text(text: str, max_len: int = 1000, overlap: int = 120) -> List[str]:
    text = " ".join(text.split())
    if len(text) <= max_len:
        return [text]
    chunks: List[str] = []
    start = 0
    while start < len(text):
        end = min(start + max_len, len(text))
        chunk = text[start:end]
        chunks.append(chunk)
        if end == len(text):
            break
        start = max(0, end - overlap)
    return chunks
