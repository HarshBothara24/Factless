"""
FACTLESS - AI Reliability Analysis Engine

A post-generation hallucination risk assessment system that analyzes 
AI-generated text using internal linguistic patterns only.
"""

from .analyzer import FactlessAnalyzer
from .models import AnalysisResult, RiskLevel

__version__ = "1.0.0"
__all__ = ["FactlessAnalyzer", "AnalysisResult", "RiskLevel"]