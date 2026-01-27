"""
Institutional Mode Service
Multi-user analytics dashboard with aggregate metrics.
"""

import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List


class InstitutionService:
    """
    Provides institutional analytics and aggregate metrics.
    Enables org-level threat intelligence and awareness tracking.
    """
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._ensure_tables()
    
    def _ensure_tables(self):
        """Create institutional analytics tables."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS institutional_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                metric_date DATE,
                total_messages INTEGER,
                new_families INTEGER,
                high_confidence_detections INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(metric_date)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def get_dashboard_metrics(self, days: int = 7) -> Dict:
        """
        Generate institutional dashboard with key metrics.
        Provides weekly trends and awareness metrics.
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        
        # Message volume trend
        cursor.execute('''
            SELECT DATE(created_at) as date, COUNT(*) as count
            FROM messages
            WHERE created_at >= ?
            GROUP BY DATE(created_at)
            ORDER BY date
        ''', (start_date,))
        
        message_trend = cursor.fetchall()
        
        # Family growth
        cursor.execute('''
            SELECT COUNT(*) as total,
                   SUM(CASE WHEN created_at >= ? THEN 1 ELSE 0 END) as new
            FROM families
        ''', (start_date,))
        
        family_stats = cursor.fetchone()
        
        # Top families by activity
        cursor.execute('''
            SELECT f.id, f.name, COUNT(m.id) as message_count,
                   MAX(m.created_at) as last_seen
            FROM families f
            JOIN messages m ON f.id = m.family_id
            GROUP BY f.id
            ORDER BY message_count DESC
            LIMIT 10
        ''', ())
        
        top_families = cursor.fetchall()
        
        # Detection confidence distribution
        cursor.execute('''
            SELECT 
                CASE 
                    WHEN similarity_score >= 0.8 THEN 'High'
                    WHEN similarity_score >= 0.5 THEN 'Medium'
                    ELSE 'Low'
                END as confidence_level,
                COUNT(*) as count
            FROM messages
            WHERE created_at >= ?
            GROUP BY confidence_level
        ''', (start_date,))
        
        confidence_dist = cursor.fetchall()
        
        conn.close()
        
        return {
            'period': f'Last {days} days',
            'overview': {
                'total_messages_period': sum(row['count'] for row in message_trend),
                'total_families': family_stats['total'],
                'new_families_period': family_stats['new'],
                'avg_messages_per_day': round(sum(row['count'] for row in message_trend) / max(days, 1), 1)
            },
            'trends': {
                'daily_messages': [
                    {'date': row['date'], 'count': row['count']}
                    for row in message_trend
                ],
                'family_growth': family_stats['new']
            },
            'top_families': [
                {
                    'id': row['id'],
                    'name': row['name'],
                    'message_count': row['message_count'],
                    'last_seen': row['last_seen']
                }
                for row in top_families
            ],
            'confidence_distribution': {
                row['confidence_level']: row['count']
                for row in confidence_dist
            }
        }
    
    def generate_awareness_report(self) -> Dict:
        """
        Generate awareness and education metrics.
        Tracks system usage and pattern recognition.
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Pattern diversity
        cursor.execute('''
            SELECT COUNT(DISTINCT representative_dna) as unique_patterns
            FROM families
        ''')
        pattern_diversity = cursor.fetchone()['unique_patterns']
        
        # Most common attack stages (if behavioral analysis has run)
        cursor.execute('''
            SELECT stage, COUNT(*) as count
            FROM behavioral_stages
            GROUP BY stage
            ORDER BY count DESC
            LIMIT 5
        ''')
        common_stages = cursor.fetchall()
        
        # Regional distribution
        cursor.execute('''
            SELECT primary_region, COUNT(*) as count
            FROM regional_profiles
            GROUP BY primary_region
        ''')
        regions = cursor.fetchall()
        
        conn.close()
        
        return {
            'awareness_metrics': {
                'unique_scam_patterns': pattern_diversity,
                'attack_stages_identified': len(common_stages),
                'geographic_coverage': len(regions)
            },
            'common_attack_stages': [
                {'stage': row['stage'], 'frequency': row['count']}
                for row in common_stages
            ],
            'regional_distribution': [
                {'region': row['primary_region'], 'count': row['count']}
                for row in regions
            ],
            'recommendations': [
                f"Focus awareness on {common_stages[0]['stage']} stage - most frequent attack vector" if common_stages else "Collect more data",
                "Regularly review top scam families for evolving tactics",
                "Monitor regional adaptations for targeted education"
            ]
        }
    
    def export_summary_report(self, days: int = 30) -> Dict:
        """
        Generate exportable summary report.
        Comprehensive overview for institutional stakeholders.
        """
        dashboard = self.get_dashboard_metrics(days)
        awareness = self.generate_awareness_report()
        
        return {
            'report_metadata': {
                'title': 'SCAM DNA Institutional Summary',
                'generated_at': datetime.now().isoformat(),
                'period_days': days,
                'system_version': 'v2.0'
            },
            'executive_summary': {
                'total_threats_analyzed': dashboard['overview']['total_messages_period'],
                'unique_threat_families': dashboard['overview']['total_families'],
                'new_variants_detected': dashboard['overview']['new_families_period'],
                'pattern_diversity': awareness['awareness_metrics']['unique_scam_patterns']
            },
            'trending_threats': dashboard['top_families'][:5],
            'detection_confidence': dashboard['confidence_distribution'],
            'awareness_insights': awareness,
            'recommendations_for_action': [
                "Increase user education on top 3 scam families",
                "Monitor emerging variants (new families in period)",
                "Review detection confidence - investigate low-confidence cases",
                "Share intelligence with partner organizations"
            ],
            'disclaimers': [
                'This report is for internal educational use only',
                'Threat intelligence is based on submitted samples and may not be comprehensive',
                'Always verify suspicious communications independently',
                'Consult cybersecurity professionals for specific incidents'
            ]
        }
