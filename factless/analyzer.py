"""
Main FACTLESS analyzer that orchestrates the 7-step pipeline.
"""

import time
from loguru import logger

from .config import FactlessConfig
from .models import AnalysisResult
from .scoring import FactlessScorer
from .modules import (
    SentenceSegmentationModule,
    ClaimExtractionModule,
    ContradictionDetectionModule,
    LogicalFlowModule,
    OverconfidenceModule,
    ClaimDensityModule,
    EntityFabricationModule,
    PlausibilityAnalysisModule
)


class FactlessAnalyzer:
    """Main FACTLESS analysis engine."""
    
    def __init__(self, config: FactlessConfig = None):
        """Initialize the analyzer with configuration."""
        self.config = config or FactlessConfig()
        
        # Initialize all modules
        self.sentence_segmentation = SentenceSegmentationModule()
        self.claim_extraction = ClaimExtractionModule(self.config)
        self.contradiction_detection = ContradictionDetectionModule(self.config)
        self.logical_flow = LogicalFlowModule()
        self.overconfidence = OverconfidenceModule(self.config)
        self.claim_density = ClaimDensityModule(self.config)
        self.entity_fabrication = EntityFabricationModule(self.config)
        self.plausibility_analysis = PlausibilityAnalysisModule(self.config)
        
        # Initialize scorer
        self.scorer = FactlessScorer(self.config)
        
        logger.info("FACTLESS analyzer initialized")
    
    def analyze(self, text: str) -> AnalysisResult:
        """
        Analyze text for hallucination risk using the 7-step pipeline.
        
        Args:
            text: AI-generated text to analyze
            
        Returns:
            AnalysisResult with risk score, level, and explanations
        """
        start_time = time.time()
        
        # Input validation
        if not text or not text.strip():
            raise ValueError("Input text cannot be empty")
        
        if len(text) > self.config.max_text_length:
            raise ValueError(f"Input text too long: {len(text)} > {self.config.max_text_length}")
        
        logger.info(f"Starting FACTLESS analysis of {len(text)} character text")
        
        try:
            # Step 1: Sentence Segmentation
            logger.info("Step 1: Sentence Segmentation")
            sentence_result = self.sentence_segmentation.process(text)
            
            if not sentence_result.sentences:
                logger.warning("No sentences found in input text")
            
            # Step 2: Claim Extraction
            logger.info("Step 2: Claim Extraction")
            claim_result = self.claim_extraction.process(sentence_result.sentences)
            
            # Step 3: Contradiction Detection
            logger.info("Step 3: Contradiction Detection")
            contradiction_result = self.contradiction_detection.process(claim_result.claims)
            
            # Step 4: Logical Flow Validation
            logger.info("Step 4: Logical Flow Validation")
            logical_flow_result = self.logical_flow.process(
                sentence_result.sentences, 
                claim_result.claims
            )
            
            # Step 5: Overconfidence Analysis
            logger.info("Step 5: Overconfidence Analysis")
            overconfidence_result = self.overconfidence.process(sentence_result.sentences)
            
            # Step 6: Claim Density Analysis
            logger.info("Step 6: Claim Density Analysis")
            claim_density_result = self.claim_density.process(
                sentence_result.sentences,
                claim_result.claims
            )
            
            # Step 7: Entity Fabrication Detection
            logger.info("Step 7: Entity Fabrication Detection")
            entity_fabrication_result = self.entity_fabrication.process(sentence_result.sentences)
            
            # Step 8: Plausibility Analysis (NEW)
            logger.info("Step 8: Plausibility Analysis")
            plausibility_result = self.plausibility_analysis.process(sentence_result.sentences)
            
            # Final Scoring and Explanation Generation
            logger.info("Generating final score and explanations")
            total_processing_time = (time.time() - start_time) * 1000
            
            result = self.scorer.create_analysis_result(
                text,
                sentence_result,
                claim_result,
                contradiction_result,
                logical_flow_result,
                overconfidence_result,
                claim_density_result,
                entity_fabrication_result,
                plausibility_result,
                total_processing_time
            )
            
            logger.info(f"Analysis complete: Risk={result.risk_level.value}, Score={result.risk_score:.3f}, Time={total_processing_time:.1f}ms")
            
            return result
            
        except Exception as e:
            logger.error(f"Analysis failed: {str(e)}")
            raise
    
    def analyze_batch(self, texts: list) -> list:
        """
        Analyze multiple texts in batch.
        
        Args:
            texts: List of AI-generated texts to analyze
            
        Returns:
            List of AnalysisResult objects
        """
        results = []
        
        for i, text in enumerate(texts):
            logger.info(f"Processing batch item {i+1}/{len(texts)}")
            try:
                result = self.analyze(text)
                results.append(result)
            except Exception as e:
                logger.error(f"Failed to analyze batch item {i+1}: {str(e)}")
                # Could add error result here instead of skipping
                continue
        
        return results
    
    def get_module_status(self) -> dict:
        """Get status information about all modules."""
        return {
            "sentence_segmentation": "ready",
            "claim_extraction": f"model: {self.config.claim_extraction_model}",
            "contradiction_detection": f"threshold: {self.config.contradiction.similarity_threshold}",
            "logical_flow": "ready",
            "overconfidence": f"absolute_terms: {len(self.config.overconfidence.absolute_terms)}",
            "claim_density": f"threshold: {self.config.claim_density.high_density_threshold}",
            "entity_fabrication": f"patterns: {len(self.config.entity_fabrication.suspicious_patterns)}",
            "config": {
                "max_text_length": self.config.max_text_length,
                "detailed_logging": self.config.enable_detailed_logging
            }
        }