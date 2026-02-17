# FACTLESS - AI Reliability Analysis Engine

A post-generation hallucination risk assessment system that analyzes AI-generated text using internal linguistic patterns only.

![FACTLESS Demo](https://img.shields.io/badge/Status-Production%20Ready-green)
![Python](https://img.shields.io/badge/Python-3.11+-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-Latest-green)
![License](https://img.shields.io/badge/License-MIT-blue)

## 🎯 Core Principles

- **Analysis Only**: No content generation, rewriting, or fact-checking
- **Internal Signals**: Uses linguistic and structural patterns, not external knowledge
- **Explainable**: Every risk signal is attributable to specific text segments
- **Model Agnostic**: Works with output from any LLM
- **Offline Capable**: No external dependencies for core analysis
- **Ethical AI**: Never asserts factual correctness, only risk assessment

## 🏗️ Architecture

FACTLESS operates as a deterministic 7-step pipeline:

1. **Sentence Segmentation** - Break text into analyzable units
2. **Claim Extraction** - Identify assertive statements using Gemini API
3. **Contradiction Detection** - Find semantic conflicts using SBERT
4. **Logical Flow Validation** - Detect reasoning flaws
5. **Overconfidence Analysis** - Identify absolute language patterns
6. **Claim Density Analysis** - Measure information density
7. **Entity Fabrication Detection** - Flag suspicious entities

## 🚀 Quick Start

### One-Command Installation

**Windows:**
```bash
install.bat
```

**Mac/Linux:**
```bash
python install.py
```

This will:
- Install all dependencies
- Download required models
- Optionally setup Gemini API
- Run tests to verify installation

### Start the Server

**Windows:**
```bash
start.bat
```

**Mac/Linux:**
```bash
python start_server.py
```

Then open: **http://localhost:8000**

### Manual Installation

If you prefer manual setup:

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   python -m spacy download en_core_web_sm
   ```

2. **Test installation**
   ```bash
   python test_api.py
   ```

3. **Start server**
   ```bash
   python start_server.py
   ```

See [QUICKSTART.md](QUICKSTART.md) for detailed instructions and troubleshooting.

## 🖥️ Web Interface

The included web interface provides:

- **Real-time Analysis**: Instant hallucination risk assessment
- **Visual Risk Scoring**: Color-coded risk levels (LOW/MEDIUM/HIGH)
- **Detailed Explanations**: Sentence-level attribution of risk signals
- **Module Insights**: Optional detailed analysis from each pipeline step
- **Example Texts**: Pre-loaded examples for testing

### Features

- 📊 **Risk Score Visualization** with progress bars
- 🔍 **Detailed Explanations** for each detected signal
- ⚙️ **Module Analysis** showing internal processing details
- 📝 **Example Library** with different risk levels
- 🎨 **Responsive Design** for desktop and mobile

## 🔧 API Usage

### Analyze Single Text

```bash
curl -X POST "http://localhost:8000/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Your AI-generated text here",
    "include_module_details": true
  }'
```

### Python SDK

```python
from factless import FactlessAnalyzer

analyzer = FactlessAnalyzer()
result = analyzer.analyze("Your AI-generated text here")

print(f"Risk Score: {result.risk_score}")
print(f"Risk Level: {result.risk_level}")
for explanation in result.explanations:
    print(f"- {explanation.description}")
```

## 📊 Risk Assessment

### Risk Levels

- **LOW** (0.0 - 0.3): Minimal hallucination indicators
- **MEDIUM** (0.3 - 0.7): Some concerning patterns detected
- **HIGH** (0.7 - 1.0): Multiple risk signals present

### Signal Types

- **Contradictions**: Semantic conflicts between claims
- **Logical Flaws**: Circular reasoning, missing assumptions
- **Overconfidence**: Absolute language without uncertainty
- **Claim Density**: Unusually high information density
- **Entity Fabrication**: Suspicious or unexplained entities

## 🐳 Docker Deployment

### Development

```bash
# Set your Gemini API key
export GEMINI_API_KEY="your_api_key_here"

# Run with Docker Compose
docker-compose up --build
```

### Production

```bash
# Build image
docker build -t factless:latest .

# Run container
docker run -d \
  -p 8000:8000 \
  -e GEMINI_API_KEY="your_api_key_here" \
  factless:latest
```

## 🧪 Testing

Run the test suite:

```bash
# Install test dependencies
pip install pytest pytest-asyncio

# Run tests
pytest

# Run with coverage
pytest --cov=factless
```

## ⚙️ Configuration

### Environment Variables

```bash
# API Configuration
GEMINI_API_KEY=your_gemini_api_key_here
FACTLESS_LOG_LEVEL=INFO

# Analysis Settings
MAX_TEXT_LENGTH=10000
ENABLE_DETAILED_LOGGING=true

# Risk Thresholds
RISK_LOW_THRESHOLD=0.3
RISK_HIGH_THRESHOLD=0.7
```

### Custom Configuration

```python
from factless import FactlessAnalyzer, FactlessConfig

config = FactlessConfig()
config.risk_thresholds.low_threshold = 0.2
config.module_weights.overconfidence = 0.3

analyzer = FactlessAnalyzer(config)
```

## 📈 Performance

- **Latency**: < 2 seconds for 1000 words
- **Memory**: ~500MB base + 50MB per request
- **Scalability**: Stateless design enables horizontal scaling
- **Throughput**: Optimized for CPU-intensive NLP operations

## 🔒 Security & Privacy

- **No Data Persistence**: Input text is not stored
- **Offline Operation**: No external API calls required (except optional Gemini)
- **Input Validation**: Prevents injection attacks
- **Deterministic**: Reproducible results for audit trails

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **SpaCy** for NLP processing
- **Sentence Transformers** for semantic similarity
- **FastAPI** for the API framework
- **Google Gemini** for claim extraction
- **Tailwind CSS** for the frontend styling

## 📞 Support

- 📖 **Documentation**: See `/docs` endpoint when running
- 🐛 **Issues**: Report bugs via GitHub issues
- 💬 **Discussions**: Use GitHub discussions for questions

---

**FACTLESS** - Reliable AI analysis through explainable internal pattern detection.