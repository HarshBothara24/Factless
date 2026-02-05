#!/usr/bin/env python3
"""
Development server runner for FACTLESS.
"""

import os
import sys
import subprocess
from pathlib import Path

def check_requirements():
    """Check if required dependencies are installed."""
    try:
        import spacy
        import nltk
        import sentence_transformers
        import fastapi
        import google.generativeai
        print("✓ All required packages are installed")
        return True
    except ImportError as e:
        print(f"✗ Missing required package: {e}")
        print("Please run: pip install -r requirements.txt")
        return False

def check_spacy_model():
    """Check if SpaCy model is downloaded."""
    try:
        import spacy
        nlp = spacy.load("en_core_web_sm")
        print("✓ SpaCy model 'en_core_web_sm' is available")
        return True
    except OSError:
        print("✗ SpaCy model 'en_core_web_sm' not found")
        print("Please run: python -m spacy download en_core_web_sm")
        return False

def check_gemini_api_key():
    """Check if Gemini API key is configured."""
    api_key = os.getenv("GEMINI_API_KEY")
    if api_key:
        print("✓ Gemini API key is configured")
        return True
    else:
        print("⚠ Gemini API key not found in environment")
        print("Set GEMINI_API_KEY environment variable or create .env file")
        print("The system will use fallback mock responses for claim extraction")
        return False

def load_env_file():
    """Load environment variables from .env file if it exists."""
    env_file = Path(".env")
    if env_file.exists():
        print("✓ Loading environment variables from .env file")
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key] = value
    else:
        print("ℹ No .env file found (optional)")

def main():
    """Main function to run the development server."""
    print("🚀 Starting FACTLESS Development Server")
    print("=" * 50)
    
    # Load environment variables
    load_env_file()
    
    # Check requirements
    if not check_requirements():
        sys.exit(1)
    
    if not check_spacy_model():
        sys.exit(1)
    
    check_gemini_api_key()
    
    # Set Python path
    current_dir = Path(__file__).parent.absolute()
    os.environ["PYTHONPATH"] = str(current_dir)
    
    print("\n🌐 Starting FastAPI server...")
    print("Frontend will be available at: http://localhost:8000")
    print("API documentation at: http://localhost:8000/docs")
    print("Press Ctrl+C to stop the server")
    print("=" * 50)
    
    # Start the server
    try:
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "api.main:app", 
            "--host", "0.0.0.0", 
            "--port", "8000", 
            "--reload",
            "--reload-dir", "factless",
            "--reload-dir", "api",
            "--reload-dir", "frontend"
        ])
    except KeyboardInterrupt:
        print("\n👋 Server stopped")

if __name__ == "__main__":
    main()