"""
Tests for FACTLESS analyzer.
"""

import pytest
from factless import FactlessAnalyzer, FactlessConfig, RiskLevel

class TestFactlessAnalyzer:
    """Test cases for the main analyzer."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.analyzer = FactlessAnalyzer()
    
    def test_analyzer_initialization(self):
        """Test analyzer initializes correctly."""
        assert self.analyzer is not None
        assert self.analyzer.config is not None
        
        # Test with custom config
        custom_config = FactlessConfig()
        custom_config.max_text_length = 5000
        custom_analyzer = FactlessAnalyzer(custom_config)
        assert custom_analyzer.config.max_text_length == 5000
    
    def test_empty_text_analysis(self):
        """Test analysis of empty text raises error."""
        with pytest.raises(ValueError, match="Input text cannot be empty"):
            self.analyzer.analyze("")
        
        with pytest.raises(ValueError, match="Input text cannot be empty"):
            self.analyzer.analyze("   ")
    
    def test_text_too_long(self):
        """Test analysis of overly long text raises error."""
        long_text = "a" * (self.analyzer.config.max_text_length + 1)
        with pytest.raises(ValueError, match="Input text too long"):
            self.analyzer.analyze(long_text)
    
    def test_simple_text_analysis(self):
        """Test analysis of simple, low-risk text."""
        text = "The weather is nice today. It might rain tomorrow."
        result = self.analyzer.analyze(text)
        
        assert result is not None
        assert 0 <= result.risk_score <= 1
        assert result.risk_level in [RiskLevel.LOW, RiskLevel.MEDIUM, RiskLevel.HIGH]
        assert isinstance(result.explanations, list)
        assert result.total_processing_time_ms > 0
        assert result.input_text_length == len(text)
    
    def test_high_risk_text_analysis(self):
        """Test analysis of high-risk text with multiple issues."""
        text = """
        Python is definitely the fastest language ever created, with absolutely zero flaws.
        However, Python is also the slowest language for any computational task.
        Dr. John Smith from MIT University published this in the Journal of Perfect Programming (2023).
        The language guarantees 100% perfect execution with 15.847392 teraflops per second performance.
        """
        
        result = self.analyzer.analyze(text)
        
        assert result is not None
        assert result.risk_score > 0.3  # Should be medium to high risk
        assert len(result.explanations) > 0  # Should have risk signals
        
        # Check for expected risk signals
        signal_types = [exp.signal_type for exp in result.explanations]
        # Should detect overconfidence, contradictions, or entity fabrication
        assert any(signal in signal_types for signal in ['overconfidence', 'contradiction', 'entity_fabrication'])
    
    def test_batch_analysis(self):
        """Test batch analysis functionality."""
        texts = [
            "Simple text.",
            "Definitely the best text ever written, guaranteed 100% perfect.",
            "This might be okay text, possibly."
        ]
        
        results = self.analyzer.analyze_batch(texts)
        
        assert len(results) == len(texts)
        for result in results:
            assert result is not None
            assert 0 <= result.risk_score <= 1
            assert result.risk_level in [RiskLevel.LOW, RiskLevel.MEDIUM, RiskLevel.HIGH]
    
    def test_module_status(self):
        """Test module status reporting."""
        status = self.analyzer.get_module_status()
        
        assert isinstance(status, dict)
        assert "sentence_segmentation" in status
        assert "claim_extraction" in status
        assert "contradiction_detection" in status
        assert "logical_flow" in status
        assert "overconfidence" in status
        assert "claim_density" in status
        assert "entity_fabrication" in status
        assert "config" in status
    
    def test_contradictory_text(self):
        """Test detection of contradictory statements."""
        text = "The sky is blue. The sky is red."
        result = self.analyzer.analyze(text)
        
        # Should detect some risk due to contradiction
        assert result.risk_score > 0
    
    def test_overconfident_text(self):
        """Test detection of overconfident language."""
        text = "This is absolutely guaranteed to be 100% perfect and will never fail."
        result = self.analyzer.analyze(text)
        
        # Should detect overconfidence
        signal_types = [exp.signal_type for exp in result.explanations]
        assert 'overconfidence' in signal_types
    
    def test_high_claim_density(self):
        """Test detection of high claim density."""
        text = "Python is fast. Python is slow. Python is popular. Python is unpopular. Python is easy."
        result = self.analyzer.analyze(text)
        
        # Should detect high claim density
        assert result.claim_density.claim_density > 1.0  # More than 1 claim per sentence
    
    def test_suspicious_entities(self):
        """Test detection of suspicious entities."""
        text = "Dr. John Smith from Harvard University published this in the Journal of Perfect Programming."
        result = self.analyzer.analyze(text)
        
        # Should detect potentially fabricated entities
        assert len(result.entity_fabrication.suspicious_entities) > 0