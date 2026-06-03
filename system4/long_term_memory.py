"""System 4 Phase 4: Vector Memory / Long-Term Memory

Embeds all studio knowledge into a vector database for semantic search.
Enables queries like:
    - "Show me all productions with strong redemption arcs"
    - "What emotional curves worked for buddy-cop films?"
    - "Find scenes with cynical trickster dialogue"

Uses ChromaDB for storage and sentence-transformers for embeddings.
"""

from __future__ import annotations

import os
import sys
import re
import hashlib
from dataclasses import dataclass, field
from typing import Optional
from pathlib import Path

# Ensure project root is on path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Embeddings
from sentence_transformers import SentenceTransformer

# Vector DB
import chromadb
from chromadb.config import Settings

# Studio imports
from bridge.obsidian_bridge import ObsidianBridge, get_bridge


# =============================================================================
# Configuration
# =============================================================================

DEFAULT_EMBEDDING_MODEL = "all-MiniLM-L6-v2"
DEFAULT_COLLECTION_NAME = "studio_memory"
DEFAULT_PERSIST_DIR = "studio/memory/embeddings"

# Document type → collection mapping
COLLECTIONS = {
    "concept": "concepts",
    "evaluation": "evaluations",
    "post_mortem": "post_mortems",
    "voice_profile": "voice_profiles",
    "scene": "scenes",
    "director_decision": "decisions",
    "character": "characters",
}


# =============================================================================
# Data Structures
# =============================================================================

@dataclass
class MemoryChunk:
    """A chunk of text ready for embedding and storage."""
    id: str
    text: str
    doc_type: str  # concept, evaluation, post_mortem, etc.
    production_id: Optional[str] = None
    concept_id: Optional[str] = None
    metadata: dict = field(default_factory=dict)


@dataclass
class SearchResult:
    """Result from a semantic search query."""
    id: str
    text: str
    doc_type: str
    distance: float
    score: float  # 0.0-1.0 similarity
    metadata: dict = field(default_factory=dict)


# =============================================================================
# Document Chunker
# =============================================================================

