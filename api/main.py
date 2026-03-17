"""
FastAPI application for FACTLESS analysis engine.
"""

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field
from typing import List, Optional
import time
from loguru import logger

from factless import FactlessAnalyzer, AnalysisResult, RiskLevel
from factless.config import FactlessConfig

# Initialize FastAPI app
app = FastAPI(
    title="FACTLESS API",
    description="AI Reliability Analysis Engine - Post-generation hallucination risk assessment",
    version="1.0.0"
)

# Add CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for frontend
app.mount("/static", StaticFiles(directory="frontend"), name="static")

# Initialize analyzer
config = FactlessConfig()

# Try to initialize analyzer at startup
try:
    logger.info("Initializing FACTLESS analyzer...")
    analyzer = FactlessAnalyzer(config)
    logger.info("✓ Analyzer initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize analyzer: {e}")
    analyzer = None


# Request/Response models
class AnalysisRequest(BaseModel):
    """Request model for text analysis."""
    text: str = Field(..., description="AI-generated text to analyze", min_length=1, max_length=10000)
    include_module_details: bool = Field(default=False, description="Include detailed module results in response")


class BatchAnalysisRequest(BaseModel):
    """Request model for batch text analysis."""
    texts: List[str] = Field(..., description="List of AI-generated texts to analyze", max_items=10)
    include_module_details: bool = Field(default=False, description="Include detailed module results in response")


class AnalysisResponse(BaseModel):
    """Response model for analysis results."""
    risk_score: float = Field(..., description="Hallucination risk score (0-1)")
    risk_level: RiskLevel = Field(..., description="Risk level category")
    explanations: List[dict] = Field(..., description="Human-readable explanations")
    processing_time_ms: float = Field(..., description="Total processing time in milliseconds")
    input_length: int = Field(..., description="Length of input text")
    module_details: Optional[dict] = Field(None, description="Detailed module results (if requested)")


class StatusResponse(BaseModel):
    """Response model for system status."""
    status: str
    version: str
    modules: dict
    config: dict


# API Endpoints
@app.get("/", response_class=HTMLResponse)
async def serve_frontend():
    """Serve the frontend application."""
    try:
        with open("frontend/index.html", "r") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        return HTMLResponse(content="""
        <html>
            <body>
                <h1>FACTLESS API</h1>
                <p>Frontend not found. API endpoints available at:</p>
                <ul>
                    <li><a href="/docs">/docs - API Documentation</a></li>
                    <li><a href="/analyze">/analyze - Analyze Text (POST)</a></li>
                    <li><a href="/status">/status - System Status</a></li>
                </ul>
            </body>
        </html>
        """)


@app.get("/api", response_model=dict)
async def api_info():
    """API information endpoint."""
    return {
        "name": "FACTLESS API",
        "description": "AI Reliability Analysis Engine",
        "version": "1.0.0",
        "endpoints": {
            "analyze": "/analyze - Analyze single text",
            "batch": "/analyze/batch - Analyze multiple texts",
            "status": "/status - System status"
        }
    }


