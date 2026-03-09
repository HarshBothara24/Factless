"""
Step 7: Entity Fabrication Detection Module

Detects suspicious entities that may be fabricated.
Uses pattern-based detection without external knowledge lookup.
"""

import re
import spacy
from typing import List, Set, Dict
from collections import defaultdict

from .base import BaseModule
from ..models import Sentence, EntitySuspicion, EntityFabricationResult
from ..config import FactlessConfig


class EntityFabricationModule(BaseModule):
    """Detects potentially fabricated entities using pattern analysis."""
    
    def __init__(self, config: FactlessConfig):
        super().__init__("EntityFabrication")
        self.config = config
        self.suspicious_patterns = config.entity_fabrication.suspicious_patterns
        self.min_explanation_distance = config.entity_fabrication.min_entity_explanation_distance
        
        # Load SpaCy for NER
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            self.log("SpaCy model not found for entity detection", "ERROR")
            raise
    
    def _process(self, sentences: List[Sentence]) -> EntityFabricationResult:
        """Detect potentially fabricated entities."""
        if not sentences:
            self.log("No sentences to analyze")
            return EntityFabricationResult(
                module_name=self.module_name,
                processing_time_ms=0,
                suspicious_entities=[],
                fabrication_risk_score=0.0
            )
        
        # Extract all entities
        all_entities = self._extract_entities(sentences)
        
        # Analyze entities for fabrication signs
        suspicious_entities = []
        
        for entity_info in all_entities:
            suspicions = self._analyze_entity_suspicion(entity_info, sentences)
            if suspicions:
                suspicious_entities.append(EntitySuspicion(
                    entity=entity_info['text'],
                    entity_type=entity_info['label'],
                    sentence_index=entity_info['sentence_index'],
                    suspicion_reasons=suspicions
                ))
        
        # Calculate overall fabrication risk score
        fabrication_risk_score = self._calculate_fabrication_risk_score(
            suspicious_entities, len(all_entities)
        )
        
        self.log(f"Found {len(suspicious_entities)} suspicious entities out of {len(all_entities)} total")
        self.log(f"Fabrication risk score: {fabrication_risk_score:.3f}")
        
        return EntityFabricationResult(
            module_name=self.module_name,
            processing_time_ms=0,  # Set by base class
            suspicious_entities=suspicious_entities,
            fabrication_risk_score=fabrication_risk_score
        )
    
    def _extract_entities(self, sentences: List[Sentence]) -> List[Dict]:
        """Extract named entities from all sentences."""
        all_entities = []
        
        for sentence in sentences:
            doc = self.nlp(sentence.text)
            
            for ent in doc.ents:
                entity_info = {
                    'text': ent.text,
                    'label': ent.label_,
                    'start_char': ent.start_char,
                    'end_char': ent.end_char,
                    'sentence_index': sentence.index,
                    'sentence_text': sentence.text
                }
                all_entities.append(entity_info)
        
        self.log(f"Extracted {len(all_entities)} entities")
        return all_entities
    
    def _analyze_entity_suspicion(self, entity_info: Dict, sentences: List[Sentence]) -> List[str]:
        """Analyze an entity for fabrication indicators."""
        suspicions = []
        entity_text = entity_info['text']
        entity_type = entity_info['label']
        sentence_index = entity_info['sentence_index']
        
        # Check for suspicious patterns
        pattern_suspicions = self._check_suspicious_patterns(entity_text, entity_type)
        suspicions.extend(pattern_suspicions)
        
        # Check for overly specific entities without explanation
        if self._is_overly_specific_unexplained(entity_info, sentences):
            suspicions.append("overly_specific_without_explanation")
        
        # Check for academic-style fabrications
        if self._is_academic_fabrication(entity_text, entity_type):
            suspicions.append("academic_style_fabrication")
        
        # Check for sudden entity introduction
        if self._is_sudden_introduction(entity_info, sentences):
            suspicions.append("sudden_unexplained_introduction")
        
        # Check for inconsistent entity usage
        if self._has_inconsistent_usage(entity_info, sentences):
            suspicions.append("inconsistent_usage_pattern")
        
        # NEW: Check for superlative claims near entity
        if self._has_superlative_claim_nearby(entity_info, sentences):
            suspicions.append("superlative_claim_without_evidence")
        
        return suspicions
    
    def _has_superlative_claim_nearby(self, entity_info: Dict, sentences: List[Sentence]) -> bool:
        """Check if entity appears near superlative claims like 'world's first', 'fastest', etc."""
        sentence_index = entity_info['sentence_index']
        
        # Check current and adjacent sentences
        check_range = range(max(0, sentence_index - 1), min(len(sentences), sentence_index + 2))
        
        superlative_patterns = [
            r"world'?s first",
            r"world'?s only",
            r"world'?s largest",
            r"world'?s fastest",
            r"first ever",
            r"only.*in the world",
            r"fastest.*in history",
            r"most advanced",
            r"revolutionary",
            r"unprecedented",
            r"never before",
        ]
        
        for i in check_range:
            sentence_text = sentences[i].text.lower()
            for pattern in superlative_patterns:
                if re.search(pattern, sentence_text):
                    return True
        
        return False
    
    def _check_suspicious_patterns(self, entity_text: str, entity_type: str) -> List[str]:
        """Check entity against known suspicious patterns."""
        suspicions = []
        
        for pattern in self.suspicious_patterns:
            if re.search(pattern, entity_text, re.IGNORECASE):
                suspicions.append(f"matches_suspicious_pattern_{pattern}")
                self.log(f"Entity '{entity_text}' matches suspicious pattern: {pattern}")
        
        return suspicions
    
    def _is_overly_specific_unexplained(self, entity_info: Dict, sentences: List[Sentence]) -> bool:
        """Check if entity is overly specific without adequate explanation."""
        entity_text = entity_info['text']
        entity_type = entity_info['label']
        sentence_index = entity_info['sentence_index']
        
        # Look for very specific entities (long names, precise numbers, etc.)
        specificity_indicators = [
            len(entity_text) > 30,  # Very long entity names
            len(entity_text.split()) > 4,  # Multi-word complex names
            re.search(r'\d{4,}', entity_text),  # Long numbers (like years)
            re.search(r'\d+\.\d{3,}', entity_text),  # Very precise decimals
            re.search(r'\d{3,}\s*km/h', entity_text),  # Specific speeds
            re.search(r'\d{4}', entity_text) and entity_type == 'DATE',  # Historical dates
        ]
        
        # Historical dates (especially old ones) are highly suspicious without context
        if entity_type == 'DATE' and re.search(r'18\d{2}|19[0-4]\d', entity_text):
            specificity_indicators.append(True)
        
        if not any(specificity_indicators):
            return False
        
        # Check if there's adequate explanation nearby
        explanation_found = False
        
        # Check current and adjacent sentences for explanatory context
        check_range = range(max(0, sentence_index - 1), min(len(sentences), sentence_index + 2))
        
        for i in check_range:
            sentence_text = sentences[i].text.lower()
            
            # Look for explanatory phrases
            explanatory_phrases = [
                "according to", "based on", "research shows", "study found",
                "published in", "reported by", "data from", "source:",
                "reference:", "citation:", "documented in"
            ]
            
            if any(phrase in sentence_text for phrase in explanatory_phrases):
                explanation_found = True
                break
        
        return not explanation_found
    
    def _is_academic_fabrication(self, entity_text: str, entity_type: str) -> bool:
        """Check for academic-style fabricated references."""
        if entity_type not in ['PERSON', 'ORG', 'WORK_OF_ART', 'GPE', 'FAC']:
            return False
        
        # Patterns that suggest fabricated academic content
        academic_fabrication_patterns = [
            r'^Dr\. [A-Z][a-z]+ [A-Z][a-z]+$',  # "Dr. John Smith" format
            r'^[A-Z][a-z]+ et al\.$',  # "Smith et al." format
            r'^Journal of [A-Z][a-z]+( [A-Z][a-z]+)*$',  # "Journal of Something"
            r'^[A-Z][a-z]+ University$',  # "Something University"
            r'^[A-Z][a-z]+ Institute$',  # "Something Institute"
        ]
        
        for pattern in academic_fabrication_patterns:
            if re.match(pattern, entity_text):
                return True
        
        # Check for suspicious person names with specific patterns
        if entity_type == 'PERSON':
            # Full names with uncommon patterns (potential fabrication)
            if re.match(r'^[A-Z][a-z]+ [A-Z][a-z]+$', entity_text):
                # Names that appear in technical/historical contexts are suspicious
                return True
        
        # Check for suspicious location/facility names
        if entity_type in ['GPE', 'FAC']:
            # Cities with "world's first" claims nearby are suspicious
            return True
        
        return False
    
    def _is_sudden_introduction(self, entity_info: Dict, sentences: List[Sentence]) -> bool:
        """Check if entity is introduced suddenly without context."""
        entity_text = entity_info['text']
        sentence_index = entity_info['sentence_index']
        
        # Skip common entities that don't need introduction
        common_entities = ['United States', 'America', 'Europe', 'Asia', 'Google', 'Microsoft', 'Apple']
        if entity_text in common_entities:
            return False
        
        # Check if entity appears in previous sentences
        for i in range(sentence_index):
            if entity_text.lower() in sentences[i].text.lower():
                return False  # Entity was mentioned before
        
        # Check if current sentence provides introduction context
        current_sentence = sentences[sentence_index].text.lower()
        introduction_phrases = [
            "introduce", "meet", "called", "named", "known as",
            "refers to", "defined as", "is a", "is an"
        ]
        
        if any(phrase in current_sentence for phrase in introduction_phrases):
            return False  # Proper introduction found
        
        return True
    
    def _has_inconsistent_usage(self, entity_info: Dict, sentences: List[Sentence]) -> bool:
        """Check for inconsistent entity usage patterns."""
        entity_text = entity_info['text']
        
        # Find all occurrences of this entity
        occurrences = []
        for i, sentence in enumerate(sentences):
            if entity_text.lower() in sentence.text.lower():
                occurrences.append(i)
        
        if len(occurrences) <= 1:
            return False  # Can't check consistency with single occurrence
        
        # Check for inconsistent context usage
        contexts = []
        for occurrence_idx in occurrences:
            sentence_text = sentences[occurrence_idx].text
            
            # Extract context around the entity
            entity_pos = sentence_text.lower().find(entity_text.lower())
            if entity_pos >= 0:
                start = max(0, entity_pos - 20)
                end = min(len(sentence_text), entity_pos + len(entity_text) + 20)
                context = sentence_text[start:end].lower()
                contexts.append(context)
        
        # Simple inconsistency check: if contexts are very different, it might be suspicious
        # This is a basic heuristic - real implementation could be more sophisticated
        if len(set(contexts)) == len(contexts) and len(contexts) > 2:
            return True  # All contexts are completely different
        
        return False
    
    def _calculate_fabrication_risk_score(self, suspicious_entities: List[EntitySuspicion], total_entities: int) -> float:
        """Calculate overall fabrication risk score."""
        if total_entities == 0:
            return 0.0
        
        risk_score = 0.0
        
        # Base risk from proportion of suspicious entities
        suspicious_ratio = len(suspicious_entities) / total_entities
        risk_score += suspicious_ratio * 0.6  # Increased from 0.5
        
        # Additional risk from severity of suspicions
        for entity in suspicious_entities:
            severity_weight = 0.0
            
            for reason in entity.suspicion_reasons:
                if "academic_style_fabrication" in reason:
                    severity_weight += 0.4  # Increased from 0.3
                elif "overly_specific_without_explanation" in reason:
                    severity_weight += 0.3  # Increased from 0.2
                elif "sudden_unexplained_introduction" in reason:
                    severity_weight += 0.25  # Increased from 0.15
                elif "inconsistent_usage_pattern" in reason:
                    severity_weight += 0.15  # Increased from 0.1
                else:
                    severity_weight += 0.1  # Increased from 0.05
            
            # Normalize by total entities and add to risk
            risk_score += severity_weight / max(total_entities, 3)  # Cap denominator at 3
        
        # Bonus risk if many entities are suspicious
        if len(suspicious_entities) > 2:  # Lowered from 3
            risk_score += 0.3  # Increased from 0.2
        
        # Extra penalty for multiple fabrication types
        unique_reasons = set()
        for entity in suspicious_entities:
            unique_reasons.update(entity.suspicion_reasons)
        
        if len(unique_reasons) > 2:
            risk_score += 0.2  # Multiple types of fabrication
        
        return min(1.0, risk_score)
    
    def _create_error_result(self, error_message: str) -> EntityFabricationResult:
        """Create error result for entity fabrication detection."""
        return EntityFabricationResult(
            module_name=self.module_name,
            processing_time_ms=0,
            suspicious_entities=[],
            fabrication_risk_score=0.0
        )