class DocumentChunker:
    """Splits markdown documents into semantically meaningful chunks."""
    
    def __init__(self, max_chunk_size: int = 512, overlap: int = 50):
        self.max_chunk_size = max_chunk_size
        self.overlap = overlap
    
    def chunk_note(self, note, doc_type: str, production_id: Optional[str] = None) -> list[MemoryChunk]:
        """Chunk an ObsidianNote into MemoryChunks."""
        chunks = []
        
        # Build rich text from frontmatter + content
        fm = note.frontmatter
        content = note.content or ""
        
        # Type-specific chunking strategies
        if doc_type == "concept":
            chunks = self._chunk_concept(note, fm, content, production_id)
        elif doc_type == "evaluation":
            chunks = self._chunk_evaluation(note, fm, content, production_id)
        elif doc_type == "post_mortem":
            chunks = self._chunk_post_mortem(note, fm, content, production_id)
        elif doc_type == "voice_profile":
            chunks = self._chunk_voice_profile(note, fm, content, production_id)
        elif doc_type == "scene":
            chunks = self._chunk_scene(note, fm, content, production_id)
        elif doc_type == "director_decision":
            chunks = self._chunk_decision(note, fm, content, production_id)
        else:
            # Generic chunking
            chunks = self._chunk_generic(note, fm, content, doc_type, production_id)
        
        return chunks
    
    def _chunk_concept(self, note, fm, content, production_id) -> list[MemoryChunk]:
        """Chunk a concept note."""
        chunks = []
        concept_id = fm.get("concept_id", note.path)
        
        # Chunk 1: Core concept (title + logline + theme)
        core_text = f"Concept: {note.title}. "
        if fm.get("logline"):
            core_text += f"Logline: {fm['logline']}. "
        if fm.get("theme"):
            core_text += f"Theme: {fm['theme']}. "
        if fm.get("genre"):
            core_text += f"Genre: {fm['genre']}. "
        if fm.get("setting"):
            core_text += f"Setting: {fm['setting']}. "
        
        chunks.append(MemoryChunk(
            id=self._chunk_id(note.path, "core"),
            text=core_text.strip(),
            doc_type="concept",
            production_id=production_id,
            concept_id=concept_id,
            metadata={"section": "core", "title": note.title}
        ))
        
        # Chunk 2: Full content
        if content:
            for i, subchunk in enumerate(self._split_text(content)):
                chunks.append(MemoryChunk(
                    id=self._chunk_id(note.path, f"content_{i}"),
                    text=subchunk,
                    doc_type="concept",
                    production_id=production_id,
                    concept_id=concept_id,
                    metadata={"section": "content", "chunk_index": i}
                ))
        
        return chunks
    
    def _chunk_evaluation(self, note, fm, content, production_id) -> list[MemoryChunk]:
        """Chunk an evaluation note."""
        chunks = []
        concept_id = fm.get("concept_id", "")
        scores = fm.get("scores", {})
        
        # Chunk 1: Overall evaluation summary
        summary = f"Evaluation for concept {concept_id}. "
        if "_combined" in scores:
            summary += f"Combined score: {scores['_combined']}. "
        
        # Add per-category summaries
        for cat in ["structure", "character", "emotion", "pacing", "theme", "dialogue"]:
            if cat in scores and isinstance(scores[cat], dict):
                cat_data = scores[cat]
                summary += f"{cat}: {cat_data.get('score', 'N/A')}. "
                if cat_data.get("issues"):
                    summary += f"Issues: {'; '.join(cat_data['issues'][:2])}. "
        
        chunks.append(MemoryChunk(
            id=self._chunk_id(note.path, "summary"),
            text=summary.strip(),
            doc_type="evaluation",
            production_id=production_id,
            concept_id=concept_id,
            metadata={"section": "summary", "has_scores": True}
        ))
        
        # Chunk 2: Full content with scores embedded
        if content:
            for i, subchunk in enumerate(self._split_text(content)):
                chunks.append(MemoryChunk(
                    id=self._chunk_id(note.path, f"content_{i}"),
                    text=subchunk,
                    doc_type="evaluation",
                    production_id=production_id,
                    concept_id=concept_id,
                    metadata={"section": "content", "chunk_index": i}
                ))
        
        return chunks
    
    def _chunk_post_mortem(self, note, fm, content, production_id) -> list[MemoryChunk]:
        """Chunk a post-mortem note."""
        chunks = []
        
        # Chunk 1: Header + key stats
        header = f"Post-mortem for production {production_id or note.path}. {note.title}. "
        if content:
            # Extract first paragraph
            first_para = content.split("\n\n")[0] if "\n\n" in content else content[:300]
            header += first_para
        
        chunks.append(MemoryChunk(
            id=self._chunk_id(note.path, "summary"),
            text=header.strip(),
            doc_type="post_mortem",
            production_id=production_id,
            metadata={"section": "summary", "title": note.title}
        ))
        
        # Chunk remaining content
        if content:
            for i, subchunk in enumerate(self._split_text(content)):
                chunks.append(MemoryChunk(
                    id=self._chunk_id(note.path, f"content_{i}"),
                    text=subchunk,
                    doc_type="post_mortem",
                    production_id=production_id,
                    metadata={"section": "content", "chunk_index": i}
                ))
        
        return chunks
    
    def _chunk_voice_profile(self, note, fm, content, production_id) -> list[MemoryChunk]:
        """Chunk a voice profile note."""
        char_name = fm.get("name", note.title.replace(" Voice", ""))
        archetype = fm.get("archetype", "")
        
        text = f"Character voice profile: {char_name}. Archetype: {archetype}. "
        text += content or ""
        
        return [MemoryChunk(
            id=self._chunk_id(note.path, "profile"),
            text=text.strip(),
            doc_type="voice_profile",
            production_id=production_id,
            metadata={"character": char_name, "archetype": archetype}
        )]
    
    def _chunk_scene(self, note, fm, content, production_id) -> list[MemoryChunk]:
        """Chunk a scene note."""
        scene_num = fm.get("scene_number", 0)
        slugline = fm.get("slugline", "")
        title = note.title
        
        text = f"Scene {scene_num}: {title}. Slugline: {slugline}. "
        text += content or ""
        
        return [MemoryChunk(
            id=self._chunk_id(note.path, "scene"),
            text=text.strip(),
            doc_type="scene",
            production_id=production_id,
            metadata={"scene_number": scene_num, "slugline": slugline}
        )]
    
    def _chunk_decision(self, note, fm, content, production_id) -> list[MemoryChunk]:
        """Chunk a director decision note."""
        verdict = fm.get("verdict", "")
        confidence = fm.get("confidence", 0)
        reason = fm.get("reason", "")
        
        text = f"Director decision for {production_id or note.path}. Verdict: {verdict}. Confidence: {confidence}. Reason: {reason}. "
        text += content or ""
        
        return [MemoryChunk(
            id=self._chunk_id(note.path, "decision"),
            text=text.strip(),
            doc_type="director_decision",
            production_id=production_id,
            metadata={"verdict": verdict, "confidence": confidence}
        )]
    
    def _chunk_generic(self, note, fm, content, doc_type, production_id) -> list[MemoryChunk]:
        """Generic chunking for unknown document types."""
        text = f"{note.title}. "
        text += content or ""
        
        return [MemoryChunk(
            id=self._chunk_id(note.path, "generic"),
            text=text.strip(),
            doc_type=doc_type,
            production_id=production_id,
            metadata={"title": note.title}
        )]
    
    def _split_text(self, text: str) -> list[str]:
        """Split text into chunks with overlap."""
        if len(text) <= self.max_chunk_size:
            return [text]
        
        chunks = []
        start = 0
        while start < len(text):
            end = start + self.max_chunk_size
            # Try to break at paragraph or sentence
            if end < len(text):
                # Look for paragraph break
                para_break = text.rfind("\n\n", start, end)
                if para_break > start + self.max_chunk_size // 2:
                    end = para_break + 2
                else:
                    # Look for sentence end
                    sent_end = max(
                        text.rfind(". ", start, end),
                        text.rfind("? ", start, end),
                        text.rfind("! ", start, end),
                    )
                    if sent_end > start + self.max_chunk_size // 2:
                        end = sent_end + 2
            
            chunks.append(text[start:end].strip())
            start = end - self.overlap
        
        return chunks
    
    def _chunk_id(self, path: str, suffix: str) -> str:
        """Generate a stable chunk ID."""
        base = f"{path}:{suffix}"
        return hashlib.md5(base.encode()).hexdigest()[:16]


