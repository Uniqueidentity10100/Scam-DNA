"""
Scam Network Graph Service
Models relationships between scam families based on shared characteristics.
"""

import sqlite3
import re
from typing import Dict, List, Tuple
from collections import defaultdict
import math


class NetworkService:
    """
    Builds and analyzes relationship networks between scam families.
    Identifies hubs, clusters, and spreading patterns.
    """
    
    def __init__(self, db_path: str):
        """Initialize with database path."""
        self.db_path = db_path
        self._ensure_tables()
    
    def _ensure_tables(self):
        """Create network relationship tables."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS family_relationships (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                family_a_id INTEGER,
                family_b_id INTEGER,
                relationship_strength REAL,
                shared_keywords TEXT,
                shared_patterns TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (family_a_id) REFERENCES families(id),
                FOREIGN KEY (family_b_id) REFERENCES families(id),
                UNIQUE(family_a_id, family_b_id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def build_network(self):
        """
        Construct relationship network between all scam families.
        Uses multiple similarity signals.
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Get all families with their messages
        cursor.execute('''
            SELECT f.id, f.name, f.representative_dna, 
                   GROUP_CONCAT(m.content, '|||') as messages
            FROM families f
            LEFT JOIN messages m ON f.id = m.family_id
            GROUP BY f.id
        ''')
        
        families = cursor.fetchall()
        
        # Build pairwise relationships
        for i, family_a in enumerate(families):
            for family_b in families[i+1:]:
                strength, shared = self._calculate_relationship(
                    dict(family_a), dict(family_b)
                )
                
                if strength > 0.1:  # Only store significant relationships
                    cursor.execute('''
                        INSERT OR REPLACE INTO family_relationships 
                        (family_a_id, family_b_id, relationship_strength, 
                         shared_keywords, shared_patterns)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (
                        family_a['id'], 
                        family_b['id'], 
                        strength,
                        ','.join(shared['keywords'][:10]),
                        ','.join(shared['patterns'][:10])
                    ))
        
        conn.commit()
        conn.close()
    
    def _calculate_relationship(self, family_a: Dict, family_b: Dict) -> Tuple[float, Dict]:
        """
        Calculate relationship strength between two families.
        Returns strength score and shared characteristics.
        """
        shared = {'keywords': [], 'patterns': []}
        signals = []
        
        # DNA code similarity
        dna_a = set(family_a.get('representative_dna', '').split('-'))
        dna_b = set(family_b.get('representative_dna', '').split('-'))
        dna_overlap = len(dna_a & dna_b) / max(len(dna_a | dna_b), 1)
        signals.append(dna_overlap * 0.4)
        
        # Extract patterns from messages
        messages_a = family_a.get('messages', '').lower()
        messages_b = family_b.get('messages', '').lower()
        
        if messages_a and messages_b:
            # Domain patterns
            domains_a = set(re.findall(r'[\w-]+\.(?:com|net|org|info)', messages_a))
            domains_b = set(re.findall(r'[\w-]+\.(?:com|net|org|info)', messages_b))
            domain_overlap = len(domains_a & domains_b) / max(len(domains_a | domains_b), 1) if (domains_a or domains_b) else 0
            signals.append(domain_overlap * 0.2)
            if domains_a & domains_b:
                shared['patterns'].extend(list(domains_a & domains_b)[:5])
            
            # URL structures
            urls_a = set(re.findall(r'https?://[^\s]+', messages_a))
            urls_b = set(re.findall(r'https?://[^\s]+', messages_b))
            url_overlap = len(urls_a & urls_b) / max(len(urls_a | urls_b), 1) if (urls_a or urls_b) else 0
            signals.append(url_overlap * 0.15)
            
            # Keywords
            common_scam_words = ['urgent', 'verify', 'account', 'suspended', 'click', 'prize', 
                                'winner', 'payment', 'confirm', 'security']
            keywords_a = {w for w in common_scam_words if w in messages_a}
            keywords_b = {w for w in common_scam_words if w in messages_b}
            keyword_overlap = len(keywords_a & keywords_b) / max(len(keywords_a | keywords_b), 1) if (keywords_a or keywords_b) else 0
            signals.append(keyword_overlap * 0.25)
            shared['keywords'].extend(list(keywords_a & keywords_b))
        
        strength = sum(signals)
        return round(strength, 3), shared
    
    def get_family_connections(self, family_id: int) -> Dict:
        """
        Get all connections for a specific family.
        Returns neighboring families and relationship details.
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Get connected families
        cursor.execute('''
            SELECT 
                CASE 
                    WHEN family_a_id = ? THEN family_b_id
                    ELSE family_a_id
                END as connected_family_id,
                relationship_strength,
                shared_keywords,
                shared_patterns
            FROM family_relationships
            WHERE family_a_id = ? OR family_b_id = ?
            ORDER BY relationship_strength DESC
            LIMIT 20
        ''', (family_id, family_id, family_id))
        
        connections = cursor.fetchall()
        
        # Get family names
        connected_data = []
        for conn_row in connections:
            cursor.execute('SELECT name FROM families WHERE id = ?', 
                          (conn_row['connected_family_id'],))
            family = cursor.fetchone()
            if family:
                connected_data.append({
                    'family_id': conn_row['connected_family_id'],
                    'family_name': family['name'],
                    'strength': conn_row['relationship_strength'],
                    'shared_keywords': conn_row['shared_keywords'].split(',') if conn_row['shared_keywords'] else [],
                    'shared_patterns': conn_row['shared_patterns'].split(',') if conn_row['shared_patterns'] else []
                })
        
        conn.close()
        
        return {
            'family_id': family_id,
            'connections': connected_data,
            'connection_count': len(connected_data)
        }
    
    def get_network_graph(self) -> Dict:
        """
        Get complete network graph data for visualization.
        Returns nodes and edges with metadata.
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Get all families (nodes)
        cursor.execute('''
            SELECT f.id, f.name, COUNT(m.id) as message_count
            FROM families f
            LEFT JOIN messages m ON f.id = m.family_id
            GROUP BY f.id
        ''')
        families = cursor.fetchall()
        
        # Get all relationships (edges)
        cursor.execute('''
            SELECT family_a_id, family_b_id, relationship_strength
            FROM family_relationships
            WHERE relationship_strength > 0.2
            ORDER BY relationship_strength DESC
            LIMIT 100
        ''')
        relationships = cursor.fetchall()
        
        # Calculate centrality (simple degree centrality)
        degree_count = defaultdict(int)
        for rel in relationships:
            degree_count[rel['family_a_id']] += 1
            degree_count[rel['family_b_id']] += 1
        
        max_degree = max(degree_count.values()) if degree_count else 1
        
        nodes = []
        for family in families:
            degree = degree_count.get(family['id'], 0)
            nodes.append({
                'id': family['id'],
                'name': family['name'],
                'message_count': family['message_count'],
                'degree': degree,
                'centrality': round(degree / max_degree, 2),
                'is_hub': degree >= max_degree * 0.7
            })
        
        edges = [
            {
                'source': rel['family_a_id'],
                'target': rel['family_b_id'],
                'weight': rel['relationship_strength']
            }
            for rel in relationships
        ]
        
        conn.close()
        
        return {
            'nodes': nodes,
            'edges': edges,
            'stats': {
                'total_families': len(nodes),
                'total_relationships': len(edges),
                'hub_count': sum(1 for n in nodes if n['is_hub']),
                'avg_connections': round(len(edges) / len(nodes), 1) if nodes else 0
            }
        }
    
    def identify_hubs(self) -> List[Dict]:
        """
        Identify major hub families with high connectivity.
        These represent widely-used scam templates.
        """
        graph_data = self.get_network_graph()
        hubs = [n for n in graph_data['nodes'] if n['is_hub']]
        return sorted(hubs, key=lambda x: x['degree'], reverse=True)
    
    def detect_fast_spreaders(self) -> List[Dict]:
        """
        Detect families showing rapid growth in connections.
        Indicates emerging scam variants.
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Get families with recent relationship growth
        cursor.execute('''
            SELECT f.id, f.name, 
                   COUNT(DISTINCT fr.id) as total_connections,
                   COUNT(DISTINCT CASE 
                       WHEN fr.created_at >= datetime('now', '-7 days') 
                       THEN fr.id END) as recent_connections
            FROM families f
            LEFT JOIN family_relationships fr 
                ON f.id = fr.family_a_id OR f.id = fr.family_b_id
            GROUP BY f.id
            HAVING recent_connections > 0
            ORDER BY (CAST(recent_connections AS FLOAT) / NULLIF(total_connections, 0)) DESC
            LIMIT 10
        ''')
        
        spreaders = cursor.fetchall()
        conn.close()
        
        return [
            {
                'family_id': row['id'],
                'family_name': row['name'],
                'total_connections': row['total_connections'],
                'recent_connections': row['recent_connections'],
                'growth_rate': round(row['recent_connections'] / max(row['total_connections'], 1), 2)
            }
            for row in spreaders
        ]
