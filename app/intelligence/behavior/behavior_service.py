"""
Behavioral Attack Modeling Engine
Classifies scam messages into attack stages and generates playbooks.
"""

import sqlite3
import re
from typing import Dict, List, Optional


class BehaviorService:
    """
    Analyzes scam tactics and classifies messages into attack stages.
    Maps the lifecycle of social engineering attacks.
    """
    
    # Attack stage definitions with pattern indicators
    STAGES = {
        'RECON': {
            'keywords': ['verify', 'confirm', 'account', 'security check', 'unusual activity'],
            'patterns': ['click here', 'review', 'validate'],
            'description': 'Information gathering phase'
        },
        'TRUST': {
            'keywords': ['official', 'department', 'representative', 'authorized', 'legitimate'],
            'patterns': ['we are', 'authorized', 'official'],
            'description': 'Authority establishment phase'
        },
        'BAIT': {
            'keywords': ['prize', 'won', 'selected', 'eligible', 'reward', 'refund'],
            'patterns': ['congratulations', 'lucky', 'winner'],
            'description': 'Incentive presentation phase'
        },
        'PRESSURE': {
            'keywords': ['urgent', 'immediately', 'expire', 'limited time', 'now', 'suspended'],
            'patterns': ['act now', 'within 24', 'last chance'],
            'description': 'Urgency creation phase'
        },
        'EXTRACTION': {
            'keywords': ['password', 'ssn', 'credit card', 'bank', 'payment', 'account number'],
            'patterns': ['enter your', 'provide', 'send'],
            'description': 'Data/money collection phase'
        }
    }
    
    def __init__(self, db_path: str):
        """Initialize with database path for stage tracking."""
        self.db_path = db_path
        self._ensure_tables()
    
    def _ensure_tables(self):
        """Create tables for behavioral tracking if they don't exist."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS behavioral_stages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                message_id INTEGER,
                family_id INTEGER,
                stage TEXT,
                confidence REAL,
                detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (message_id) REFERENCES messages(id),
                FOREIGN KEY (family_id) REFERENCES families(id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS playbooks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                family_id INTEGER UNIQUE,
                typical_flow TEXT,
                next_likely_stage TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (family_id) REFERENCES families(id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def classify_stage(self, message_id: int) -> Dict:
        """
        Classify a message into its attack stage.
        Returns stage classification with confidence and indicators.
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Get message content
        cursor.execute('SELECT content, family_id FROM messages WHERE id = ?', (message_id,))
        row = cursor.fetchone()
        
        if not row:
            conn.close()
            return {'error': 'Message not found'}
        
        content = row['content'].lower()
        family_id = row['family_id']
        
        # Score each stage
        stage_scores = {}
        for stage, indicators in self.STAGES.items():
            score = 0
            matched_indicators = []
            
            # Check keywords
            for keyword in indicators['keywords']:
                if keyword in content:
                    score += 2
                    matched_indicators.append(keyword)
            
            # Check patterns
            for pattern in indicators['patterns']:
                if pattern in content:
                    score += 3
                    matched_indicators.append(pattern)
            
            if score > 0:
                stage_scores[stage] = {
                    'score': score,
                    'indicators': matched_indicators
                }
        
        # Determine primary stage
        if not stage_scores:
            primary_stage = 'UNKNOWN'
            confidence = 0.0
            indicators = []
        else:
            primary_stage = max(stage_scores.keys(), key=lambda k: stage_scores[k]['score'])
            max_possible = len(self.STAGES[primary_stage]['keywords']) * 2 + \
                          len(self.STAGES[primary_stage]['patterns']) * 3
            confidence = min(stage_scores[primary_stage]['score'] / max_possible, 1.0)
            indicators = stage_scores[primary_stage]['indicators']
        
        # Store classification
        cursor.execute('''
            INSERT INTO behavioral_stages (message_id, family_id, stage, confidence)
            VALUES (?, ?, ?, ?)
        ''', (message_id, family_id, primary_stage, confidence))
        
        conn.commit()
        conn.close()
        
        return {
            'message_id': message_id,
            'primary_stage': primary_stage,
            'confidence': round(confidence, 2),
            'description': self.STAGES.get(primary_stage, {}).get('description', 'Unknown stage'),
            'matched_indicators': indicators[:5],  # Limit to 5 for display
            'all_stages': {k: v['score'] for k, v in stage_scores.items()}
        }
    
    def get_family_playbook(self, family_id: int) -> Dict:
        """
        Generate attack playbook for a scam family.
        Shows typical stage progression and predicted next steps.
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Get all stages for this family
        cursor.execute('''
            SELECT stage, COUNT(*) as count, AVG(confidence) as avg_conf
            FROM behavioral_stages
            WHERE family_id = ?
            GROUP BY stage
            ORDER BY count DESC
        ''', (family_id,))
        
        stage_frequency = cursor.fetchall()
        
        # Get chronological stage progression
        cursor.execute('''
            SELECT bs.stage, bs.detected_at, m.content
            FROM behavioral_stages bs
            JOIN messages m ON bs.message_id = m.id
            WHERE bs.family_id = ?
            ORDER BY bs.detected_at ASC
            LIMIT 50
        ''', (family_id,))
        
        timeline = cursor.fetchall()
        
        # Determine typical flow
        if timeline:
            typical_flow = ' → '.join([row['stage'] for row in timeline[:10]])
            
            # Predict next stage based on patterns
            stages_seen = [row['stage'] for row in timeline]
            last_stage = stages_seen[-1] if stages_seen else 'RECON'
            
            # Simple transition logic
            stage_order = ['RECON', 'TRUST', 'BAIT', 'PRESSURE', 'EXTRACTION']
            try:
                current_index = stage_order.index(last_stage)
                next_stage = stage_order[min(current_index + 1, len(stage_order) - 1)]
            except ValueError:
                next_stage = 'PRESSURE'
        else:
            typical_flow = 'Insufficient data'
            next_stage = 'RECON'
        
        # Store playbook
        cursor.execute('''
            INSERT OR REPLACE INTO playbooks (family_id, typical_flow, next_likely_stage)
            VALUES (?, ?, ?)
        ''', (family_id, typical_flow, next_stage))
        
        conn.commit()
        conn.close()
        
        return {
            'family_id': family_id,
            'typical_flow': typical_flow,
            'stage_frequency': [dict(row) for row in stage_frequency],
            'next_likely_stage': next_stage,
            'next_stage_description': self.STAGES.get(next_stage, {}).get('description', ''),
            'timeline': [
                {
                    'stage': row['stage'],
                    'timestamp': row['detected_at'],
                    'preview': row['content'][:100] + '...' if len(row['content']) > 100 else row['content']
                }
                for row in timeline[:10]
            ]
        }
    
    def get_defensive_guidance(self, stage: str) -> Dict:
        """
        Provide stage-specific defensive recommendations.
        Educational only, no instruction to engage.
        """
        guidance = {
            'RECON': {
                'warning': 'Attacker is gathering information',
                'indicators': ['Unexpected verification requests', 'Generic greetings', 'Pressure to confirm details'],
                'recommendation': 'Verify sender through official channels before responding'
            },
            'TRUST': {
                'warning': 'Attacker is establishing false authority',
                'indicators': ['Claims of official status', 'Use of logos/branding', 'Professional language'],
                'recommendation': 'Independently verify claimed affiliation through official contact methods'
            },
            'BAIT': {
                'warning': 'Attacker is offering false incentives',
                'indicators': ['Unexpected prizes', 'Too-good-to-be-true offers', 'Urgency to claim'],
                'recommendation': 'Remember: legitimate organizations do not require payment to receive prizes'
            },
            'PRESSURE': {
                'warning': 'Attacker is creating artificial urgency',
                'indicators': ['Countdown timers', 'Threats of account closure', 'Limited-time offers'],
                'recommendation': 'Legitimate services provide reasonable time for verification'
            },
            'EXTRACTION': {
                'warning': 'Attacker is attempting data/money collection',
                'indicators': ['Requests for passwords', 'Payment demands', 'Personal information requests'],
                'recommendation': 'Never provide sensitive information through unsolicited communications'
            }
        }
        
        return guidance.get(stage, {
            'warning': 'Unknown attack stage',
            'indicators': [],
            'recommendation': 'Exercise caution and verify through official channels'
        })
