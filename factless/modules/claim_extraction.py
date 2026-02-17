"""
Step 2: Claim Extraction Module

Extracts structured claims from sentences using Gemini API.
The LLM acts only as a linguistic parser, not a fact-checker.
"""

import json
import time
import os
from typing import List, Dict, Any
import google.generativeai as genai

from .base import BaseModule
from ..models import Sentence, Claim, ClaimExtractionResult
from ..config import FactlessConfig


class ClaimExtractionModule(BaseModule):
    """Extracts claims from sentences using Gemini API as linguistic parser."""
    
    def __init__(self, config: FactlessConfig):
        super().__init__("ClaimExtraction")
        self.config = config
        
        # Initialize Gemini API
        api_key = config.gemini_api_key or os.getenv("GEMINI_API_KEY")
        if not api_key:
            self.log("GEMINI_API_KEY not found in config or environment", "WARNING")
            self.gemini_available = False
        else:
            try:
                genai.configure(api_key=api_key)
                self.model = genai.GenerativeModel(config.claim_extraction_model)
                self.gemini_available = True
                self.log(f"Initialized Gemini model: {config.claim_extraction_model}")
            except Exception as e:
                self.log(f"Failed to initialize Gemini: {str(e)}", "ERROR")
                self.gemini_available = False
        
        self.llm_model = config.claim_extraction_model
        self.temperature = config.claim_extraction_temperature
        self.max_tokens = config.claim_extraction_max_tokens
    
    def _process(self, sentences: List[Sentence]) -> ClaimExtractionResult:
        """Extract claims from sentences."""
        if not sentences:
            self.log("No sentences to process")
            return ClaimExtractionResult(
                module_name=self.module_name,
                processing_time_ms=0,
                claims=[],
                llm_model=self.llm_model,
                llm_latency_ms=0
            )
        
        all_claims = []
        total_llm_time = 0
        
        for sentence in sentences:
            start_time = time.time()
            
            try:
                claims = self._extract_claims_from_sentence(sentence)
                all_claims.extend(claims)
                
                llm_time = (time.time() - start_time) * 1000
                total_llm_time += llm_time
                
                self.log(f"Extracted {len(claims)} claims from sentence {sentence.index}")
                
            except Exception as e:
                self.log(f"Error extracting claims from sentence {sentence.index}: {str(e)}", "ERROR")
                continue
        
        self.log(f"Total claims extracted: {len(all_claims)}")
        
        return ClaimExtractionResult(
            module_name=self.module_name,
            processing_time_ms=0,  # Set by base class
            claims=all_claims,
            llm_model=self.llm_model,
            llm_latency_ms=total_llm_time
        )
    
    def _extract_claims_from_sentence(self, sentence: Sentence) -> List[Claim]:
        """Extract claims from a single sentence using LLM."""
        
        # Construct the prompt for claim extraction
        prompt = self._build_claim_extraction_prompt(sentence.text)
        
        # Simulate LLM call (in real implementation, call actual LLM)
        response = self._call_llm(prompt)
        
        # Parse the structured response
        try:
            claims_data = json.loads(response)
            claims = []
            
            for claim_data in claims_data.get("claims", []):
                claim = Claim(
                    text=claim_data["text"],
                    sentence_index=sentence.index,
                    claim_type=claim_data.get("type", "fact"),
                    confidence_markers=claim_data.get("confidence_markers", [])
                )
                claims.append(claim)
            
            return claims
            
        except json.JSONDecodeError as e:
            self.log(f"Failed to parse LLM response as JSON: {str(e)}", "ERROR")
            return []
    
    def _build_claim_extraction_prompt(self, sentence_text: str) -> str:
        """Build the prompt for claim extraction."""
        return f"""You are a linguistic parser. Extract assertive claims from the sentence below.

CRITICAL: Respond ONLY with valid JSON. No explanations, no markdown, just pure JSON.

RULES:
- Only extract claims explicitly stated in the sentence
- Do not add information not present in the original text
- Do not verify or judge correctness of claims
- A claim is any assertive statement presenting a fact, guarantee, or explanation
- Include confidence markers (words indicating certainty/uncertainty)

Sentence: "{sentence_text}"

Respond with ONLY this JSON structure (no other text):
{{
    "claims": [
        {{
            "text": "exact claim text from sentence",
            "type": "fact",
            "confidence_markers": []
        }}
    ]
}}"""
    
    def _call_llm(self, prompt: str) -> str:
        """
        Call Gemini API for claim extraction.
        Falls back to mock response if API is unavailable.
        """
        
        if not self.gemini_available:
            self.log("Gemini API not available, using fallback", "WARNING")
            return self._mock_response()
        
        try:
            # Configure generation parameters
            generation_config = genai.types.GenerationConfig(
                temperature=self.temperature,
                max_output_tokens=self.max_tokens,
            )
            
            # Generate response
            response = self.model.generate_content(
                prompt,
                generation_config=generation_config
            )
            
            if response.text:
                response_text = response.text.strip()
                
                # Try to extract JSON from markdown code blocks if present
                if "```json" in response_text:
                    # Extract JSON from markdown code block
                    start = response_text.find("```json") + 7
                    end = response_text.find("```", start)
                    if end > start:
                        response_text = response_text[start:end].strip()
                elif "```" in response_text:
                    # Extract from generic code block
                    start = response_text.find("```") + 3
                    end = response_text.find("```", start)
                    if end > start:
                        response_text = response_text[start:end].strip()
                
                # Validate it's JSON
                try:
                    json.loads(response_text)
                    return response_text
                except json.JSONDecodeError:
                    self.log(f"Gemini returned non-JSON response: {response_text[:100]}", "WARNING")
                    return self._mock_response()
            else:
                self.log("Empty response from Gemini", "WARNING")
                return self._mock_response()
                
        except Exception as e:
            self.log(f"Gemini API error: {str(e)}", "ERROR")
            return self._mock_response()
    
    def _mock_response(self) -> str:
        """Fallback mock response when Gemini is unavailable."""
        return json.dumps({
            "claims": [
                {
                    "text": "Mock claim extraction (Gemini unavailable)",
                    "type": "fact",
                    "confidence_markers": []
                }
            ]
        })
    
    def _create_error_result(self, error_message: str) -> ClaimExtractionResult:
        """Create error result for claim extraction."""
        return ClaimExtractionResult(
            module_name=self.module_name,
            processing_time_ms=0,
            claims=[],
            llm_model=self.llm_model,
            llm_latency_ms=0
        )