"""
Data models for FACTLESS analysis results and internal structures.
"""

from enum import Enum
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class RiskLevel(str, Enum):
    """Risk level categories for hallucination assessment."""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class Sentence(BaseModel):
    """Individual sentence with metadata."""
    text: str
    index: int
    start_char: int
    end_char: int


class Claim(BaseModel):
    """Extracted claim from a sentence."""
    text: str
    sentence_index: int
    claim_type: str  # fact, guarantee, explanation, etc.
    confidence_markers: List[str] = Field(default_factory=list)


class ContradictionPair(BaseModel):
    """Pair of contradicting claims."""
    claim1_index: int
    claim2_index: int
    similarity_score: float
    contradiction_type: str


class LogicalFlaw(BaseModel):
    """Detected logical reasoning flaw."""
    flaw_type: str  # circular, cause_effect_inversion, missing_assumption
    sentence_indices: List[int]
    description: str


class OverconfidenceSignal(BaseModel):
    """Overconfidence indicators in text."""
    sentence_index: int
    absolute_terms: List[str]
    confidence_score: float  # 0-1, higher = more overconfident


class EntitySuspicion(BaseModel):
    """Suspicious entity detection."""
    entity: str
    entity_type: str
    sentence_index: int
    suspicion_reasons: List[str]


class ModuleResult(BaseModel):
    """Base class for module analysis results."""
    module_name: str
    processing_time_ms: float
    logs: List[str] = Field(default_factory=list)


class SentenceSegmentationResult(ModuleResult):
    """Results from sentence segmentation module."""
    sentences: List[Sentence]


class ClaimExtractionResult(ModuleResult):
    """Results from claim extraction module."""
    claims: List[Claim]
    llm_model: str
    llm_latency_ms: float


class ContradictionDetectionResult(ModuleResult):
    """Results from contradiction detection module."""
    contradictions: List[ContradictionPair]
    similarity_threshold: float


class LogicalFlowResult(ModuleResult):
    """Results from logical flow validation module."""
    logical_flaws: List[LogicalFlaw]


class OverconfidenceResult(ModuleResult):
    """Results from overconfidence analysis module."""
    overconfidence_signals: List[OverconfidenceSignal]
    avg_confidence_score: float


class ClaimDensityResult(ModuleResult):
    """Results from claim density analysis module."""
    claim_density: float  # claims per sentence
    density_risk_score: float  # 0-1


class EntityFabricationResult(ModuleResult):
    """Results from entity fabrication detection module."""
    suspicious_entities: List[EntitySuspicion]
    fabrication_risk_score: float  # 0-1


class Explanation(BaseModel):
    """Human-readable explanation of a risk signal."""
    signal_type: str
    sentence_indices: List[int]
    description: str
    risk_contribution: float  # 0-1


class AnalysisResult(BaseModel):
    """Final analysis result from FACTLESS."""
    risk_score: float = Field(..., ge=0.0, le=1.0, description="Overall hallucination risk score")
    risk_level: RiskLevel
    explanations: List[Explanation]
    
    # Module results for debugging/audit
    sentence_segmentation: SentenceSegmentationResult
    claim_extraction: ClaimExtractionResult
    contradiction_detection: ContradictionDetectionResult
    logical_flow: LogicalFlowResult
    overconfidence_analysis: OverconfidenceResult
    claim_density: ClaimDensityResult
    entity_fabrication: EntityFabricationResult
    
    # Metadata
    total_processing_time_ms: float
    input_text_length: int
    analysis_timestamp: str