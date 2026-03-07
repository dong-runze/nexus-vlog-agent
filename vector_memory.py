import abc
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

class VectorRecord(BaseModel):
    id: str
    embedding: List[float]
    metadata: Optional[Dict[str, Any]] = None

class AbstractVectorDB(abc.ABC):
    """
    Abstract Base Class for Vector Database Interfaces.
    """
    
    @abc.abstractmethod
    async def insert(self, record: VectorRecord) -> bool:
        """Insert a new vector record into the database."""
        pass
        
    @abc.abstractmethod
    async def search(self, query_embedding: List[float], top_k: int = 5) -> List[VectorRecord]:
        """Search for the top_k most similar vectors to the query."""
        pass
        
    @abc.abstractmethod
    async def delete(self, record_id: str) -> bool:
        """Delete a record by its ID."""
        pass

import os
import json
import numpy as np

class LocalNumpyVectorDB(AbstractVectorDB):
    """
    A NumPy-backed local vector database with cosine similarity search and JSON persistence.
    """
    def __init__(self):
        self.file_path = "data/vlog_memory.json"
        self._storage: Dict[str, VectorRecord] = {}
        # Ensure directory exists
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
        self._load()
        
    def _load(self):
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for k, v in data.items():
                        self._storage[k] = VectorRecord(**v)
            except Exception as e:
                print(f"Error loading vector DB: {e}")
                
    def _save(self):
        try:
            with open(self.file_path, "w", encoding="utf-8") as f:
                # Use model_dump or dict based on pydantic version
                data = {k: v.model_dump() if hasattr(v, 'model_dump') else v.dict() for k, v in self._storage.items()}
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving vector DB: {e}")

    async def insert(self, record: VectorRecord) -> bool:
        self._storage[record.id] = record
        self._save()
        return True
        
    async def search(self, query_embedding: List[float], top_k: int = 5) -> List[VectorRecord]:
        if not self._storage:
            return []
            
        records = list(self._storage.values())
        embeddings = np.array([r.embedding for r in records])
        query_vec = np.array(query_embedding)
        
        # Calculate cosine similarity
        norm_embeddings = np.linalg.norm(embeddings, axis=1)
        norm_query = np.linalg.norm(query_vec)
        
        if norm_query == 0:
            return []
            
        valid_indices = norm_embeddings != 0
        similarities = np.zeros(len(records))
        
        if np.any(valid_indices):
            similarities[valid_indices] = np.dot(embeddings[valid_indices], query_vec) / (norm_embeddings[valid_indices] * norm_query)
            
        # Get top-k indices sorted descending
        top_indices = np.argsort(similarities)[::-1][:top_k]
        return [records[i] for i in top_indices]
        
    async def delete(self, record_id: str) -> bool:
        if record_id in self._storage:
            del self._storage[record_id]
            self._save()
            return True
        return False

class VertexAIVectorDB(AbstractVectorDB):
    """
    Production-ready Vector DB interface targeting Google Cloud Vertex AI Vector Search.
    """
    def __init__(self, project_id: str, location: str, index_endpoint: str, index_id: str):
        self.project_id = project_id
        self.location = location
        self.index_endpoint = index_endpoint
        self.index_id = index_id
        # In a real environment, we'd initialize the Vertex AI matching engine client here
        
    async def insert(self, record: VectorRecord) -> bool:
        # TODO: Implement insertion logic for Vertex AI Vector Search
        raise NotImplementedError("VertexAIVectorDB.insert is not fully implemented yet.")
        
    async def search(self, query_embedding: List[float], top_k: int = 5) -> List[VectorRecord]:
        # TODO: Implement search logic using Vertex AI Vector Search
        raise NotImplementedError("VertexAIVectorDB.search is not fully implemented yet.")
        
    async def delete(self, record_id: str) -> bool:
        # TODO: Implement deletion logic for Vertex AI
        raise NotImplementedError("VertexAIVectorDB.delete is not fully implemented yet.")
