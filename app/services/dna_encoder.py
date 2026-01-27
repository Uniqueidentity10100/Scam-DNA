"""
Scam DNA Encoder - Core analysis engine

This service analyzes scam messages and extracts their "genetic code" -
patterns of emotional manipulation, structural markers, and linguistic tricks.
"""

import re
from typing import Dict, List, Tuple

class DNAEncoder:
    """
    Analyzes text to identify scam patterns and generate DNA codes.
    """
    
    def __init__(self):
        # Emotional signal patterns
        self.urgency_patterns = [
            r'\b(urgent|immediately|now|hurry|quick|limited time|expires|deadline|asap)\b',
            r'\b(act now|don\'t wait|last chance|final notice|today only)\b',
            r'\b(48 hours|24 hours|ending soon|while supplies last)\b'
        ]
        
        self.fear_patterns = [
            r'\b(suspended|locked|blocked|terminated|closed|cancelled|frozen)\b',
            r'\b(unusual activity|security alert|unauthorized|breach|compromised)\b',
            r'\b(lose access|will be deleted|consequences|legal action|arrest)\b'
        ]
        
        self.reward_patterns = [
            r'\b(won|winner|prize|reward|congratulations|selected|claim)\b',
            r'\b(free|bonus|gift|inheritance|lottery|jackpot)\b',
            r'\b(\$[\d,]+|million|thousand|cash|money|refund)\b'
        ]
        
        self.authority_patterns = [
            r'\b(bank|paypal|amazon|apple|microsoft|google|irs|fbi|police)\b',
            r'\b(official|verified|department|agency|customer service|support team)\b',
            r'\b(ceo|manager|director|officer|representative)\b'
        ]
        
        self.trust_patterns = [
            r'\b(trusted|secure|verified|legitimate|authorized|certified)\b',
            r'\b(protect|safety|security|guarantee)\b'
        ]
        
        # Structural markers
        self.link_pattern = r'(https?://|www\.|bit\.ly|tinyurl\.com)'
        self.payment_patterns = [
            r'\b(credit card|debit card|bank account|routing number|ssn|social security)\b',
            r'\b(wire transfer|western union|moneygram|bitcoin|crypto|wallet address)\b',
            r'\b(payment|pay now|send money|transfer funds)\b'
        ]
        
        self.identity_patterns = [
            r'\b(verify|confirm|update|validate) (your )?(account|identity|information|details)\b',
            r'\b(enter|provide|submit) (your )?(password|pin|credentials)\b'
        ]
        
        self.contact_switch_patterns = [
            r'\b(call|text|email|whatsapp|telegram) (me |us )?(at|on)\b',
            r'\b(reply to|respond to|contact us at)\b'
        ]
    
    def analyze(self, text: str) -> Tuple[str, Dict[str, List[str]], str]:
        """
        Analyze text and extract scam DNA.
        
        Args:
            text: Message text to analyze
            
        Returns:
            Tuple of (dna_code, signals_dict, category)
        """
        text_lower = text.lower()
        
        # Extract emotional signals
        emotional_signals = []
        if self._matches_patterns(text_lower, self.urgency_patterns):
            emotional_signals.append('urgency')
        if self._matches_patterns(text_lower, self.fear_patterns):
            emotional_signals.append('fear')
        if self._matches_patterns(text_lower, self.reward_patterns):
            emotional_signals.append('reward')
        if self._matches_patterns(text_lower, self.authority_patterns):
            emotional_signals.append('authority')
        if self._matches_patterns(text_lower, self.trust_patterns):
            emotional_signals.append('trust')
        
        # Extract structural markers
        structural_markers = []
        if re.search(self.link_pattern, text_lower):
            structural_markers.append('link')
        if self._matches_patterns(text_lower, self.payment_patterns):
            structural_markers.append('payment')
        if self._matches_patterns(text_lower, self.identity_patterns):
            structural_markers.append('identity')
        if self._matches_patterns(text_lower, self.contact_switch_patterns):
            structural_markers.append('contact_switch')
        
        # Extract linguistic patterns
        linguistic_patterns = []
        
        # Check for excessive capitalization
        caps_ratio = sum(1 for c in text if c.isupper()) / max(len(text), 1)
        if caps_ratio > 0.3:
            linguistic_patterns.append('excessive_caps')
        
        # Check for multiple exclamation marks
        if text.count('!') >= 3:
            linguistic_patterns.append('multiple_exclamations')
        
        # Check for poor grammar indicators
        if re.search(r'\b(kindly|do the needful|revert back)\b', text_lower):
            linguistic_patterns.append('unusual_phrasing')
        
        # Check for generic greetings
        if re.search(r'^(dear (customer|user|member|sir|madam)|hello there|greetings)', text_lower):
            linguistic_patterns.append('generic_greeting')
        
        # Generate DNA code
        dna_code = self._generate_dna_code(emotional_signals, structural_markers)
        
        # Determine category
        category = self._determine_category(emotional_signals, structural_markers)
        
        signals = {
            'emotional': emotional_signals,
            'structural': structural_markers,
            'linguistic': linguistic_patterns
        }
        
        return dna_code, signals, category
    
    def _matches_patterns(self, text: str, patterns: List[str]) -> bool:
        """Check if text matches any pattern in the list."""
        return any(re.search(pattern, text, re.IGNORECASE) for pattern in patterns)
    
    def _generate_dna_code(self, emotional: List[str], structural: List[str]) -> str:
        """
        Generate a DNA code from detected patterns.
        Format: EMO1-EMO2-STRUCT1-STRUCT2
        """
        code_parts = []
        
        # Add emotional signals (abbreviated)
        emotion_map = {
            'urgency': 'URG',
            'fear': 'FEAR',
            'reward': 'RWD',
            'authority': 'AUTH',
            'trust': 'TRST'
        }
        for emotion in emotional:
            if emotion in emotion_map:
                code_parts.append(emotion_map[emotion])
        
        # Add structural markers (abbreviated)
        structure_map = {
            'link': 'LNK',
            'payment': 'PAY',
            'identity': 'ID',
            'contact_switch': 'CSWT'
        }
        for structure in structural:
            if structure in structure_map:
                code_parts.append(structure_map[structure])
        
        return '-'.join(code_parts) if code_parts else 'UNK'
    
    def _determine_category(self, emotional: List[str], structural: List[str]) -> str:
        """
        Determine the most likely scam category based on patterns.
        """
        # Phishing: fear + authority + identity/link
        if 'fear' in emotional and 'authority' in emotional:
            if 'identity' in structural or 'link' in structural:
                return 'phishing'
        
        # Financial fraud: reward + payment
        if 'reward' in emotional and 'payment' in structural:
            return 'financial_fraud'
        
        # Tech support scam: fear + authority + contact_switch
        if 'fear' in emotional and 'contact_switch' in structural:
            return 'tech_support'
        
        # Romance/Trust scam: trust + payment
        if 'trust' in emotional and 'payment' in structural:
            return 'romance_scam'
        
        # Job/Crypto scam: reward + urgency
        if 'reward' in emotional and 'urgency' in emotional:
            return 'opportunity_scam'
        
        return 'general_scam'
