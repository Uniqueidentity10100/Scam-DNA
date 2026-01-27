"""
Intelligence Controller
Coordinates all intelligence modules and provides unified interface.
"""

from app.intelligence.behavior.behavior_service import BehaviorService
from app.intelligence.network.network_service import NetworkService
from app.intelligence.forecast.confidence_service import ConfidenceService
from app.intelligence.forecast.evolution_service import EvolutionService
from app.intelligence.forecast.region_service import RegionService
from app.intelligence.forecast.counter_service import CounterService
from app.intelligence.evidence.evidence_service import EvidenceService
from app.intelligence.institutional.institution_service import InstitutionService


class IntelligenceController:
    """
    Central controller for all intelligence operations.
    Provides clean interface for threat analysis features.
    """
    
    def __init__(self, db_path):
        """Initialize all intelligence services with shared database."""
        self.behavior = BehaviorService(db_path)
        self.network = NetworkService(db_path)
        self.confidence = ConfidenceService(db_path)
        self.evolution = EvolutionService(db_path)
        self.region = RegionService(db_path)
        self.counter = CounterService(db_path)
        self.evidence = EvidenceService(db_path)
        self.institution = InstitutionService(db_path)
    
    def analyze_full_intelligence(self, message_id, family_id):
        """
        Generate comprehensive intelligence report for a message.
        Returns integrated analysis from all modules.
        """
        return {
            'behavioral_stage': self.behavior.classify_stage(message_id),
            'network_position': self.network.get_family_connections(family_id),
            'confidence_scores': self.confidence.calculate_scores(message_id),
            'counter_strategies': self.counter.generate_countermeasures(family_id)
        }
