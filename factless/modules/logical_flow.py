"""
Step 4: Logical Flow Validation Module

Validates logical reasoning flow in the text.
Detects circular reasoning, cause-effect inversions, and missing assumptions.
This is reasoning validation, NOT fact-checking.
"""

import re
from typing import List, Set, Tuple
from collections import defaultdict

from .base import BaseModule
from ..models import Sentence, Claim, LogicalFlaw, LogicalFlowResult


class LogicalFlowModule(BaseModule):
    """Validates logical flow and reasoning patterns."""
    
    def __init__(self):
        super().__init__("LogicalFlow")
        
        # Causal indicators
        self.cause_indicators = [
            "because", "since", "due to", "as a result of", "caused by",
            "leads to", "results in", "therefore", "thus", "hence",
            "consequently", "so", "which means", "this causes"
        ]
        
        # Conclusion indicators
        self.conclusion_indicators = [
            "therefore", "thus", "hence", "consequently", "so",
            "in conclusion", "as a result", "this shows", "this proves",
            "we can conclude", "it follows that"
        ]
        
        # Assumption indicators
        self.assumption_indicators = [
            "assuming", "given that", "if", "suppose", "let's say",
            "provided that", "on the condition that", "granted that"
        ]
    
    def _process(self, sentences: List[Sentence], claims: List[Claim]) -> LogicalFlowResult:
        """Validate logical flow in the text."""
        if not sentences or not claims:
            self.log("No sentences or claims to analyze")
            return LogicalFlowResult(
                module_name=self.module_name,
                processing_time_ms=0,
                logical_flaws=[]
            )
        
        logical_flaws = []
        
        # Check for circular reasoning
        circular_flaws = self._detect_circular_reasoning(sentences, claims)
        logical_flaws.extend(circular_flaws)
        
        # Check for cause-effect inversions
        causal_flaws = self._detect_cause_effect_inversions(sentences)
        logical_flaws.extend(causal_flaws)
        
        # Check for missing assumptions
        assumption_flaws = self._detect_missing_assumptions(sentences, claims)
        logical_flaws.extend(assumption_flaws)
        
        # Check for logical gaps
        gap_flaws = self._detect_logical_gaps(sentences)
        logical_flaws.extend(gap_flaws)
        
        self.log(f"Found {len(logical_flaws)} logical flaws")
        
        return LogicalFlowResult(
            module_name=self.module_name,
            processing_time_ms=0,  # Set by base class
            logical_flaws=logical_flaws
        )
    
    def _detect_circular_reasoning(self, sentences: List[Sentence], claims: List[Claim]) -> List[LogicalFlaw]:
        """Detect circular reasoning patterns."""
        flaws = []
        
        # Build claim dependency graph
        dependencies = self._build_dependency_graph(sentences, claims)
        
        # Find cycles in the dependency graph
        cycles = self._find_cycles(dependencies)
        
        for cycle in cycles:
            if len(cycle) >= 2:  # Meaningful cycle
                flaw = LogicalFlaw(
                    flaw_type="circular_reasoning",
                    sentence_indices=cycle,
                    description=f"Circular reasoning detected: sentences {cycle} form a logical loop"
                )
                flaws.append(flaw)
                self.log(f"Circular reasoning in sentences: {cycle}")
        
        return flaws
    
    def _build_dependency_graph(self, sentences: List[Sentence], claims: List[Claim]) -> dict:
        """Build a graph of logical dependencies between sentences."""
        dependencies = defaultdict(set)
        
        for i, sentence in enumerate(sentences):
            text = sentence.text.lower()
            
            # Look for references to previous statements
            if any(indicator in text for indicator in self.cause_indicators + self.conclusion_indicators):
                # This sentence depends on previous context
                for j in range(i):
                    # Simple heuristic: if sentences share key terms, there might be a dependency
                    if self._sentences_related(sentences[j], sentence):
                        dependencies[i].add(j)
        
        return dependencies
    
    def _sentences_related(self, sent1: Sentence, sent2: Sentence) -> bool:
        """Check if two sentences are logically related."""
        # Extract key terms (nouns, verbs) from both sentences
        words1 = set(re.findall(r'\b[a-zA-Z]{3,}\b', sent1.text.lower()))
        words2 = set(re.findall(r'\b[a-zA-Z]{3,}\b', sent2.text.lower()))
        
        # Remove common stop words
        stop_words = {"the", "and", "but", "for", "are", "with", "this", "that", "they", "have", "from"}
        words1 -= stop_words
        words2 -= stop_words
        
        # Check for significant overlap
        if len(words1) == 0 or len(words2) == 0:
            return False
        
        overlap = len(words1.intersection(words2))
        return overlap >= 2 or overlap / min(len(words1), len(words2)) > 0.3
    
    def _find_cycles(self, graph: dict) -> List[List[int]]:
        """Find cycles in the dependency graph using DFS."""
        cycles = []
        visited = set()
        rec_stack = set()
        
        def dfs(node, path):
            if node in rec_stack:
                # Found a cycle
                cycle_start = path.index(node)
                cycle = path[cycle_start:]
                cycles.append(cycle)
                return
            
            if node in visited:
                return
            
            visited.add(node)
            rec_stack.add(node)
            path.append(node)
            
            for neighbor in graph.get(node, []):
                dfs(neighbor, path.copy())
            
            rec_stack.remove(node)
        
        for node in graph:
            if node not in visited:
                dfs(node, [])
        
        return cycles
    
    def _detect_cause_effect_inversions(self, sentences: List[Sentence]) -> List[LogicalFlaw]:
        """Detect cause-effect relationship inversions."""
        flaws = []
        
        for i in range(len(sentences) - 1):
            current = sentences[i].text.lower()
            next_sent = sentences[i + 1].text.lower()
            
            # Look for temporal/causal inconsistencies
            if self._has_causal_inversion(current, next_sent):
                flaw = LogicalFlaw(
                    flaw_type="cause_effect_inversion",
                    sentence_indices=[i, i + 1],
                    description=f"Potential cause-effect inversion between sentences {i} and {i + 1}"
                )
                flaws.append(flaw)
                self.log(f"Cause-effect inversion detected between sentences {i} and {i + 1}")
        
        return flaws
    
    def _has_causal_inversion(self, text1: str, text2: str) -> bool:
        """Check if two sentences have inverted cause-effect relationship."""
        # Look for temporal markers that suggest inversion
        temporal_early = ["before", "earlier", "previously", "first", "initially"]
        temporal_late = ["after", "later", "subsequently", "then", "finally"]
        
        # If first sentence has "later" markers and second has "earlier" markers
        has_late_in_first = any(marker in text1 for marker in temporal_late)
        has_early_in_second = any(marker in text2 for marker in temporal_early)
        
        if has_late_in_first and has_early_in_second:
            return True
        
        # Check for effect-before-cause patterns
        if "because" in text2 and any(indicator in text1 for indicator in self.conclusion_indicators):
            return True
        
        return False
    
    def _detect_missing_assumptions(self, sentences: List[Sentence], claims: List[Claim]) -> List[LogicalFlaw]:
        """Detect logical jumps that require unstated assumptions."""
        flaws = []
        
        for i in range(len(sentences) - 1):
            current = sentences[i].text.lower()
            next_sent = sentences[i + 1].text.lower()
            
            # Look for logical jumps
            if self._has_logical_jump(current, next_sent):
                flaw = LogicalFlaw(
                    flaw_type="missing_assumption",
                    sentence_indices=[i, i + 1],
                    description=f"Logical jump detected: missing assumption between sentences {i} and {i + 1}"
                )
                flaws.append(flaw)
                self.log(f"Missing assumption between sentences {i} and {i + 1}")
        
        return flaws
    
    def _has_logical_jump(self, text1: str, text2: str) -> bool:
        """Check if there's a logical jump between two sentences."""
        # If second sentence has strong conclusion indicators but first doesn't provide sufficient premise
        has_strong_conclusion = any(indicator in text2 for indicator in ["therefore", "thus", "proves", "shows"])
        has_weak_premise = not any(indicator in text1 for indicator in self.cause_indicators + ["evidence", "data", "study"])
        
        return has_strong_conclusion and has_weak_premise
    
    def _detect_logical_gaps(self, sentences: List[Sentence]) -> List[LogicalFlaw]:
        """Detect gaps in logical argumentation."""
        flaws = []
        
        # Look for argument structures with missing steps
        for i in range(len(sentences)):
            text = sentences[i].text.lower()
            
            # Strong conclusions without adequate support
            if any(indicator in text for indicator in ["definitely", "certainly", "proves", "undoubtedly"]):
                # Check if previous sentences provide adequate support
                support_count = 0
                for j in range(max(0, i - 3), i):  # Check previous 3 sentences
                    prev_text = sentences[j].text.lower()
                    if any(indicator in prev_text for indicator in ["evidence", "study", "research", "data", "because"]):
                        support_count += 1
                
                if support_count == 0:
                    flaw = LogicalFlaw(
                        flaw_type="insufficient_support",
                        sentence_indices=[i],
                        description=f"Strong conclusion in sentence {i} lacks adequate support"
                    )
                    flaws.append(flaw)
                    self.log(f"Insufficient support for conclusion in sentence {i}")
        
        return flaws
    
    def _create_error_result(self, error_message: str) -> LogicalFlowResult:
        """Create error result for logical flow validation."""
        return LogicalFlowResult(
            module_name=self.module_name,
            processing_time_ms=0,
            logical_flaws=[]
        )