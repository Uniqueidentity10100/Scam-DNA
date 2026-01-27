"""
Region Service - Regional Adaptation Layer
Tracks geographic and linguistic patterns in scams.
"""

import sqlite3
from typing import Dict, List
import re


class RegionService:
    """
    Analyzes regional and linguistic characteristics of scams.
    Maps cultural adaptation patterns.
    """
    
    # Regional indicators (simplified for prototype)
    REGIONAL_MARKERS = {
        'North America': {
            'currency': ['$', 'USD', 'dollar'],
            'formats': ['SSN', 'ZIP', '###-##-####'],
            'organizations': ['IRS', 'Social Security', 'Amazon', 'PayPal']
        },
        'Europe': {
            'currency': ['€', 'EUR', 'euro', '£', 'GBP'],
            'formats': ['VAT', 'IBAN'],
            'organizations': ['HMRC', 'Europol']
        },
        'Asia-Pacific': {
            'currency': ['¥', 'yuan', 'yen', 'rupee'],
            'formats': [],
            'organizations': ['Alibaba', 'WeChat']
        },
        'Global': {
            'currency': [],
            'formats': [],
            'organizations': ['WHO', 'UN', 'Microsoft', 'Google']
        }
    }
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._ensure_tables()
    
    def _ensure_tables(self):
        """Create regional tracking tables."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS regional_profiles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                family_id INTEGER UNIQUE,
                primary_region TEXT,
                language_style TEXT,
                cultural_hooks TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (family_id) REFERENCES families(id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def classify_region(self, message_id: int) -> Dict:
        """
        Classify message's likely target region.
        Returns region and supporting evidence.
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('SELECT content, family_id FROM messages WHERE id = ?', (message_id,))
        message = cursor.fetchone()
        conn.close()
        
        if not message:
            return {'error': 'Message not found'}
        
        content = message['content']
        
        # Score each region
        region_scores = {}
        evidence = {}
        
        for region, markers in self.REGIONAL_MARKERS.items():
            score = 0
            found = []
            
            for currency in markers['currency']:
                if currency in content:
                    score += 3
                    found.append(f'Currency: {currency}')
            
            for org in markers['organizations']:
                if org.lower() in content.lower():
                    score += 2
                    found.append(f'Organization: {org}')
            
            for fmt in markers['formats']:
                if fmt in content:
                    score += 1
                    found.append(f'Format: {fmt}')
            
            if score > 0:
                region_scores[region] = score
                evidence[region] = found
        
        # Determine primary region
        if not region_scores:
            primary_region = 'Unknown'
            confidence = 0.0
        else:
            primary_region = max(region_scores.keys(), key=lambda k: region_scores[k])
            total_score = sum(region_scores.values())
            confidence = region_scores[primary_region] / total_score if total_score > 0 else 0
        
        return {
            'message_id': message_id,
            'primary_region': primary_region,
            'confidence': round(confidence, 2),
            'evidence': evidence.get(primary_region, []),
            'all_regions': region_scores
        }
    
    def get_family_regional_profile(self, family_id: int) -> Dict:
        """
        Generate comprehensive regional profile for a family.
        Aggregates patterns across all family messages.
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Get all family messages
        cursor.execute('''
            SELECT id, content
            FROM messages
            WHERE family_id = ?
        ''', (family_id,))
        
        messages = cursor.fetchall()
        
        # Aggregate regional classifications
        region_counts = {}
        all_evidence = []
        
        for msg in messages:
            classification = self.classify_region(msg['id'])
            region = classification.get('primary_region', 'Unknown')
            region_counts[region] = region_counts.get(region, 0) + 1
            all_evidence.extend(classification.get('evidence', []))
        
        # Determine dominant region
        if region_counts and 'Unknown' in region_counts and len(region_counts) > 1:
            del region_counts['Unknown']
        
        dominant_region = max(region_counts.keys(), key=lambda k: region_counts[k]) if region_counts else 'Unknown'
        
        # Detect cultural hooks (simplified)
        cultural_hooks = self._detect_cultural_hooks(messages)
        
        conn.close()
        
        return {
            'family_id': family_id,
            'dominant_region': dominant_region,
            'regional_distribution': region_counts,
            'cultural_hooks': cultural_hooks[:10],
            'sample_count': len(messages)
        }
    
    def _detect_cultural_hooks(self, messages: List) -> List[str]:
        """Identify culturally-specific manipulation tactics."""
        hooks = set()
        all_content = ' '.join([m['content'].lower() for m in messages])
        
        # Authority patterns
        if any(auth in all_content for auth in ['government', 'tax', 'irs', 'hmrc']):
            hooks.add('Government authority appeal')
        
        # Financial urgency
        if any(fin in all_content for fin in ['account frozen', 'suspended', 'payment']):
            hooks.add('Financial threat')
        
        # Social proof
        if any(social in all_content for social in ['winner', 'selected', 'prize']):
            hooks.add('Reward/prize incentive')
        
        # Family/personal
        if any(pers in all_content for pers in ['family', 'loved one', 'emergency']):
            hooks.add('Personal/emotional appeal')
        
        return list(hooks)
    
    def compare_regions(self) -> Dict:
        """
        Compare scam patterns across regions.
        Returns comparative analysis.
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('SELECT id FROM families LIMIT 50')
        families = cursor.fetchall()
        conn.close()
        
        # Aggregate by region
        regional_stats = {}
        for family in families:
            profile = self.get_family_regional_profile(family['id'])
            region = profile['dominant_region']
            
            if region not in regional_stats:
                regional_stats[region] = {
                    'family_count': 0,
                    'cultural_hooks': set()
                }
            
            regional_stats[region]['family_count'] += 1
            regional_stats[region]['cultural_hooks'].update(profile['cultural_hooks'])
        
        # Convert sets to lists for JSON serialization
        for region in regional_stats:
            regional_stats[region]['cultural_hooks'] = list(regional_stats[region]['cultural_hooks'])
        
        return {
            'regional_breakdown': regional_stats,
            'total_regions': len(regional_stats),
            'note': 'Regional classification is based on content analysis and may not reflect actual origin'
        }
