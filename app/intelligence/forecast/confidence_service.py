"""
Adaptive Trust Scoring - Confidence Service
Multi-source confidence model with explainability.
"""

import sqlite3
from typing import Dict


class ConfidenceService:
    """
    Calculates multi-dimensional confidence scores.
    Provides transparent scoring with human-readable explanations.
    """
    
    def __init__(self, db_path: str):
        self.db_path = db_path
    
    def calculate_scores(self, message_id: int) -> Dict:
        """
        Generate comprehensive confidence scores from multiple sources.
        Returns weighted aggregate with explanations.
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT m.*, f.mutation_count, 
                   (SELECT COUNT(*) FROM messages WHERE family_id = f.id) as family_size
            FROM messages m
            LEFT JOIN families f ON m.family_id = f.id
            WHERE m.id = ?
        ''', (message_id,))
        
        message = cursor.fetchone()
        conn.close()
        
        if not message:
            return {'error': 'Message not found'}
        
        content = message['content'].lower()
        
        # Language confidence: based on pattern clarity
        lang_score, lang_reason = self._calculate_language_confidence(content)
        
        # Pattern confidence: based on DNA matching
        pattern_score, pattern_reason = self._calculate_pattern_confidence(message)
        
        # Network confidence: based on family connections
        network_score, network_reason = self._calculate_network_confidence(message)
        
        # Historical confidence: based on family data
        hist_score, hist_reason = self._calculate_historical_confidence(message)
        
        # Weighted aggregate
        weights = {'language': 0.3, 'pattern': 0.3, 'network': 0.2, 'historical': 0.2}
        aggregate = (
            lang_score * weights['language'] +
            pattern_score * weights['pattern'] +
            network_score * weights['network'] +
            hist_score * weights['historical']
        )
        
        return {
            'message_id': message_id,
            'aggregate_confidence': round(aggregate, 2),
            'scores': {
                'language': {'score': lang_score, 'explanation': lang_reason},
                'pattern': {'score': pattern_score, 'explanation': pattern_reason},
                'network': {'score': network_score, 'explanation': network_reason},
                'historical': {'score': hist_score, 'explanation': hist_reason}
            },
            'interpretation': self._interpret_confidence(aggregate),
            'limitations': 'Confidence scores are estimates. Always verify suspicious communications independently.'
        }
    
    def _calculate_language_confidence(self, content: str) -> tuple:
        """Assess clarity of scam patterns in language."""
        score = 0.5
        reasons = []
        
        # High-confidence indicators
        scam_phrases = ['verify your account', 'click here', 'urgent action', 'suspended']
        matches = sum(1 for phrase in scam_phrases if phrase in content)
        if matches >= 2:
            score += 0.3
            reasons.append(f'{matches} strong scam phrases detected')
        
        # Grammar issues (simplified check)
        if content.count('  ') > 2 or content.count('!') > 3:
            score += 0.1
            reasons.append('Unusual formatting patterns')
        
        return min(score, 1.0), ' | '.join(reasons) if reasons else 'Standard language patterns'
    
    def _calculate_pattern_confidence(self, message: Dict) -> tuple:
        """Assess DNA pattern match quality."""
        dna = message.get('dna_code', '')
        if not dna or dna == 'UNKNOWN':
            return 0.3, 'Weak pattern match'
        
        components = dna.split('-')
        score = min(len(components) / 5.0, 1.0)
        return score, f'{len(components)} pattern components identified'
    
    def _calculate_network_confidence(self, message: Dict) -> tuple:
        """Assess based on family network position."""
        family_size = message.get('family_size', 0)
        if family_size > 10:
            return 0.8, f'Large family ({family_size} members) - well-documented pattern'
        elif family_size > 3:
            return 0.6, f'Medium family ({family_size} members)'
        else:
            return 0.4, f'Small family ({family_size} members) - limited samples'
    
    def _calculate_historical_confidence(self, message: Dict) -> tuple:
        """Assess based on mutation history."""
        mutations = message.get('mutation_count', 0)
        if mutations > 5:
            return 0.7, f'{mutations} mutations tracked - active variant'
        elif mutations > 0:
            return 0.6, f'{mutations} mutations observed'
        else:
            return 0.5, 'Original variant - no mutation history'
    
    def _interpret_confidence(self, score: float) -> str:
        """Provide human-readable confidence interpretation."""
        if score >= 0.8:
            return 'High confidence - strong match to known patterns'
        elif score >= 0.6:
            return 'Moderate confidence - matches typical characteristics'
        elif score >= 0.4:
            return 'Low confidence - limited pattern matches'
        else:
            return 'Very low confidence - uncertain classification'
