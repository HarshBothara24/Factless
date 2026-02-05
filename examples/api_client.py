"""
Example API client for FACTLESS service.
"""

import requests
import json
from typing import List, Dict, Any

class FactlessClient:
    """Client for FACTLESS API."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip('/')
    
    def analyze(self, text: str, include_module_details: bool = False) -> Dict[str, Any]:
        """Analyze a single text."""
        response = requests.post(
            f"{self.base_url}/analyze",
            json={
                "text": text,
                "include_module_details": include_module_details
            }
        )
        response.raise_for_status()
        return response.json()
    
    def analyze_batch(self, texts: List[str], include_module_details: bool = False) -> List[Dict[str, Any]]:
        """Analyze multiple texts."""
        response = requests.post(
            f"{self.base_url}/analyze/batch",
            json={
                "texts": texts,
                "include_module_details": include_module_details
            }
        )
        response.raise_for_status()
        return response.json()
    
    def get_status(self) -> Dict[str, Any]:
        """Get system status."""
        response = requests.get(f"{self.base_url}/status")
        response.raise_for_status()
        return response.json()
    
    def health_check(self) -> Dict[str, Any]:
        """Check system health."""
        response = requests.get(f"{self.base_url}/health")
        response.raise_for_status()
        return response.json()

def main():
    # Initialize client
    client = FactlessClient()
    
    # Check if service is running
    try:
        health = client.health_check()
        print(f"✓ Service is healthy: {health}")
    except requests.exceptions.ConnectionError:
        print("✗ Cannot connect to FACTLESS API. Make sure the service is running.")
        print("  Start with: uvicorn api.main:app --reload")
        return
    
    # Example texts
    texts = [
        "Machine learning algorithms can help analyze large datasets efficiently.",
        "Python is absolutely the best programming language ever created, with zero flaws whatsoever. Dr. Jane Doe from Harvard University proved this in her 2023 study published in the Journal of Perfect Programming.",
        "The weather forecast suggests it might rain tomorrow, though conditions could change."
    ]
    
    print("\n=== Single Text Analysis ===")
    for i, text in enumerate(texts):
        print(f"\nText {i+1}: {text[:50]}...")
        
        try:
            result = client.analyze(text, include_module_details=True)
            
            print(f"Risk Score: {result['risk_score']:.3f}")
            print(f"Risk Level: {result['risk_level']}")
            print(f"Processing Time: {result['processing_time_ms']:.1f}ms")
            
            if result['explanations']:
                print("Risk Signals:")
                for exp in result['explanations']:
                    print(f"  - {exp['signal_type']}: {exp['description']}")
            
            if 'module_details' in result:
                details = result['module_details']
                print(f"Module Details: {details['sentence_count']} sentences, {details['claim_count']} claims")
        
        except requests.exceptions.HTTPError as e:
            print(f"Error analyzing text: {e}")
    
    print("\n=== Batch Analysis ===")
    try:
        batch_results = client.analyze_batch(texts)
        
        for i, result in enumerate(batch_results):
            print(f"Text {i+1}: Risk={result['risk_level']}, Score={result['risk_score']:.3f}")
    
    except requests.exceptions.HTTPError as e:
        print(f"Error in batch analysis: {e}")
    
    print("\n=== System Status ===")
    try:
        status = client.get_status()
        print(f"Status: {status['status']}")
        print(f"Version: {status['version']}")
        print("Configuration:")
        for key, value in status['config'].items():
            print(f"  {key}: {value}")
    
    except requests.exceptions.HTTPError as e:
        print(f"Error getting status: {e}")

if __name__ == "__main__":
    main()