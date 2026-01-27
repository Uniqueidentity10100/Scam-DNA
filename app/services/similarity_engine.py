"""
Similarity & Mutation Engine

This service compares scam messages using semantic embeddings,
groups them into families, and tracks how scam tactics evolve over time.
"""

import numpy as np
from sentence_transformers import SentenceTransformer
import json
from typing import List, Tuple, Optional
from sklearn.metrics.pairwise import cosine_similarity

class SimilarityEngine:
    """
    Handles similarity comparison and mutation detection between scam messages.
    """
    
    def __init__(self):
        # Use a lightweight, efficient model for embeddings
        # This model is good for semantic similarity tasks
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Mutation thresholds
        self.SIMILARITY_THRESHOLD_FAMILY = 0.75  # Messages above this belong to same family
        self.SIMILARITY_THRESHOLD_MINOR = 0.85   # Above this is minor mutation
        
    def generate_embedding(self, text: str) -> np.ndarray:
        """
        Generate semantic embedding vector for text.
        
        Args:
            text: Message text
            
        Returns:
            numpy array: Embedding vector
        """
        embedding = self.model.encode(text, convert_to_numpy=True)
        return embedding
    
    def compute_similarity(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """
        Compute cosine similarity between two embeddings.
        
        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector
            
        Returns:
            float: Similarity score between 0 and 1
        """
        # Reshape for sklearn
        emb1 = embedding1.reshape(1, -1)
        emb2 = embedding2.reshape(1, -1)
        
        similarity = cosine_similarity(emb1, emb2)[0][0]
        return float(similarity)
    
    def find_closest_match(self, new_embedding: np.ndarray, 
                          existing_messages: List[dict]) -> Optional[Tuple[dict, float]]:
        """
        Find the closest matching message from existing database.
        
        Args:
            new_embedding: Embedding of the new message
            existing_messages: List of existing message dictionaries with embeddings
            
        Returns:
            Tuple of (closest_message, similarity_score) or None if no messages
        """
        if not existing_messages:
            return None
        
        best_match = None
        best_similarity = -1.0
        
        for msg in existing_messages:
            if msg.get('embedding_vector'):
                # Parse stored embedding
                stored_embedding = np.array(json.loads(msg['embedding_vector']))
                similarity = self.compute_similarity(new_embedding, stored_embedding)
                
                if similarity > best_similarity:
                    best_similarity = similarity
                    best_match = msg
        
        if best_match:
            return best_match, best_similarity
        return None
    
    def determine_mutation_type(self, similarity_score: float) -> str:
        """
        Classify the type of mutation based on similarity.
        
        Args:
            similarity_score: Similarity score between 0 and 1
            
        Returns:
            str: Mutation type classification
        """
        if similarity_score >= self.SIMILARITY_THRESHOLD_MINOR:
            return 'minor_mutation'
        elif similarity_score >= self.SIMILARITY_THRESHOLD_FAMILY:
            return 'major_mutation'
        else:
            return 'original'
    
    def calculate_mutation_score(self, similarity_score: float) -> float:
        """
        Convert similarity to mutation score.
        Higher mutation score = more different from parent.
        
        Args:
            similarity_score: Similarity between 0 and 1
            
        Returns:
            float: Mutation score (0 = identical, 1 = completely different)
        """
        return 1.0 - similarity_score
    
    def identify_changed_elements(self, dna_code1: str, dna_code2: str) -> List[str]:
        """
        Identify which DNA elements changed between two messages.
        
        Args:
            dna_code1: DNA code of first message
            dna_code2: DNA code of second message
            
        Returns:
            List of changed elements
        """
        elements1 = set(dna_code1.split('-'))
        elements2 = set(dna_code2.split('-'))
        
        added = elements2 - elements1
        removed = elements1 - elements2
        
        changes = []
        if added:
            changes.extend([f'added_{elem}' for elem in added])
        if removed:
            changes.extend([f'removed_{elem}' for elem in removed])
        
        return changes
    
    def serialize_embedding(self, embedding: np.ndarray) -> str:
        """
        Convert numpy embedding to JSON string for storage.
        
        Args:
            embedding: Numpy array embedding
            
        Returns:
            str: JSON serialized embedding
        """
        return json.dumps(embedding.tolist())
    
    def deserialize_embedding(self, embedding_str: str) -> np.ndarray:
        """
        Convert stored JSON string back to numpy array.
        
        Args:
            embedding_str: JSON string of embedding
            
        Returns:
            numpy array: Embedding vector
        """
        return np.array(json.loads(embedding_str))
