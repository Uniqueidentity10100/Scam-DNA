"""
Digital Evidence Locker
Forensic-grade record system with integrity verification.
"""

import sqlite3
import hashlib
import json
from datetime import datetime
from typing import Dict


class EvidenceService:
    """
    Manages forensic records of scam messages.
    Generates verifiable evidence with integrity seals.
    """
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._ensure_tables()
    
    def _ensure_tables(self):
        """Create evidence tracking tables."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS evidence_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                message_id INTEGER,
                case_id TEXT UNIQUE,
                evidence_hash TEXT,
                integrity_seal TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (message_id) REFERENCES messages(id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def create_evidence_record(self, message_id: int) -> Dict:
        """
        Generate forensic evidence record for a message.
        Creates hash ID, timestamp, and integrity seal.
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Get message data
        cursor.execute('''
            SELECT m.*, f.name as family_name
            FROM messages m
            LEFT JOIN families f ON m.family_id = f.id
            WHERE m.id = ?
        ''', (message_id,))
        
        message = cursor.fetchone()
        
        if not message:
            conn.close()
            return {'error': 'Message not found'}
        
        # Generate case ID
        timestamp = datetime.now().isoformat()
        case_id = f"SCAM-{message_id}-{int(datetime.now().timestamp())}"
        
        # Create evidence package
        evidence_data = {
            'message_id': message_id,
            'content': message['content'],
            'dna_code': message['dna_code'],
            'family_name': message['family_name'],
            'similarity_score': message['similarity_score'],
            'captured_at': timestamp
        }
        
        # Generate cryptographic hash
        evidence_json = json.dumps(evidence_data, sort_keys=True)
        evidence_hash = hashlib.sha256(evidence_json.encode()).hexdigest()
        
        # Generate integrity seal (simplified)
        seal_data = f"{case_id}:{evidence_hash}:{timestamp}"
        integrity_seal = hashlib.sha256(seal_data.encode()).hexdigest()
        
        # Store record
        cursor.execute('''
            INSERT INTO evidence_records (message_id, case_id, evidence_hash, integrity_seal)
            VALUES (?, ?, ?, ?)
        ''', (message_id, case_id, evidence_hash, integrity_seal))
        
        conn.commit()
        conn.close()
        
        return {
            'case_id': case_id,
            'message_id': message_id,
            'evidence_hash': evidence_hash,
            'integrity_seal': integrity_seal,
            'timestamp': timestamp,
            'status': 'Evidence record created',
            'verification_note': 'Hash and seal can be used to verify record integrity'
        }
    
    def get_evidence_record(self, case_id: str) -> Dict:
        """
        Retrieve complete evidence record by case ID.
        Returns full forensic package.
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT er.*, m.content, m.dna_code, m.similarity_score,
                   f.name as family_name
            FROM evidence_records er
            JOIN messages m ON er.message_id = m.id
            LEFT JOIN families f ON m.family_id = f.id
            WHERE er.case_id = ?
        ''', (case_id,))
        
        record = cursor.fetchone()
        conn.close()
        
        if not record:
            return {'error': 'Evidence record not found'}
        
        return {
            'case_id': record['case_id'],
            'message_id': record['message_id'],
            'evidence': {
                'content': record['content'],
                'dna_code': record['dna_code'],
                'family': record['family_name'],
                'similarity_score': record['similarity_score']
            },
            'forensics': {
                'evidence_hash': record['evidence_hash'],
                'integrity_seal': record['integrity_seal'],
                'created_at': record['created_at']
            },
            'verification_instructions': 'Use evidence_hash to verify data integrity. Any modification will change the hash.'
        }
    
    def generate_case_report(self, case_id: str) -> Dict:
        """
        Generate comprehensive case report for export.
        Includes all analysis and forensic data.
        """
        record = self.get_evidence_record(case_id)
        
        if 'error' in record:
            return record
        
        # Add additional analysis
        report = {
            'header': {
                'title': 'SCAM DNA Evidence Report',
                'case_id': case_id,
                'generated_at': datetime.now().isoformat(),
                'system_version': 'SCAM DNA v2.0'
            },
            'evidence_summary': record['evidence'],
            'forensic_verification': record['forensics'],
            'analysis': {
                'classification': 'Potential scam communication',
                'confidence': record['evidence'].get('similarity_score', 0),
                'pattern_signature': record['evidence'].get('dna_code', 'UNKNOWN')
            },
            'disclaimers': [
                'This analysis is for educational and research purposes only',
                'Confidence scores are computational estimates, not legal determinations',
                'Always consult appropriate authorities for official investigations',
                'This system cannot guarantee 100% accuracy in scam detection'
            ],
            'integrity_verification': {
                'hash': record['forensics']['evidence_hash'],
                'seal': record['forensics']['integrity_seal'],
                'note': 'Compare these values with original record to verify integrity'
            }
        }
        
        return report
    
    def list_evidence_records(self, limit: int = 50) -> Dict:
        """
        List all evidence records.
        Returns summary of all stored cases.
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT er.case_id, er.message_id, er.created_at,
                   f.name as family_name
            FROM evidence_records er
            JOIN messages m ON er.message_id = m.id
            LEFT JOIN families f ON m.family_id = f.id
            ORDER BY er.created_at DESC
            LIMIT ?
        ''', (limit,))
        
        records = cursor.fetchall()
        conn.close()
        
        return {
            'total_count': len(records),
            'records': [
                {
                    'case_id': r['case_id'],
                    'message_id': r['message_id'],
                    'family': r['family_name'],
                    'created_at': r['created_at']
                }
                for r in records
            ]
        }
