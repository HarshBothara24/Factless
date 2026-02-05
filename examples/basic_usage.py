"""
Basic usage examples for FACTLESS analyzer.
"""

from factless import FactlessAnalyzer, FactlessConfig

def main():
    # Initialize analyzer with default configuration
    analyzer = FactlessAnalyzer()
    
    # Example 1: Low risk text
    low_risk_text = """
    Machine learning is a subset of artificial intelligence that focuses on algorithms 
    that can learn from data. It's commonly used in applications like recommendation 
    systems and image recognition. The field has grown significantly in recent years.
    """
    
    print("=== Example 1: Low Risk Text ===")
    result = analyzer.analyze(low_risk_text)
    print(f"Risk Score: {result.risk_score:.3f}")
    print(f"Risk Level: {result.risk_level}")
    print("Explanations:")
    for exp in result.explanations:
        print(f"  - {exp.description}")
    print()
    
    # Example 2: High risk text with contradictions and overconfidence
    high_risk_text = """
    Python is definitely the fastest programming language ever created, with absolutely 
    zero performance issues. It was invented in 1995 by Dr. John Smith at MIT University. 
    However, Python is also the slowest language for computational tasks. The language 
    guarantees 100% perfect execution in all scenarios. According to the Journal of 
    Computer Excellence (2023), Python processes data at 15.847392 teraflops per second.
    """
    
    print("=== Example 2: High Risk Text ===")
    result = analyzer.analyze(high_risk_text)
    print(f"Risk Score: {result.risk_score:.3f}")
    print(f"Risk Level: {result.risk_level}")
    print("Explanations:")
    for exp in result.explanations:
        print(f"  - {exp.description}")
    print()
    
    # Example 3: Custom configuration
    custom_config = FactlessConfig()
    custom_config.risk_thresholds.low_threshold = 0.2
    custom_config.risk_thresholds.high_threshold = 0.6
    custom_config.module_weights.overconfidence = 0.3  # Increase overconfidence weight
    
    custom_analyzer = FactlessAnalyzer(custom_config)
    
    print("=== Example 3: Custom Configuration ===")
    result = custom_analyzer.analyze(high_risk_text)
    print(f"Risk Score: {result.risk_score:.3f}")
    print(f"Risk Level: {result.risk_level}")
    print()
    
    # Example 4: Batch analysis
    texts = [
        "The weather is nice today.",
        "AI will definitely replace all human jobs by next Tuesday, guaranteed.",
        "Research suggests that climate change may impact weather patterns."
    ]
    
    print("=== Example 4: Batch Analysis ===")
    results = analyzer.analyze_batch(texts)
    for i, result in enumerate(results):
        print(f"Text {i+1}: Risk={result.risk_level.value}, Score={result.risk_score:.3f}")
    print()
    
    # Example 5: Module status
    print("=== Example 5: Module Status ===")
    status = analyzer.get_module_status()
    for module, info in status.items():
        print(f"{module}: {info}")

if __name__ == "__main__":
    main()