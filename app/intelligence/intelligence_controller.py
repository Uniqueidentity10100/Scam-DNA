"""
Intelligence Controller
Coordinates all intelligence modules and provides unified interface.
Acts as the central SOC-style orchestration layer.
"""

from app.intelligence.behavior.behavior_service import BehaviorService
from app.intelligence.network.network_service import NetworkService
from app.intelligence.forecast.confidence_service import ConfidenceService
from app.intelligence.forecast.evolution_service import EvolutionService
from app.intelligence.forecast.region_service import RegionService
from app.intelligence.forecast.counter_service import CounterService
from app.intelligence.evidence.evidence_service import EvidenceService
from app.intelligence.institutional.institution_service import InstitutionService
from app.intelligence.forecast.spam_gate import classify_message
from app.intelligence.forecast.risk_engine import calculate_risk

# Core analysis services
from app.services.dna_encoder import DNAEncoder
from app.services.similarity_engine import SimilarityEngine


class IntelligenceController:
    """
    Central controller for all intelligence operations.
    Provides a two-stage analysis pipeline:
    1. Spam Gate (SPAM / NOT_SPAM)
    2. Full Intelligence & Risk Analysis (for suspicious messages only)
    """

    def __init__(self):
        """Initialize all intelligence services with shared database."""
        self.db_path = 'data/scam_dna.db'
        self.behavior = BehaviorService(self.db_path)
        self.network = NetworkService(self.db_path)
        self.confidence = ConfidenceService(self.db_path)
        self.evolution = EvolutionService(self.db_path)
        self.region = RegionService(self.db_path)
        self.counter = CounterService(self.db_path)
        self.evidence = EvidenceService(self.db_path)
        self.institution = InstitutionService(self.db_path)

        # Core engines
        self.dna_encoder = DNAEncoder()
        self.similarity_engine = SimilarityEngine()

    # -------------------------
    # PRIMARY ENTRY POINT
    # -------------------------
    def analyze_message(self, message_text, message_id=None, family_id=None):
        """
        Main intelligence pipeline.
        Returns a unified, explainable analysis report.
        """

        # 1. Spam Gate
        spam_result = classify_message(message_text)

        report = {
            "spam_label": spam_result["label"],
            "spam_score": spam_result["score"],
            "spam_explanation": spam_result["explanation"]
        }

        # 2. Safe Exit for Legit Messages
        if spam_result["label"] == "NOT_SPAM":
            report.update({
                "status": "SAFE",
                "dna_code": None,
                "risk_label": "LOW",
                "risk_score": 0,
                "risk_explanation": [
                    "Message classified as legitimate.",
                    "No scam patterns or high-risk signals detected."
                ]
            })
            return report

        # -------------------------
        # 3. Deep Intelligence Path
        # -------------------------

        # DNA Encoding
        dna_code = self.dna_encoder.encode(message_text)

        # Behavioral Stage
        stage = self.behavior.classify_stage(message_text)

        # Similarity & Mutation
        similarity_score, mutation_level, detected_family_id = \
            self.similarity_engine.find_similarity(message_text)

        # Risk Calculation
        risk = calculate_risk(
            dna_code=dna_code,
            stage=stage,
            similarity_score=similarity_score,
            mutation_level=mutation_level
        )

        # Evidence Report
        evidence_id = self.evidence.create_case(
            message_text=message_text,
            dna_code=dna_code,
            risk_label=risk["label"]
        )

        # Counter Strategies
        counter_strategies = self.counter.generate_countermeasures(
            detected_family_id or family_id
        )

        # Network Intelligence
        network_position = self.network.get_family_connections(
            detected_family_id or family_id
        )

        # Evolution Timeline
        evolution_data = self.evolution.get_family_timeline(
            detected_family_id or family_id
        )

        # Confidence Breakdown
        confidence_scores = self.confidence.calculate_scores(
            message_text, dna_code, similarity_score
        )

        # -------------------------
        # 4. Unified Report
        # -------------------------
        report.update({
            "status": "SPAM",
            "dna_code": dna_code,
            "behavioral_stage": stage,
            "similarity_score": similarity_score,
            "mutation_level": mutation_level,
            "family_id": detected_family_id,
            "risk_label": risk["label"],
            "risk_score": risk["score"],
            "risk_explanation": risk["explanation"],
            "confidence_scores": confidence_scores,
            "network_position": network_position,
            "evolution_timeline": evolution_data,
            "counter_strategies": counter_strategies,
            "evidence_case_id": evidence_id
        })

        return report

    # -------------------------
    # LEGACY SUPPORT
    # -------------------------
    def analyze_full_intelligence(self, message_id, family_id):
        """
        Backward-compatible method for family-based analysis.
        """
        return {
            "behavioral_stage": self.behavior.classify_stage(message_id),
            "network_position": self.network.get_family_connections(family_id),
            "confidence_scores": self.confidence.calculate_scores(message_id),
            "counter_strategies": self.counter.generate_countermeasures(family_id)
        }
