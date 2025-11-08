"""
FAISS Vector Store
Fast semantic search for skill profiles using FAISS
"""
import faiss
import numpy as np
from typing import List, Dict, Optional
from sentence_transformers import SentenceTransformer


class FAISSVectorStore:
    """FAISS-based vector store for skill profile indexing"""

    def __init__(self, embedding_model: str = "all-MiniLM-L6-v2"):
        """
        Initialize FAISS vector store

        Args:
            embedding_model: Sentence transformer model name
        """
        self.encoder = SentenceTransformer(embedding_model)
        self.dimension = 384  # all-MiniLM-L6-v2 dimension
        self.index = faiss.IndexFlatL2(self.dimension)
        self.documents = []
        self._is_indexed = False

    def add_documents(self, texts: List[str], metadatas: List[Dict]):
        """
        Add documents to the vector store

        Args:
            texts: List of text documents to index
            metadatas: List of metadata dicts for each document
        """
        if len(texts) != len(metadatas):
            raise ValueError("texts and metadatas must have same length")

        # Encode texts
        print(f"   Encoding {len(texts)} documents...")
        embeddings = self.encoder.encode(texts, show_progress_bar=False)

        # Add to FAISS index
        embeddings_array = np.array(embeddings).astype('float32')
        self.index.add(embeddings_array)

        # Store documents with metadata
        for text, metadata in zip(texts, metadatas):
            self.documents.append({
                "text": text,
                "metadata": metadata
            })

        self._is_indexed = True
        print(f"   ✓ Indexed {len(texts)} documents")

    def search(self, query: str, k: int = 5, filter_metadata: Optional[Dict] = None) -> List[Dict]:
        """
        Semantic search for relevant documents

        Args:
            query: Search query
            k: Number of results to return
            filter_metadata: Optional metadata filters

        Returns:
            List of documents with metadata and distances
        """
        if not self._is_indexed:
            return []

        # Encode query
        query_embedding = self.encoder.encode([query])
        query_array = np.array(query_embedding).astype('float32')

        # Search FAISS index
        distances, indices = self.index.search(query_array, min(k * 2, len(self.documents)))

        # Collect results
        results = []
        for idx, dist in zip(indices[0], distances[0]):
            if idx < len(self.documents):
                doc = self.documents[idx].copy()
                doc["distance"] = float(dist)
                doc["similarity"] = 1 / (1 + float(dist))  # Convert distance to similarity

                # Apply metadata filters if provided
                if filter_metadata:
                    if self._matches_filter(doc["metadata"], filter_metadata):
                        results.append(doc)
                else:
                    results.append(doc)

                if len(results) >= k:
                    break

        return results

    def _matches_filter(self, metadata: Dict, filter_dict: Dict) -> bool:
        """Check if metadata matches filter criteria"""
        for key, value in filter_dict.items():
            if key not in metadata:
                return False

            if isinstance(value, dict):
                # Handle operators like {"$gte": 0.75}
                if "$gte" in value:
                    if metadata[key] < value["$gte"]:
                        return False
                elif "$lte" in value:
                    if metadata[key] > value["$lte"]:
                        return False
                elif "$in" in value:
                    if metadata[key] not in value["$in"]:
                        return False
            else:
                # Direct equality
                if metadata[key] != value:
                    return False

        return True

    def clear(self):
        """Clear the index and documents"""
        self.index = faiss.IndexFlatL2(self.dimension)
        self.documents = []
        self._is_indexed = False

    def get_stats(self) -> Dict:
        """Get index statistics"""
        return {
            "total_documents": len(self.documents),
            "index_size": self.index.ntotal,
            "dimension": self.dimension,
            "is_indexed": self._is_indexed
        }


# Example usage
if __name__ == "__main__":
    # Test vector store
    store = FAISSVectorStore()

    # Sample documents
    docs = [
        "Python programming language with 5 years experience",
        "JavaScript and React for web development",
        "Machine learning with TensorFlow and PyTorch",
        "Leadership and team management skills"
    ]

    metadatas = [
        {"type": "skill", "category": "technical", "confidence": 0.9},
        {"type": "skill", "category": "technical", "confidence": 0.85},
        {"type": "skill", "category": "technical", "confidence": 0.8},
        {"type": "skill", "category": "soft", "confidence": 0.75}
    ]

    # Index
    store.add_documents(docs, metadatas)

    # Search
    results = store.search("Does candidate know Python?", k=3)
    for r in results:
        print(f"Text: {r['text'][:50]}... | Similarity: {r['similarity']:.2f}")

    print("\nVector Store module loaded successfully")
