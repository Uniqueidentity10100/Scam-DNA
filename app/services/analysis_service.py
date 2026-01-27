"""
Analysis service that coordinates DNA encoding and similarity detection
"""

from app.services.dna_encoder import DNAEncoder
from app.services.similarity_engine import SimilarityEngine
from app.models.database import get_db_connection
import json

class AnalysisService:
    """
    Coordinates the full analysis pipeline for scam messages.
    """
    
    def __init__(self, db_path):
        self.db_path = db_path
        self.encoder = DNAEncoder()
        self.similarity_engine = SimilarityEngine()
    
    def analyze_message(self, text: str) -> dict:
        """
        Perform complete analysis on a scam message.
        
        Args:
            text: Message text to analyze
            
        Returns:
            dict: Complete analysis results
        """
        # Step 1: Generate DNA code and extract patterns
        dna_code, signals, category = self.encoder.analyze(text)
        
        # Step 2: Generate semantic embedding
        embedding = self.similarity_engine.generate_embedding(text)
        embedding_str = self.similarity_engine.serialize_embedding(embedding)
        
        # Step 3: Find similar messages in database
        existing_messages = self._get_all_messages()
        match_result = self.similarity_engine.find_closest_match(embedding, existing_messages)
        
        family_id = None
        mutation_score = 0.0
        mutation_type = 'original'
        parent_message_id = None
        
        if match_result:
            closest_message, similarity = match_result
            mutation_score = self.similarity_engine.calculate_mutation_score(similarity)
            mutation_type = self.similarity_engine.determine_mutation_type(similarity)
            
            # If similar enough, assign to same family
            if similarity >= self.similarity_engine.SIMILARITY_THRESHOLD_FAMILY:
                family_id = closest_message['family_id']
                parent_message_id = closest_message['id']
            else:
                # Create new family
                family_id = self._create_family(dna_code, category)
        else:
            # First message - create new family
            family_id = self._create_family(dna_code, category)
        
        # Step 4: Store the message
        message_id = self._store_message(
            text, dna_code, category, signals, 
            embedding_str, family_id, mutation_score, mutation_type
        )
        
        # Step 5: Record mutation if applicable
        if parent_message_id and mutation_type != 'original':
            changed_elements = self.similarity_engine.identify_changed_elements(
                closest_message['dna_code'], dna_code
            )
            self._record_mutation(parent_message_id, message_id, mutation_score, changed_elements)
        
        return {
            'message_id': message_id,
            'dna_code': dna_code,
            'category': category,
            'signals': signals,
            'family_id': family_id,
            'mutation_type': mutation_type,
            'mutation_score': round(mutation_score, 3)
        }
    
    def _get_all_messages(self):
        """Retrieve all messages from database."""
        conn = get_db_connection(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM messages')
        messages = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return messages
    
    def _create_family(self, dna_code: str, category: str) -> int:
        """Create a new scam family."""
        conn = get_db_connection(self.db_path)
        cursor = conn.cursor()
        
        family_name = f"{category.upper()}_{dna_code[:15]}"
        description = f"Scam family characterized by {category} tactics"
        
        cursor.execute('''
            INSERT INTO families (name, description, primary_dna_code, member_count)
            VALUES (?, ?, ?, 0)
        ''', (family_name, description, dna_code))
        
        family_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return family_id
    
    def _store_message(self, content, dna_code, category, signals, 
                       embedding_str, family_id, mutation_score, mutation_type):
        """Store analyzed message in database."""
        conn = get_db_connection(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO messages (
                content, dna_code, category, emotional_signals, 
                structural_markers, linguistic_patterns, embedding_vector,
                family_id, mutation_score, mutation_type
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            content, dna_code, category,
            json.dumps(signals['emotional']),
            json.dumps(signals['structural']),
            json.dumps(signals['linguistic']),
            embedding_str,
            family_id,
            mutation_score,
            mutation_type
        ))
        
        message_id = cursor.lastrowid
        
        # Update family member count
        cursor.execute('''
            UPDATE families 
            SET member_count = member_count + 1,
                last_seen = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (family_id,))
        
        conn.commit()
        conn.close()
        
        return message_id
    
    def _record_mutation(self, parent_id, child_id, mutation_score, changed_elements):
        """Record a mutation event."""
        conn = get_db_connection(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO mutations (parent_message_id, child_message_id, mutation_score, changed_elements)
            VALUES (?, ?, ?, ?)
        ''', (parent_id, child_id, mutation_score, json.dumps(changed_elements)))
        
        conn.commit()
        conn.close()
