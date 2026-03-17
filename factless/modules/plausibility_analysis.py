"""
Step 8: Plausibility Analysis Module

Detects implausible content through balanced factuality verification.
Uses Gemini to evaluate both suspicion and verification signals.
"""

import re
import json
from typing import List, Dict, Set
from datetime import datetime

import google.generativeai as genai

from .base import BaseModule
from ..models import Sentence, PlausibilitySignal, PlausibilityAnalysisResult


class PlausibilityAnalysisModule(BaseModule):
    """Analyzes text for real-world plausibility using balanced factuality verification."""
    
    def __init__(self, config=None):
        super().__init__("PlausibilityAnalysis")
        self.config = config
        
        # Initialize Gemini if API key is available
        self.gemini_model = None
        
        # Try to get API key from config or environment
        api_key = None
        if config and hasattr(config, 'gemini_api_key') and config.gemini_api_key:
            api_key = config.gemini_api_key
        else:
            # Fallback to environment variable
            import os
            api_key = os.getenv("GEMINI_API_KEY", "")
        
        if api_key:
            try:
                genai.configure(api_key=api_key)
                self.gemini_model = genai.GenerativeModel('gemini-2.5-flash')
                self.log("Initialized Gemini model for factuality verification")
            except Exception as e:
                self.log(f"Failed to initialize Gemini: {e}")
        else:
            self.log("No Gemini API key found, using fallback pattern analysis")
        
        # Fallback patterns for when Gemini is not available
        self.fallback_suspicious_patterns = [
            r'brain signal.*programming',
            r'thought.*control.*train',
            r'solar.*1897',
            r'magnetic levitation.*18\d{2}',
            r'neural.*interface.*18\d{2}',
            r'wireless.*18\d{2}'
        ]
    
    def _process(self, sentences: List[Sentence]) -> PlausibilityAnalysisResult:
        """Analyze sentences for plausibility using balanced factuality verification."""
        if not sentences:
            self.log("No sentences to analyze")
            return PlausibilityAnalysisResult(
                module_name=self.module_name,
                processing_time_ms=0,
                signals=[],
                plausibility_risk_score=0.0
            )
        
        # Combine all sentences into one text for analysis
        full_text = " ".join([sentence.text for sentence in sentences])
        
        if self.gemini_model:
            # Use Gemini for balanced factuality verification
            signals, risk_score = self._analyze_with_gemini(full_text, sentences)
        else:
            # Fallback to pattern-based analysis
            signals, risk_score = self._analyze_with_patterns(sentences)
        
        self.log(f"Found {len(signals)} plausibility issues")
        self.log(f"Plausibility risk score: {risk_score:.3f}")
        
        return PlausibilityAnalysisResult(
            module_name=self.module_name,
            processing_time_ms=0,  # Set by base class
            logs=[],  # Will be set by base class
            signals=signals,
            plausibility_risk_score=risk_score
        )
    
    def _analyze_with_gemini(self, text: str, sentences: List[Sentence]) -> tuple:
        """Use Gemini for balanced factuality verification."""
        
        system_prompt = """You are a factuality verification assistant.
Your task is NOT just to detect hallucinations, but to BALANCE:
- Suspicion signals (why something might be fake)
- Verification signals (why something might be real)

Step 1: Extract key claims
Focus on:
- Technologies
- Dates
- Locations
- Named entities
- Numerical facts

Step 2: Evaluate TWO sides
A. Suspicion Signals (increase risk)
- Unrealistic technology combinations
- Timeline mismatch
- Sci-fi like claims presented as real
- No references for strong claims
- Overly detailed but unverifiable facts

B. Verification Signals (REDUCE risk)
- Claim matches general real-world knowledge
- Technology aligns with time period
- No exaggerated or impossible claims
- Widely known or commonly accepted facts
- Logical and realistic progression

Step 3: Decide risk score
Rules:
- If strong suspicion signals AND no verification → 80–95%
- If mixed signals → 40–70%
- If mostly verifiable and realistic → 5–30%

Step 4: Output reasoning in simple language
Examples:
- "This seems realistic and aligns with known technology"
- "Timeline and technology are consistent"
- "Claim appears exaggerated or unrealistic"
- "No supporting context for strong claims"

Important:
- Do NOT assume something is false just because it is unfamiliar
- Do NOT penalize normal factual sentences
- Only assign high risk when claims are clearly implausible or unverifiable

Return your analysis as JSON:
{
  "risk_score": 0.0-1.0,
  "reasoning": "brief explanation",
  "suspicion_signals": ["list of concerning elements"],
  "verification_signals": ["list of supporting elements"],
  "overall_assessment": "realistic/mixed/suspicious"
}"""

        try:
            prompt = f"{system_prompt}\n\nAnalyze this text:\n{text}"
            response = self.gemini_model.generate_content(prompt)
            
            # Parse JSON response
            response_text = response.text.strip()
            if response_text.startswith('```json'):
                response_text = response_text[7:-3].strip()
            elif response_text.startswith('```'):
                response_text = response_text[3:-3].strip()
            
            try:
                analysis = json.loads(response_text)
            except json.JSONDecodeError:
                self.log(f"Gemini returned non-JSON response: {response_text[:100]}...")
                # Try to extract risk score from text
                import re
                score_match = re.search(r'"risk_score":\s*([0-9.]+)', response_text)
                if score_match:
                    risk_score = float(score_match.group(1))
                    analysis = {
                        "risk_score": risk_score,
                        "reasoning": "Analysis completed but JSON parsing failed",
                        "suspicion_signals": [],
                        "verification_signals": [],
                        "overall_assessment": "mixed"
                    }
                else:
                    # Fallback to pattern analysis
                    return self._analyze_with_patterns(sentences)
            
            # Convert to signals
            signals = []
            risk_score = analysis.get("risk_score", 0.0)
            reasoning = analysis.get("reasoning", "No reasoning provided")
            
            # Create signals based on suspicion signals
            suspicion_signals = analysis.get("suspicion_signals", [])
            for i, signal_desc in enumerate(suspicion_signals):
                signals.append(PlausibilitySignal(
                    signal_type="FACTUALITY_CONCERN",
                    sentence_index=min(i, len(sentences) - 1),
                    description=signal_desc,
                    severity=min(0.8, risk_score + 0.1)
                ))
            
            # If no specific signals but high risk, create a general signal
            if not signals and risk_score > 0.6:
                signals.append(PlausibilitySignal(
                    signal_type="FACTUALITY_CONCERN",
                    sentence_index=0,
                    description=reasoning,
                    severity=risk_score
                ))
            
            self.log(f"Gemini analysis: risk={risk_score:.3f}, assessment={analysis.get('overall_assessment', 'unknown')}")
            
            return signals, risk_score
            
        except Exception as e:
            self.log(f"Gemini analysis failed: {e}")
            # Fallback to pattern analysis
            return self._analyze_with_patterns(sentences)
    
    def _analyze_with_patterns(self, sentences: List[Sentence]) -> tuple:
        """Fallback pattern-based analysis when Gemini is not available."""
        signals = []
        
        for sentence in sentences:
            text = sentence.text.lower()
            
            # Check for suspicious patterns
            for pattern in self.fallback_suspicious_patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    signals.append(PlausibilitySignal(
                        signal_type="SUSPICIOUS_PATTERN",
                        sentence_index=sentence.index,
                        description=f"Suspicious pattern detected: {pattern}",
                        severity=0.7
                    ))
        
        # Calculate risk score based on signals
        if len(signals) >= 3:
            risk_score = 0.8
        elif len(signals) >= 2:
            risk_score = 0.6
        elif len(signals) >= 1:
            risk_score = 0.4
        else:
            risk_score = 0.0
        
        return signals, risk_score
    
    def _create_error_result(self, error_message: str) -> PlausibilityAnalysisResult:
        """Create error result for plausibility analysis."""
        return PlausibilityAnalysisResult(
            module_name=self.module_name,
            processing_time_ms=0,
            logs=[],
            signals=[],
            plausibility_risk_score=0.0
        )