# =============================================================================
# Embedding Engine
# =============================================================================

class EmbeddingEngine:
    """Generates embeddings using sentence-transformers."""
    
    def __init__(self, model_name: str = DEFAULT_EMBEDDING_MODEL):
        self.model_name = model_name
        self._model: Optional[SentenceTransformer] = None
    
    @property
    def model(self) -> SentenceTransformer:
        """Lazy-load the model."""
        if self._model is None:
            print(f"[EmbeddingEngine] Loading model: {self.model_name}")
            self._model = SentenceTransformer(self.model_name)
            print(f"[EmbeddingEngine] Model loaded. Dim: {self._model.get_embedding_dimension()}")
        return self._model
    
    def embed(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings for a list of texts."""
        if not texts:
            return []
        return self.model.encode(texts, show_progress_bar=False).tolist()
    
    def embed_query(self, text: str) -> list[float]:
        """Generate embedding for a single query."""
        return self.embed([text])[0]


# =============================================================================
# Vector Store
# =============================================================================

class VectorStore:
    """ChromaDB wrapper with per-document-type collections."""
    
    def __init__(self, persist_dir: str = DEFAULT_PERSIST_DIR):
        self.persist_dir = Path(persist_dir)
        self.persist_dir.mkdir(parents=True, exist_ok=True)
        
        # Use PersistentClient for new ChromaDB API
        self.client = chromadb.PersistentClient(path=str(self.persist_dir))
        self._collections: dict[str, Any] = {}
    
    def get_collection(self, name: str):
        """Get or create a collection."""
        if name not in self._collections:
            self._collections[name] = self.client.get_or_create_collection(
                name=name,
                metadata={"hnsw:space": "cosine"}
            )
        return self._collections[name]
    
    def add_chunks(self, chunks: list[MemoryChunk], embeddings: list[list[float]]) -> None:
        """Add chunks with embeddings to the store."""
        if not chunks or not embeddings:
            return
        
        # Group by doc_type → collection
        by_collection: dict[str, list[tuple[MemoryChunk, list[float]]]] = {}
        for chunk, emb in zip(chunks, embeddings):
            coll_name = COLLECTIONS.get(chunk.doc_type, "misc")
            by_collection.setdefault(coll_name, []).append((chunk, emb))
        
        for coll_name, items in by_collection.items():
            collection = self.get_collection(coll_name)
            ids = [item[0].id for item in items]
            texts = [item[0].text for item in items]
            embs = [item[1] for item in items]
            metadatas = [{
                "doc_type": item[0].doc_type,
                "production_id": item[0].production_id or "",
                "concept_id": item[0].concept_id or "",
                **item[0].metadata,
            } for item in items]
            
            collection.add(
                ids=ids,
                documents=texts,
                embeddings=embs,
                metadatas=metadatas,
            )
    
    def search(
        self,
        query_embedding: list[float],
        doc_types: Optional[list[str]] = None,
        production_id: Optional[str] = None,
        n_results: int = 10,
    ) -> list[SearchResult]:
        """Semantic search across collections."""
        all_results = []
        
        # Determine which collections to search
        if doc_types:
            collection_names = [COLLECTIONS.get(dt, "misc") for dt in doc_types]
        else:
            collection_names = list(set(COLLECTIONS.values()))
        
        for coll_name in collection_names:
            try:
                collection = self.get_collection(coll_name)
                
                # Build where clause
                where = {}
                if production_id:
                    where["production_id"] = production_id
                
                results = collection.query(
                    query_embeddings=[query_embedding],
                    n_results=n_results,
                    where=where if where else None,
                )
                
                if results["ids"] and results["ids"][0]:
                    for i, doc_id in enumerate(results["ids"][0]):
                        distance = results["distances"][0][i]
                        # Cosine distance → similarity score (0-1)
                        score = 1.0 - distance
                        
                        all_results.append(SearchResult(
                            id=doc_id,
                            text=results["documents"][0][i],
                            doc_type=results["metadatas"][0][i].get("doc_type", "unknown"),
                            distance=distance,
                            score=round(score, 3),
                            metadata={k: v for k, v in results["metadatas"][0][i].items() 
                                     if k not in ("doc_type", "production_id", "concept_id")}
                        ))
            except Exception as e:
                print(f"[VectorStore] Search error in {coll_name}: {e}")
                continue
        
        # Sort by score descending
        all_results.sort(key=lambda r: r.score, reverse=True)
        return all_results[:n_results]
    
    def delete_by_production(self, production_id: str) -> None:
        """Delete all chunks for a production."""
        for coll_name in set(COLLECTIONS.values()):
            try:
                collection = self.get_collection(coll_name)
                collection.delete(where={"production_id": production_id})
            except Exception:
                pass
    
    def count(self) -> dict[str, int]:
        """Count documents per collection."""
        counts = {}
        for coll_name in set(COLLECTIONS.values()):
            try:
                collection = self.get_collection(coll_name)
                counts[coll_name] = collection.count()
            except Exception:
                counts[coll_name] = 0
        return counts
    
    def persist(self) -> None:
        """Persist the database to disk."""
        # ChromaDB with duckdb+parquet persists automatically
        pass


# =============================================================================
# Long-Term Memory
# =============================================================================

class LongTermMemory:
    """High-level interface for vector memory operations.
    
    Usage:
        ltm = LongTermMemory()
        ltm.ingest_vault()  # Index all vault documents
        
        results = ltm.search("redemption arcs in animated films")
        for r in results:
            print(f"{r.score:.2f} | {r.doc_type}: {r.text[:100]}")
    """
    
    def __init__(
        self,
        bridge: Optional[ObsidianBridge] = None,
        persist_dir: str = DEFAULT_PERSIST_DIR,
        model_name: str = DEFAULT_EMBEDDING_MODEL,
    ):
        self.bridge = bridge or get_bridge()
        self.chunker = DocumentChunker()
        self.embedder = EmbeddingEngine(model_name)
        self.store = VectorStore(persist_dir)
    
    # -------------------------------------------------------------------------
    # Ingestion
    # -------------------------------------------------------------------------
    
    def ingest_vault(self, production_id: Optional[str] = None) -> dict[str, int]:
        """Ingest all documents from the vault into vector memory.
        
        Args:
            production_id: If provided, only ingest documents for this production.
        
        Returns:
            Count of chunks ingested per document type.
        """
        counts: dict[str, int] = {}
        
        # Ingest concepts
        counts["concepts"] = self._ingest_folder(
            "concepts", "concept", production_id
        )
        
        # Ingest evaluations
        counts["evaluations"] = self._ingest_folder(
            "reviews", "evaluation", production_id, path_filter=lambda p: "evaluation_" in p
        )
        
        # Ingest post-mortems
        counts["post_mortems"] = self._ingest_folder(
            "memory/post_mortems", "post_mortem", production_id,
            path_filter=lambda p: "post_mortem_" in p
        )
        
        # Ingest voice profiles
        counts["voice_profiles"] = self._ingest_folder(
            "characters", "voice_profile", production_id,
            path_filter=lambda p: "_voice.md" in p
        )
        
        # Ingest scenes
        counts["scenes"] = self._ingest_folder(
            "scenes", "scene", production_id
        )
        
        # Ingest director decisions
        counts["decisions"] = self._ingest_folder(
            "reviews", "director_decision", production_id,
            path_filter=lambda p: "director_decision_" in p
        )
        
        return counts
    
    def _ingest_folder(
        self,
        folder: str,
        doc_type: str,
        production_id: Optional[str] = None,
        path_filter: Optional[callable] = None,
    ) -> int:
        """Ingest all notes from a folder."""
        notes = self.bridge.query_notes(folder=folder)
        
        if path_filter:
            notes = [n for n in notes if path_filter(n.path)]
        
        if production_id:
            notes = [n for n in notes if production_id in n.path]
        
        total_chunks = 0
        for note in notes:
            # Determine production_id from path if not provided
            pid = production_id or self._extract_production_id(note.path)
            chunks = self.chunker.chunk_note(note, doc_type, pid)
            
            if chunks:
                embeddings = self.embedder.embed([c.text for c in chunks])
                self.store.add_chunks(chunks, embeddings)
                total_chunks += len(chunks)
        
        return total_chunks
    
    def ingest_production(self, production_id: str) -> dict[str, int]:
        """Ingest a single production's documents."""
        # Delete existing chunks for this production to avoid duplicates
        self.store.delete_by_production(production_id)
        return self.ingest_vault(production_id=production_id)
    
    def _extract_production_id(self, path: str) -> Optional[str]:
        """Try to extract production_id from a file path."""
        # Patterns: package_PRODID.md, evaluation_PRODID.md, post_mortem_PRODID.md
        patterns = [
            r"package_([^/]+)\.md",
            r"evaluation_([^/]+)\.md",
            r"post_mortem_([^/]+)\.md",
            r"director_decision_([^/]+)\.md",
        ]
        for pattern in patterns:
            m = re.search(pattern, path)
            if m:
                return m.group(1)
        return None
    
    # -------------------------------------------------------------------------
    # Search
    # -------------------------------------------------------------------------
    
    def search(
        self,
        query: str,
        doc_types: Optional[list[str]] = None,
        production_id: Optional[str] = None,
        n_results: int = 10,
    ) -> list[SearchResult]:
        """Semantic search with natural language query."""
        embedding = self.embedder.embed_query(query)
        return self.store.search(
            query_embedding=embedding,
            doc_types=doc_types,
            production_id=production_id,
            n_results=n_results,
        )
    
    def search_similar(
        self,
        text: str,
        doc_types: Optional[list[str]] = None,
        n_results: int = 5,
    ) -> list[SearchResult]:
        """Find documents similar to the given text."""
        return self.search(text, doc_types=doc_types, n_results=n_results)
    
    def ask(self, question: str, n_results: int = 5) -> str:
        """Ask a question and get a natural language answer from memory.
        
        Returns a formatted string with the most relevant evidence.
        """
        results = self.search(question, n_results=n_results)
        if not results:
            return "No relevant memories found."
        
        lines = [f"**Question:** {question}", ""]
        for i, r in enumerate(results, 1):
            lines.append(f"{i}. **{r.doc_type.upper()}** (score: {r.score:.2f})")
            lines.append(f"   {r.text[:250]}{'...' if len(r.text) > 250 else ''}")
            if r.metadata:
                meta_str = ", ".join(f"{k}={v}" for k, v in list(r.metadata.items())[:3])
                lines.append(f"   _{meta_str}_")
            lines.append("")
        
        return "\n".join(lines)
    
    # -------------------------------------------------------------------------
    # Stats
    # -------------------------------------------------------------------------
    
    def stats(self) -> dict[str, Any]:
        """Get memory statistics."""
        return {
            "collections": self.store.count(),
            "embedding_model": self.embedder.model_name,
            "embedding_dimension": self.embedder.model.get_embedding_dimension(),
        }


# =============================================================================
# Singleton + Convenience
# =============================================================================

_long_term_memory: Optional[LongTermMemory] = None


def get_long_term_memory() -> LongTermMemory:
    """Get or create the singleton LongTermMemory instance."""
    global _long_term_memory
    if _long_term_memory is None:
        _long_term_memory = LongTermMemory()
    return _long_term_memory


def search_memory(query: str, **kwargs) -> list[SearchResult]:
    """Convenience function: search the global memory."""
    return get_long_term_memory().search(query, **kwargs)


# =============================================================================
# CLI
# =============================================================================

if __name__ == "__main__":
    import sys
    
    ltm = LongTermMemory()
    
    if len(sys.argv) < 2:
        print("Usage: python long_term_memory.py <command> [args]")
        print("")
        print("Commands:")
        print("  ingest              Ingest all vault documents")
        print("  ingest <prod_id>    Ingest specific production")
        print("  search <query>      Search memory")
        print("  ask <question>      Ask a question")
        print("  stats               Show memory stats")
        print("")
        sys.exit(1)
    
    cmd = sys.argv[1]
    
    if cmd == "ingest":
        prod_id = sys.argv[2] if len(sys.argv) > 2 else None
        counts = ltm.ingest_vault(production_id=prod_id)
        print("Ingestion complete:")
        for doc_type, count in counts.items():
            print(f"  {doc_type}: {count} chunks")
        print(f"\nTotal: {sum(counts.values())} chunks")
    
    elif cmd == "search":
        query = " ".join(sys.argv[2:])
        results = ltm.search(query)
        print(f"Search: '{query}'")
        print(f"Results: {len(results)}")
        for r in results:
            print(f"\n  [{r.doc_type}] score={r.score:.3f}")
            print(f"  {r.text[:200]}...")
    
    elif cmd == "ask":
        question = " ".join(sys.argv[2:])
        print(ltm.ask(question))
    
    elif cmd == "stats":
        stats = ltm.stats()
        print("Memory Stats:")
        print(f"  Model: {stats['embedding_model']} ({stats['embedding_dimension']}d)")
        print("  Collections:")
        for name, count in stats["collections"].items():
            print(f"    {name}: {count}")
    
    else:
        print(f"Unknown command: {cmd}")
        sys.exit(1)
