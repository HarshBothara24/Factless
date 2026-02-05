"""
Step 5: Overconfidence Analysis Module

Detects overconfident language patterns that may indicate hallucination.
Analyzes absolute terms and absence of uncertainty markers.
"""

import re
from typing import List

from .base import BaseModule
from ..models import Sentence, OverconfidenceSignal, OverconfidenceResult
from ..config import FactlessConfig


class OverconfidenceModule(BaseModule):
    """Analyzes text for overconfident language patterns."""
    
    def __init__(self, config: FactlessConfig):
        super().__init__("OverconfidenceAnalysis")
        self.config = config
        self.absolute_terms = config.overconfidence.absolute_terms
        self.uncertainty_markers = config.overconfidence.uncertainty_markers
    
    def _process(self, sentences: List[Sentence]) -> OverconfidenceResult:
        """Analyze sentences for overconfidence signals."""
        if not sentences:
            self.log("No sentences to analyze")
            return OverconfidenceResult(
                module_name=self.module_name,
                processing_time_ms=0,
                overconfidence_signals=[],
                avg_confidence_score=0.0
            )
        
        overconfidence_signals = []
        confidence_scores = []
        
        for sentence in sentences:
            signal = self._analyze_sentence_confidence(sentence)
            if signal:
                overconfidence_signals.append(signal)
            
            confidence_scores.append(signal.confidence_score if signal else 0.0)
        
        avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0.0
        
        self.log(f"Found {len(overconfidence_signals)} overconfidence signals")
        self.log(f"Average confidence score: {avg_confidence:.3f}")
        
        return OverconfidenceResult(
            module_name=self.module_name,
            processing_time_ms=0,  # Set by base class
            overconfidence_signals=overconfidence_signals,
            avg_confidence_score=avg_confidence
        )
    
    def _analyze_sentence_confidence(self, sentence: Sentence) -> OverconfidenceSignal:
        """Analyze a single sentence for overconfidence."""
        text = sentence.text.lower()
        
        # Find absolute terms
        absolute_found = []
        for term in self.absolute_terms:
            if term.lower() in text:
                absolute_found.append(term)
        
        # Find uncertainty markers
        uncertainty_found = []
        for marker in self.uncertainty_markers:
            if marker.lower() in text:
                uncertainty_found.append(marker)
        
        # Calculate confidence score
        confidence_score = self._calculate_confidence_score(
            text, absolute_found, uncertainty_found
        )
        
        # Only create signal if there's significant overconfidence
        if confidence_score > 0.3:  # Threshold for reporting
            return OverconfidenceSignal(
                sentence_index=sentence.index,
                absolute_terms=absolute_found,
                confidence_score=confidence_score
            )
        
        return None
    
    def _calculate_confidence_score(self, text: str, absolute_terms: List[str], uncertainty_markers: List[str]) -> float:
        """Calculate overconfidence score for a sentence."""
        score = 0.0
        
        # Base score from absolute terms
        if absolute_terms:
            # Weight by strength of absolute terms
            strong_absolutes = ["impossible", "never", "always", "guaranteed", "100%", "zero chance"]
            medium_absolutes = ["definitely", "certainly", "absolutely", "completely"]
            
            for term in absolute_terms:
                if term.lower() in strong_absolutes:
                    score += 0.4
                elif term.lower() in medium_absolutes:
                    score += 0.3
                else:
                    score += 0.2
        
        # Penalty for uncertainty markers (reduces overconfidence)
        uncertainty_penalty = len(uncertainty_markers) * 0.15
        score = max(0.0, score - uncertainty_penalty)
        
        # Additional patterns that increase confidence score
        
        # Superlatives without qualification
        superlative_pattern = r'\b(best|worst|most|least|highest|lowest|greatest|smallest)\b'
        if re.search(superlative_pattern, text) and not uncertainty_markers:
            score += 0.2
        
        # Numerical precision without uncertainty
        precise_numbers = re.findall(r'\b\d+\.\d{2,}\b', text)  # Numbers with 2+ decimal places
        if precise_numbers and not uncertainty_markers:
            score += 0.15 * len(precise_numbers)
        
        # Claims about future with certainty
        future_certain = re.search(r'\b(will definitely|will certainly|guaranteed to)\b', text)
        if future_certain:
            score += 0.3
        
        # Universal quantifiers without hedging
        universal_pattern = r'\b(all|every|everyone|everything|nobody|nothing|none)\b'
        if re.search(universal_pattern, text) and not uncertainty_markers:
            score += 0.25
        
        # Excessive use of emphatic language
        emphatic_count = len(re.findall(r'\b(very|extremely|incredibly|amazingly|perfectly)\b', text))
        if emphatic_count > 1:
            score += 0.1 * emphatic_count
        
        # Cap the score at 1.0
        return min(1.0, score)
    
    def _create_error_result(self, error_message: str) -> OverconfidenceResult:
        """Create error result for overconfidence analysis."""
        return OverconfidenceResult(
            module_name=self.module_name,
            processing_time_ms=0,
            overconfidence_signals=[],
            avg_confidence_score=0.0
        )