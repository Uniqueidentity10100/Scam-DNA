"""Forecast module initialization"""
from .confidence_service import ConfidenceService
from .evolution_service import EvolutionService
from .region_service import RegionService
from .counter_service import CounterService

__all__ = ['ConfidenceService', 'EvolutionService', 'RegionService', 'CounterService']
