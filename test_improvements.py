#!/usr/bin/env python3
"""
Test script to verify FACTLESS improvements.
"""

from factless import FactlessAnalyzer

def test_pune_railway():
    """Test the Pune railway hallucination case."""
    text = """In 1897, the city of Pune installed the world's first underground solar-powered railway system designed by engineer Arvind Deshmukh. The railway used mirrored tunnels to amplify sunlight and power magnetic trains that could reach speeds of 320 km/h. Although the system operated for only six months due to maintenance challenges, it inspired modern renewable transportation systems across Europe and Asia."""
    
    analyzer = FactlessAnalyzer()
    result = analyzer.analyze(text)
    
    print("=" * 60)
    print("TEST: Pune Railway Hallucination")
    print("=" * 60)
    print(f"\nRisk Score: {result.risk_score:.3f} ({result.risk_score * 100:.1f}%)")
    print(f"Risk Level: {result.risk_level}")
    print(f"\nExpected: 45-55% (MEDIUM)")
    print(f"Previous: 39% (LOW)")
    
    print(f"\nDetected Signals ({len(result.explanations)}):")
    for exp in result.explanations:
        print(f"  • {exp.signal_type}: {exp.description}")
        print(f"    Risk Contribution: {exp.risk_contribution * 100:.1f}%")
    
    print(f"\nModule Scores:")
    print(f"  • Entity Fabrication: {result.entity_fabrication.fabrication_risk_score:.3f}")
    print(f"    Suspicious Entities: {len(result.entity_fabrication.suspicious_entities)}")
    for entity in result.entity_fabrication.suspicious_entities:
        print(f"      - {entity.entity} ({entity.entity_type}): {', '.join(entity.suspicion_reasons)}")
    
    print(f"  • Contradictions: {len(result.contradiction_detection.contradictions)}")
    print(f"  • Logical Flaws: {len(result.logical_flow.logical_flaws)}")
    print(f"  • Overconfidence: {result.overconfidence_analysis.avg_confidence_score:.3f}")
    print(f"  • Claim Density: {result.claim_density.claim_density:.2f}")
    
    return result

def test_obvious_contradiction():
    """Test obvious contradiction case."""
    text = """Python is absolutely the fastest programming language ever created, guaranteed 100% perfect execution. However, Python is also the slowest language for computational tasks."""
    
    analyzer = FactlessAnalyzer()
    result = analyzer.analyze(text)
    
    print("\n" + "=" * 60)
    print("TEST: Obvious Contradiction")
    print("=" * 60)
    print(f"\nRisk Score: {result.risk_score:.3f} ({result.risk_score * 100:.1f}%)")
    print(f"Risk Level: {result.risk_level}")
    print(f"\nExpected: 70-80% (HIGH)")
    
    print(f"\nDetected Signals ({len(result.explanations)}):")
    for exp in result.explanations:
        print(f"  • {exp.signal_type}: {exp.description}")
    
    return result

def test_low_risk():
    """Test low risk case."""
    text = """Machine learning is a subset of artificial intelligence that focuses on algorithms that can learn from data. It's commonly used in applications like recommendation systems and image recognition."""
    
    analyzer = FactlessAnalyzer()
    result = analyzer.analyze(text)
    
    print("\n" + "=" * 60)
    print("TEST: Low Risk Text")
    print("=" * 60)
    print(f"\nRisk Score: {result.risk_score:.3f} ({result.risk_score * 100:.1f}%)")
    print(f"Risk Level: {result.risk_level}")
    print(f"\nExpected: 10-20% (LOW)")
    
    print(f"\nDetected Signals ({len(result.explanations)}):")
    if result.explanations:
        for exp in result.explanations:
            print(f"  • {exp.signal_type}: {exp.description}")
    else:
        print("  No significant risk signals detected")
    
    return result

def main():
    """Run all tests."""
    print("\n🧪 FACTLESS Improvement Tests\n")
    
    try:
        # Test 1: Pune Railway (main issue)
        result1 = test_pune_railway()
        
        # Test 2: Obvious contradiction
        result2 = test_obvious_contradiction()
        
        # Test 3: Low risk baseline
        result3 = test_low_risk()
        
        # Summary
        print("\n" + "=" * 60)
        print("SUMMARY")
        print("=" * 60)
        print(f"\n1. Pune Railway: {result1.risk_score * 100:.1f}% ({result1.risk_level})")
        print(f"   Improvement: {'✓ IMPROVED' if result1.risk_score > 0.39 else '✗ NO CHANGE'}")
        
        print(f"\n2. Contradiction: {result2.risk_score * 100:.1f}% ({result2.risk_level})")
        print(f"   Status: {'✓ HIGH RISK' if result2.risk_level == 'HIGH' else '⚠ NEEDS IMPROVEMENT'}")
        
        print(f"\n3. Low Risk: {result3.risk_score * 100:.1f}% ({result3.risk_level})")
        print(f"   Status: {'✓ LOW RISK' if result3.risk_level == 'LOW' else '⚠ FALSE POSITIVE'}")
        
        print("\n✅ All tests completed successfully!\n")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}\n")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()