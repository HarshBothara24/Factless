"""
Step 6: Claim Density Analysis Module

Analyzes the density of claims per sentence.
High claim density can indicate hallucination or information overload.
"""

from typing import List

from .base import BaseModule
from ..models import Sentence, Claim, ClaimDensityResult
from ..config import FactlessConfig


class ClaimDensityModule(BaseModule):
    """Analyzes claim density as a hallucination risk indicator."""
    
    def __init__(self, config: FactlessConfig):
        super().__init__("ClaimDensityAnalysis")
        self.config = config
        self.high_density_threshold = config.claim_density.high_density_threshold
        self.very_high_density_threshold = config.claim_density.very_high_density_threshold
    
    def _process(self, sentences: List[Sentence], claims: List[Claim]) -> ClaimDensityResult:
        """Analyze claim density across the text."""
        if not sentences:
            self.log("No sentences to analyze")
            return ClaimDensityResult(
                module_name=self.module_name,
                processing_time_ms=0,
                claim_density=0.0,
                density_risk_score=0.0
            )
        
        if not claims:
            self.log("No claims found - density is zero")
            return ClaimDensityResult(
                module_name=self.module_name,
                processing_time_ms=0,
                claim_density=0.0,
                density_risk_score=0.0
            )
        
        # Calculate overall claim density
        claim_density = len(claims) / len(sentences)
        
        # Calculate per-sentence density distribution
        sentence_claim_counts = self._count_claims_per_sentence(sentences, claims)
        
        # Calculate risk score based on density patterns
        density_risk_score = self._calculate_density_risk_score(
            claim_density, sentence_claim_counts
        )
        
        self.log(f"Overall claim density: {claim_density:.2f} claims per sentence")
        self.log(f"Density risk score: {density_risk_score:.3f}")
        
        # Log high-density sentences
        for i, count in enumerate(sentence_claim_counts):
            if count >= self.high_density_threshold:
                self.log(f"High density in sentence {i}: {count} claims")
        
        return ClaimDensityResult(
            module_name=self.module_name,
            processing_time_ms=0,  # Set by base class
            claim_density=claim_density,
            density_risk_score=density_risk_score
        )
    
    def _count_claims_per_sentence(self, sentences: List[Sentence], claims: List[Claim]) -> List[int]:
        """Count claims per sentence."""
        sentence_counts = [0] * len(sentences)
        
        for claim in claims:
            if 0 <= claim.sentence_index < len(sentences):
                sentence_counts[claim.sentence_index] += 1
        
        return sentence_counts
    
    def _calculate_density_risk_score(self, overall_density: float, sentence_counts: List[int]) -> float:
        """Calculate risk score based on claim density patterns."""
        risk_score = 0.0
        
        # Base risk from overall density
        if overall_density >= self.very_high_density_threshold:
            risk_score += 0.6
        elif overall_density >= self.high_density_threshold:
            risk_score += 0.4
        elif overall_density >= 1.5:
            risk_score += 0.2
        
        # Additional risk from density spikes
        very_high_sentences = sum(1 for count in sentence_counts if count >= self.very_high_density_threshold)
        high_sentences = sum(1 for count in sentence_counts if count >= self.high_density_threshold)
        
        if very_high_sentences > 0:
            # Penalize very high density sentences more heavily
            spike_risk = min(0.3, very_high_sentences * 0.1)
            risk_score += spike_risk
            self.log(f"Found {very_high_sentences} very high density sentences")
        
        if high_sentences > len(sentence_counts) * 0.3:  # More than 30% of sentences are high density
            risk_score += 0.2
            self.log(f"High proportion of dense sentences: {high_sentences}/{len(sentence_counts)}")
        
        # Risk from density variance (inconsistent information flow)
        if len(sentence_counts) > 1:
            variance_risk = self._calculate_variance_risk(sentence_counts)
            risk_score += variance_risk
        
        # Cap at 1.0
        return min(1.0, risk_score)
    
    def _calculate_variance_risk(self, sentence_counts: List[int]) -> float:
        """Calculate risk from density variance."""
        if len(sentence_counts) <= 1:
            return 0.0
        
        # Calculate variance in claim density
        mean_count = sum(sentence_counts) / len(sentence_counts)
        variance = sum((count - mean_count) ** 2 for count in sentence_counts) / len(sentence_counts)
        
        # High variance indicates inconsistent information flow
        # This could suggest fabricated details mixed with normal text
        if variance > 2.0:  # Threshold for concerning variance
            variance_risk = min(0.2, variance * 0.05)
            self.log(f"High density variance detected: {variance:.2f}")
            return variance_risk
        
        return 0.0
    
    def _create_error_result(self, error_message: str) -> ClaimDensityResult:
        """Create error result for claim density analysis."""
        return ClaimDensityResult(
            module_name=self.module_name,
            processing_time_ms=0,
            claim_density=0.0,
            density_risk_score=0.0
        )