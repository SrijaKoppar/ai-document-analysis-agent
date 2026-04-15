from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import os
import pickle
from typing import List, Dict, Optional

class VectorStore:
    def __init__(self, index_path="vector_store/faiss_index.idx", data_path="vector_store/data.pkl"):
        self.index_path = index_path
        self.data_path = data_path
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        self.index = None
        self.data = []  # list of dicts: {text, metadata}

        os.makedirs(os.path.dirname(self.index_path), exist_ok=True)
        self._load_or_init_index()

    def _load_or_init_index(self):
        if os.path.exists(self.index_path) and os.path.exists(self.data_path):
            self.index = faiss.read_index(self.index_path)
            with open(self.data_path, "rb") as f:
                self.data = pickle.load(f)
        else:
            dim = self.embedding_model.get_sentence_embedding_dimension()
            self.index = faiss.IndexFlatL2(dim)
            self.data = []

    def add_texts(self, texts: List[str], metadatas: Optional[List[Dict]] = None):
        """
        Add a list of texts and optional metadata to the FAISS index.
        """
        embeddings = self.embedding_model.encode(texts, normalize_embeddings=True)
        embeddings = np.array(embeddings).astype('float32')

        self.index.add(embeddings)

        if metadatas is None:
            metadatas = [{}] * len(texts)

        for text, meta in zip(texts, metadatas):
            self.data.append({"text": text, "metadata": meta})

    def save(self):
        faiss.write_index(self.index, self.index_path)
        with open(self.data_path, "wb") as f:
            pickle.dump(self.data, f)

    def search(self, query: str, top_k: int = 3) -> List[Dict]:
        """
        Search for the most relevant texts given a query.
        Returns top_k text + metadata results.
        """
        query_embedding = self.embedding_model.encode([query], normalize_embeddings=True).astype('float32')
        distances, indices = self.index.search(query_embedding, top_k)

        results = []
        for idx in indices[0]:
            if idx < len(self.data):
                results.append(self.data[idx])
        return results

    def clear(self):
        """
        Clear the FAISS index and metadata cache.
        """
        dim = self.embedding_model.get_sentence_embedding_dimension()
        self.index = faiss.IndexFlatL2(dim)
        self.data = []
        self.save()

# ---------------------- 🔹 Helper functions for external use ----------------------

_vector_store = VectorStore()

def load_and_search(query: str, top_k: int = 3) -> List[str]:
    """
    Utility wrapper to use the singleton VectorStore for searching.
    Returns only the 'text' part of results for RAG chaining.
    """
    results = _vector_store.search(query, top_k=top_k)
    return [res["text"] for res in results]

def add_texts_to_store(texts: List[str], metadatas: Optional[List[Dict]] = None):
    """
    Utility wrapper to use the singleton VectorStore for adding data.
    """
    _vector_store.add_texts(texts, metadatas)
    _vector_store.save()

def clear_vector_store():
    """
    Utility wrapper to clear the vector store.
    """
    _vector_store.clear()