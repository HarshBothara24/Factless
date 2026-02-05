"""
Tests for FACTLESS API endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from api.main import app

class TestFactlessAPI:
    """Test cases for the API endpoints."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.client = TestClient(app)
    
    def test_root_endpoint(self):
        """Test root endpoint returns API information."""
        response = self.client.get("/")
        assert response.status_code == 200
        
        data = response.json()
        assert "name" in data
        assert "FACTLESS API" in data["name"]
        assert "endpoints" in data
    
    def test_health_endpoint(self):
        """Test health check endpoint."""
        response = self.client.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
    
    def test_status_endpoint(self):
        """Test status endpoint."""
        response = self.client.get("/status")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
        assert data["version"] == "1.0.0"
        assert "modules" in data
        assert "config" in data
    
    def test_analyze_endpoint_simple(self):
        """Test analyze endpoint with simple text."""
        request_data = {
            "text": "The weather is nice today.",
            "include_module_details": False
        }
        
        response = self.client.post("/analyze", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "risk_score" in data
        assert "risk_level" in data
        assert "explanations" in data
        assert "processing_time_ms" in data
        assert "input_length" in data
        assert 0 <= data["risk_score"] <= 1
        assert data["risk_level"] in ["LOW", "MEDIUM", "HIGH"]
        assert data["input_length"] == len(request_data["text"])
    
    def test_analyze_endpoint_with_details(self):
        """Test analyze endpoint with module details."""
        request_data = {
            "text": "This is definitely the best text ever written, guaranteed perfect.",
            "include_module_details": True
        }
        
        response = self.client.post("/analyze", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "module_details" in data
        
        details = data["module_details"]
        assert "sentence_count" in details
        assert "claim_count" in details
        assert "contradiction_count" in details
        assert "logical_flaw_count" in details
        assert "overconfidence_signals" in details
        assert "claim_density" in details
        assert "suspicious_entities" in details
    
    def test_analyze_endpoint_empty_text(self):
        """Test analyze endpoint with empty text."""
        request_data = {"text": ""}
        
        response = self.client.post("/analyze", json=request_data)
        assert response.status_code == 422  # Validation error
    
    def test_analyze_endpoint_text_too_long(self):
        """Test analyze endpoint with overly long text."""
        request_data = {"text": "a" * 10001}  # Exceeds max length
        
        response = self.client.post("/analyze", json=request_data)
        assert response.status_code == 400
        
        data = response.json()
        assert "too long" in data["detail"]
    
    def test_batch_analyze_endpoint(self):
        """Test batch analyze endpoint."""
        request_data = {
            "texts": [
                "Simple text.",
                "Definitely the best text ever, guaranteed perfect.",
                "This might be okay."
            ],
            "include_module_details": False
        }
        
        response = self.client.post("/analyze/batch", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 3
        
        for result in data:
            assert "risk_score" in result
            assert "risk_level" in result
            assert "explanations" in result
            assert 0 <= result["risk_score"] <= 1
    
    def test_batch_analyze_too_many_texts(self):
        """Test batch analyze with too many texts."""
        request_data = {
            "texts": ["text"] * 11  # Exceeds batch limit
        }
        
        response = self.client.post("/analyze/batch", json=request_data)
        assert response.status_code == 400
        
        data = response.json()
        assert "exceed" in data["detail"]
    
    def test_analyze_high_risk_text(self):
        """Test analyze endpoint with high-risk text."""
        request_data = {
            "text": """
            Python is absolutely the fastest language ever, guaranteed 100% perfect.
            However, Python is also the slowest language for computation.
            Dr. John Smith from MIT University proved this in the Journal of Perfect Programming.
            """,
            "include_module_details": True
        }
        
        response = self.client.post("/analyze", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        
        # Should detect multiple risk signals
        assert len(data["explanations"]) > 0
        
        # Should have higher risk score
        assert data["risk_score"] > 0.3
        
        # Check module details
        details = data["module_details"]
        assert details["sentence_count"] > 0
        assert details["claim_count"] > 0
    
    def test_request_validation(self):
        """Test request validation."""
        # Missing required field
        response = self.client.post("/analyze", json={})
        assert response.status_code == 422
        
        # Invalid field type
        response = self.client.post("/analyze", json={"text": 123})
        assert response.status_code == 422
        
        # Text too short (empty after validation)
        response = self.client.post("/analyze", json={"text": ""})
        assert response.status_code == 422