"""
Counter-Strategy Generator
Defensive response engine with educational guidance.
"""

import sqlite3
from typing import Dict, List


class CounterService:
    """
    Generates defensive strategies and educational countermeasures.
    Provides verification checklists and safe response guidance.
    """
    
    def __init__(self, db_path: str):
        self.db_path = db_path
    
    def generate_countermeasures(self, family_id: int) -> Dict:
        """
        Create comprehensive protection playbook for a scam family.
        Returns verification checklist, response templates, and red flags.
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Get family data
        cursor.execute('''
            SELECT f.name, f.representative_dna,
                   COUNT(m.id) as message_count
            FROM families f
            LEFT JOIN messages m ON f.id = m.family_id
            WHERE f.id = ?
            GROUP BY f.id
        ''', (family_id,))
        
        family = cursor.fetchone()
        
        if not family:
            conn.close()
            return {'error': 'Family not found'}
        
        # Get sample messages to analyze patterns
        cursor.execute('''
            SELECT content FROM messages
            WHERE family_id = ?
            LIMIT 10
        ''', (family_id,))
        
        samples = cursor.fetchall()
        conn.close()
        
        # Analyze common patterns
        dna_components = family['representative_dna'].split('-')
        content_patterns = self._analyze_patterns(samples)
        
        # Generate strategies
        verification_checklist = self._generate_verification_checklist(dna_components, content_patterns)
        safe_responses = self._generate_safe_responses(content_patterns)
        red_flags = self._identify_red_flags(dna_components, content_patterns)
        
        return {
            'family_id': family_id,
            'family_name': family['name'],
            'protection_playbook': {
                'verification_checklist': verification_checklist,
                'safe_response_templates': safe_responses,
                'red_flag_summary': red_flags,
                'general_guidance': self._get_general_guidance()
            },
            'disclaimer': 'These are educational guidelines only. Always consult official sources when in doubt.'
        }
    
    def _analyze_patterns(self, samples: List) -> Dict:
        """Extract common tactical patterns from samples."""
        all_content = ' '.join([s['content'].lower() for s in samples])
        
        patterns = {
            'requests_action': any(action in all_content for action in ['click', 'verify', 'confirm', 'update']),
            'creates_urgency': any(urgent in all_content for urgent in ['urgent', 'immediately', 'expire', 'limited']),
            'requests_credentials': any(cred in all_content for cred in ['password', 'account number', 'ssn', 'pin']),
            'offers_reward': any(reward in all_content for reward in ['prize', 'winner', 'refund', 'gift']),
            'threatens_consequences': any(threat in all_content for threat in ['suspended', 'closed', 'penalty', 'legal']),
            'impersonates_authority': any(auth in all_content for auth in ['bank', 'government', 'official', 'department'])
        }
        
        return patterns
    
    def _generate_verification_checklist(self, dna_components: List, patterns: Dict) -> List[str]:
        """Create step-by-step verification checklist."""
        checklist = [
            "Verify sender identity through official channels (not links in the message)"
        ]
        
        if patterns.get('requests_action'):
            checklist.append("Do NOT click any links - navigate to the official website directly")
        
        if patterns.get('requests_credentials'):
            checklist.append("Confirm that legitimate organizations never request passwords via email/SMS")
        
        if patterns.get('creates_urgency'):
            checklist.append("Take time to verify - urgency is a manipulation tactic")
        
        if patterns.get('offers_reward'):
            checklist.append("Verify prize authenticity through official lottery/organization websites")
        
        if patterns.get('impersonates_authority'):
            checklist.append("Contact the organization directly using phone numbers from official websites")
        
        checklist.extend([
            "Check for spelling/grammar errors (common in scams)",
            "Verify email address matches official domain",
            "Search for the message text online to see if others reported it as a scam"
        ])
        
        return checklist
    
    def _generate_safe_responses(self, patterns: Dict) -> List[Dict]:
        """Generate appropriate response templates (educational, defensive only)."""
        responses = [
            {
                'scenario': 'Suspicious verification request',
                'template': 'I will verify this directly by contacting your organization through official channels.',
                'action': 'Delete the message and contact the organization using verified contact information'
            }
        ]
        
        if patterns.get('creates_urgency'):
            responses.append({
                'scenario': 'Urgent action demanded',
                'template': 'I need time to verify this request through official channels.',
                'action': 'Do not respond under pressure. Verify independently.'
            })
        
        if patterns.get('offers_reward'):
            responses.append({
                'scenario': 'Unexpected prize notification',
                'template': 'I did not enter any contests. I will verify through official channels.',
                'action': 'Research the organization. Legitimate prizes do not require fees or personal info upfront.'
            })
        
        responses.append({
            'scenario': 'General suspicious communication',
            'template': 'No response necessary',
            'action': 'Report to appropriate authorities (FTC, IC3, local law enforcement)'
        })
        
        return responses
    
    def _identify_red_flags(self, dna_components: List, patterns: Dict) -> List[str]:
        """Summarize key warning signs."""
        flags = []
        
        if 'URG' in dna_components or patterns.get('creates_urgency'):
            flags.append("Artificial urgency to bypass careful verification")
        
        if 'FEAR' in dna_components or patterns.get('threatens_consequences'):
            flags.append("Threats or fear tactics to compel immediate action")
        
        if patterns.get('requests_credentials'):
            flags.append("Requests for sensitive information (passwords, SSN, etc.)")
        
        if patterns.get('requests_action'):
            flags.append("Unsolicited links or attachments")
        
        if 'AUTH' in dna_components or patterns.get('impersonates_authority'):
            flags.append("Impersonation of trusted organizations")
        
        if patterns.get('offers_reward'):
            flags.append("Too-good-to-be-true offers or unexpected winnings")
        
        flags.append("Poor spelling/grammar or unusual formatting")
        flags.append("Generic greetings instead of personalized")
        
        return flags
    
    def _get_general_guidance(self) -> Dict:
        """Return general protective principles."""
        return {
            'core_principles': [
                "Verify independently - never trust unsolicited communications",
                "Legitimate organizations do not request sensitive info via email/SMS",
                "Take time - urgency is a manipulation tactic",
                "When in doubt, contact organizations directly using official contact info"
            ],
            'reporting': [
                "FTC: reportfraud.ftc.gov",
                "IC3 (Internet Crime Complaint Center): ic3.gov",
                "Local law enforcement for immediate threats"
            ],
            'note': 'These guidelines are educational. Trust your instincts and verify when uncertain.'
        }
