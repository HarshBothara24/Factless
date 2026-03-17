"""
Configuration settings for FACTLESS analysis engine.
"""

import os
from typing import Dict, Any
from pydantic import BaseModel


class ModuleWeights(BaseModel):
    """Weights for combining module scores into final risk score."""
    contradiction: float = 0.15
    logical_flow: float = 0.10
    overconfidence: float = 0.10
    claim_density: float = 0.10
    entity_fabrication: float = 0.25
    plausibility_analysis: float = 0.30  # NEW - highest weight for plausibility issues


class RiskThresholds(BaseModel):
    """Thresholds for risk level categorization."""
    low_threshold: float = 0.25  # Below this = LOW risk (lowered from 0.3)
    high_threshold: float = 0.60  # Above this = HIGH risk (lowered from 0.7)


class ContradictionConfig(BaseModel):
    """Configuration for contradiction detection."""
    similarity_threshold: float = 0.85  # SBERT similarity threshold
    semantic_opposition_threshold: float = 0.3  # Threshold for semantic opposition


class OverconfidenceConfig(BaseModel):
    """Configuration for overconfidence detection."""
    absolute_terms: list = [
        "always", "never", "guaranteed", "impossible", "certain", "definitely",
        "absolutely", "completely", "entirely", "perfectly", "exactly", "precisely",
        "undoubtedly", "unquestionably", "without doubt", "100%", "zero chance",
        "first ever", "world's first", "only", "sole", "unique", "exclusively",
        "invariably", "unfailingly", "infallibly"
    ]
    uncertainty_markers: list = [
        "might", "could", "may", "possibly", "perhaps", "likely", "probably",
        "seems", "appears", "suggests", "indicates", "approximately", "roughly",
        "around", "about", "typically", "generally", "usually", "often", "reportedly",
        "allegedly", "claimed", "purportedly"
    ]


class ClaimDensityConfig(BaseModel):
    """Configuration for claim density analysis."""
    high_density_threshold: float = 2.0  # Claims per sentence
    very_high_density_threshold: float = 3.0


class EntityFabricationConfig(BaseModel):
    """Configuration for entity fabrication detection."""
    suspicious_patterns: list = [
        r"et al\.",  # Academic citations
        r"\(\d{4}\)",  # Year citations
        r"Journal of \w+",  # Academic journals
        r"University of \w+",  # Universities
        r"Dr\. [A-Z][a-z]+ [A-Z][a-z]+",  # Doctor names
        r"[A-Z][a-z]+ et al\. \(\d{4}\)",  # Full citations
        r"world'?s? first",  # World's first claims
        r"first ever",  # First ever claims
        r"invented by [A-Z][a-z]+ [A-Z][a-z]+",  # Invention claims
        r"designed by [A-Z][a-z]+ [A-Z][a-z]+",  # Design claims
        r"discovered by [A-Z][a-z]+ [A-Z][a-z]+",  # Discovery claims
    ]
    min_entity_explanation_distance: int = 50  # Characters


class FactlessConfig(BaseModel):
    """Main configuration for FACTLESS system."""
    module_weights: ModuleWeights = ModuleWeights()
    risk_thresholds: RiskThresholds = RiskThresholds()
    contradiction: ContradictionConfig = ContradictionConfig()
    overconfidence: OverconfidenceConfig = OverconfidenceConfig()
    claim_density: ClaimDensityConfig = ClaimDensityConfig()
    entity_fabrication: EntityFabricationConfig = EntityFabricationConfig()
    
    # LLM settings for claim extraction
    claim_extraction_model: str = "gemini-2.5-flash"  # Configurable
    claim_extraction_temperature: float = 0.0
    claim_extraction_max_tokens: int = 200
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")  # Load from environment variable
    
    # Performance settings
    max_text_length: int = 10000  # Characters
    enable_detailed_logging: bool = True