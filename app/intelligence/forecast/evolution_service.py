"""
Evolution Service - Scam Mutation Replay System
Time-based replay of scam mutations with step-through visualization.
"""

import sqlite3
from typing import Dict, List
from datetime import datetime


class EvolutionService:
    """
    Tracks and replays scam evolution over time.
    Enables temporal analysis of mutation patterns.
    """
    
    def __init__(self, db_path: str):
        self.db_path = db_path
    
    def get_family_timeline(self, family_id: int) -> Dict:
        """
        Get chronological evolution of a scam family.
        Returns timestamped versions with mutation annotations.
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Get all messages in chronological order
        cursor.execute('''
            SELECT id, content, dna_code, similarity_score, created_at
            FROM messages
            WHERE family_id = ?
            ORDER BY created_at ASC
        ''', (family_id,))
        
        messages = cursor.fetchall()
        
        # Get mutations
        cursor.execute('''
            SELECT original_id, mutated_id, mutation_type, mutation_score, detected_at
            FROM mutations
            WHERE family_id = ?
            ORDER BY detected_at ASC
        ''', (family_id,))
        
        mutations = cursor.fetchall()
        conn.close()
        
        # Build timeline with annotations
        timeline = []
        for i, msg in enumerate(messages):
            # Find mutations involving this message
            related_mutations = [
                m for m in mutations 
                if m['mutated_id'] == msg['id'] or m['original_id'] == msg['id']
            ]
            
            # Detect changes from previous version
            changes = []
            if i > 0:
                prev_dna = messages[i-1]['dna_code']
                curr_dna = msg['dna_code']
                if prev_dna != curr_dna:
                    changes = self._detect_dna_changes(prev_dna, curr_dna)
            
            timeline.append({
                'step': i + 1,
                'message_id': msg['id'],
                'timestamp': msg['created_at'],
                'dna_code': msg['dna_code'],
                'preview': msg['content'][:150] + '...' if len(msg['content']) > 150 else msg['content'],
                'mutation_type': related_mutations[0]['mutation_type'] if related_mutations else 'original',
                'changes': changes,
                'is_significant': len(changes) >= 2 or any(m['mutation_score'] > 0.7 for m in related_mutations)
            })
        
        return {
            'family_id': family_id,
            'total_steps': len(timeline),
            'timeline': timeline,
            'summary': {
                'originals': sum(1 for t in timeline if t['mutation_type'] == 'original'),
                'minor_mutations': sum(1 for t in timeline if t['mutation_type'] == 'minor_mutation'),
                'major_mutations': sum(1 for t in timeline if t['mutation_type'] == 'major_mutation'),
                'significant_changes': sum(1 for t in timeline if t['is_significant'])
            }
        }
    
    def _detect_dna_changes(self, prev_dna: str, curr_dna: str) -> List[str]:
        """Identify specific DNA component changes."""
        prev_parts = set(prev_dna.split('-'))
        curr_parts = set(curr_dna.split('-'))
        
        added = curr_parts - prev_parts
        removed = prev_parts - curr_parts
        
        changes = []
        if added:
            changes.append(f'Added: {", ".join(added)}')
        if removed:
            changes.append(f'Removed: {", ".join(removed)}')
        
        return changes
    
    def get_step_detail(self, family_id: int, step: int) -> Dict:
        """
        Get detailed view of a specific evolution step.
        Returns full context and mutation analysis.
        """
        timeline = self.get_family_timeline(family_id)
        
        if step < 1 or step > len(timeline['timeline']):
            return {'error': 'Invalid step number'}
        
        step_data = timeline['timeline'][step - 1]
        
        # Get full message content
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('SELECT content FROM messages WHERE id = ?', 
                      (step_data['message_id'],))
        message = cursor.fetchone()
        conn.close()
        
        return {
            **step_data,
            'full_content': message['content'] if message else '',
            'context': {
                'previous_step': step - 1 if step > 1 else None,
                'next_step': step + 1 if step < len(timeline['timeline']) else None,
                'total_steps': len(timeline['timeline'])
            }
        }
