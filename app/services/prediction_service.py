"""
Prediction and insights service

Analyzes mutation trends and generates defensive predictions
about how scam families may evolve.
"""

from app.models.database import get_db_connection
import json
from collections import Counter
from datetime import datetime, timedelta

class PredictionService:
    """
    Generates insights and predictions based on scam family evolution patterns.
    """
    
    def __init__(self, db_path):
        self.db_path = db_path
    
    def generate_family_insights(self, family_id: int) -> dict:
        """
        Generate insights for a specific scam family.
        
        Args:
            family_id: ID of the scam family
            
        Returns:
            dict: Insights about the family's evolution
        """
        conn = get_db_connection(self.db_path)
        cursor = conn.cursor()
        
        # Get family info
        cursor.execute('SELECT * FROM families WHERE id = ?', (family_id,))
        family = dict(cursor.fetchone())
        
        # Get all messages in family
        cursor.execute('''
            SELECT * FROM messages 
            WHERE family_id = ? 
            ORDER BY analyzed_at ASC
        ''', (family_id,))
        messages = [dict(row) for row in cursor.fetchall()]
        
        # Get mutations
        cursor.execute('''
            SELECT m.*, 
                   parent.dna_code as parent_dna,
                   child.dna_code as child_dna
            FROM mutations m
            JOIN messages parent ON m.parent_message_id = parent.id
            JOIN messages child ON m.child_message_id = child.id
            WHERE parent.family_id = ?
            ORDER BY m.detected_at ASC
        ''', (family_id,))
        mutations = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        
        # Analyze patterns
        emotional_trends = self._analyze_signal_trends(messages, 'emotional_signals')
        structural_trends = self._analyze_signal_trends(messages, 'structural_markers')
        
        # Calculate mutation velocity
        mutation_velocity = self._calculate_mutation_velocity(mutations)
        
        # Generate prediction
        prediction = self._generate_prediction(
            family, messages, mutations, emotional_trends, structural_trends
        )
        
        return {
            'family': family,
            'total_messages': len(messages),
            'total_mutations': len(mutations),
            'emotional_trends': emotional_trends,
            'structural_trends': structural_trends,
            'mutation_velocity': mutation_velocity,
            'prediction': prediction
        }
    
    def generate_global_insights(self) -> dict:
        """
        Generate system-wide insights across all families.
        
        Returns:
            dict: Global patterns and trends
        """
        conn = get_db_connection(self.db_path)
        cursor = conn.cursor()
        
        # Get category distribution
        cursor.execute('''
            SELECT category, COUNT(*) as count 
            FROM messages 
            GROUP BY category 
            ORDER BY count DESC
        ''')
        category_dist = [dict(row) for row in cursor.fetchall()]
        
        # Get most active families
        cursor.execute('''
            SELECT f.*, COUNT(m.id) as message_count
            FROM families f
            LEFT JOIN messages m ON f.id = m.family_id
            GROUP BY f.id
            ORDER BY message_count DESC
            LIMIT 10
        ''')
        top_families = [dict(row) for row in cursor.fetchall()]
        
        # Get mutation rate over time
        cursor.execute('''
            SELECT DATE(detected_at) as date, COUNT(*) as mutations
            FROM mutations
            GROUP BY DATE(detected_at)
            ORDER BY date DESC
            LIMIT 30
        ''')
        mutation_timeline = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        
        return {
            'category_distribution': category_dist,
            'top_families': top_families,
            'mutation_timeline': mutation_timeline,
            'recommendations': self._generate_recommendations(category_dist)
        }
    
    def _analyze_signal_trends(self, messages: list, signal_field: str) -> dict:
        """Analyze how a signal type changes over time."""
        all_signals = []
        for msg in messages:
            if msg.get(signal_field):
                signals = json.loads(msg[signal_field])
                all_signals.extend(signals)
        
        signal_counts = Counter(all_signals)
        return dict(signal_counts.most_common(10))
    
    def _calculate_mutation_velocity(self, mutations: list) -> float:
        """
        Calculate how quickly this family is mutating.
        Returns mutations per day.
        """
        if len(mutations) < 2:
            return 0.0
        
        first = datetime.fromisoformat(mutations[0]['detected_at'])
        last = datetime.fromisoformat(mutations[-1]['detected_at'])
        
        days_elapsed = (last - first).days or 1
        velocity = len(mutations) / days_elapsed
        
        return round(velocity, 2)
    
    def _generate_prediction(self, family, messages, mutations, 
                            emotional_trends, structural_trends) -> str:
        """
        Generate a defensive prediction about future evolution.
        """
        predictions = []
        
        # Analyze emotional evolution
        if 'urgency' in emotional_trends and emotional_trends['urgency'] > len(messages) * 0.5:
            predictions.append(
                "This family frequently uses time pressure tactics. "
                "Future variants may introduce fake countdown timers or expiration notices."
            )
        
        if 'authority' in emotional_trends:
            predictions.append(
                "Strong authority impersonation detected. "
                "Watch for variants that spoof additional organizations or government agencies."
            )
        
        # Analyze structural evolution
        if 'link' in structural_trends:
            predictions.append(
                "Link-based redirection is a core tactic. "
                "Expect increasingly sophisticated URL obfuscation and lookalike domains."
            )
        
        if 'payment' in structural_trends and 'identity' in structural_trends:
            predictions.append(
                "This family combines payment requests with credential harvesting. "
                "Future iterations may add multi-step verification processes to appear more legitimate."
            )
        
        # Analyze mutation patterns
        if len(mutations) > 5:
            avg_mutation_score = sum(m['mutation_score'] for m in mutations) / len(mutations)
            if avg_mutation_score > 0.3:
                predictions.append(
                    "High mutation rate observed. "
                    "This family is actively adapting, likely in response to detection methods."
                )
        
        if not predictions:
            predictions.append(
                "Limited evolution observed so far. "
                "Continue monitoring for changes in emotional triggers and structural patterns."
            )
        
        return " ".join(predictions)
    
    def _generate_recommendations(self, category_dist: list) -> list:
        """Generate defensive recommendations based on trends."""
        recommendations = []
        
        if not category_dist:
            return ["Continue collecting data to generate insights."]
        
        top_category = category_dist[0]['category']
        
        category_advice = {
            'phishing': "Enable multi-factor authentication and verify sender addresses before clicking links.",
            'financial_fraud': "Never send money to unverified recipients. Verify through official channels.",
            'tech_support': "Legitimate tech companies do not cold-call customers. Hang up and call official numbers.",
            'romance_scam': "Be cautious of online relationships that quickly move to financial discussions.",
            'opportunity_scam': "Research opportunities independently. If it sounds too good to be true, it probably is."
        }
        
        if top_category in category_advice:
            recommendations.append(category_advice[top_category])
        
        recommendations.append(
            "Always verify unexpected messages through official channels before taking action."
        )
        
        return recommendations
