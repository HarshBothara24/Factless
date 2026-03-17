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
    LogicalFlowResult, OverconfidenceResult, ClaimDensityResult, EntityFabricationResult,
    PlausibilityAnalysisResult
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
        entity_fabrication_result: EntityFabricationResult,
        plausibility_result: PlausibilityAnalysisResult
    ) -> float:
        """Calculate weighted final risk score with new plausibility analysis."""
        
        # Extract individual module scores with improved scaling
        
        # Contradictions: Each contradiction is serious, scale more aggressively
        contradiction_count = len(contradiction_result.contradictions)
        if contradiction_count == 0:
            contradiction_score = 0.0
        elif contradiction_count == 1:
            contradiction_score = 0.4  # Single contradiction is already concerning
        elif contradiction_count == 2:
            contradiction_score = 0.7  # Two contradictions is high risk
        else:
            contradiction_score = 1.0  # Three or more is maximum risk
        
        # Logical flaws: Similar aggressive scaling
        logical_flaw_count = len(logical_flow_result.logical_flaws)
        if logical_flaw_count == 0:
            logical_flow_score = 0.0
        elif logical_flaw_count == 1:
            logical_flow_score = 0.3
        elif logical_flaw_count == 2:
            logical_flow_score = 0.6
        else:
            logical_flow_score = 1.0
        
        # Overconfidence: Use existing score but boost if very high
        overconfidence_score = overconfidence_result.avg_confidence_score
        if overconfidence_score > 0.7:
            overconfidence_score = min(1.0, overconfidence_score * 1.2)
        
        # Claim density: Use existing score
        claim_density_score = claim_density_result.density_risk_score
        
        # Entity fabrication: This is the key issue - boost significantly for multiple entities
        entity_fabrication_score = entity_fabrication_result.fabrication_risk_score
        suspicious_entity_count = len(entity_fabrication_result.suspicious_entities)
        
        # Boost entity fabrication score based on count and severity
        if suspicious_entity_count >= 4:  # 4+ suspicious entities = very high risk
            entity_fabrication_score = min(1.0, entity_fabrication_score * 1.5)
        elif suspicious_entity_count >= 2:  # 2-3 suspicious entities = high risk
            entity_fabrication_score = min(1.0, entity_fabrication_score * 1.3)
        
        # NEW: Plausibility analysis - this is the most important for detecting fabricated content
        plausibility_score = plausibility_result.plausibility_risk_score
        plausibility_signal_count = len(plausibility_result.signals)
        
        # Weighted combination with new plausibility analysis
        final_score = (
            self.weights.contradiction * contradiction_score +
            self.weights.logical_flow * logical_flow_score +
            self.weights.overconfidence * overconfidence_score +
            self.weights.claim_density * claim_density_score +
            self.weights.entity_fabrication * entity_fabrication_score +
            self.weights.plausibility_analysis * plausibility_score
        )
        
        # Hallucination amplification: If multiple modules detect issues, it's likely hallucinated
        active_modules = 0
        if contradiction_score > 0.2:
            active_modules += 1
        if logical_flow_score > 0.2:
            active_modules += 1
        if overconfidence_score > 0.3:
            active_modules += 1
        if claim_density_score > 0.3:
            active_modules += 1
        if entity_fabrication_score > 0.4:
            active_modules += 1
        if plausibility_score > 0.4:  # NEW
            active_modules += 1
        
        # Apply progressive multipliers for multiple active modules
        if active_modules >= 5:  # 5+ modules detecting issues = very likely hallucinated
            final_score = min(1.0, final_score * 1.5)
        elif active_modules >= 4:  # 4+ modules = very likely hallucinated
            final_score = min(1.0, final_score * 1.4)
        elif active_modules >= 3:  # 3 modules = likely hallucinated
            final_score = min(1.0, final_score * 1.25)
        elif active_modules >= 2:  # 2 modules = concerning
            final_score = min(1.0, final_score * 1.15)
        
        # Special case: If we have many suspicious entities (4+), this is almost certainly fabricated
        if suspicious_entity_count >= 4:
            final_score = max(final_score, 0.75)  # Minimum 0.75 for 4+ suspicious entities
        
        # NEW: Special case for plausibility issues - these are strong indicators of fabrication
        if plausibility_signal_count >= 5:
            final_score = max(final_score, 0.85)  # Minimum 0.85 for 5+ plausibility issues
        elif plausibility_signal_count >= 4:
            final_score = max(final_score, 0.80)  # Minimum 0.80 for 4+ plausibility issues
        elif plausibility_signal_count >= 3:
            final_score = max(final_score, 0.75)  # Minimum 0.75 for 3+ plausibility issues
        
        # Additional boost for very high plausibility scores (0.85+)
        if plausibility_score >= 0.85:
            final_score = max(final_score, 0.85)  # If plausibility module is very confident, trust it
        
        # Special case: High entity fabrication + high plausibility = almost certainly fabricated
        if entity_fabrication_score >= 0.8 and plausibility_score >= 0.8:
            final_score = max(final_score, 0.90)  # Both modules agree = very high confidence
        
        # NEW: Special combinations that strongly indicate fabrication
        timeline_mismatch = any(s.signal_type == "TIMELINE_MISMATCH" for s in plausibility_result.signals)
        impossible_tech = any(s.signal_type == "IMPOSSIBLE_TECH_COMBINATION" for s in plausibility_result.signals)
        
        if timeline_mismatch and impossible_tech:
            final_score = max(final_score, 0.80)  # Futuristic tech + past timeline = very suspicious
        
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
        entity_fabrication_result: EntityFabricationResult,
        plausibility_result: PlausibilityAnalysisResult
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
        
        # NEW: Plausibility explanations
        explanations.extend(self._explain_plausibility_issues(plausibility_result))
        
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
    
    def _explain_plausibility_issues(self, result: PlausibilityAnalysisResult) -> List[Explanation]:
        """Generate explanations for plausibility issues."""
        explanations = []
        
        for signal in result.signals:
            explanation = Explanation(
                signal_type="plausibility_issue",
                sentence_indices=[signal.sentence_index],
                description=signal.description,
                risk_contribution=signal.severity * 0.3  # Scale by severity
            )
            explanations.append(explanation)
        
        return explanations


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
        plausibility_result: PlausibilityAnalysisResult,
        total_processing_time: float
    ) -> AnalysisResult:
        """Create final analysis result with scoring and explanations."""
        
        # Calculate final risk score
        risk_score = self.scoring_engine.calculate_final_score(
            contradiction_result,
            logical_flow_result,
            overconfidence_result,
            claim_density_result,
            entity_fabrication_result,
            plausibility_result
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
            entity_fabrication_result,
            plausibility_result
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
            plausibility_analysis=plausibility_result,
            total_processing_time_ms=total_processing_time,
            input_text_length=len(input_text),
            analysis_timestamp=datetime.now().isoformat()
        )