@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_text(request: AnalysisRequest):
    """
    Analyze a single text for hallucination risk.
    
    Returns risk score, level, and explanations based on internal linguistic patterns.
    """
    try:
        logger.info(f"Received analysis request: {len(request.text)} characters")
        
        # Perform analysis
        result = analyzer.analyze(request.text)
        
        logger.info(f"Analysis complete: risk={result.risk_level.value}, score={result.risk_score:.3f}")
        
        # Prepare response
        response_data = {
            "risk_score": result.risk_score,
            "risk_level": result.risk_level,
            "explanations": [
                {
                    "signal_type": exp.signal_type,
                    "sentence_indices": exp.sentence_indices,
                    "description": exp.description,
                    "risk_contribution": exp.risk_contribution
                }
                for exp in result.explanations
            ],
            "processing_time_ms": result.total_processing_time_ms,
            "input_length": result.input_text_length
        }
        
        # Add module details if requested
        if request.include_module_details:
            response_data["module_details"] = {
                "sentence_count": len(result.sentence_segmentation.sentences),
                "claim_count": len(result.claim_extraction.claims),
                "contradiction_count": len(result.contradiction_detection.contradictions),
                "logical_flaw_count": len(result.logical_flow.logical_flaws),
                "overconfidence_signals": len(result.overconfidence_analysis.overconfidence_signals),
                "claim_density": result.claim_density.claim_density,
                "suspicious_entities": len(result.entity_fabrication.suspicious_entities),
                "plausibility_signals": len(result.plausibility_analysis.signals)
            }
        
        return AnalysisResponse(**response_data)
        
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Analysis failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")
        
        return AnalysisResponse(**response_data)
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@app.post("/analyze/batch", response_model=List[AnalysisResponse])
async def analyze_batch(request: BatchAnalysisRequest):
    """
    Analyze multiple texts for hallucination risk.
    
    Returns list of analysis results for each input text.
    """
    try:
        # Validate batch size
        if len(request.texts) > 10:
            raise HTTPException(status_code=400, detail="Batch size cannot exceed 10 texts")
        
        results = []
        
        for text in request.texts:
            try:
                # Perform analysis
                result = analyzer.analyze(text)
                
                # Prepare response
                response_data = {
                    "risk_score": result.risk_score,
                    "risk_level": result.risk_level,
                    "explanations": [
                        {
                            "signal_type": exp.signal_type,
                            "sentence_indices": exp.sentence_indices,
                            "description": exp.description,
                            "risk_contribution": exp.risk_contribution
                        }
                        for exp in result.explanations
                    ],
                    "processing_time_ms": result.total_processing_time_ms,
                    "input_length": result.input_text_length
                }
                
                # Add module details if requested
                if request.include_module_details:
                    response_data["module_details"] = {
                        "sentence_count": len(result.sentence_segmentation.sentences),
                        "claim_count": len(result.claim_extraction.claims),
                        "contradiction_count": len(result.contradiction_detection.contradictions),
                        "logical_flaw_count": len(result.logical_flow.logical_flaws),
                        "overconfidence_signals": len(result.overconfidence_analysis.overconfidence_signals),
                        "claim_density": result.claim_density.claim_density,
                        "suspicious_entities": len(result.entity_fabrication.suspicious_entities),
                        "plausibility_signals": len(result.plausibility_analysis.signals)
                    }
                
                results.append(AnalysisResponse(**response_data))
                
            except Exception as e:
                # Add error result for failed analysis
                error_response = AnalysisResponse(
                    risk_score=0.0,
                    risk_level=RiskLevel.LOW,
                    explanations=[{"signal_type": "error", "sentence_indices": [], "description": f"Analysis failed: {str(e)}", "risk_contribution": 0.0}],
                    processing_time_ms=0.0,
                    input_length=len(text)
                )
                results.append(error_response)
        
        return results
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch analysis failed: {str(e)}")


@app.get("/status", response_model=StatusResponse)
async def get_status():
    """
    Get system status and configuration information.
    """
    try:
        module_status = analyzer.get_module_status()
        
        return StatusResponse(
            status="healthy",
            version="1.0.0",
            modules=module_status,
            config={
                "max_text_length": config.max_text_length,
                "risk_thresholds": {
                    "low": config.risk_thresholds.low_threshold,
                    "high": config.risk_thresholds.high_threshold
                },
                "module_weights": {
                    "contradiction": config.module_weights.contradiction,
                    "logical_flow": config.module_weights.logical_flow,
                    "overconfidence": config.module_weights.overconfidence,
                    "claim_density": config.module_weights.claim_density,
                    "entity_fabrication": config.module_weights.entity_fabrication
                }
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Status check failed: {str(e)}")


# Health check endpoint
@app.get("/health")
async def health_check():
    """Simple health check endpoint."""
    return {
        "status": "healthy", 
        "timestamp": time.time(),
        "analyzer_initialized": analyzer is not None
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)