"""
Scoring and explainability engine for FACTLESS.

Combines signals from all modules into final risk score and generates
human-readable explanations.
"""

import numpy as np
from typing import List
from datetime import datetime

from .models import (
    AnalysisResult, RiskLevel, Explanation,
    SentenceSegmentationResult, ClaimExtractionResult, ContradictionDetectionResult,
    LogicalFlowResult, OverconfidenceResult, ClaimDensityResult, EntityFabricationResult
)
from .config import FactlessConfig


class ScoringEngine:
    """Combines module signals into final risk assessment."""
    
    def __init__(self, config: FactlessConfig):
        self.config = config
        self.weights = config.module_weights
        self.thresholds = config.risk_thresholds
    
    def calculate_final_score(
        self,
        contradiction_result: ContradictionDetectionResult,
        logical_flow_result: LogicalFlowResult,
        overconfidence_result: OverconfidenceResult,
        claim_density_result: ClaimDensityResult,
        entity_fabrication_result: EntityFabricationResult
    ) -> float:
        """Calculate weighted final risk score."""
        
        # Extract individual module scores
        contradiction_score = len(contradiction_result.contradictions) * 0.25  # Increased from 0.2
        contradiction_score = min(1.0, contradiction_score)
        
        logical_flow_score = len(logical_flow_result.logical_flaws) * 0.20  # Increased from 0.15
        logical_flow_score = min(1.0, logical_flow_score)
        
        overconfidence_score = overconfidence_result.avg_confidence_score
        
        claim_density_score = claim_density_result.density_risk_score
        
        entity_fabrication_score = entity_fabrication_result.fabrication_risk_score
        
        # Weighted combination
        final_score = (
            self.weights.contradiction * contradiction_score +
            self.weights.logical_flow * logical_flow_score +
            self.weights.overconfidence * overconfidence_score +
            self.weights.claim_density * claim_density_score +
            self.weights.entity_fabrication * entity_fabrication_score
        )
        
        # Bonus multiplier if multiple high-risk signals detected
        high_risk_signals = 0
        if entity_fabrication_score > 0.6:
            high_risk_signals += 1
        if contradiction_score > 0.5:
            high_risk_signals += 1
        if overconfidence_score > 0.5:
            high_risk_signals += 1
        if claim_density_score > 0.7:
            high_risk_signals += 1
        
        # Apply multiplier for multiple high-risk signals
        if high_risk_signals >= 2:
            final_score = min(1.0, final_score * 1.15)  # 15% boost
        elif high_risk_signals >= 3:
            final_score = min(1.0, final_score * 1.25)  # 25% boost
        
        return min(1.0, final_score)
    
    def determine_risk_level(self, risk_score: float) -> RiskLevel:
        """Determine risk level category from score."""
        if risk_score < self.thresholds.low_threshold:
            return RiskLevel.LOW
        elif risk_score < self.thresholds.high_threshold:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.HIGH


