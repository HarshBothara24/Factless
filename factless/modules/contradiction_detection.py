"""
Step 3: Contradiction Detection Module

Detects semantic contradictions between claims using SBERT similarity.
No external knowledge - only internal semantic opposition detection.
"""

import numpy as np
from sentence_transformers import SentenceTransformer
from typing import List
from scipy.spatial.distance import cosine

from .base import BaseModule
from ..models import Claim, ContradictionPair, ContradictionDetectionResult
from ..config import FactlessConfig


class ContradictionDetectionModule(BaseModule):
    """Detects contradictions between claims using semantic similarity."""
    
    def __init__(self, config: FactlessConfig):
        super().__init__("ContradictionDetection")
        self.config = config
        self.similarity_threshold = config.contradiction.similarity_threshold
        self.opposition_threshold = config.contradiction.semantic_opposition_threshold
        
        # Load sentence transformer model
        try:
            self.sentence_model = SentenceTransformer('all-MiniLM-L6-v2')
            self.log("Loaded sentence transformer model")
        except Exception as e:
            self.log(f"Failed to load sentence transformer: {str(e)}", "ERROR")
            raise
    
    def _process(self, claims: List[Claim]) -> ContradictionDetectionResult:
        """Detect contradictions between claims."""
        if len(claims) < 2:
            self.log("Need at least 2 claims to detect contradictions")
            return ContradictionDetectionResult(
                module_name=self.module_name,
                processing_time_ms=0,
                contradictions=[],
                similarity_threshold=self.similarity_threshold
            )
        
        contradictions = []
        
        # Generate embeddings for all claims
        claim_texts = [claim.text for claim in claims]
        embeddings = self.sentence_model.encode(claim_texts)
        
        self.log(f"Generated embeddings for {len(claims)} claims")
        
        # Compare all pairs of claims
        for i in range(len(claims)):
            for j in range(i + 1, len(claims)):
                contradiction = self._check_contradiction_pair(
                    claims[i], claims[j], embeddings[i], embeddings[j], i, j
                )
                
                if contradiction:
                    contradictions.append(contradiction)
        
        self.log(f"Found {len(contradictions)} contradictions")
        
        return ContradictionDetectionResult(
            module_name=self.module_name,
            processing_time_ms=0,  # Set by base class
            contradictions=contradictions,
            similarity_threshold=self.similarity_threshold
        )
    
    def _check_contradiction_pair(
        self, 
        claim1: Claim, 
        claim2: Claim, 
        embedding1: np.ndarray, 
        embedding2: np.ndarray,
        index1: int,
        index2: int
    ) -> ContradictionPair:
        """Check if two claims contradict each other."""
        
        # Skip claims from the same sentence (unlikely to contradict)
        if claim1.sentence_index == claim2.sentence_index:
            return None
        
        # Calculate semantic similarity
        similarity = 1 - cosine(embedding1, embedding2)
        
        # High similarity but semantic opposition indicates contradiction
        if similarity > self.similarity_threshold:
            contradiction_type = self._classify_contradiction(claim1, claim2)
            
            if contradiction_type:
                self.log(f"Contradiction detected: '{claim1.text}' vs '{claim2.text}' (similarity: {similarity:.3f})")
                
                return ContradictionPair(
                    claim1_index=index1,
                    claim2_index=index2,
                    similarity_score=similarity,
                    contradiction_type=contradiction_type
                )
        
        return None
    
    def _classify_contradiction(self, claim1: Claim, claim2: Claim) -> str:
        """Classify the type of contradiction between two claims."""
        
        text1 = claim1.text.lower()
        text2 = claim2.text.lower()
        
        # Direct negation patterns
        negation_pairs = [
            ("is", "is not"), ("are", "are not"), ("was", "was not"), ("were", "were not"),
            ("can", "cannot"), ("will", "will not"), ("should", "should not"),
            ("always", "never"), ("all", "none"), ("every", "no"),
            ("possible", "impossible"), ("true", "false"), ("yes", "no")
        ]
        
        for pos, neg in negation_pairs:
            if (pos in text1 and neg in text2) or (neg in text1 and pos in text2):
                return "direct_negation"
        
        # Numerical contradictions
        if self._has_numerical_contradiction(text1, text2):
            return "numerical_contradiction"
        
        # Temporal contradictions
        if self._has_temporal_contradiction(text1, text2):
            return "temporal_contradiction"
        
        # Categorical contradictions (mutually exclusive categories)
        if self._has_categorical_contradiction(text1, text2):
            return "categorical_contradiction"
        
        return None
    
    def _has_numerical_contradiction(self, text1: str, text2: str) -> bool:
        """Check for contradictory numerical claims."""
        import re
        
        # Extract numbers from both texts
        numbers1 = re.findall(r'\d+(?:\.\d+)?', text1)
        numbers2 = re.findall(r'\d+(?:\.\d+)?', text2)
        
        if not numbers1 or not numbers2:
            return False
        
        # Look for contradictory numerical relationships
        # This is a simplified check - real implementation would be more sophisticated
        try:
            num1 = float(numbers1[0])
            num2 = float(numbers2[0])
            
            # Check for contradictory comparisons
            if ("more than" in text1 and "less than" in text2) or \
               ("greater than" in text1 and "smaller than" in text2) or \
               ("increase" in text1 and "decrease" in text2):
                return True
                
        except ValueError:
            pass
        
        return False
    
    def _has_temporal_contradiction(self, text1: str, text2: str) -> bool:
        """Check for contradictory temporal claims."""
        temporal_opposites = [
            ("before", "after"), ("earlier", "later"), ("past", "future"),
            ("yesterday", "tomorrow"), ("previous", "next"), ("old", "new")
        ]
        
        for early, late in temporal_opposites:
            if (early in text1 and late in text2) or (late in text1 and early in text2):
                return True
        
        return False
    
    def _has_categorical_contradiction(self, text1: str, text2: str) -> bool:
        """Check for mutually exclusive categorical claims."""
        exclusive_categories = [
            ["hot", "cold"], ["big", "small"], ["fast", "slow"],
            ["easy", "difficult"], ["safe", "dangerous"], ["cheap", "expensive"],
            ["public", "private"], ["open", "closed"], ["success", "failure"]
        ]
        
        for category in exclusive_categories:
            words_in_text1 = [word for word in category if word in text1]
            words_in_text2 = [word for word in category if word in text2]
            
            if words_in_text1 and words_in_text2 and words_in_text1 != words_in_text2:
                return True
        
        return False
    
    def _create_error_result(self, error_message: str) -> ContradictionDetectionResult:
        """Create error result for contradiction detection."""
        return ContradictionDetectionResult(
            module_name=self.module_name,
            processing_time_ms=0,
            contradictions=[],
            similarity_threshold=self.similarity_threshold
        )