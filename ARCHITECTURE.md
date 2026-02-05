# FACTLESS Architecture Design

## System Overview

FACTLESS is a post-generation AI reliability analysis engine that assesses hallucination risk in AI-generated text using internal linguistic patterns only. The system operates as a deterministic 7-step pipeline that produces explainable risk assessments.

## Core Principles

### Ethical AI Compliance
- **No Truth Claims**: FACTLESS never asserts factual correctness or incorrectness
- **Risk Assessment Only**: Provides risk indicators based on internal patterns
- **Explainable Results**: Every risk signal is attributable to specific text segments
- **Human-in-the-Loop**: Final decisions always remain with users

### Technical Constraints
- **No External Knowledge**: No retrieval, search, or external fact-checking
- **Model Agnostic**: Works with output from any LLM
- **Deterministic**: Reproducible results for the same input
- **Offline Capable**: No internet dependencies for core analysis

## Architecture Components

### 1. Analysis Pipeline (7 Steps)

```
Input Text → Step 1 → Step 2 → Step 3 → Step 4 → Step 5 → Step 6 → Step 7 → Risk Score + Explanations
```

#### Step 1: Sentence Segmentation
- **Purpose**: Break text into analyzable units
- **Technology**: SpaCy + NLTK fallback
- **Output**: List of sentences with character positions
- **Special Handling**: Splits long compound sentences

#### Step 2: Claim Extraction
- **Purpose**: Identify assertive statements
- **Technology**: Lightweight LLM (temperature=0, constrained)
- **LLM Role**: Linguistic parser only, not fact-checker
- **Output**: Structured claims with confidence markers
- **Constraints**: No new information added, strict JSON output

#### Step 3: Contradiction Detection
- **Purpose**: Find semantic conflicts between claims
- **Technology**: Sentence Transformers (SBERT)
- **Method**: Similarity analysis + opposition detection
- **Output**: Contradiction pairs with classification

#### Step 4: Logical Flow Validation
- **Purpose**: Detect reasoning flaws
- **Technology**: Pattern analysis + dependency graphs
- **Detects**: Circular reasoning, cause-effect inversions, missing assumptions
- **Output**: Logical flaw indicators

#### Step 5: Overconfidence Analysis
- **Purpose**: Identify absolute language patterns
- **Technology**: Pattern matching + linguistic analysis
- **Detects**: Absolute terms, lack of uncertainty markers
- **Output**: Confidence scores per sentence

#### Step 6: Claim Density Analysis
- **Purpose**: Measure information density
- **Technology**: Statistical analysis
- **Metric**: Claims per sentence + variance analysis
- **Output**: Density risk score

#### Step 7: Entity Fabrication Detection
- **Purpose**: Flag suspicious entities
- **Technology**: SpaCy NER + pattern analysis
- **Detects**: Academic fabrications, unexplained specificity
- **Output**: Suspicious entity flags

### 2. Scoring Engine

#### Weighted Aggregation
```python
final_score = (
    0.25 * contradiction_score +
    0.20 * logical_flow_score +
    0.15 * overconfidence_score +
    0.15 * claim_density_score +
    0.25 * entity_fabrication_score
)
```

#### Risk Level Classification
- **LOW**: score < 0.3
- **MEDIUM**: 0.3 ≤ score < 0.7  
- **HIGH**: score ≥ 0.7

### 3. Explainability System

#### Explanation Generation
- Maps internal signals to human-readable descriptions
- Attributes explanations to specific sentences
- Provides risk contribution scores
- Maintains transparency requirements

#### Example Explanation
```json
{
  "signal_type": "overconfidence",
  "sentence_indices": [2],
  "description": "Overconfident language detected: absolutely, guaranteed (confidence score: 0.85)",
  "risk_contribution": 0.13
}
```

## Technology Stack

### Core NLP
- **SpaCy**: Sentence segmentation, NER
- **NLTK**: Fallback sentence tokenization
- **Sentence Transformers**: Semantic similarity (SBERT)

### Math & Computation
- **NumPy**: Numerical operations
- **SciPy**: Statistical analysis, distance metrics

### API Layer
- **FastAPI**: REST API framework
- **Pydantic**: Data validation and serialization
- **Uvicorn**: ASGI server

### Deployment
- **Docker**: Containerization
- **Docker Compose**: Multi-service orchestration

## Data Flow

### Input Processing
1. Text validation (length, encoding)
2. Preprocessing (normalization)
3. Pipeline execution (7 steps)
4. Score calculation
5. Explanation generation

### Module Communication
- Each module is independent and stateless
- Structured data models for inter-module communication
- Comprehensive logging at each step
- Error handling with graceful degradation

### Output Structure
```python
AnalysisResult(
    risk_score: float,           # 0-1 overall risk
    risk_level: RiskLevel,       # LOW/MEDIUM/HIGH
    explanations: List[Explanation],
    module_results: {...},       # Detailed results from each step
    metadata: {...}              # Processing time, timestamps
)
```

## Performance Characteristics

### Latency Targets
- **Single Analysis**: < 2 seconds for 1000 words
- **Batch Processing**: Linear scaling
- **API Response**: < 100ms overhead

### Scalability
- **Stateless Design**: Horizontal scaling possible
- **Memory Efficient**: Streaming processing where possible
- **CPU Bound**: Optimized for CPU-intensive NLP operations

### Resource Requirements
- **Memory**: ~500MB base + 50MB per concurrent request
- **CPU**: Multi-core beneficial for batch processing
- **Storage**: Minimal (models cached in memory)

## Security & Privacy

### Data Handling
- **No Persistence**: Input text not stored
- **In-Memory Processing**: Temporary data only
- **No External Calls**: Offline operation

### Model Security
- **Deterministic Models**: Reproducible outputs
- **Version Pinning**: Consistent model versions
- **Input Validation**: Prevents injection attacks

## Monitoring & Observability

### Logging
- **Structured Logs**: JSON format with correlation IDs
- **Module-Level**: Detailed logs from each pipeline step
- **Performance Metrics**: Processing times, error rates

### Health Checks
- **API Health**: Endpoint availability
- **Model Health**: NLP model loading status
- **Resource Health**: Memory and CPU utilization

### Audit Trail
- **Analysis Logs**: Complete processing history
- **Configuration Tracking**: Settings and model versions
- **Error Tracking**: Failure analysis and recovery

## Extension Points

### Custom Modules
- **Base Module Class**: Standardized interface
- **Plugin Architecture**: Easy addition of new analysis steps
- **Configuration System**: Flexible parameter tuning

### Custom Scoring
- **Weighted Combinations**: Adjustable module weights
- **Threshold Tuning**: Customizable risk levels
- **Domain Adaptation**: Specialized configurations

### Integration Options
- **REST API**: Standard HTTP interface
- **Python SDK**: Direct library integration
- **Batch Processing**: File-based analysis
- **Streaming**: Real-time analysis pipeline

## Production Considerations

### Deployment Patterns
- **Single Instance**: Docker container
- **Load Balanced**: Multiple instances behind proxy
- **Microservices**: Separate services per module

### Configuration Management
- **Environment Variables**: Runtime configuration
- **Config Files**: Complex settings
- **Feature Flags**: Experimental features

### Error Handling
- **Graceful Degradation**: Partial results on module failure
- **Retry Logic**: Transient error recovery
- **Circuit Breakers**: Prevent cascade failures

This architecture ensures FACTLESS operates as a reliable, explainable, and ethical AI reliability assessment system while maintaining high performance and scalability.