class ExplainabilityGenerator:
    """Generates human-readable explanations for risk signals."""
    
    def __init__(self, config: FactlessConfig):
        self.config = config
    
    def generate_explanations(
        self,
        sentences: List,
        contradiction_result: ContradictionDetectionResult,
        logical_flow_result: LogicalFlowResult,
        overconfidence_result: OverconfidenceResult,
        claim_density_result: ClaimDensityResult,
        entity_fabrication_result: EntityFabricationResult
    ) -> List[Explanation]:
        """Generate explanations for all detected risk signals."""
        
        explanations = []
        
        # Contradiction explanations
        explanations.extend(self._explain_contradictions(contradiction_result))
        
        # Logical flow explanations
        explanations.extend(self._explain_logical_flaws(logical_flow_result))
        
        # Overconfidence explanations
        explanations.extend(self._explain_overconfidence(overconfidence_result))
        
        # Claim density explanations
        explanations.extend(self._explain_claim_density(claim_density_result))
        
        # Entity fabrication explanations
        explanations.extend(self._explain_entity_fabrication(entity_fabrication_result))
        
        return explanations
    
    def _explain_contradictions(self, result: ContradictionDetectionResult) -> List[Explanation]:
        """Generate explanations for contradictions."""
        explanations = []
        
        for contradiction in result.contradictions:
            explanation = Explanation(
                signal_type="contradiction",
                sentence_indices=[contradiction.claim1_index, contradiction.claim2_index],
                description=f"Contradiction detected between claims (type: {contradiction.contradiction_type}, similarity: {contradiction.similarity_score:.2f})",
                risk_contribution=0.2  # Each contradiction contributes this much risk
            )
            explanations.append(explanation)
        
        return explanations
    
    def _explain_logical_flaws(self, result: LogicalFlowResult) -> List[Explanation]:
        """Generate explanations for logical flaws."""
        explanations = []
        
        for flaw in result.logical_flaws:
            risk_contribution = self._calculate_logical_flaw_risk(flaw.flaw_type)
            
            explanation = Explanation(
                signal_type="logical_flaw",
                sentence_indices=flaw.sentence_indices,
                description=f"Logical flaw detected: {flaw.description}",
                risk_contribution=risk_contribution
            )
            explanations.append(explanation)
        
        return explanations
    
    def _explain_overconfidence(self, result: OverconfidenceResult) -> List[Explanation]:
        """Generate explanations for overconfidence signals."""
        explanations = []
        
        for signal in result.overconfidence_signals:
            terms_text = ", ".join(signal.absolute_terms) if signal.absolute_terms else "overconfident language"
            
            explanation = Explanation(
                signal_type="overconfidence",
                sentence_indices=[signal.sentence_index],
                description=f"Overconfident language detected: {terms_text} (confidence score: {signal.confidence_score:.2f})",
                risk_contribution=signal.confidence_score * 0.15  # Scale by confidence level
            )
            explanations.append(explanation)
        
        return explanations
    
    def _explain_claim_density(self, result: ClaimDensityResult) -> List[Explanation]:
        """Generate explanations for claim density issues."""
        explanations = []
        
        if result.density_risk_score > 0.3:
            explanation = Explanation(
                signal_type="claim_density",
                sentence_indices=[],  # Applies to whole text
                description=f"High claim density detected: {result.claim_density:.2f} claims per sentence (risk score: {result.density_risk_score:.2f})",
                risk_contribution=result.density_risk_score
            )
            explanations.append(explanation)
        
        return explanations
    
    def _explain_entity_fabrication(self, result: EntityFabricationResult) -> List[Explanation]:
        """Generate explanations for entity fabrication signals."""
        explanations = []
        
        # Calculate individual entity risk contributions based on severity
        for entity in result.suspicious_entities:
            reasons_text = ", ".join([r.replace('_', ' ') for r in entity.suspicion_reasons])
            
            # Calculate risk contribution based on suspicion types
            risk_contribution = 0.0
            for reason in entity.suspicion_reasons:
                if "academic_style_fabrication" in reason:
                    risk_contribution += 0.15
                elif "overly_specific_without_explanation" in reason:
                    risk_contribution += 0.12
                elif "sudden_unexplained_introduction" in reason:
                    risk_contribution += 0.10
                elif "matches_suspicious_pattern" in reason:
                    risk_contribution += 0.08
                else:
                    risk_contribution += 0.05
            
            # Cap at reasonable maximum
            risk_contribution = min(risk_contribution, 0.25)
            
            explanation = Explanation(
                signal_type="entity_fabrication",
                sentence_indices=[entity.sentence_index],
                description=f"Suspicious entity '{entity.entity}' ({entity.entity_type}): {reasons_text}",
                risk_contribution=risk_contribution
            )
            explanations.append(explanation)
        
        return explanations
    
    def _calculate_logical_flaw_risk(self, flaw_type: str) -> float:
        """Calculate risk contribution for different logical flaw types."""
        risk_weights = {
            "circular_reasoning": 0.25,
            "cause_effect_inversion": 0.20,
            "missing_assumption": 0.15,
            "insufficient_support": 0.10
        }
        
        return risk_weights.get(flaw_type, 0.10)


class FactlessScorer:
    """Main scoring coordinator for FACTLESS analysis."""
    
    def __init__(self, config: FactlessConfig):
        self.config = config
        self.scoring_engine = ScoringEngine(config)
        self.explainability_generator = ExplainabilityGenerator(config)
    
    def create_analysis_result(
        self,
        input_text: str,
        sentence_result: SentenceSegmentationResult,
        claim_result: ClaimExtractionResult,
        contradiction_result: ContradictionDetectionResult,
        logical_flow_result: LogicalFlowResult,
        overconfidence_result: OverconfidenceResult,
        claim_density_result: ClaimDensityResult,
        entity_fabrication_result: EntityFabricationResult,
        total_processing_time: float
    ) -> AnalysisResult:
        """Create final analysis result with scoring and explanations."""
        
        # Calculate final risk score
        risk_score = self.scoring_engine.calculate_final_score(
            contradiction_result,
            logical_flow_result,
            overconfidence_result,
            claim_density_result,
            entity_fabrication_result
        )
        
        # Determine risk level
        risk_level = self.scoring_engine.determine_risk_level(risk_score)
        
        # Generate explanations
        explanations = self.explainability_generator.generate_explanations(
            sentence_result.sentences,
            contradiction_result,
            logical_flow_result,
            overconfidence_result,
            claim_density_result,
            entity_fabrication_result
        )
        
        # Create final result
        return AnalysisResult(
            risk_score=risk_score,
            risk_level=risk_level,
            explanations=explanations,
            sentence_segmentation=sentence_result,
            claim_extraction=claim_result,
            contradiction_detection=contradiction_result,
            logical_flow=logical_flow_result,
            overconfidence_analysis=overconfidence_result,
            claim_density=claim_density_result,
            entity_fabrication=entity_fabrication_result,
            total_processing_time_ms=total_processing_time,
            input_text_length=len(input_text),
            analysis_timestamp=datetime.now().isoformat()
        )